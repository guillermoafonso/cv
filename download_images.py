#!/usr/bin/env python3
"""
Download free images from Pixabay for the spelling game.
All images are from Pixabay and are free for commercial use (Pixabay License).
"""

import os
import urllib.request
import ssl

# Create images directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, 'images')

# Direct download URLs from Pixabay (PNG format)
# These are all free images under the Pixabay Content License
# Source: https://pixabay.com - Free for commercial use, no attribution required
IMAGE_URLS = {
    'dog': 'https://cdn.pixabay.com/photo/2013/07/12/18/20/dog-153963_640.png',
    'cat': 'https://cdn.pixabay.com/photo/2014/04/13/20/49/cat-323262_640.png',
    'car': 'https://cdn.pixabay.com/photo/2013/07/12/14/07/car-147828_640.png',
    'tree': 'https://cdn.pixabay.com/photo/2016/03/02/13/59/tree-1232109_640.png',
    'foot': 'https://cdn.pixabay.com/photo/2012/04/10/23/41/foot-27062_640.png',
    'hand': 'https://cdn.pixabay.com/photo/2013/07/12/14/48/hand-148563_640.png',
    'arm': 'https://cdn.pixabay.com/photo/2014/04/03/10/55/arm-311270_640.png',
    'head': 'https://cdn.pixabay.com/photo/2013/07/12/14/33/face-148456_640.png',
    'sun': 'https://cdn.pixabay.com/photo/2013/07/12/19/30/sun-154711_640.png',
    'moon': 'https://cdn.pixabay.com/photo/2014/04/02/10/44/moon-304154_640.png',
    'star': 'https://cdn.pixabay.com/photo/2012/04/01/18/51/star-24151_640.png',
    'milk': 'https://cdn.pixabay.com/photo/2013/07/13/01/21/milk-155473_640.png',
    'bed': 'https://cdn.pixabay.com/photo/2014/04/03/10/02/bed-309103_640.png',
    'house': 'https://cdn.pixabay.com/photo/2013/07/12/17/00/house-151685_640.png',
}

def download_image(word, url):
    """Download a single image."""
    filename = os.path.join(IMAGES_DIR, f'{word}.png')

    if os.path.exists(filename):
        print(f"  ✓ {word}.png already exists, skipping")
        return True

    try:
        # Create SSL context that doesn't verify certificates (for older Python versions)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        print(f"  Downloading {word}.png...", end=' ', flush=True)

        # Add headers to look like a browser
        request = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; EducationalGame/1.0)'}
        )

        with urllib.request.urlopen(request, context=context, timeout=30) as response:
            data = response.read()

        with open(filename, 'wb') as f:
            f.write(data)

        print("✓")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    print("╔════════════════════════════════════════╗")
    print("║     Spelling Game Image Downloader     ║")
    print("╚════════════════════════════════════════╝")
    print()
    print("This script downloads free images from Pixabay")
    print("for use with the spelling game.")
    print()
    print("All images are under the Pixabay Content License")
    print("(free for commercial use, no attribution required)")
    print()

    # Create images directory if it doesn't exist
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
        print(f"Created directory: {IMAGES_DIR}")

    print(f"\nDownloading {len(IMAGE_URLS)} images...\n")

    success_count = 0
    fail_count = 0

    for word, url in IMAGE_URLS.items():
        if download_image(word, url):
            success_count += 1
        else:
            fail_count += 1

    print()
    print("═" * 44)
    print(f"  Downloaded: {success_count}/{len(IMAGE_URLS)} images")

    if fail_count > 0:
        print(f"  Failed: {fail_count} images")
        print()
        print("  Some images failed to download.")
        print("  You can download them manually from pixabay.com")
        print("  and save them in the 'images' folder as:")
        print("  dog.png, cat.png, car.png, etc.")
    else:
        print()
        print("  All images downloaded successfully!")
        print("  You can now run the spelling game:")
        print("  python3 counting_game.py")

    print()


if __name__ == "__main__":
    main()
