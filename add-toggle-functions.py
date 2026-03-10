"""
Add the missing toggle functions to sketch.js
"""

with open('sketch.js', 'r', encoding='utf-8') as f:
    sketch = f.read()

# Find where to add the functions - before keyPressed
# Add the toggle functions before keyPressed

toggle_functions = '''
// Mode toggle functions
function toggleVisualizationMode() {
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

function showModeNotification() {
  // This will be handled by HTML overlay
  let modeIndicator = document.getElementById('modeIndicator');
  if (modeIndicator) {
    modeIndicator.textContent = visualMode === 'horizontal' ? 'HORIZONTAL MODE' : 'RADIAL MODE';
    modeIndicator.classList.add('show');
    setTimeout(() => {
      modeIndicator.classList.remove('show');
    }, 1500);
  }
}

// Expose to window for button access
if (typeof window !== 'undefined') {
  window.toggleVisualizationMode = toggleVisualizationMode;
  window.showModeNotification = showModeNotification;
}

'''

# Add before keyPressed function
sketch = sketch.replace(
    'function keyPressed() {',
    toggle_functions + 'function keyPressed() {'
)

# Add M key handler in keyPressed if not already there
if "key === 'm'" not in sketch.lower():
    sketch = sketch.replace(
        "  } else if (key === 'h' || key === 'H') {\n    showUI = !showUI;\n  }\n}",
        "  } else if (key === 'h' || key === 'H') {\n    showUI = !showUI;\n  } else if (key === 'm' || key === 'M') {\n    toggleVisualizationMode();\n  }\n}"
    )

with open('sketch.js', 'w', encoding='utf-8') as f:
    f.write(sketch)

print("✓ Added toggle functions to sketch.js")
print("  - toggleVisualizationMode()")
print("  - showModeNotification()")
print("  - Exposed to window scope")
print("  - Added M key handler")
