#!/usr/bin/env python3
"""
Symbol Counting & Spelling Game for Raspberry Pi
Two game modes: count symbols or spell words from pictures.
Uses Pygame for fullscreen display and drawing.

Configuration: Edit config.json to change settings remotely
Statistics: View stats.json to see game progress and errors
"""

import random
import os
import math
import json
import sys
import signal
from datetime import datetime

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    print("Pygame is required. Install with: sudo apt install python3-pygame")
    sys.exit(1)

# Symbols to use for the counting game
SYMBOLS = ['★', '●', '♦', '♠', '♥', '▲', '■', '○', '◆', '☆']

# Words for the spelling game
SPELLING_WORDS = ['DOG', 'CAR', 'CAT', 'TREE', 'BALL', 'APPLE', 'FISH', 'BOOK',
                  'SUN', 'MOON', 'STAR', 'MILK', 'BED', 'HOUSE']

# Default settings (can be overridden by config.json)
DEFAULT_CONFIG = {
    "min_count": 5,
    "max_count": 10,
    "required_correct": 5,
    "escape_code": "LETMEOUT",
    "auto_sync": False
}


def sync_with_gdrive(action="sync"):
    """Run the Google Drive sync script if it exists.

    Fails gracefully if no internet or sync fails - game continues normally.

    Args:
        action: 'pull', 'push', or 'sync'
    """
    import subprocess
    script_path = os.path.join(get_script_dir(), 'sync_gdrive.sh')

    if os.path.exists(script_path):
        try:
            result = subprocess.run(
                [script_path, action],
                capture_output=True,
                text=True,
                timeout=10  # Short timeout - don't block the game
            )
            # Silently ignore failures - sync is optional
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception):
            # No internet, timeout, or other error - just skip sync
            pass

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 60, 60)
GREEN = (60, 180, 60)
BLUE = (60, 100, 200)
YELLOW = (255, 220, 50)
ORANGE = (255, 150, 50)
BROWN = (139, 90, 43)
PINK = (255, 180, 180)
GRAY = (150, 150, 150)
LIGHT_BLUE = (135, 206, 235)
DARK_GREEN = (34, 120, 34)
BEIGE = (245, 222, 179)
DARK_GRAY = (80, 80, 80)


def get_script_dir():
    """Get the directory where this script is located."""
    return os.path.dirname(os.path.abspath(__file__))


def load_config():
    """Load configuration from config.json, or use defaults."""
    config_path = os.path.join(get_script_dir(), 'config.json')
    config = DEFAULT_CONFIG.copy()

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                loaded = json.load(f)
                config.update(loaded)
    except (json.JSONDecodeError, IOError):
        pass

    return config


def load_stats():
    """Load existing stats from stats.json."""
    stats_path = os.path.join(get_script_dir(), 'stats.json')

    try:
        if os.path.exists(stats_path):
            with open(stats_path, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass

    return {
        "total_sessions": 0,
        "total_rounds": 0,
        "total_correct": 0,
        "total_wrong": 0,
        "sessions": []
    }


def save_stats(stats):
    """Save stats to stats.json."""
    stats_path = os.path.join(get_script_dir(), 'stats.json')

    try:
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
    except IOError:
        pass


def log_round(session, correct_answer, user_answer, was_correct, symbol):
    """Log a single round to the session."""
    session["rounds"].append({
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "correct_answer": correct_answer,
        "user_answer": user_answer,
        "was_correct": was_correct
    })


# ============== PYGAME FULLSCREEN HELPERS ==============

def init_fullscreen():
    """Initialize Pygame in fullscreen mode and return screen + dimensions."""
    pygame.init()
    info = pygame.display.Info()
    screen_w, screen_h = info.current_w, info.current_h
    screen = pygame.display.set_mode((screen_w, screen_h), pygame.FULLSCREEN)
    pygame.display.set_caption("Counting Game")
    pygame.mouse.set_visible(False)
    return screen, screen_w, screen_h


def draw_text(screen, text, x, y, font, color=BLACK, center=True):
    """Render text on the screen."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(rendered, rect)
    return rect


def wait_for_key(screen):
    """Wait for any key press. Returns the key event, or None if quit."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                return event
        pygame.time.wait(30)


def get_text_input(screen, screen_w, screen_h, prompt, font_prompt, font_input, escape_code):
    """Get text input from the user via Pygame keyboard events.

    Returns:
        tuple: (text, was_escape) - the entered text and whether escape code was typed
    """
    typed = ""
    cursor_blink = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (typed, False)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return (typed, typed.upper() == escape_code.upper())
                elif event.key == pygame.K_BACKSPACE:
                    typed = typed[:-1]
                else:
                    char = event.unicode
                    if char and char.isprintable():
                        typed += char

        # Draw input area at the bottom
        input_area_y = screen_h - 140
        pygame.draw.rect(screen, WHITE, (0, input_area_y, screen_w, 140))
        pygame.draw.line(screen, GRAY, (50, input_area_y), (screen_w - 50, input_area_y), 2)

        # Prompt
        draw_text(screen, prompt, screen_w // 2, input_area_y + 35, font_prompt, DARK_GRAY)

        # Input box
        box_w = 300
        box_x = (screen_w - box_w) // 2
        box_y = input_area_y + 60
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_w, 50))
        pygame.draw.rect(screen, BLACK, (box_x, box_y, box_w, 50), 3)

        # Typed text
        draw_text(screen, typed, screen_w // 2, box_y + 25, font_input, BLACK)

        # Blinking cursor
        cursor_blink = (cursor_blink + 1) % 60
        if cursor_blink < 40:
            text_surface = font_input.render(typed, True, BLACK)
            cursor_x = screen_w // 2 + text_surface.get_width() // 2 + 3
            pygame.draw.line(screen, BLACK, (cursor_x, box_y + 10), (cursor_x, box_y + 40), 2)

        pygame.display.flip()
        pygame.time.wait(16)


def show_message_screen(screen, screen_w, screen_h, lines, bg_color=WHITE, wait=True):
    """Show a message screen with centered text lines.

    Args:
        lines: list of (text, font, color) tuples
        wait: if True, wait for key press
    """
    screen.fill(bg_color)
    total_height = sum(font.get_height() + 15 for _, font, _ in lines)
    start_y = (screen_h - total_height) // 2

    y = start_y
    for text, font, color in lines:
        draw_text(screen, text, screen_w // 2, y, font, color)
        y += font.get_height() + 15

    pygame.display.flip()

    if wait:
        wait_for_key(screen)


# ============== COUNTING GAME (FULLSCREEN) ==============

def play_counting_round_fullscreen(screen, screen_w, screen_h, correct_so_far, total_needed, config):
    """Play a single counting round in fullscreen Pygame.

    Returns:
        tuple: (result, details) where result is 'correct', 'wrong', or 'escape'
    """
    min_count = config.get("min_count", 5)
    max_count = config.get("max_count", 10)
    escape_code = config.get("escape_code", "LETMEOUT")

    count = random.randint(min_count, max_count)
    symbol = random.choice(SYMBOLS)

    # Draw the round screen
    screen.fill(WHITE)

    # Progress bar at top
    font_progress = pygame.font.Font(None, 36)
    progress_text = f"{correct_so_far} of {total_needed} correct"
    draw_text(screen, progress_text, screen_w // 2, 40, font_progress, DARK_GRAY)

    # Draw progress bar
    bar_w = 300
    bar_h = 12
    bar_x = (screen_w - bar_w) // 2
    bar_y = 60
    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=6)
    if total_needed > 0:
        fill_w = int(bar_w * correct_so_far / total_needed)
        if fill_w > 0:
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_w, bar_h), border_radius=6)

    # Scatter symbols on screen
    font_symbol = pygame.font.Font(None, 72)
    margin_x = 120
    margin_top = 110
    margin_bottom = 180
    area_w = screen_w - 2 * margin_x
    area_h = screen_h - margin_top - margin_bottom

    # Place symbols at random positions without overlapping
    positions = []
    min_dist = 70  # Minimum distance between symbols
    for _ in range(count):
        attempts = 0
        while attempts < 200:
            x = random.randint(margin_x, margin_x + area_w)
            y = random.randint(margin_top, margin_top + area_h)
            # Check distance from existing symbols
            too_close = False
            for px, py in positions:
                if math.hypot(x - px, y - py) < min_dist:
                    too_close = True
                    break
            if not too_close:
                positions.append((x, y))
                break
            attempts += 1
        else:
            # If couldn't find non-overlapping spot, place anyway
            x = random.randint(margin_x, margin_x + area_w)
            y = random.randint(margin_top, margin_top + area_h)
            positions.append((x, y))

    # Pick a random color for symbols this round
    symbol_colors = [RED, BLUE, DARK_GREEN, ORANGE, (150, 50, 150)]
    sym_color = random.choice(symbol_colors)

    for (x, y) in positions:
        draw_text(screen, symbol, x, y, font_symbol, sym_color)

    # Question text
    font_question = pygame.font.Font(None, 40)
    font_input = pygame.font.Font(None, 48)

    prompt = f"How many  {symbol}  do you see?"
    draw_text(screen, prompt, screen_w // 2, screen_h - 130, font_question, BLACK)

    pygame.display.flip()

    # Get input
    typed, was_escape = get_text_input(
        screen, screen_w, screen_h,
        "Type your answer and press Enter:",
        pygame.font.Font(None, 30),
        font_input,
        escape_code
    )

    if was_escape:
        return ('escape', {"count": count, "symbol": symbol, "user_answer": None})

    # Try to parse the answer
    try:
        answer_num = int(typed.strip())
    except ValueError:
        answer_num = -1  # Will be marked wrong

    details = {"count": count, "symbol": symbol, "user_answer": answer_num}

    # Show result
    font_result = pygame.font.Font(None, 64)
    font_detail = pygame.font.Font(None, 40)

    if answer_num == count:
        screen.fill(WHITE)
        draw_text(screen, "Correct!", screen_w // 2, screen_h // 2 - 40, font_result, GREEN)
        draw_text(screen, f"There were {count} symbols.", screen_w // 2, screen_h // 2 + 30, font_detail, DARK_GRAY)
        remaining = total_needed - (correct_so_far + 1)
        if remaining > 0:
            draw_text(screen, f"{remaining} more to go!", screen_w // 2, screen_h // 2 + 90, font_detail, DARK_GRAY)
        draw_text(screen, "Press any key...", screen_w // 2, screen_h - 60, pygame.font.Font(None, 30), GRAY)
        pygame.display.flip()
        if remaining > 0:
            wait_for_key(screen)
        else:
            pygame.time.wait(1200)
        return ('correct', details)
    else:
        screen.fill(WHITE)
        draw_text(screen, "Not quite.", screen_w // 2, screen_h // 2 - 40, font_result, RED)
        draw_text(screen, f"There were {count} symbols.", screen_w // 2, screen_h // 2 + 30, font_detail, DARK_GRAY)
        draw_text(screen, "Press any key...", screen_w // 2, screen_h - 60, pygame.font.Font(None, 30), GRAY)
        pygame.display.flip()
        wait_for_key(screen)
        return ('wrong', details)


def counting_game(boot_mode=False):
    """Run the locked counting game in fullscreen - must get required_correct to exit."""
    # Skip sync at boot - no internet yet
    if not boot_mode:
        sync_with_gdrive("pull")

    # Load configuration
    config = load_config()
    total_needed = config.get("required_correct", 5)
    min_count = config.get("min_count", 5)
    max_count = config.get("max_count", 10)
    auto_sync = config.get("auto_sync", False)

    # Load stats and start a new session
    stats = load_stats()
    session = {
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "config": {
            "min_count": min_count,
            "max_count": max_count,
            "required_correct": total_needed
        },
        "completed": False,
        "escaped": False,
        "rounds": []
    }

    # Initialize fullscreen
    screen, screen_w, screen_h = init_fullscreen()

    # Title screen
    font_title = pygame.font.Font(None, 72)
    font_sub = pygame.font.Font(None, 40)
    font_small = pygame.font.Font(None, 30)

    show_message_screen(screen, screen_w, screen_h, [
        ("SYMBOL COUNTING GAME", font_title, BLACK),
        ("", font_small, WHITE),
        ("Count the symbols on each screen!", font_sub, DARK_GRAY),
        (f"Get {total_needed} correct to finish!", font_sub, DARK_GRAY),
        (f"(counting {min_count} to {max_count} symbols)", font_small, GRAY),
        ("", font_small, WHITE),
        ("Press any key to start...", font_small, GRAY),
    ])

    correct = 0

    while correct < total_needed:
        result, details = play_counting_round_fullscreen(
            screen, screen_w, screen_h, correct, total_needed, config
        )

        if result == 'escape':
            session["escaped"] = True
            session["end_time"] = datetime.now().isoformat()
            stats["total_sessions"] += 1
            stats["sessions"].append(session)
            save_stats(stats)
            if auto_sync and not boot_mode:
                sync_with_gdrive("push")

            show_message_screen(screen, screen_w, screen_h, [
                ("Escape code accepted.", font_sub, DARK_GRAY),
                ("Exiting...", font_small, GRAY),
            ])
            pygame.quit()
            return

        was_correct = (result == 'correct')
        log_round(session, details["count"], details["user_answer"], was_correct, details["symbol"])

        if was_correct:
            correct += 1
            stats["total_correct"] += 1
        else:
            stats["total_wrong"] += 1

        stats["total_rounds"] += 1
        save_stats(stats)

    # Mark session complete
    session["completed"] = True
    session["end_time"] = datetime.now().isoformat()
    stats["total_sessions"] += 1
    stats["sessions"].append(session)
    save_stats(stats)
    if auto_sync and not boot_mode:
        sync_with_gdrive("push")

    # Victory screen
    font_big = pygame.font.Font(None, 96)
    show_message_screen(screen, screen_w, screen_h, [
        ("YOU DID IT!", font_big, GREEN),
        ("", font_sub, WHITE),
        (f"You got {total_needed} correct answers!", font_sub, DARK_GRAY),
        ("Great counting!", font_sub, DARK_GRAY),
        ("", font_small, WHITE),
        ("Press any key to exit...", font_small, GRAY),
    ])

    pygame.quit()


# ============== DRAWING FUNCTIONS (for spelling game) ==============

def draw_dog(screen, cx, cy):
    """Draw a simple dog."""
    pygame.draw.ellipse(screen, BROWN, (cx - 60, cy - 20, 120, 70))
    pygame.draw.circle(screen, BROWN, (cx - 70, cy - 30), 40)
    pygame.draw.ellipse(screen, BROWN, (cx - 120, cy - 70, 30, 50))
    pygame.draw.ellipse(screen, BROWN, (cx - 50, cy - 70, 30, 50))
    pygame.draw.circle(screen, WHITE, (cx - 85, cy - 40), 12)
    pygame.draw.circle(screen, WHITE, (cx - 55, cy - 40), 12)
    pygame.draw.circle(screen, BLACK, (cx - 85, cy - 40), 6)
    pygame.draw.circle(screen, BLACK, (cx - 55, cy - 40), 6)
    pygame.draw.circle(screen, BLACK, (cx - 70, cy - 15), 8)
    pygame.draw.arc(screen, BLACK, (cx - 85, cy - 20, 30, 20), 3.14, 0, 2)
    pygame.draw.arc(screen, BROWN, (cx + 40, cy - 40, 40, 60), 0, 2.5, 8)
    pygame.draw.rect(screen, BROWN, (cx - 45, cy + 40, 15, 40))
    pygame.draw.rect(screen, BROWN, (cx - 10, cy + 40, 15, 40))
    pygame.draw.rect(screen, BROWN, (cx + 20, cy + 40, 15, 40))
    pygame.draw.rect(screen, BROWN, (cx + 45, cy + 40, 15, 40))


def draw_cat(screen, cx, cy):
    """Draw a simple cat."""
    pygame.draw.ellipse(screen, ORANGE, (cx - 50, cy - 10, 100, 70))
    pygame.draw.circle(screen, ORANGE, (cx, cy - 50), 45)
    pygame.draw.polygon(screen, ORANGE, [(cx - 40, cy - 80), (cx - 25, cy - 120), (cx - 10, cy - 80)])
    pygame.draw.polygon(screen, ORANGE, [(cx + 40, cy - 80), (cx + 25, cy - 120), (cx + 10, cy - 80)])
    pygame.draw.polygon(screen, PINK, [(cx - 35, cy - 85), (cx - 25, cy - 110), (cx - 15, cy - 85)])
    pygame.draw.polygon(screen, PINK, [(cx + 35, cy - 85), (cx + 25, cy - 110), (cx + 15, cy - 85)])
    pygame.draw.ellipse(screen, GREEN, (cx - 25, cy - 60, 18, 25))
    pygame.draw.ellipse(screen, GREEN, (cx + 7, cy - 60, 18, 25))
    pygame.draw.ellipse(screen, BLACK, (cx - 19, cy - 55, 6, 18))
    pygame.draw.ellipse(screen, BLACK, (cx + 13, cy - 55, 6, 18))
    pygame.draw.polygon(screen, PINK, [(cx, cy - 35), (cx - 8, cy - 25), (cx + 8, cy - 25)])
    for i in [-1, 1]:
        pygame.draw.line(screen, BLACK, (cx + i * 10, cy - 28), (cx + i * 50, cy - 35), 2)
        pygame.draw.line(screen, BLACK, (cx + i * 10, cy - 25), (cx + i * 50, cy - 25), 2)
        pygame.draw.line(screen, BLACK, (cx + i * 10, cy - 22), (cx + i * 50, cy - 15), 2)
    pygame.draw.arc(screen, ORANGE, (cx + 30, cy - 20, 60, 80), 4.5, 1.5, 10)


def draw_car(screen, cx, cy):
    """Draw a simple car."""
    pygame.draw.rect(screen, RED, (cx - 80, cy - 20, 160, 50), border_radius=10)
    pygame.draw.rect(screen, RED, (cx - 40, cy - 60, 80, 45), border_radius=8)
    pygame.draw.rect(screen, LIGHT_BLUE, (cx - 35, cy - 55, 30, 30), border_radius=3)
    pygame.draw.rect(screen, LIGHT_BLUE, (cx + 5, cy - 55, 30, 30), border_radius=3)
    pygame.draw.circle(screen, BLACK, (cx - 45, cy + 30), 25)
    pygame.draw.circle(screen, GRAY, (cx - 45, cy + 30), 12)
    pygame.draw.circle(screen, BLACK, (cx + 45, cy + 30), 25)
    pygame.draw.circle(screen, GRAY, (cx + 45, cy + 30), 12)
    pygame.draw.circle(screen, YELLOW, (cx + 75, cy), 10)
    pygame.draw.circle(screen, RED, (cx - 75, cy), 8)


def draw_tree(screen, cx, cy):
    """Draw a simple tree."""
    pygame.draw.rect(screen, BROWN, (cx - 20, cy, 40, 80))
    pygame.draw.circle(screen, DARK_GREEN, (cx, cy - 60), 60)
    pygame.draw.circle(screen, GREEN, (cx - 45, cy - 20), 45)
    pygame.draw.circle(screen, GREEN, (cx + 45, cy - 20), 45)
    pygame.draw.circle(screen, DARK_GREEN, (cx, cy - 30), 50)


def draw_ball(screen, cx, cy):
    """Draw a colorful beach ball."""
    pygame.draw.circle(screen, RED, (cx, cy), 70)
    pygame.draw.arc(screen, BLUE, (cx - 70, cy - 70, 140, 140), 0.5, 1.5, 70)
    pygame.draw.arc(screen, YELLOW, (cx - 70, cy - 70, 140, 140), 2.0, 3.0, 70)
    pygame.draw.arc(screen, GREEN, (cx - 70, cy - 70, 140, 140), 3.5, 4.5, 70)
    pygame.draw.arc(screen, WHITE, (cx - 70, cy - 70, 140, 140), 5.0, 6.0, 70)
    pygame.draw.circle(screen, BLACK, (cx, cy), 70, 3)
    pygame.draw.circle(screen, WHITE, (cx - 25, cy - 30), 15)


def draw_apple(screen, cx, cy):
    """Draw a red apple."""
    pygame.draw.circle(screen, RED, (cx, cy), 60)
    pygame.draw.circle(screen, RED, (cx - 25, cy + 10), 50)
    pygame.draw.circle(screen, RED, (cx + 25, cy + 10), 50)
    pygame.draw.rect(screen, BROWN, (cx - 4, cy - 75, 8, 25))
    pygame.draw.ellipse(screen, GREEN, (cx + 5, cy - 75, 35, 18))
    pygame.draw.circle(screen, (255, 200, 200), (cx - 20, cy - 25), 12)


def draw_fish(screen, cx, cy):
    """Draw a colorful fish."""
    pygame.draw.ellipse(screen, ORANGE, (cx - 70, cy - 35, 120, 70))
    pygame.draw.polygon(screen, ORANGE, [(cx + 40, cy), (cx + 90, cy - 40), (cx + 90, cy + 40)])
    pygame.draw.polygon(screen, YELLOW, [(cx - 20, cy - 35), (cx, cy - 70), (cx + 20, cy - 35)])
    pygame.draw.polygon(screen, YELLOW, [(cx - 20, cy + 35), (cx, cy + 60), (cx + 20, cy + 35)])
    pygame.draw.circle(screen, WHITE, (cx - 35, cy - 5), 15)
    pygame.draw.circle(screen, BLACK, (cx - 35, cy - 5), 7)
    pygame.draw.arc(screen, BLACK, (cx - 65, cy + 5, 20, 15), 3.14, 0, 3)
    pygame.draw.arc(screen, (200, 120, 40), (cx - 30, cy - 20, 30, 30), 0, 3.14, 2)
    pygame.draw.arc(screen, (200, 120, 40), (cx, cy - 15, 30, 30), 0, 3.14, 2)
    pygame.draw.arc(screen, (200, 120, 40), (cx - 15, cy + 5, 30, 30), 0, 3.14, 2)


def draw_book(screen, cx, cy):
    """Draw an open book."""
    pygame.draw.rect(screen, WHITE, (cx - 90, cy - 50, 80, 100))
    pygame.draw.rect(screen, BLACK, (cx - 90, cy - 50, 80, 100), 2)
    pygame.draw.rect(screen, WHITE, (cx + 10, cy - 50, 80, 100))
    pygame.draw.rect(screen, BLACK, (cx + 10, cy - 50, 80, 100), 2)
    pygame.draw.rect(screen, RED, (cx - 10, cy - 55, 20, 110))
    pygame.draw.rect(screen, (150, 30, 30), (cx - 10, cy - 55, 20, 110), 2)
    for i in range(5):
        pygame.draw.line(screen, GRAY, (cx - 80, cy - 35 + i * 18), (cx - 20, cy - 35 + i * 18), 2)
    for i in range(5):
        pygame.draw.line(screen, GRAY, (cx + 20, cy - 35 + i * 18), (cx + 80, cy - 35 + i * 18), 2)


def draw_sun(screen, cx, cy):
    """Draw a simple sun."""
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x1 = cx + int(60 * math.cos(rad))
        y1 = cy + int(60 * math.sin(rad))
        x2 = cx + int(100 * math.cos(rad))
        y2 = cy + int(100 * math.sin(rad))
        pygame.draw.line(screen, YELLOW, (x1, y1), (x2, y2), 8)
    pygame.draw.circle(screen, YELLOW, (cx, cy), 55)
    pygame.draw.circle(screen, ORANGE, (cx, cy), 55, 5)
    pygame.draw.circle(screen, BLACK, (cx - 18, cy - 10), 6)
    pygame.draw.circle(screen, BLACK, (cx + 18, cy - 10), 6)
    pygame.draw.arc(screen, BLACK, (cx - 20, cy + 5, 40, 25), 3.14, 0, 3)


def draw_moon(screen, cx, cy):
    """Draw a crescent moon."""
    pygame.draw.circle(screen, YELLOW, (cx, cy), 70)
    pygame.draw.circle(screen, WHITE, (cx + 40, cy - 20), 55)
    pygame.draw.circle(screen, (230, 200, 50), (cx - 30, cy - 20), 8)
    pygame.draw.circle(screen, (230, 200, 50), (cx - 45, cy + 20), 6)
    pygame.draw.circle(screen, (230, 200, 50), (cx - 20, cy + 35), 5)


def draw_star(screen, cx, cy):
    """Draw a star."""
    points = []
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        points.append((cx + int(80 * math.cos(angle)), cy + int(80 * math.sin(angle))))
        angle = math.radians(i * 72 - 90 + 36)
        points.append((cx + int(35 * math.cos(angle)), cy + int(35 * math.sin(angle))))
    pygame.draw.polygon(screen, YELLOW, points)
    pygame.draw.polygon(screen, ORANGE, points, 4)


def draw_milk(screen, cx, cy):
    """Draw a 3D milk carton with glass."""
    pygame.draw.polygon(screen, (220, 220, 220), [
        (cx - 10, cy - 60), (cx + 20, cy - 70), (cx + 20, cy + 50), (cx - 10, cy + 60)
    ])
    pygame.draw.rect(screen, WHITE, (cx - 70, cy - 60, 60, 120))
    pygame.draw.rect(screen, BLUE, (cx - 70, cy - 60, 60, 120), 3)
    pygame.draw.polygon(screen, (240, 240, 240), [
        (cx - 70, cy - 60), (cx - 40, cy - 90), (cx - 10, cy - 60)
    ])
    pygame.draw.polygon(screen, BLUE, [
        (cx - 70, cy - 60), (cx - 40, cy - 90), (cx - 10, cy - 60)
    ], 2)
    pygame.draw.polygon(screen, (230, 230, 230), [
        (cx - 40, cy - 90), (cx - 10, cy - 60), (cx + 20, cy - 70), (cx - 10, cy - 100)
    ])
    pygame.draw.polygon(screen, BLUE, [
        (cx - 40, cy - 90), (cx - 10, cy - 60), (cx + 20, cy - 70), (cx - 10, cy - 100)
    ], 2)
    pygame.draw.ellipse(screen, BLACK, (cx - 60, cy - 30, 18, 12))
    pygame.draw.ellipse(screen, BLACK, (cx - 40, cy - 5, 20, 14))
    pygame.draw.ellipse(screen, BLACK, (cx - 55, cy + 25, 15, 10))
    pygame.draw.polygon(screen, LIGHT_BLUE, [
        (cx + 50, cy - 10), (cx + 110, cy - 10), (cx + 105, cy + 60), (cx + 55, cy + 60)
    ])
    pygame.draw.polygon(screen, (100, 180, 220), [
        (cx + 50, cy - 10), (cx + 110, cy - 10), (cx + 105, cy + 60), (cx + 55, cy + 60)
    ], 3)
    pygame.draw.polygon(screen, WHITE, [
        (cx + 53, cy + 5), (cx + 107, cy + 5), (cx + 104, cy + 57), (cx + 56, cy + 57)
    ])


def draw_bed(screen, cx, cy):
    """Draw a detailed bed."""
    pygame.draw.rect(screen, BROWN, (cx - 100, cy - 80, 25, 130))
    pygame.draw.rect(screen, (100, 60, 30), (cx - 100, cy - 80, 25, 130), 3)
    pygame.draw.circle(screen, BROWN, (cx - 88, cy - 80), 12)
    pygame.draw.rect(screen, BROWN, (cx + 75, cy - 40, 25, 90))
    pygame.draw.rect(screen, (100, 60, 30), (cx + 75, cy - 40, 25, 90), 3)
    pygame.draw.circle(screen, BROWN, (cx + 88, cy - 40), 12)
    pygame.draw.rect(screen, (120, 80, 50), (cx - 75, cy + 35, 150, 15))
    pygame.draw.rect(screen, WHITE, (cx - 75, cy - 25, 150, 60))
    pygame.draw.rect(screen, (200, 200, 200), (cx - 75, cy - 25, 150, 60), 2)
    pygame.draw.ellipse(screen, WHITE, (cx - 70, cy - 45, 55, 30))
    pygame.draw.ellipse(screen, (180, 180, 180), (cx - 70, cy - 45, 55, 30), 2)
    pygame.draw.ellipse(screen, (250, 250, 250), (cx - 55, cy - 40, 50, 25))
    pygame.draw.ellipse(screen, (180, 180, 180), (cx - 55, cy - 40, 50, 25), 2)
    pygame.draw.rect(screen, RED, (cx - 75, cy + 5, 150, 30))
    pygame.draw.rect(screen, (180, 50, 50), (cx - 75, cy + 5, 150, 30), 2)
    pygame.draw.line(screen, (150, 40, 40), (cx - 75, cy + 5), (cx + 75, cy + 5), 3)
    pygame.draw.rect(screen, WHITE, (cx - 75, cy - 5, 150, 12))
    pygame.draw.rect(screen, BROWN, (cx - 80, cy + 45, 12, 25))
    pygame.draw.rect(screen, BROWN, (cx + 68, cy + 45, 12, 25))


def draw_house(screen, cx, cy):
    """Draw a simple house."""
    pygame.draw.rect(screen, BEIGE, (cx - 70, cy - 30, 140, 100))
    pygame.draw.polygon(screen, RED, [(cx - 85, cy - 30), (cx, cy - 100), (cx + 85, cy - 30)])
    pygame.draw.rect(screen, BROWN, (cx - 20, cy + 10, 40, 60))
    pygame.draw.circle(screen, YELLOW, (cx + 12, cy + 40), 5)
    pygame.draw.rect(screen, LIGHT_BLUE, (cx - 55, cy - 10, 30, 30))
    pygame.draw.rect(screen, LIGHT_BLUE, (cx + 25, cy - 10, 30, 30))
    pygame.draw.line(screen, WHITE, (cx - 40, cy - 10), (cx - 40, cy + 20), 2)
    pygame.draw.line(screen, WHITE, (cx - 55, cy + 5), (cx - 25, cy + 5), 2)
    pygame.draw.line(screen, WHITE, (cx + 40, cy - 10), (cx + 40, cy + 20), 2)
    pygame.draw.line(screen, WHITE, (cx + 25, cy + 5), (cx + 55, cy + 5), 2)
    pygame.draw.rect(screen, BROWN, (cx + 40, cy - 85, 25, 40))


# Dictionary mapping words to drawing functions
DRAW_FUNCTIONS = {
    'DOG': draw_dog,
    'CAT': draw_cat,
    'CAR': draw_car,
    'TREE': draw_tree,
    'BALL': draw_ball,
    'APPLE': draw_apple,
    'FISH': draw_fish,
    'BOOK': draw_book,
    'SUN': draw_sun,
    'MOON': draw_moon,
    'STAR': draw_star,
    'MILK': draw_milk,
    'BED': draw_bed,
    'HOUSE': draw_house,
}


def show_drawing(word):
    """Display a drawn image using Pygame."""
    pygame.init()

    width, height = 400, 350
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("What is this?")

    screen.fill(WHITE)

    cx, cy = width // 2, height // 2 - 20
    if word in DRAW_FUNCTIONS:
        DRAW_FUNCTIONS[word](screen, cx, cy)

    font = pygame.font.Font(None, 24)
    text = font.render("Press any key or close window when ready", True, BLACK)
    text_rect = text.get_rect(center=(width // 2, height - 20))
    screen.blit(text, text_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                waiting = False

    pygame.quit()
    return True


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')


def play_spelling_round(round_num, target_correct, available_words):
    """Play a single round of the spelling game."""
    clear_screen()
    print(f"\n═══ Round {round_num} of {target_correct} ═══\n")

    word = random.choice(available_words)

    print("Look at the picture window and spell what you see!\n")

    show_drawing(word)

    answer = input("\nWhat was it? Type your answer: ").strip().upper()

    if answer == word:
        print(f"\n✓ Correct! It's a {word}!")
        return True, word
    else:
        print(f"\n✗ Not quite. It was a {word}.")
        return False, word


def spelling_game():
    """Run the spelling game - need 3 correct to finish."""
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║        SPELLING GAME                   ║")
    print("║                                        ║")
    print("║  Look at the picture and spell the    ║")
    print("║  word! Get 3 correct to win!          ║")
    print("╚════════════════════════════════════════╝")
    print(f"\n{len(SPELLING_WORDS)} words available!")
    print("\nPress Enter to start...")
    input()

    correct = 0
    target = 3
    round_num = 0
    used_words = []

    while correct < target:
        round_num += 1

        word_pool = [w for w in SPELLING_WORDS if w not in used_words[-3:]]
        if not word_pool:
            word_pool = SPELLING_WORDS

        success, word = play_spelling_round(correct + 1, target, word_pool)
        used_words.append(word)

        if success:
            correct += 1
            if correct < target:
                print(f"\n{correct} down, {target - correct} to go!")
        else:
            print("\nTry again! Keep going!")

        input("\nPress Enter to continue...")

    clear_screen()
    print("\n╔════════════════════════════════════════╗")
    print("║          YOU WIN!                      ║")
    print("╠════════════════════════════════════════╣")
    print(f"║   You got 3 correct in {round_num} rounds!      ║")
    print("╚════════════════════════════════════════╝")
    print("\n🎉 Great spelling!")
    print()


def main():
    """Run the counting game directly (locked mode, fullscreen)."""
    boot_mode = '--boot' in sys.argv
    counting_game(boot_mode=boot_mode)


# Keep spelling_game available for future use but not in main menu
def main_with_menu():
    """Alternative main with menu (not used by default)."""
    while True:
        clear_screen()
        print("╔════════════════════════════════════════╗")
        print("║         LEARNING GAMES                 ║")
        print("║                                        ║")
        print("║  Choose a game:                        ║")
        print("║                                        ║")
        print("║    1. Counting Game                    ║")
        print("║    2. Spelling Game                    ║")
        print("║    3. Quit                             ║")
        print("║                                        ║")
        print("╚════════════════════════════════════════╝")

        print(f"\n  ✓ Pygame ready - all {len(SPELLING_WORDS)} pictures available!")

        choice = input("\nEnter 1, 2, or 3: ").strip()

        if choice == '1':
            counting_game()
            input("Press Enter to return to menu...")
        elif choice == '2':
            spelling_game()
            input("Press Enter to return to menu...")
        elif choice == '3':
            clear_screen()
            print("\nThanks for playing! Goodbye!\n")
            break
        else:
            print("Please enter 1, 2, or 3.")
            input()


if __name__ == "__main__":
    main()
