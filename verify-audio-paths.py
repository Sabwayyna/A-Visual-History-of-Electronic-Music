"""
Verify all audio paths are correct and files exist
"""

import os
import json

# Load song mapping
with open('song-mapping.json', 'r', encoding='utf-8') as f:
    songs = json.load(f)

print("Checking all audio files...\n")

all_exist = True
for song in songs:
    audio_path = song['audio']
    full_path = audio_path  # Already relative to project root

    if os.path.exists(full_path):
        file_size = os.path.getsize(full_path)
        file_size_mb = file_size / (1024 * 1024)
        print(f"✓ {song['filename']}")
        print(f"  Audio: {audio_path}")
        print(f"  Size: {file_size_mb:.2f} MB")

        # Check the HTML file references this audio
        html_path = os.path.join('songs', song['filename'])
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Check if AUTO_LOAD_AUDIO points to the right file
            expected_path = f"../{audio_path}"
            if expected_path in html_content:
                print(f"  HTML reference: ✓ Correct")
            else:
                print(f"  HTML reference: ✗ MISMATCH")
                print(f"    Expected: {expected_path}")
                all_exist = False
        else:
            print(f"  HTML file: ✗ NOT FOUND")
            all_exist = False

        print()
    else:
        print(f"✗ {song['filename']}")
        print(f"  Audio: {audio_path} - FILE NOT FOUND")
        print()
        all_exist = False

if all_exist:
    print("\n✓ All audio files exist and HTML references are correct!")
else:
    print("\n✗ Some files are missing or references are incorrect")
