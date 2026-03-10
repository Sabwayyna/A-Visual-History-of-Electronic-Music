#!/usr/bin/env python3
import os
import re

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
songs_dir = os.path.join(script_dir, 'songs')

# Find all song HTML files
files = [f for f in os.listdir(songs_dir) if f.endswith('.html')]

print(f"Simplifying controls panel in {len(files)} song files...")

for file in files:
    file_path = os.path.join(songs_dir, file)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the controls panel CSS
    old_controls_panel = re.search(
        r'(/\*\s*Controls panel.*?\*/.*?#controlsPanel\s*\{[^}]+\})',
        content,
        flags=re.DOTALL
    )

    if old_controls_panel:
        # New simplified controls panel styling
        new_controls_panel = '''/* Controls panel - simplified white text */
        #controlsPanel {
            position: fixed;
            top: 80px;
            right: 20px;
            background: transparent;
            padding: 20px 24px;
            color: #ffffff;
            font-size: 14px;
            z-index: 99;
            min-width: 180px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
            line-height: 2;
        }'''

        content = content.replace(old_controls_panel.group(1), new_controls_panel)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✓ {file}")
    else:
        print(f"⚠ Could not find controls panel CSS in {file}")

print("\n✅ Controls panel simplified to white text with no background!")
