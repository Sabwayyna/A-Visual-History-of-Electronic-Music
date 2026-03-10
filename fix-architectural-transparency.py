"""
Fix architectural elements (white rectangles):
1. Make them more transparent (0.5 → 0.18 alpha)
2. Only appear in loud significant parts (bass > 0.25 → bass > 0.5)
3. Reduce frequency (0.25 → 0.08 probability)
4. Add isVeryLoud condition for more selectivity
"""

with open('sketch.js', 'r', encoding='utf-8') as f:
    sketch = f.read()

# 1. Make architectural elements more transparent
sketch = sketch.replace(
    "  let baseColor = getShapeColor(vol, 'bass', false, false, false, 0.5);",
    "  let baseColor = getShapeColor(vol, 'bass', false, false, false, 0.18); // More transparent"
)

# 2. Only appear in loud significant parts + reduce frequency
sketch = sketch.replace(
    '''    // Architectural elements - moderate frequency
    if (random() < 0.25 && bass > 0.25) {''',
    '''    // Architectural elements - RARE, loud parts only
    if (random() < 0.08 && bass > 0.5 && isVeryLoud) {'''
)

# 3. Keep the very strong beat architectural elements but reduce frequency
sketch = sketch.replace(
    '''    // Add architectural bracket on very strong beats
    if (vol > 0.8 && random() < 0.25) {''',
    '''    // Add architectural bracket on very strong beats - REDUCED
    if (vol > 0.8 && random() < 0.12) {'''
)

with open('sketch.js', 'w', encoding='utf-8') as f:
    f.write(sketch)

print("✓ Fixed architectural elements (white rectangles):")
print("  - Transparency: 50% → 18% opacity (much more transparent)")
print("  - Frequency: 25% → 8% chance (appear 68% less)")
print("  - Threshold: bass > 0.25 → bass > 0.5 (only loud parts)")
print("  - Added isVeryLoud condition (only significant moments)")
print("  - Strong beat frequency: 25% → 12%")
print("  → White rectangles will now be subtle and rare, only in loud climactic moments")
