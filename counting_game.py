#!/usr/bin/env python3
"""
Symbol Counting Game for Raspberry Pi
Displays random symbols and asks the user to count them.
"""

import random
import os

# Symbols to use for the game
SYMBOLS = ['★', '●', '♦', '♠', '♥', '▲', '■', '○', '◆', '☆']

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def display_symbols(count, symbol):
    """Display symbols in a scattered pattern."""
    # Create a grid to place symbols
    grid_width = 40
    grid_height = 10
    grid = [[' ' for _ in range(grid_width)] for _ in range(grid_height)]

    # Place symbols randomly on the grid
    placed = 0
    attempts = 0
    while placed < count and attempts < 1000:
        x = random.randint(0, grid_width - 1)
        y = random.randint(0, grid_height - 1)
        if grid[y][x] == ' ':
            grid[y][x] = symbol
            placed += 1
        attempts += 1

    # Print the grid with a border
    print('┌' + '─' * grid_width + '┐')
    for row in grid:
        print('│' + ''.join(row) + '│')
    print('└' + '─' * grid_width + '┘')

def play_round(round_num):
    """Play a single round of the counting game."""
    clear_screen()
    print(f"\n═══ Round {round_num} of 5 ═══\n")

    # Generate random count and symbol
    count = random.randint(5, 10)
    symbol = random.choice(SYMBOLS)

    # Display the symbols
    display_symbols(count, symbol)

    # Get user's answer
    print(f"\nHow many '{symbol}' symbols do you see?")

    while True:
        try:
            answer = int(input("Your answer: "))
            break
        except ValueError:
            print("Please enter a number.")

    # Check answer
    if answer == count:
        print(f"\n✓ Correct! There were {count} symbols.")
        return True
    else:
        print(f"\n✗ Not quite. There were {count} symbols.")
        return False

def main():
    """Main game loop."""
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

    # Play 5 rounds
    for round_num in range(1, 6):
        if play_round(round_num):
            score += 1

        if round_num < 5:
            input("\nPress Enter for the next round...")

    # Show final score
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

    print("\nThanks for playing!\n")

if __name__ == "__main__":
    main()
