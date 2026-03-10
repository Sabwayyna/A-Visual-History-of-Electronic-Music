#!/usr/bin/env python3
import os
import re

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
songs_dir = os.path.join(script_dir, 'songs')

# Find all song HTML files
files = [f for f in os.listdir(songs_dir) if f.endswith('.html')]

print(f"Carefully removing mode indicator from {len(files)} song files...")

for file in files:
    file_path = os.path.join(songs_dir, file)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove the mode indicator CSS - be very specific
    content = re.sub(
        r'        /\* Mode indicator overlay \*/\s+#modeIndicator \{[^}]+\}\s+#modeIndicator\.show \{[^}]+\}',
        '',
        content,
        flags=re.MULTILINE
    )

    # Remove the mode indicator HTML element - be very specific
    content = re.sub(
        r'    <!-- Mode indicator -->\s+<div id="modeIndicator">(?:RADIAL MODE|HORIZONTAL MODE)</div>\s+',
        '',
        content
    )

    # Remove the showModeNotification function definition - very carefully
    content = re.sub(
        r'function showModeNotification\(\) \{\s+// This will be handled by HTML overlay\s+let modeIndicator = document\.getElementById\(\'modeIndicator\'\);\s+if \(modeIndicator\) \{\s+modeIndicator\.textContent = visualMode === \'horizontal\' \? \'HORIZONTAL MODE\' : \'RADIAL MODE\';\s+modeIndicator\.classList\.add\(\'show\'\);\s+setTimeout\(\(\) => \{\s+modeIndicator\.classList\.remove\(\'show\'\);\s+\}, 1500\);\s+\}\s+\}',
        '',
        content,
        flags=re.MULTILINE
    )

    # Remove the call to showModeNotification() inside toggleVisualizationMode
    content = re.sub(
        r'  // Show brief notification\s+showModeNotification\(\);\s+',
        '',
        content
    )

    # Remove window.showModeNotification export
    content = re.sub(
        r'  window\.showModeNotification = showModeNotification;\s+',
        '',
        content
    )

    # Clean up extra blank lines (3 or more)
    content = re.sub(r'\n{3,}', '\n\n', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ {file}")

print("\n✅ Mode indicator carefully removed from all song pages!")
