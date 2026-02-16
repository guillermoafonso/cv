# Setup: Counting Game at Boot

This makes the counting game run automatically when the Raspberry Pi
starts up. The child must complete the game before the desktop loads.

## Setup Steps

### 1. Make the boot script executable

```bash
chmod +x ~/cv/boot_game.sh
```

### 2. Edit the service file with your username

If your Pi username is NOT `pi`, edit `counting-game.service` and
replace both instances of `pi` with your actual username:

```bash
nano ~/cv/counting-game.service
```

Change these two lines:
- `ExecStart=/home/pi/cv/boot_game.sh` → `/home/YOURUSERNAME/cv/boot_game.sh`
- `User=pi` → `User=YOURUSERNAME`

### 3. Install the systemd service

```bash
sudo cp ~/cv/counting-game.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable counting-game.service
```

### 4. Reboot to test

```bash
sudo reboot
```

The counting game should appear before the desktop loads.

## How to Disable

If you want to stop the game from running at boot:

```bash
sudo systemctl disable counting-game.service
sudo reboot
```

## How to Re-enable

```bash
sudo systemctl enable counting-game.service
sudo reboot
```

## Troubleshooting

Check if the service ran correctly:
```bash
sudo systemctl status counting-game.service
sudo journalctl -u counting-game.service
```

If the game doesn't display, the video driver may need changing.
Check the log output above for errors.
