#!/usr/bin/env python3
import os
import re

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
songs_dir = os.path.join(script_dir, 'songs')

# Find all song HTML files
files = [f for f in os.listdir(songs_dir) if f.endswith('.html')]

print(f"Removing mode indicator from {len(files)} song files...")

for file in files:
    file_path = os.path.join(songs_dir, file)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove the mode indicator CSS block
    content = re.sub(
        r'/\*\s*Mode indicator overlay\s*\*/.*?#modeIndicator\.show\s*\{[^}]+\}',
        '',
        content,
        flags=re.DOTALL
    )

    # Remove the mode indicator HTML element
    content = re.sub(
        r'<!--\s*Mode indicator\s*-->.*?<div id="modeIndicator">.*?</div>',
        '',
        content,
        flags=re.DOTALL
    )

    # Remove the showModeNotification function
    content = re.sub(
        r'function showModeNotification\(\)\s*\{[^}]*\}',
        '',
        content,
        flags=re.DOTALL
    )

    # Remove calls to showModeNotification()
    content = re.sub(
        r'\s*showModeNotification\(\);',
        '',
        content
    )

    # Clean up extra whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ {file}")

print("\n✅ Mode indicator removed from all song pages!")
