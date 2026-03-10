"""
Fix the mode toggle button by properly exposing the function to window scope
"""

import os
import json

# Load song mapping
with open('song-mapping.json', 'r', encoding='utf-8') as f:
    songs = json.load(f)

# Fix each song HTML file
for song in songs:
    filepath = os.path.join('songs', song['filename'])

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Change the button onclick to use a properly exposed function
    # Replace the onclick in the HTML
    content = content.replace(
        '<div id="modeToggleBtn" onclick="toggleVisualizationMode()">',
        '<div id="modeToggleBtn">'
    )

    # Add a script section after the p5 sketch to wire up the button
    # Find the closing script tag and add our wiring before it
    content = content.replace(
        '''    </script>
</body>
</html>''',
        '''    </script>
    <script>
        // Wire up mode toggle button after page loads
        window.addEventListener('load', function() {
            const modeBtn = document.getElementById('modeToggleBtn');
            if (modeBtn) {
                modeBtn.addEventListener('click', function() {
                    // Call the p5.js function through window scope
                    if (typeof toggleVisualizationMode === 'function') {
                        toggleVisualizationMode();
                    }
                });
            }
        });
    </script>
</body>
</html>'''
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Fixed: {song['filename']}")

# Also update sketch.js to expose the function properly
with open('sketch.js', 'r', encoding='utf-8') as f:
    sketch = f.read()

# Make sure the function is exposed to window
sketch = sketch.replace(
    '''function toggleVisualizationMode() {
  if (visualMode === 'horizontal') {
    visualMode = 'radial';
    console.log('Switched to RADIAL mode (center-outward)');
  } else {
    visualMode = 'horizontal';
    console.log('Switched to HORIZONTAL mode (left-to-right)');
  }
  // Show brief notification
  showModeNotification();
}''',
    '''function toggleVisualizationMode() {
  if (visualMode === 'horizontal') {
    visualMode = 'radial';
    console.log('Switched to RADIAL mode (center-outward)');
  } else {
    visualMode = 'horizontal';
    console.log('Switched to HORIZONTAL mode (left-to-right)');
  }
  // Show brief notification
  showModeNotification();
}

// Expose to window for button access
if (typeof window !== 'undefined') {
  window.toggleVisualizationMode = toggleVisualizationMode;
}'''
)

with open('sketch.js', 'w', encoding='utf-8') as f:
    f.write(sketch)

print(f"\n✓ Fixed mode toggle button for all {len(songs)} song pages!")
print("  - Properly wired button click event")
print("  - Exposed function to window scope")
print("  - Added event listener after page load")
