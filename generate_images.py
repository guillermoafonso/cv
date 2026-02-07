#!/usr/bin/env python3
"""
Generate and save all spelling game images as PNG files.
"""

import os
import sys

try:
    import pygame
except ImportError:
    print("Please install pygame: sudo apt install python3-pygame")
    sys.exit(1)

# Import drawing functions from the game
from counting_game import (
    DRAW_FUNCTIONS, WHITE, SPELLING_WORDS
)

def generate_all_images():
    """Generate and save all images as PNG files."""
    pygame.init()

    # Create images folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)

    print("Generating images...\n")

    for word in SPELLING_WORDS:
        # Create surface
        width, height = 400, 350
        surface = pygame.Surface((width, height))
        surface.fill(WHITE)

        # Draw the image
        cx, cy = width // 2, height // 2 - 20
        if word in DRAW_FUNCTIONS:
            DRAW_FUNCTIONS[word](surface, cx, cy)

        # Save as PNG
        filename = os.path.join(images_dir, f'{word.lower()}.png')
        pygame.image.save(surface, filename)
        print(f"  Saved: {filename}")

    pygame.quit()

    print(f"\nDone! {len(SPELLING_WORDS)} images saved to: {images_dir}")
    print("\nReview the images and let me know which ones you'd like changed.")

if __name__ == "__main__":
    generate_all_images()
