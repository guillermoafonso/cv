#!/usr/bin/env python3
"""
Symbol Counting & Spelling Game for Raspberry Pi
Two game modes: count symbols or spell words from pictures.
Uses Pygame to draw simple pictures for the spelling game.
No external images needed - everything is drawn programmatically!
"""

import random
import os
import math

# Check if pygame is available for the spelling game
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# Symbols to use for the counting game
SYMBOLS = ['★', '●', '♦', '♠', '♥', '▲', '■', '○', '◆', '☆']

# Words for the spelling game
SPELLING_WORDS = ['DOG', 'CAR', 'CAT', 'TREE', 'FOOT', 'HAND', 'ARM', 'HEAD',
                  'SUN', 'MOON', 'STAR', 'MILK', 'BED', 'HOUSE']

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


def play_counting_round(round_num):
    """Play a single round of the counting game."""
    clear_screen()
    print(f"\n═══ Round {round_num} of 5 ═══\n")

    count = random.randint(5, 10)
    symbol = random.choice(SYMBOLS)

    display_symbols(count, symbol)

    print(f"\nHow many '{symbol}' symbols do you see?")

    while True:
        try:
            answer = int(input("Your answer: "))
            break
        except ValueError:
            print("Please enter a number.")

    if answer == count:
        print(f"\n✓ Correct! There were {count} symbols.")
        return True
    else:
        print(f"\n✗ Not quite. There were {count} symbols.")
        return False


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


def draw_foot(screen, cx, cy):
    """Draw a simple foot."""
    # Main foot
    pygame.draw.ellipse(screen, BEIGE, (cx - 40, cy - 30, 80, 120))
    # Toes
    pygame.draw.circle(screen, BEIGE, (cx - 30, cy - 45), 18)
    pygame.draw.circle(screen, BEIGE, (cx - 8, cy - 55), 20)
    pygame.draw.circle(screen, BEIGE, (cx + 15, cy - 50), 18)
    pygame.draw.circle(screen, BEIGE, (cx + 32, cy - 40), 15)
    pygame.draw.circle(screen, BEIGE, (cx + 42, cy - 25), 12)
    # Outline
    pygame.draw.ellipse(screen, BROWN, (cx - 40, cy - 30, 80, 120), 3)


def draw_hand(screen, cx, cy):
    """Draw a simple hand."""
    # Palm
    pygame.draw.ellipse(screen, BEIGE, (cx - 40, cy - 20, 80, 90))
    # Fingers
    pygame.draw.ellipse(screen, BEIGE, (cx - 35, cy - 90, 18, 70))  # pinky
    pygame.draw.ellipse(screen, BEIGE, (cx - 15, cy - 110, 20, 90))  # ring
    pygame.draw.ellipse(screen, BEIGE, (cx + 5, cy - 115, 20, 95))  # middle
    pygame.draw.ellipse(screen, BEIGE, (cx + 25, cy - 105, 20, 85))  # index
    # Thumb
    pygame.draw.ellipse(screen, BEIGE, (cx + 45, cy - 40, 30, 55))
    # Outlines
    pygame.draw.ellipse(screen, BROWN, (cx - 40, cy - 20, 80, 90), 2)


def draw_arm(screen, cx, cy):
    """Draw a simple arm."""
    # Upper arm
    pygame.draw.ellipse(screen, BEIGE, (cx - 100, cy - 25, 100, 50))
    # Forearm
    pygame.draw.ellipse(screen, BEIGE, (cx - 20, cy - 25, 100, 50))
    # Hand
    pygame.draw.circle(screen, BEIGE, (cx + 90, cy), 35)
    # Outline
    pygame.draw.ellipse(screen, BROWN, (cx - 100, cy - 25, 100, 50), 3)
    pygame.draw.ellipse(screen, BROWN, (cx - 20, cy - 25, 100, 50), 3)
    pygame.draw.circle(screen, BROWN, (cx + 90, cy), 35, 3)


def draw_head(screen, cx, cy):
    """Draw a simple head/face."""
    # Face
    pygame.draw.circle(screen, BEIGE, (cx, cy), 80)
    # Hair
    pygame.draw.arc(screen, BROWN, (cx - 85, cy - 90, 170, 100), 0, 3.14, 20)
    # Eyes
    pygame.draw.ellipse(screen, WHITE, (cx - 40, cy - 25, 30, 20))
    pygame.draw.ellipse(screen, WHITE, (cx + 10, cy - 25, 30, 20))
    pygame.draw.circle(screen, BLUE, (cx - 25, cy - 15), 8)
    pygame.draw.circle(screen, BLUE, (cx + 25, cy - 15), 8)
    pygame.draw.circle(screen, BLACK, (cx - 25, cy - 15), 4)
    pygame.draw.circle(screen, BLACK, (cx + 25, cy - 15), 4)
    # Nose
    pygame.draw.polygon(screen, BROWN, [(cx, cy - 5), (cx - 10, cy + 20), (cx + 10, cy + 20)])
    # Mouth
    pygame.draw.arc(screen, RED, (cx - 25, cy + 25, 50, 30), 3.14, 0, 4)
    # Ears
    pygame.draw.ellipse(screen, BEIGE, (cx - 95, cy - 20, 25, 40))
    pygame.draw.ellipse(screen, BEIGE, (cx + 70, cy - 20, 25, 40))


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
    # Stars around
    for pos in [(-80, -60), (70, -70), (-70, 50), (80, 40), (0, -90)]:
        pygame.draw.polygon(screen, YELLOW, [
            (cx + pos[0], cy + pos[1] - 8),
            (cx + pos[0] - 3, cy + pos[1] + 3),
            (cx + pos[0] + 3, cy + pos[1] + 3)
        ])


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
    """Draw a milk carton."""
    # Carton body
    pygame.draw.rect(screen, WHITE, (cx - 40, cy - 60, 80, 120))
    pygame.draw.rect(screen, BLUE, (cx - 40, cy - 60, 80, 120), 3)
    # Top fold
    pygame.draw.polygon(screen, WHITE, [(cx - 40, cy - 60), (cx, cy - 90), (cx + 40, cy - 60)])
    pygame.draw.polygon(screen, BLUE, [(cx - 40, cy - 60), (cx, cy - 90), (cx + 40, cy - 60)], 3)
    # Cow spots decoration
    pygame.draw.ellipse(screen, BLACK, (cx - 25, cy - 30, 20, 15))
    pygame.draw.ellipse(screen, BLACK, (cx + 5, cy - 10, 25, 18))
    pygame.draw.ellipse(screen, BLACK, (cx - 20, cy + 20, 18, 12))
    # Glass of milk
    pygame.draw.rect(screen, LIGHT_BLUE, (cx - 15, cy + 70, 30, 40), border_radius=3)
    pygame.draw.rect(screen, WHITE, (cx - 12, cy + 75, 24, 30))


def draw_bed(screen, cx, cy):
    """Draw a simple bed."""
    # Mattress
    pygame.draw.rect(screen, WHITE, (cx - 90, cy - 20, 180, 60))
    pygame.draw.rect(screen, BLUE, (cx - 90, cy - 20, 180, 60), 3)
    # Pillow
    pygame.draw.ellipse(screen, WHITE, (cx - 80, cy - 35, 50, 30))
    pygame.draw.ellipse(screen, BLUE, (cx - 80, cy - 35, 50, 30), 2)
    # Blanket
    pygame.draw.rect(screen, RED, (cx - 90, cy, 180, 40))
    pygame.draw.rect(screen, (180, 40, 40), (cx - 90, cy, 180, 40), 3)
    # Headboard
    pygame.draw.rect(screen, BROWN, (cx - 100, cy - 70, 20, 120))
    # Footboard
    pygame.draw.rect(screen, BROWN, (cx + 80, cy - 40, 20, 90))
    # Legs
    pygame.draw.rect(screen, BROWN, (cx - 95, cy + 40, 15, 30))
    pygame.draw.rect(screen, BROWN, (cx + 80, cy + 40, 15, 30))


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
    'FOOT': draw_foot,
    'HAND': draw_hand,
    'ARM': draw_arm,
    'HEAD': draw_head,
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
    """Run the counting game."""
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║      SYMBOL COUNTING GAME              ║")
    print("║                                        ║")
    print("║  Count the symbols on each screen!    ║")
    print("║  You will have 5 rounds.              ║")
    print("╚════════════════════════════════════════╝")
    print("\nPress Enter to start...")
    input()

    score = 0

    for round_num in range(1, 6):
        if play_counting_round(round_num):
            score += 1

        if round_num < 5:
            input("\nPress Enter for the next round...")

    clear_screen()
    print("\n╔════════════════════════════════════════╗")
    print("║            GAME OVER!                  ║")
    print("╠════════════════════════════════════════╣")
    print(f"║      Your score: {score} out of 5            ║")
    print("╚════════════════════════════════════════╝")

    if score == 5:
        print("\n🎉 Perfect score! Amazing!")
    elif score >= 3:
        print("\n👍 Good job!")
    else:
        print("\n💪 Keep practicing!")

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
    """Main menu to choose game mode."""
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
