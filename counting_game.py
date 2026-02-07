#!/usr/bin/env python3
"""
Symbol Counting & Spelling Game for Raspberry Pi
Two game modes: count symbols or spell words from pictures.
Uses Pygame to draw simple pictures for the spelling game.
No external images needed - everything is drawn programmatically!

Configuration: Edit config.json to change settings remotely
Statistics: View stats.json to see game progress and errors
"""

import random
import os
import math
import json
from datetime import datetime

# Check if pygame is available for the spelling game
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

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
    "escape_code": "LETMEOUT"
}

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
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load config.json, using defaults. Error: {e}")

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
    except IOError as e:
        print(f"Warning: Could not save stats. Error: {e}")


def log_round(session, correct_answer, user_answer, was_correct, symbol):
    """Log a single round to the session."""
    session["rounds"].append({
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "correct_answer": correct_answer,
        "user_answer": user_answer,
        "was_correct": was_correct
    })


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')


def display_symbols(count, symbol):
    """Display symbols in a scattered pattern."""
    grid_width = 40
    grid_height = 10
    grid = [[' ' for _ in range(grid_width)] for _ in range(grid_height)]

    placed = 0
    attempts = 0
    while placed < count and attempts < 1000:
        x = random.randint(0, grid_width - 1)
        y = random.randint(0, grid_height - 1)
        if grid[y][x] == ' ':
            grid[y][x] = symbol
            placed += 1
        attempts += 1

    print('┌' + '─' * grid_width + '┐')
    for row in grid:
        print('│' + ''.join(row) + '│')
    print('└' + '─' * grid_width + '┘')


def play_counting_round(correct_so_far, total_needed, config):
    """Play a single round of the counting game.

    Returns:
        tuple: (result, details) where result is 'correct', 'wrong', or 'escape'
               and details is a dict with count, symbol, user_answer
    """
    clear_screen()
    print(f"\n═══ {correct_so_far} of {total_needed} correct ═══\n")

    min_count = config.get("min_count", 5)
    max_count = config.get("max_count", 10)
    escape_code = config.get("escape_code", "LETMEOUT")

    count = random.randint(min_count, max_count)
    symbol = random.choice(SYMBOLS)

    display_symbols(count, symbol)

    print(f"\nHow many '{symbol}' symbols do you see?")

    while True:
        answer = input("Your answer: ").strip()

        # Check for escape code
        if answer.upper() == escape_code.upper():
            return ('escape', {"count": count, "symbol": symbol, "user_answer": None})

        try:
            answer_num = int(answer)
            break
        except ValueError:
            print("Please enter a number.")

    details = {"count": count, "symbol": symbol, "user_answer": answer_num}

    if answer_num == count:
        print(f"\n✓ Correct! There were {count} symbols.")
        return ('correct', details)
    else:
        print(f"\n✗ Not quite. There were {count} symbols.")
        return ('wrong', details)


# ============== DRAWING FUNCTIONS ==============

def draw_dog(screen, cx, cy):
    """Draw a simple dog."""
    # Body
    pygame.draw.ellipse(screen, BROWN, (cx - 60, cy - 20, 120, 70))
    # Head
    pygame.draw.circle(screen, BROWN, (cx - 70, cy - 30), 40)
    # Ears
    pygame.draw.ellipse(screen, BROWN, (cx - 120, cy - 70, 30, 50))
    pygame.draw.ellipse(screen, BROWN, (cx - 50, cy - 70, 30, 50))
    # Eyes
    pygame.draw.circle(screen, WHITE, (cx - 85, cy - 40), 12)
    pygame.draw.circle(screen, WHITE, (cx - 55, cy - 40), 12)
    pygame.draw.circle(screen, BLACK, (cx - 85, cy - 40), 6)
    pygame.draw.circle(screen, BLACK, (cx - 55, cy - 40), 6)
    # Nose
    pygame.draw.circle(screen, BLACK, (cx - 70, cy - 15), 8)
    # Mouth
    pygame.draw.arc(screen, BLACK, (cx - 85, cy - 20, 30, 20), 3.14, 0, 2)
    # Tail
    pygame.draw.arc(screen, BROWN, (cx + 40, cy - 40, 40, 60), 0, 2.5, 8)
    # Legs
    pygame.draw.rect(screen, BROWN, (cx - 45, cy + 40, 15, 40))
    pygame.draw.rect(screen, BROWN, (cx - 10, cy + 40, 15, 40))
    pygame.draw.rect(screen, BROWN, (cx + 20, cy + 40, 15, 40))
    pygame.draw.rect(screen, BROWN, (cx + 45, cy + 40, 15, 40))


def draw_cat(screen, cx, cy):
    """Draw a simple cat."""
    # Body
    pygame.draw.ellipse(screen, ORANGE, (cx - 50, cy - 10, 100, 70))
    # Head
    pygame.draw.circle(screen, ORANGE, (cx, cy - 50), 45)
    # Ears (triangles)
    pygame.draw.polygon(screen, ORANGE, [(cx - 40, cy - 80), (cx - 25, cy - 120), (cx - 10, cy - 80)])
    pygame.draw.polygon(screen, ORANGE, [(cx + 40, cy - 80), (cx + 25, cy - 120), (cx + 10, cy - 80)])
    pygame.draw.polygon(screen, PINK, [(cx - 35, cy - 85), (cx - 25, cy - 110), (cx - 15, cy - 85)])
    pygame.draw.polygon(screen, PINK, [(cx + 35, cy - 85), (cx + 25, cy - 110), (cx + 15, cy - 85)])
    # Eyes
    pygame.draw.ellipse(screen, GREEN, (cx - 25, cy - 60, 18, 25))
    pygame.draw.ellipse(screen, GREEN, (cx + 7, cy - 60, 18, 25))
    pygame.draw.ellipse(screen, BLACK, (cx - 19, cy - 55, 6, 18))
    pygame.draw.ellipse(screen, BLACK, (cx + 13, cy - 55, 6, 18))
    # Nose
    pygame.draw.polygon(screen, PINK, [(cx, cy - 35), (cx - 8, cy - 25), (cx + 8, cy - 25)])
    # Whiskers
    for i in [-1, 1]:
        pygame.draw.line(screen, BLACK, (cx + i * 10, cy - 28), (cx + i * 50, cy - 35), 2)
        pygame.draw.line(screen, BLACK, (cx + i * 10, cy - 25), (cx + i * 50, cy - 25), 2)
        pygame.draw.line(screen, BLACK, (cx + i * 10, cy - 22), (cx + i * 50, cy - 15), 2)
    # Tail
    pygame.draw.arc(screen, ORANGE, (cx + 30, cy - 20, 60, 80), 4.5, 1.5, 10)


def draw_car(screen, cx, cy):
    """Draw a simple car."""
    # Body
    pygame.draw.rect(screen, RED, (cx - 80, cy - 20, 160, 50), border_radius=10)
    # Top/cabin
    pygame.draw.rect(screen, RED, (cx - 40, cy - 60, 80, 45), border_radius=8)
    # Windows
    pygame.draw.rect(screen, LIGHT_BLUE, (cx - 35, cy - 55, 30, 30), border_radius=3)
    pygame.draw.rect(screen, LIGHT_BLUE, (cx + 5, cy - 55, 30, 30), border_radius=3)
    # Wheels
    pygame.draw.circle(screen, BLACK, (cx - 45, cy + 30), 25)
    pygame.draw.circle(screen, GRAY, (cx - 45, cy + 30), 12)
    pygame.draw.circle(screen, BLACK, (cx + 45, cy + 30), 25)
    pygame.draw.circle(screen, GRAY, (cx + 45, cy + 30), 12)
    # Headlights
    pygame.draw.circle(screen, YELLOW, (cx + 75, cy), 10)
    pygame.draw.circle(screen, RED, (cx - 75, cy), 8)


def draw_tree(screen, cx, cy):
    """Draw a simple tree."""
    # Trunk
    pygame.draw.rect(screen, BROWN, (cx - 20, cy, 40, 80))
    # Foliage (three circles)
    pygame.draw.circle(screen, DARK_GREEN, (cx, cy - 60), 60)
    pygame.draw.circle(screen, GREEN, (cx - 45, cy - 20), 45)
    pygame.draw.circle(screen, GREEN, (cx + 45, cy - 20), 45)
    pygame.draw.circle(screen, DARK_GREEN, (cx, cy - 30), 50)


def draw_ball(screen, cx, cy):
    """Draw a colorful beach ball."""
    # Main ball
    pygame.draw.circle(screen, RED, (cx, cy), 70)
    # Stripes
    pygame.draw.arc(screen, BLUE, (cx - 70, cy - 70, 140, 140), 0.5, 1.5, 70)
    pygame.draw.arc(screen, YELLOW, (cx - 70, cy - 70, 140, 140), 2.0, 3.0, 70)
    pygame.draw.arc(screen, GREEN, (cx - 70, cy - 70, 140, 140), 3.5, 4.5, 70)
    pygame.draw.arc(screen, WHITE, (cx - 70, cy - 70, 140, 140), 5.0, 6.0, 70)
    # Outline
    pygame.draw.circle(screen, BLACK, (cx, cy), 70, 3)
    # Shine highlight
    pygame.draw.circle(screen, WHITE, (cx - 25, cy - 30), 15)


def draw_apple(screen, cx, cy):
    """Draw a red apple."""
    # Main apple body
    pygame.draw.circle(screen, RED, (cx, cy), 60)
    pygame.draw.circle(screen, RED, (cx - 25, cy + 10), 50)
    pygame.draw.circle(screen, RED, (cx + 25, cy + 10), 50)
    # Stem
    pygame.draw.rect(screen, BROWN, (cx - 4, cy - 75, 8, 25))
    # Leaf
    pygame.draw.ellipse(screen, GREEN, (cx + 5, cy - 75, 35, 18))
    # Shine highlight
    pygame.draw.circle(screen, (255, 200, 200), (cx - 20, cy - 25), 12)


def draw_fish(screen, cx, cy):
    """Draw a colorful fish."""
    # Body
    pygame.draw.ellipse(screen, ORANGE, (cx - 70, cy - 35, 120, 70))
    # Tail
    pygame.draw.polygon(screen, ORANGE, [(cx + 40, cy), (cx + 90, cy - 40), (cx + 90, cy + 40)])
    # Fins
    pygame.draw.polygon(screen, YELLOW, [(cx - 20, cy - 35), (cx, cy - 70), (cx + 20, cy - 35)])
    pygame.draw.polygon(screen, YELLOW, [(cx - 20, cy + 35), (cx, cy + 60), (cx + 20, cy + 35)])
    # Eye
    pygame.draw.circle(screen, WHITE, (cx - 35, cy - 5), 15)
    pygame.draw.circle(screen, BLACK, (cx - 35, cy - 5), 7)
    # Mouth
    pygame.draw.arc(screen, BLACK, (cx - 65, cy + 5, 20, 15), 3.14, 0, 3)
    # Scales pattern
    pygame.draw.arc(screen, (200, 120, 40), (cx - 30, cy - 20, 30, 30), 0, 3.14, 2)
    pygame.draw.arc(screen, (200, 120, 40), (cx, cy - 15, 30, 30), 0, 3.14, 2)
    pygame.draw.arc(screen, (200, 120, 40), (cx - 15, cy + 5, 30, 30), 0, 3.14, 2)


def draw_book(screen, cx, cy):
    """Draw an open book."""
    # Left page
    pygame.draw.rect(screen, WHITE, (cx - 90, cy - 50, 80, 100))
    pygame.draw.rect(screen, BLACK, (cx - 90, cy - 50, 80, 100), 2)
    # Right page
    pygame.draw.rect(screen, WHITE, (cx + 10, cy - 50, 80, 100))
    pygame.draw.rect(screen, BLACK, (cx + 10, cy - 50, 80, 100), 2)
    # Spine
    pygame.draw.rect(screen, RED, (cx - 10, cy - 55, 20, 110))
    pygame.draw.rect(screen, (150, 30, 30), (cx - 10, cy - 55, 20, 110), 2)
    # Text lines on left page
    for i in range(5):
        pygame.draw.line(screen, GRAY, (cx - 80, cy - 35 + i * 18), (cx - 20, cy - 35 + i * 18), 2)
    # Text lines on right page
    for i in range(5):
        pygame.draw.line(screen, GRAY, (cx + 20, cy - 35 + i * 18), (cx + 80, cy - 35 + i * 18), 2)


def draw_sun(screen, cx, cy):
    """Draw a simple sun."""
    # Rays
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x1 = cx + int(60 * math.cos(rad))
        y1 = cy + int(60 * math.sin(rad))
        x2 = cx + int(100 * math.cos(rad))
        y2 = cy + int(100 * math.sin(rad))
        pygame.draw.line(screen, YELLOW, (x1, y1), (x2, y2), 8)
    # Center
    pygame.draw.circle(screen, YELLOW, (cx, cy), 55)
    pygame.draw.circle(screen, ORANGE, (cx, cy), 55, 5)
    # Face
    pygame.draw.circle(screen, BLACK, (cx - 18, cy - 10), 6)
    pygame.draw.circle(screen, BLACK, (cx + 18, cy - 10), 6)
    pygame.draw.arc(screen, BLACK, (cx - 20, cy + 5, 40, 25), 3.14, 0, 3)


def draw_moon(screen, cx, cy):
    """Draw a crescent moon."""
    # Main moon circle
    pygame.draw.circle(screen, YELLOW, (cx, cy), 70)
    # Cut out circle to make crescent
    pygame.draw.circle(screen, WHITE, (cx + 40, cy - 20), 55)
    # Add some crater details
    pygame.draw.circle(screen, (230, 200, 50), (cx - 30, cy - 20), 8)
    pygame.draw.circle(screen, (230, 200, 50), (cx - 45, cy + 20), 6)
    pygame.draw.circle(screen, (230, 200, 50), (cx - 20, cy + 35), 5)


def draw_star(screen, cx, cy):
    """Draw a star."""
    # 5-pointed star
    points = []
    for i in range(5):
        # Outer points
        angle = math.radians(i * 72 - 90)
        points.append((cx + int(80 * math.cos(angle)), cy + int(80 * math.sin(angle))))
        # Inner points
        angle = math.radians(i * 72 - 90 + 36)
        points.append((cx + int(35 * math.cos(angle)), cy + int(35 * math.sin(angle))))
    pygame.draw.polygon(screen, YELLOW, points)
    pygame.draw.polygon(screen, ORANGE, points, 4)


def draw_milk(screen, cx, cy):
    """Draw a 3D milk carton with glass."""
    # Carton - right side (3D effect)
    pygame.draw.polygon(screen, (220, 220, 220), [
        (cx - 10, cy - 60), (cx + 20, cy - 70), (cx + 20, cy + 50), (cx - 10, cy + 60)
    ])
    # Carton - front face
    pygame.draw.rect(screen, WHITE, (cx - 70, cy - 60, 60, 120))
    pygame.draw.rect(screen, BLUE, (cx - 70, cy - 60, 60, 120), 3)
    # Carton - top (3D)
    pygame.draw.polygon(screen, (240, 240, 240), [
        (cx - 70, cy - 60), (cx - 40, cy - 90), (cx - 10, cy - 60)
    ])
    pygame.draw.polygon(screen, BLUE, [
        (cx - 70, cy - 60), (cx - 40, cy - 90), (cx - 10, cy - 60)
    ], 2)
    # Top fold peak (3D)
    pygame.draw.polygon(screen, (230, 230, 230), [
        (cx - 40, cy - 90), (cx - 10, cy - 60), (cx + 20, cy - 70), (cx - 10, cy - 100)
    ])
    pygame.draw.polygon(screen, BLUE, [
        (cx - 40, cy - 90), (cx - 10, cy - 60), (cx + 20, cy - 70), (cx - 10, cy - 100)
    ], 2)
    # Cow spots on front
    pygame.draw.ellipse(screen, BLACK, (cx - 60, cy - 30, 18, 12))
    pygame.draw.ellipse(screen, BLACK, (cx - 40, cy - 5, 20, 14))
    pygame.draw.ellipse(screen, BLACK, (cx - 55, cy + 25, 15, 10))
    # Glass of milk to the right
    pygame.draw.polygon(screen, LIGHT_BLUE, [
        (cx + 50, cy - 10), (cx + 110, cy - 10), (cx + 105, cy + 60), (cx + 55, cy + 60)
    ])
    pygame.draw.polygon(screen, (100, 180, 220), [
        (cx + 50, cy - 10), (cx + 110, cy - 10), (cx + 105, cy + 60), (cx + 55, cy + 60)
    ], 3)
    # Milk in glass
    pygame.draw.polygon(screen, WHITE, [
        (cx + 53, cy + 5), (cx + 107, cy + 5), (cx + 104, cy + 57), (cx + 56, cy + 57)
    ])


def draw_bed(screen, cx, cy):
    """Draw a detailed bed."""
    # Headboard (decorative)
    pygame.draw.rect(screen, BROWN, (cx - 100, cy - 80, 25, 130))
    pygame.draw.rect(screen, (100, 60, 30), (cx - 100, cy - 80, 25, 130), 3)
    pygame.draw.circle(screen, BROWN, (cx - 88, cy - 80), 12)  # Decorative top
    # Footboard
    pygame.draw.rect(screen, BROWN, (cx + 75, cy - 40, 25, 90))
    pygame.draw.rect(screen, (100, 60, 30), (cx + 75, cy - 40, 25, 90), 3)
    pygame.draw.circle(screen, BROWN, (cx + 88, cy - 40), 12)  # Decorative top
    # Bed frame base
    pygame.draw.rect(screen, (120, 80, 50), (cx - 75, cy + 35, 150, 15))
    # Mattress
    pygame.draw.rect(screen, WHITE, (cx - 75, cy - 25, 150, 60))
    pygame.draw.rect(screen, (200, 200, 200), (cx - 75, cy - 25, 150, 60), 2)
    # Pillow
    pygame.draw.ellipse(screen, WHITE, (cx - 70, cy - 45, 55, 30))
    pygame.draw.ellipse(screen, (180, 180, 180), (cx - 70, cy - 45, 55, 30), 2)
    # Second pillow
    pygame.draw.ellipse(screen, (250, 250, 250), (cx - 55, cy - 40, 50, 25))
    pygame.draw.ellipse(screen, (180, 180, 180), (cx - 55, cy - 40, 50, 25), 2)
    # Blanket with fold detail
    pygame.draw.rect(screen, RED, (cx - 75, cy + 5, 150, 30))
    pygame.draw.rect(screen, (180, 50, 50), (cx - 75, cy + 5, 150, 30), 2)
    # Blanket fold line
    pygame.draw.line(screen, (150, 40, 40), (cx - 75, cy + 5), (cx + 75, cy + 5), 3)
    # Sheet showing
    pygame.draw.rect(screen, WHITE, (cx - 75, cy - 5, 150, 12))
    # Legs
    pygame.draw.rect(screen, BROWN, (cx - 80, cy + 45, 12, 25))
    pygame.draw.rect(screen, BROWN, (cx + 68, cy + 45, 12, 25))


def draw_house(screen, cx, cy):
    """Draw a simple house."""
    # Main building
    pygame.draw.rect(screen, BEIGE, (cx - 70, cy - 30, 140, 100))
    # Roof
    pygame.draw.polygon(screen, RED, [(cx - 85, cy - 30), (cx, cy - 100), (cx + 85, cy - 30)])
    # Door
    pygame.draw.rect(screen, BROWN, (cx - 20, cy + 10, 40, 60))
    pygame.draw.circle(screen, YELLOW, (cx + 12, cy + 40), 5)
    # Windows
    pygame.draw.rect(screen, LIGHT_BLUE, (cx - 55, cy - 10, 30, 30))
    pygame.draw.rect(screen, LIGHT_BLUE, (cx + 25, cy - 10, 30, 30))
    pygame.draw.line(screen, WHITE, (cx - 40, cy - 10), (cx - 40, cy + 20), 2)
    pygame.draw.line(screen, WHITE, (cx - 55, cy + 5), (cx - 25, cy + 5), 2)
    pygame.draw.line(screen, WHITE, (cx + 40, cy - 10), (cx + 40, cy + 20), 2)
    pygame.draw.line(screen, WHITE, (cx + 25, cy + 5), (cx + 55, cy + 5), 2)
    # Chimney
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

    # Window size
    width, height = 400, 350
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("What is this?")

    # Draw background
    screen.fill(WHITE)

    # Draw the image
    cx, cy = width // 2, height // 2 - 20
    if word in DRAW_FUNCTIONS:
        DRAW_FUNCTIONS[word](screen, cx, cy)

    # Instructions text
    font = pygame.font.Font(None, 24)
    text = font.render("Press any key or close window when ready", True, BLACK)
    text_rect = text.get_rect(center=(width // 2, height - 20))
    screen.blit(text, text_rect)

    pygame.display.flip()

    # Wait for user
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                waiting = False

    pygame.quit()
    return True


def play_spelling_round(round_num, target_correct, available_words):
    """Play a single round of the spelling game."""
    clear_screen()
    print(f"\n═══ Round {round_num} of {target_correct} ═══\n")

    word = random.choice(available_words)

    print("Look at the picture window and spell what you see!\n")

    # Show drawing
    show_drawing(word)

    # Get answer
    answer = input("\nWhat was it? Type your answer: ").strip().upper()

    if answer == word:
        print(f"\n✓ Correct! It's a {word}!")
        return True, word
    else:
        print(f"\n✗ Not quite. It was a {word}.")
        return False, word


def counting_game():
    """Run the locked counting game - must get required_correct to exit."""
    # Load configuration
    config = load_config()
    total_needed = config.get("required_correct", 5)
    min_count = config.get("min_count", 5)
    max_count = config.get("max_count", 10)

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

    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║      SYMBOL COUNTING GAME              ║")
    print("║                                        ║")
    print("║  Count the symbols on each screen!    ║")
    print(f"║  Get {total_needed} correct to finish!             ║")
    print(f"║  (counting {min_count} to {max_count} symbols)           ║")
    print("╚════════════════════════════════════════╝")
    print("\nPress Enter to start...")
    input()

    correct = 0

    while correct < total_needed:
        result, details = play_counting_round(correct, total_needed, config)

        if result == 'escape':
            # Log escape
            session["escaped"] = True
            session["end_time"] = datetime.now().isoformat()
            stats["total_sessions"] += 1
            stats["sessions"].append(session)
            save_stats(stats)

            clear_screen()
            print("\n🔓 Escape code accepted. Exiting...\n")
            return

        # Log this round
        was_correct = (result == 'correct')
        log_round(session, details["count"], details["user_answer"], was_correct, details["symbol"])

        if was_correct:
            correct += 1
            stats["total_correct"] += 1
            if correct < total_needed:
                print(f"\n{total_needed - correct} more to go!")
        else:
            stats["total_wrong"] += 1

        stats["total_rounds"] += 1
        save_stats(stats)  # Save after each round

        input("\nPress Enter to continue...")

    # Mark session complete
    session["completed"] = True
    session["end_time"] = datetime.now().isoformat()
    stats["total_sessions"] += 1
    stats["sessions"].append(session)
    save_stats(stats)

    # Victory screen
    clear_screen()
    print("\n╔════════════════════════════════════════╗")
    print("║         🎉 YOU DID IT! 🎉              ║")
    print("║                                        ║")
    print(f"║      You got {total_needed} correct answers!       ║")
    print("║                                        ║")
    print("║          Great counting!              ║")
    print("╚════════════════════════════════════════╝")
    print()


def spelling_game():
    """Run the spelling game - need 3 correct to finish."""
    if not PYGAME_AVAILABLE:
        print("\n❌ Pygame is not installed!")
        print("Install it with: sudo apt install python3-pygame")
        print("Or: pip3 install pygame")
        input("\nPress Enter to return to menu...")
        return

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

        # Filter out recently used words
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
    """Run the counting game directly (locked mode)."""
    counting_game()
    clear_screen()
    print("\nThanks for playing! Goodbye!\n")


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

        if PYGAME_AVAILABLE:
            print(f"\n  ✓ Pygame ready - all {len(SPELLING_WORDS)} pictures available!")
        else:
            print("\n  ⚠ Pygame not installed (needed for spelling)")

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
