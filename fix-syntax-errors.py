#!/usr/bin/env python3
import os
import re

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
songs_dir = os.path.join(script_dir, 'songs')

# Find all song HTML files
files = [f for f in os.listdir(songs_dir) if f.endswith('.html')]

print(f"Fixing syntax errors in {len(files)} song files...")

for file in files:
    file_path = os.path.join(songs_dir, file)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove orphaned setTimeout closing
    content = re.sub(r',\s*1500\);\s*\}\s*\}', '', content)

    # Remove duplicate "Expose to window" blocks - keep only one
    # First, find all occurrences
    expose_pattern = r'// Expose to window for button access\s+if \(typeof window !== \'undefined\'\) \{\s+window\.toggleVisualizationMode = toggleVisualizationMode;\s+\}'

    # Find all matches
    matches = list(re.finditer(expose_pattern, content))

    # Remove all but the first occurrence
    if len(matches) > 1:
        for match in reversed(matches[1:]):  # Keep first, remove rest
            content = content[:match.start()] + content[match.end():]

    # Clean up excessive blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ {file}")

print("\n✅ Syntax errors fixed!")
