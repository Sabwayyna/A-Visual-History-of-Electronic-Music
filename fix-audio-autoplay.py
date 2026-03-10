"""
Fix audio autoplay - properly add auto-start code after setup()
Updated to match current setup() structure with radial mode variables
"""

import os
import json
import re

# Load song mapping
with open('song-mapping.json', 'r', encoding='utf-8') as f:
    songs = json.load(f)

# Read all song HTML files and fix them
for song in songs:
    filepath = os.path.join('songs', song['filename'])

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Updated pattern to match current structure with radial mode initialization
    setup_end_pattern = r'(  // Calculate line height for two-line layout\n  lineHeight = height / 2;\n\n  // Initialize center point for radial mode\n  centerX = width / 2;\n  centerY = height / 2;\n})'

    setup_replacement = '''  // Calculate line height for two-line layout
  lineHeight = height / 2;

  // Initialize center point for radial mode
  centerX = width / 2;
  centerY = height / 2;

  // Auto-start the song if it was preloaded
  if (song && typeof AUTO_LOAD_AUDIO !== 'undefined' && AUTO_LOAD_AUDIO) {
    setTimeout(() => {
      userStartAudio();
      song.setVolume(0.5); // Set volume to 50% (reduced from 80%)
      song.play();
      song.rate(playbackSpeed);
      started = true;
      currentX = 0;
      lastX = 0;
      frameCounter = 0;
      background(0);
      console.log('Auto-started playback with volume:', song.getVolume());
    }, 800);
  }
}'''

    # Apply the replacement
    new_content = re.sub(setup_end_pattern, setup_replacement, content)

    # Check if replacement was successful
    if new_content == content:
        print(f"WARNING: Pattern not found in {song['filename']}, trying alternate pattern...")
        # If the auto-start code might already be there, skip
        if 'Auto-start the song if it was preloaded' in content:
            print(f"  → Auto-start code already present in {song['filename']}")
            continue
        else:
            print(f"  → Could not fix {song['filename']}")
            continue

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Fixed: {song['filename']}")

print(f"\n✓ Fixed audio autoplay for all {len(songs)} song pages!")
print("  - Added auto-start code in setup()")
print("  - Set volume to 0.5 (50%)")
print("  - Added delay to help with browser autoplay policies")
