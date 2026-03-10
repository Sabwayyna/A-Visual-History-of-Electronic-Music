"""
1. Speed up radial expansion
2. Reduce white rectangles (architectural elements)
"""

with open('sketch.js', 'r', encoding='utf-8') as f:
    sketch = f.read()

# Speed up radial expansion - increase maxRadius from 0.45 to 0.65
sketch = sketch.replace(
    '''    // Map progress to radius (0 to max radius)
    let maxRadius = min(width, height) * 0.45; // Stay within bounds
    currentRadius = totalProgress * maxRadius;''',
    '''    // Map progress to radius (0 to max radius) - FASTER EXPANSION
    let maxRadius = min(width, height) * 0.65; // Larger radius for faster expansion
    currentRadius = totalProgress * maxRadius;'''
)

# Reduce architectural elements (white rectangles) frequency
sketch = sketch.replace(
    '''    // Architectural elements
    if (random() < 0.4 && bass > 0.1) {''',
    '''    // Architectural elements - REDUCED FREQUENCY
    if (random() < 0.15 && bass > 0.2) {'''
)

# Also reduce the size of architectural elements when they do appear
sketch = sketch.replace(
    '''      addArchitecturalElement(currentX + random(-15, 15), archY, map(bass, 0, 1, 25, 90), map(bass, 0, 1, 18, 70), vol);''',
    '''      addArchitecturalElement(currentX + random(-15, 15), archY, map(bass, 0, 1, 15, 60), map(bass, 0, 1, 12, 45), vol); // Smaller'''
)

# Reduce cross-hatching too (they can look rectangular)
sketch = sketch.replace(
    '''    // Cross-hatching patterns
    if (random() < 0.4 && (isLoud || mid > 0.15)) {''',
    '''    // Cross-hatching patterns - REDUCED
    if (random() < 0.25 && (isLoud || mid > 0.2)) {'''
)

# Make organic blobs and wave patterns more prominent instead
sketch = sketch.replace(
    '''    // Organic blob clusters - more frequent
    if (random() < 0.45 && vol > 0.08) {''',
    '''    // Organic blob clusters - MORE FREQUENT (less rectangles)
    if (random() < 0.55 && vol > 0.06) {'''
)

sketch = sketch.replace(
    '''    // Wave patterns - more frequent
    if (random() < 0.5 && (treble > 0.08 || highMid > 0.08)) {''',
    '''    // Wave patterns - MORE FREQUENT (less rectangles)
    if (random() < 0.6 && (treble > 0.06 || highMid > 0.06)) {'''
)

with open('sketch.js', 'w', encoding='utf-8') as f:
    f.write(sketch)

print("✓ Adjusted radial mode and reduced rectangles:")
print("  - Radial expansion: 0.45 → 0.65 (44% faster)")
print("  - Architectural elements: 40% → 15% frequency")
print("  - Architectural size: reduced by ~30%")
print("  - Cross-hatching: 40% → 25% frequency")
print("  - Organic blobs: 45% → 55% (more curved shapes)")
print("  - Wave patterns: 50% → 60% (more curved shapes)")
1122