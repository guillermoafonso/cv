#!/usr/bin/env python3
"""
Symbol Counting & Spelling Game for Raspberry Pi
Two game modes: count symbols or spell words from pictures.
Uses Pygame to display images for the spelling game.
"""

import random
import os
import sys

# Check if pygame is available for the spelling game
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# Symbols to use for the counting game
SYMBOLS = ['★', '●', '♦', '♠', '♥', '▲', '■', '○', '◆', '☆']

# Words for the spelling game (images should be in 'images' folder)
SPELLING_WORDS = ['DOG', 'CAR', 'CAT', 'TREE', 'FOOT', 'HAND', 'ARM', 'HEAD',
                  'SUN', 'MOON', 'STAR', 'MILK', 'BED', 'HOUSE']


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')


def get_script_dir():
    """Get the directory where this script is located."""
    return os.path.dirname(os.path.abspath(__file__))


def get_images_dir():
    """Get the path to the images directory."""
    return os.path.join(get_script_dir(), 'images')


def check_images():
    """Check which images are available and return list of available words."""
    images_dir = get_images_dir()
    available = []

    if not os.path.exists(images_dir):
        return available

    for word in SPELLING_WORDS:
        # Check for common image formats
        for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            image_path = os.path.join(images_dir, word.lower() + ext)
            if os.path.exists(image_path):
                available.append(word)
                break

    return available


def get_image_path(word):
    """Get the full path to an image for a word."""
    images_dir = get_images_dir()
    for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
        image_path = os.path.join(images_dir, word.lower() + ext)
        if os.path.exists(image_path):
            return image_path
    return None


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


def show_image_pygame(word):
    """Display an image using Pygame. Returns when user closes window or presses a key."""
    image_path = get_image_path(word)
    if not image_path:
        return False

    pygame.init()

    # Load and scale image
    try:
        image = pygame.image.load(image_path)
    except pygame.error as e:
        print(f"Error loading image: {e}")
        pygame.quit()
        return False

    # Scale image to fit nicely on screen (max 500x500 while keeping aspect ratio)
    max_size = 500
    img_width, img_height = image.get_size()
    scale = min(max_size / img_width, max_size / img_height)
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    image = pygame.transform.scale(image, (new_width, new_height))

    # Create window
    window_width = new_width + 40
    window_height = new_height + 80
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("What is this? (Close window when ready)")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Font for instructions
    font = pygame.font.Font(None, 28)
    text = font.render("Close window or press any key when ready to answer", True, BLACK)
    text_rect = text.get_rect(center=(window_width // 2, window_height - 30))

    # Center image
    image_rect = image.get_rect(center=(window_width // 2, (window_height - 50) // 2))

    # Display
    screen.fill(WHITE)
    screen.blit(image, image_rect)
    screen.blit(text, text_rect)
    pygame.display.flip()

    # Wait for user to close window or press key
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

    # Show image in Pygame window
    if not show_image_pygame(word):
        print("Error: Could not display image.")
        return False, word

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

    available_words = check_images()

    if len(available_words) < 3:
        print("\n❌ Not enough images found!")
        print(f"Found {len(available_words)} images, need at least 3.")
        print(f"\nPlease run: python3 download_images.py")
        print("Or manually add images to the 'images' folder.")
        print(f"\nImages should be named: dog.png, cat.png, etc.")
        print(f"Supported formats: PNG, JPG, GIF, BMP")
        input("\nPress Enter to return to menu...")
        return

    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║        SPELLING GAME                   ║")
    print("║                                        ║")
    print("║  Look at the picture and spell the    ║")
    print("║  word! Get 3 correct to win!          ║")
    print("╚════════════════════════════════════════╝")
    print(f"\n{len(available_words)} words available: {', '.join(available_words)}")
    print("\nPress Enter to start...")
    input()

    correct = 0
    target = 3
    round_num = 0
    used_words = []

    while correct < target:
        round_num += 1

        # Filter out recently used words if possible
        word_pool = [w for w in available_words if w not in used_words[-3:]]
        if not word_pool:
            word_pool = available_words

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

        # Show status
        if PYGAME_AVAILABLE:
            available = check_images()
            print(f"\n  Spelling game: {len(available)}/14 images ready")
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
