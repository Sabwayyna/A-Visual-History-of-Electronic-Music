"""
Fix audio playback - ensure songs have volume set and play audibly
"""

import os
import json

# Load song mapping
with open('song-mapping.json', 'r', encoding='utf-8') as f:
    songs = json.load(f)

# Read all song HTML files and fix them
for song in songs:
    filepath = os.path.join('songs', song['filename'])

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix 1: Add volume setting in the auto-start section
    content = content.replace(
        '''      userStartAudio();
      song.play();
      song.rate(playbackSpeed);
      started = true;''',
        '''      userStartAudio();
      song.setVolume(0.8); // Set volume to 80%
      song.play();
      song.rate(playbackSpeed);
      started = true;'''
    )

    # Fix 2: Also add volume setting in the setup auto-start (after preload)
    content = content.replace(
        '''    setTimeout(() => {
      userStartAudio();
      song.play();
      song.rate(playbackSpeed);
      started = true;
      currentX = 0;
      lastX = 0;
      frameCounter = 0;
      background(0);
      console.log('Auto-started playback');
    }, 500);''',
        '''    setTimeout(() => {
      userStartAudio();
      song.setVolume(0.8); // Set volume to 80%
      song.play();
      song.rate(playbackSpeed);
      started = true;
      currentX = 0;
      lastX = 0;
      frameCounter = 0;
      background(0);
      console.log('Auto-started playback with volume');
    }, 500);'''
    )

    # Fix 3: Ensure amplitude analyzer is set up correctly with smoothing
    content = content.replace(
        'amp = new p5.Amplitude(0.8);',
        'amp = new p5.Amplitude(0.9);'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Fixed: {song['filename']}")

print(f"\n✓ Fixed audio volume for all {len(songs)} song pages!")
print("  - Set volume to 0.8 (80%)")
print("  - Added explicit setVolume() calls")
print("  - Improved amplitude detection")
