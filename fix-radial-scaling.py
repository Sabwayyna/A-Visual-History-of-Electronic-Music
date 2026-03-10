"""
1. Disable architectural elements (white rectangles) in radial mode
2. Add progressive size scaling - shapes start small at center, grow larger outward
"""

with open('sketch.js', 'r', encoding='utf-8') as f:
    sketch = f.read()

# 1. Disable architectural elements in radial mode
sketch = sketch.replace(
    '''    // Architectural elements - REDUCED FREQUENCY
    if (random() < 0.15 && bass > 0.2) {''',
    '''    // Architectural elements - DISABLED IN RADIAL MODE
    if (visualMode === 'horizontal' && random() < 0.15 && bass > 0.2) {'''
)

# 2. Add size scaling variable after the visualMode position calculations
# Find the section where we calculate positions and add sizeMultiplier
sketch = sketch.replace(
    '''  } else if (visualMode === 'radial') {
    // RADIAL MODE: Center-outward expansion in spiral
    // Map progress to angle (0-360 degrees, multiple rotations)
    let rotations = 8; // Number of full rotations throughout the song
    currentAngle = totalProgress * 360 * rotations;

    // Map progress to radius (0 to max radius) - FASTER EXPANSION
    let maxRadius = min(width, height) * 0.65; // Larger radius for faster expansion
    currentRadius = totalProgress * maxRadius;

    // Calculate X, Y from polar coordinates
    currentX = centerX + cos(currentAngle) * currentRadius;
    currentLine = 0; // Not used in radial mode
  }''',
    '''  } else if (visualMode === 'radial') {
    // RADIAL MODE: Center-outward expansion in spiral
    // Map progress to angle (0-360 degrees, multiple rotations)
    let rotations = 8; // Number of full rotations throughout the song
    currentAngle = totalProgress * 360 * rotations;

    // Map progress to radius (0 to max radius) - FASTER EXPANSION
    let maxRadius = min(width, height) * 0.65; // Larger radius for faster expansion
    currentRadius = totalProgress * maxRadius;

    // Calculate X, Y from polar coordinates
    currentX = centerX + cos(currentAngle) * currentRadius;
    currentLine = 0; // Not used in radial mode
  }

  // Size multiplier for radial mode - start small at center, grow outward
  let sizeMultiplier = 1.0;
  if (visualMode === 'radial') {
    // Scale from 0.3 (30% size at center) to 1.5 (150% size at edge)
    sizeMultiplier = map(totalProgress, 0, 1, 0.3, 1.5);
  }'''
)

# 3. Apply sizeMultiplier to all shape generation calls
# Find and update the generateShapes function call to pass sizeMultiplier
sketch = sketch.replace(
    '''  // Generate shapes periodically based on volume
  if (shouldGenerate && vol > 0.003) {
    generateShapes(vol, subBass, bass, lowMid, mid, highMid, treble, isBeat, isLoud, isVeryLoud, isQuiet, volChange);
  }''',
    '''  // Generate shapes periodically based on volume
  if (shouldGenerate && vol > 0.003) {
    generateShapes(vol, subBass, bass, lowMid, mid, highMid, treble, isBeat, isLoud, isVeryLoud, isQuiet, volChange, sizeMultiplier);
  }'''
)

# 4. Update generateShapes function signature to accept sizeMultiplier
sketch = sketch.replace(
    '''function generateShapes(vol, subBass, bass, lowMid, mid, highMid, treble, isBeat, isLoud, isVeryLoud, isQuiet, volChange) {''',
    '''function generateShapes(vol, subBass, bass, lowMid, mid, highMid, treble, isBeat, isLoud, isVeryLoud, isQuiet, volChange, sizeMultiplier = 1.0) {'''
)

# 5. Apply sizeMultiplier to shape sizes throughout generateShapes
# Update blob sizes
sketch = sketch.replace(
    '''      addOrganicBlob(blobX, blobY, map(vol, 0, 1, 30, 80), vol);''',
    '''      addOrganicBlob(blobX, blobY, map(vol, 0, 1, 30, 80) * sizeMultiplier, vol);'''
)

# Update scattered field sizes
sketch = sketch.replace(
    '''      let fieldWidth = random(50, 120);
      let fieldHeight = random(40, 100);
      addScatteredField(fieldX, fieldY, fieldWidth, fieldHeight, map(vol, 0, 1, 0.4, 1.2), vol);''',
    '''      let fieldWidth = random(50, 120) * sizeMultiplier;
      let fieldHeight = random(40, 100) * sizeMultiplier;
      addScatteredField(fieldX, fieldY, fieldWidth, fieldHeight, map(vol, 0, 1, 0.4, 1.2) * sizeMultiplier, vol);'''
)

# Update frequency band shapes (circles, blobs)
sketch = sketch.replace(
    '''      addFrequencyShape(currentX + random(-10, 10), subBassY, map(subBass, 0, 1, 15, 50), subBass, vol);''',
    '''      addFrequencyShape(currentX + random(-10, 10), subBassY, map(subBass, 0, 1, 15, 50) * sizeMultiplier, subBass, vol);'''
)

sketch = sketch.replace(
    '''      addFrequencyShape(currentX + random(-8, 8), bassY, map(bass, 0, 1, 12, 45), bass, vol);''',
    '''      addFrequencyShape(currentX + random(-8, 8), bassY, map(bass, 0, 1, 12, 45) * sizeMultiplier, bass, vol);'''
)

sketch = sketch.replace(
    '''      addFrequencyShape(currentX + random(-6, 6), lowMidY, map(lowMid, 0, 1, 10, 40), lowMid, vol);''',
    '''      addFrequencyShape(currentX + random(-6, 6), lowMidY, map(lowMid, 0, 1, 10, 40) * sizeMultiplier, lowMid, vol);'''
)

sketch = sketch.replace(
    '''      addFrequencyShape(currentX + random(-5, 5), midY, map(mid, 0, 1, 8, 35), mid, vol);''',
    '''      addFrequencyShape(currentX + random(-5, 5), midY, map(mid, 0, 1, 8, 35) * sizeMultiplier, mid, vol);'''
)

sketch = sketch.replace(
    '''      addFrequencyShape(currentX + random(-4, 4), highMidY, map(highMid, 0, 1, 6, 30), highMid, vol);''',
    '''      addFrequencyShape(currentX + random(-4, 4), highMidY, map(highMid, 0, 1, 6, 30) * sizeMultiplier, highMid, vol);'''
)

sketch = sketch.replace(
    '''      addFrequencyShape(currentX + random(-3, 3), trebleY, map(treble, 0, 1, 4, 25), treble, vol);''',
    '''      addFrequencyShape(currentX + random(-3, 3), trebleY, map(treble, 0, 1, 4, 25) * sizeMultiplier, treble, vol);'''
)

# Update wave patterns
sketch = sketch.replace(
    '''      addWavePattern(waveX, waveY, map(treble + highMid, 0, 2, 35, 90), map(treble, 0, 1, 25, 70), vol);''',
    '''      addWavePattern(waveX, waveY, map(treble + highMid, 0, 2, 35, 90) * sizeMultiplier, map(treble, 0, 1, 25, 70) * sizeMultiplier, vol);'''
)

# Update cross-hatching
sketch = sketch.replace(
    '''      addCrossHatch(hatchX, hatchY, map(mid, 0, 1, 35, 90), map(mid, 0, 1, 35, 90), vol);''',
    '''      addCrossHatch(hatchX, hatchY, map(mid, 0, 1, 35, 90) * sizeMultiplier, map(mid, 0, 1, 35, 90) * sizeMultiplier, vol);'''
)

# Update circular burst
sketch = sketch.replace(
    '''    if (isBeat && random() < 0.55) {
      let burstSize = map(vol, 0, 1, 30, 90);''',
    '''    if (isBeat && random() < 0.55) {
      let burstSize = map(vol, 0, 1, 30, 90) * sizeMultiplier;'''
)

with open('sketch.js', 'w', encoding='utf-8') as f:
    f.write(sketch)

print("✓ Fixed radial mode:")
print("  - DISABLED architectural elements (white rectangles) in radial mode")
print("  - Added progressive size scaling:")
print("    • Shapes start at 30% size at center")
print("    • Gradually grow to 150% size at outer edge")
print("  - Applied scaling to all shape types:")
print("    • Frequency shapes, blobs, fields")
print("    • Wave patterns, cross-hatching")
print("    • Circular bursts")
