#!/usr/bin/env python3
"""Screen Timer - Parental control overlay timer for Wayland (Raspberry Pi).

Monitors specified processes and displays a countdown overlay.
When time runs out, the monitored process is terminated.
Runs as a systemd system service for bypass resistance.

Configuration: /etc/screen-timer/config.json
State:         /var/lib/screen-timer/state.json

Admin commands:
  screen-timer --status              Show remaining time
  screen-timer --reset               Reset to full daily allowance
  screen-timer --add-time MINUTES    Add extra minutes
  screen-timer --set-time MINUTES    Set remaining time to exact value
"""

import json
import os
import signal
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

CONFIG_PATH = "/etc/screen-timer/config.json"
STATE_PATH = "/var/lib/screen-timer/state.json"


# ---------------------------------------------------------------------------
# Config / state helpers
# ---------------------------------------------------------------------------

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_state(config):
    """Load state, performing a daily reset if the date has changed."""
    try:
        with open(STATE_PATH) as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}

    today = date.today().isoformat()
    if state.get("date") != today:
        state = {
            "date": today,
            "remaining_seconds": config["daily_minutes"] * 60,
        }
        save_state(state)

    return state


def save_state(state):
    Path(STATE_PATH).parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_PATH)


# ---------------------------------------------------------------------------
# Process helpers
# ---------------------------------------------------------------------------

def find_process(name, user=None):
    """Return the PID of a running process (or None)."""
    try:
        cmd = ["pgrep", "-x", name]
        if user:
            cmd = ["pgrep", "-u", user, "-x", name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return int(result.stdout.strip().split("\n")[0])
    except Exception:
        pass
    return None


def find_any_process(names, user=None):
    """Return (pid, name) for the first matching process, or (None, None)."""
    for name in names:
        pid = find_process(name, user)
        if pid is not None:
            return pid, name
    return None, None


def kill_processes(names, user=None):
    for name in names:
        try:
            cmd = ["pkill", "-x", name]
            if user:
                cmd = ["pkill", "-u", user, "-x", name]
            subprocess.run(cmd)
        except Exception:
            pass


def get_wayland_env(pid):
    """Extract Wayland-related env vars from a running process."""
    try:
        raw = Path(f"/proc/{pid}/environ").read_text()
        environ = raw.split("\0")
        keys = {
            "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR", "DISPLAY",
            "DBUS_SESSION_BUS_ADDRESS", "GDK_BACKEND",
        }
        env = {}
        for var in environ:
            if "=" in var:
                k, v = var.split("=", 1)
                if k in keys:
                    env[k] = v
        return env
    except (PermissionError, FileNotFoundError):
        return {}


# ---------------------------------------------------------------------------
# Overlay (runs in a subprocess)
# ---------------------------------------------------------------------------

def run_overlay(remaining_seconds, warn_seconds, watch_processes, watch_user):
    """GTK3 + gtk-layer-shell overlay. Called in a child process."""
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        gi.require_version("GtkLayerShell", "0.1")
        from gi.repository import Gdk, GLib, Gtk, GtkLayerShell
    except (ImportError, ValueError) as e:
        print(
            f"screen-timer: overlay dependencies missing: {e}\n"
            "Install with: sudo apt install python3-gi "
            "gir1.2-gtk-3.0 gir1.2-gtklayershell-0.1",
            file=sys.stderr,
        )
        sys.exit(1)

    save_counter = 0

    class OverlayWindow(Gtk.Window):
        def __init__(self):
            super().__init__()
            self.remaining = remaining_seconds
            self.quitting = False

            # -- layer-shell setup --
            GtkLayerShell.init_for_window(self)
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
            GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 10)
            GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 10)
            GtkLayerShell.set_keyboard_mode(
                self, GtkLayerShell.KeyboardMode.NONE
            )
            GtkLayerShell.set_exclusive_zone(self, 0)

            # -- widgets --
            self.label = Gtk.Label()
            self.add(self.label)

            # -- CSS --
            self.css = Gtk.CssProvider()
            self._apply_style(warning=False)
            screen = Gdk.Screen.get_default()
            if screen:
                Gtk.StyleContext.add_provider_for_screen(
                    screen, self.css,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
                )

            self._update_display()

            # -- timers --
            GLib.timeout_add(1000, self._tick)
            GLib.timeout_add(5000, self._check_process)

            self.connect("destroy", self._on_destroy)
            self.show_all()

        # --- styling ---

        def _apply_style(self, warning):
            if warning:
                data = b"""window {
                    background-color: rgba(180, 0, 0, 0.9);
                    border-radius: 12px;
                    padding: 10px 18px;
                }"""
            else:
                data = b"""window {
                    background-color: rgba(0, 0, 0, 0.75);
                    border-radius: 12px;
                    padding: 8px 16px;
                }"""
            self.css.load_from_data(data)

        # --- display ---

        @staticmethod
        def _fmt(seconds):
            m, s = divmod(max(0, seconds), 60)
            return f"{m:02d}:{s:02d}"

        def _update_display(self):
            t = self._fmt(self.remaining)
            if self.remaining <= warn_seconds:
                self._apply_style(warning=True)
                col = "#ffffff"
                if self.remaining <= 10:
                    col = "#ffffff" if self.remaining % 2 == 0 else "#ffaaaa"
                self.label.set_markup(
                    f'<span font="28" color="{col}" weight="bold">{t}</span>'
                    f'\n<span font="12" color="#ffffff">'
                    f"Closing in {self.remaining}s</span>"
                )
            else:
                self._apply_style(warning=False)
                self.label.set_markup(
                    f'<span font="24" color="white">{t}</span>'
                )

        # --- callbacks ---

        def _tick(self):
            nonlocal save_counter
            if self.quitting:
                return False

            if self.remaining > 0:
                self.remaining -= 1
                self._update_display()

                save_counter += 1
                if save_counter >= 10:
                    save_counter = 0
                    self._persist()

                if self.remaining <= 0:
                    self._persist()
                    kill_processes(watch_processes, watch_user)
                    GLib.timeout_add(2000, self._quit)
                    return False

            return True

        def _check_process(self):
            if self.quitting:
                return False
            pid, _ = find_any_process(watch_processes, watch_user)
            if pid is None:
                self._persist()
                self._quit()
                return False
            return True

        # --- state ---

        def _persist(self):
            try:
                state = {"date": date.today().isoformat(),
                         "remaining_seconds": self.remaining}
                save_state(state)
            except Exception:
                pass

        def _quit(self):
            self.quitting = True
            Gtk.main_quit()
            return False

        def _on_destroy(self, _widget):
            self._persist()

    win = OverlayWindow()

    def _sig_handler(_sig, _frame):
        win._persist()
        Gtk.main_quit()

    signal.signal(signal.SIGTERM, _sig_handler)
    signal.signal(signal.SIGINT, _sig_handler)

    Gtk.main()


# ---------------------------------------------------------------------------
# Monitor loop (main process, runs as root via systemd)
# ---------------------------------------------------------------------------

def monitor():
    config = load_config()
    procs = config.get("watch_processes", ["minetest"])
    user = config.get("watch_user")
    warn = config.get("warn_seconds", 60)

    print(f"screen-timer: watching {procs} for user={user or 'any'}")

    while True:
        # wait for a watched process to appear
        pid, proc_name = find_any_process(procs, user)
        if pid is None:
            time.sleep(3)
            continue

        print(f"screen-timer: detected {proc_name} (pid {pid})")

        state = load_state(config)
        remaining = state["remaining_seconds"]

        if remaining <= 0:
            print("screen-timer: no time left today, terminating process")
            kill_processes(procs, user)
            time.sleep(10)
            continue

        # resolve Wayland display from the target process
        wayland_env = get_wayland_env(pid)
        if not wayland_env.get("WAYLAND_DISPLAY"):
            print("screen-timer: WAYLAND_DISPLAY not found, retrying...")
            time.sleep(5)
            continue

        print(f"screen-timer: launching overlay ({remaining}s remaining)")

        env = os.environ.copy()
        env.update(wayland_env)
        env["GDK_BACKEND"] = "wayland"

        try:
            overlay = subprocess.Popen(
                [sys.executable, os.path.abspath(__file__), "--overlay"],
                env=env,
            )
            overlay.wait()
        except Exception as e:
            print(f"screen-timer: overlay error: {e}", file=sys.stderr)

        print("screen-timer: overlay exited, resuming monitor")
        time.sleep(2)


# ---------------------------------------------------------------------------
# Admin CLI
# ---------------------------------------------------------------------------

def cmd_status():
    config = load_config()
    state = load_state(config)
    m, s = divmod(state["remaining_seconds"], 60)
    total = config["daily_minutes"]
    print(f"Date:       {state['date']}")
    print(f"Remaining:  {m}m {s}s")
    print(f"Daily limit: {total}m")
    print(f"Processes:  {config.get('watch_processes', [])}")
    print(f"User:       {config.get('watch_user', 'any')}")


def cmd_reset():
    config = load_config()
    state = {
        "date": date.today().isoformat(),
        "remaining_seconds": config["daily_minutes"] * 60,
    }
    save_state(state)
    print(f"Reset to {config['daily_minutes']} minutes.")


def cmd_add_time(minutes):
    config = load_config()
    state = load_state(config)
    state["remaining_seconds"] += minutes * 60
    save_state(state)
    m, s = divmod(state["remaining_seconds"], 60)
    print(f"Added {minutes}m. Remaining: {m}m {s}s")


def cmd_set_time(minutes):
    config = load_config()
    state = load_state(config)
    state["remaining_seconds"] = minutes * 60
    save_state(state)
    print(f"Set to {minutes}m.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        monitor()
        return

    cmd = sys.argv[1]

    if cmd == "--overlay":
        config = load_config()
        state = load_state(config)
        run_overlay(
            remaining_seconds=state["remaining_seconds"],
            warn_seconds=config.get("warn_seconds", 60),
            watch_processes=config.get("watch_processes", ["minetest"]),
            watch_user=config.get("watch_user"),
        )
    elif cmd == "--status":
        cmd_status()
    elif cmd == "--reset":
        cmd_reset()
    elif cmd == "--add-time":
        if len(sys.argv) < 3:
            print("Usage: screen-timer --add-time MINUTES")
            sys.exit(1)
        cmd_add_time(int(sys.argv[2]))
    elif cmd == "--set-time":
        if len(sys.argv) < 3:
            print("Usage: screen-timer --set-time MINUTES")
            sys.exit(1)
        cmd_set_time(int(sys.argv[2]))
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
