#!/usr/bin/env python3
"""
Symbol Counting & Spelling Game for Raspberry Pi
Two game modes: count symbols or spell words from pictures.
"""

import random
import os

# Symbols to use for the counting game
SYMBOLS = ['★', '●', '♦', '♠', '♥', '▲', '■', '○', '◆', '☆']

# ASCII art pictures for spelling game
PICTURES = {
    'DOG': """
        / \\__
       (    @\\___
       /         O
      /   (_____/
     /_____/   U
    """,
    'CAT': """
       /\\_/\\
      ( o.o )
       > ^ <
      /|   |\\
     (_|   |_)
    """,
    'CAR': """
        ______
       /|_||_\\`.__
      (   _    _ _\\
      =`-(_)--(_)-'
    """,
    'TREE': """
          /\\
         /  \\
        /    \\
       /______\\
          ||
          ||
    """,
    'FOOT': """
       _____
      /     \\
     |       |
     |       |
      \\_____/
       |||||
    """,
    'HAND': """
          _
       __|_|__
      |  |_|  |
      |   _   |
       \\ | | /
        \\   /
         |_|
    """,
    'ARM': """
      ____
     /    \\___
    |         \\___
     \\____        \\
          \\______/
    """,
    'HEAD': """
        _____
       /     \\
      |  o o  |
      |   >   |
      |  \\_/  |
       \\_____/
    """,
    'SUN': """
        \\   |   /
         \\  |  /
       ---[===]---
         /  |  \\
        /   |   \\
    """,
    'MOON': """
          ___
        _/   \\
       /      |
      |       |
       \\_    /
         \\__/
    """,
    'STAR': """
           *
          /|\\
         / | \\
        *--+--*
         \\ | /
          \\|/
           *
    """,
    'MILK': """
        _____
       |     |
       |MILK |
       |     |
       |_____|
    """,
    'BED': """
        _________
       |  ___    |
       | |   |   |
       |_|___|___|
       |_________|
    """,
    'HOUSE': """
           /\\
          /  \\
         /    \\
        /______\\
        |  __  |
        | |  | |
        |_|__|_|
    """,
}


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


def display_picture(word):
    """Display the ASCII art picture for a word."""
    print('┌' + '─' * 30 + '┐')
    for line in PICTURES[word].split('\n'):
        if line:
            # Pad the line to fit in the box
            padded = line[:28].ljust(28)
            print('│ ' + padded + ' │')
    print('└' + '─' * 30 + '┘')


def play_spelling_round(round_num, target_correct):
    """Play a single round of the spelling game."""
    clear_screen()
    print(f"\n═══ Round {round_num} of {target_correct} ═══\n")

    word = random.choice(list(PICTURES.keys()))

    print("What is this? Spell the word:\n")
    display_picture(word)

    answer = input("\nYour answer: ").strip().upper()

    if answer == word:
        print(f"\n✓ Correct! It's a {word}!")
        return True
    else:
        print(f"\n✗ Not quite. It was a {word}.")
        return False


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
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║        SPELLING GAME                   ║")
    print("║                                        ║")
    print("║  Look at the picture and spell the    ║")
    print("║  word! Get 3 correct to win!          ║")
    print("╚════════════════════════════════════════╝")
    print("\nPress Enter to start...")
    input()

    correct = 0
    target = 3
    round_num = 0

    while correct < target:
        round_num += 1
        if play_spelling_round(correct + 1, target):
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
