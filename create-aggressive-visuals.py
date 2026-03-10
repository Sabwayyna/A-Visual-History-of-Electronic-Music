"""
Create even more aggressive visuals - make them larger, faster, and more frequent
"""

with open('sketch.js', 'r', encoding='utf-8') as f:
    original = f.read()

improved = original

# Make generation happen EVERY frame if there's any audio
improved = improved.replace(
    '''  // Generate shapes with balanced frequency - MORE SENSITIVE FOR QUIET SOUNDS
  let shouldGenerate = false;

  if (isBeat && vol > 0.05) { // Lowered from 0.2
    shouldGenerate = true; // Generate on beats with any reasonable volume
  } else if (frameCounter % 2 === 0 && vol > 0.03) { // Every 2nd frame (was 3rd), lowered from 0.1
    shouldGenerate = true; // More frequent generation
  } else if (vol > 0.2) { // Lowered from 0.4
    shouldGenerate = true; // Loud sections generate more
  } else if (vol > 0.01 && random() < 0.3) { // Add random generation for very quiet sounds
    shouldGenerate = true;
  }

  if (shouldGenerate && vol > 0.005) { // Lowered from 0.01''',
    '''  // Generate shapes VERY AGGRESSIVELY - almost every frame
  let shouldGenerate = false;

  if (isBeat && vol > 0.02) { // Even more sensitive
    shouldGenerate = true;
  } else if (vol > 0.01) { // Generate if there's ANY volume
    shouldGenerate = true;
  } else if (random() < 0.5) { // 50% chance even in silence for visual continuity
    shouldGenerate = true;
  }

  // Generate MULTIPLE shapes per frame for density
  let shapesToGenerate = 1;
  if (vol > 0.3) shapesToGenerate = 3;
  else if (vol > 0.15) shapesToGenerate = 2;
  else if (vol > 0.05) shapesToGenerate = 1;
  else shapesToGenerate = 1; // At least one even in quiet parts

  for (let sg = 0; sg < shapesToGenerate; sg++) {
  if (shouldGenerate && vol > 0.001) { // Almost always generate'''
)

# Close the for loop at the end of generateShapes call
improved = improved.replace(
    '''    // Generate shapes based on audio with 6 frequency bands
    generateShapes(vol, subBassNorm, bassNorm, lowMidNorm, midNorm, highMidNorm, trebleNorm, isBeat, isLoud, isVeryLoud, isQuiet, volChange);
    lastX = currentX;''',
    '''    // Generate shapes based on audio with 6 frequency bands
    generateShapes(vol, subBassNorm, bassNorm, lowMidNorm, midNorm, highMidNorm, trebleNorm, isBeat, isLoud, isVeryLoud, isQuiet, volChange);
  } // End shapes loop
    lastX = currentX;'''
)

# Make ALL shapes MUCH larger - multiply all size parameters by 2-3x
improved = improved.replace(
    '''      addOrganicBlob(currentX + random(-30, 30), blobY, map(vol, 0, 1, 10, 50), vol); // Lowered min size from 15''',
    '''      addOrganicBlob(currentX + random(-30, 30), blobY, map(vol, 0, 1, 25, 100), vol); // 2.5x larger'''
)

improved = improved.replace(
    '''      addScatteredField(currentX, fieldY, fieldWidth, fieldHeight, map(vol, 0, 1, 0.3, 1.2), vol); // Lowered min from 0.4''',
    '''      addScatteredField(currentX, fieldY, fieldWidth, fieldHeight, map(vol, 0, 1, 0.8, 2.5), vol); // Much denser'''
)

improved = improved.replace(
    '''      addCrossHatch(currentX, hatchY, map(vol, 0, 1, 15, 60), map(vol, 0, 1, 20, 80), map(vol, 0, 1, 3, 12), vol); // Lowered mins''',
    '''      addCrossHatch(currentX, hatchY, map(vol, 0, 1, 35, 120), map(vol, 0, 1, 40, 150), map(vol, 0, 1, 8, 25), vol); // Much larger'''
)

improved = improved.replace(
    '''      addWavePattern(currentX + random(-20, 20), waveY, map(treble, 0, 1, 25, 100), map(treble, 0, 1, 3, 18), vol); // Lowered mins''',
    '''      addWavePattern(currentX + random(-20, 20), waveY, map(treble, 0, 1, 50, 180), map(treble, 0, 1, 8, 35), vol); // Much larger waves'''
)

improved = improved.replace(
    '''      addArchitecturalElement(currentX + random(-15, 15), archY, map(bass, 0, 1, 25, 90), map(bass, 0, 1, 18, 70), vol); // Lowered mins''',
    '''      addArchitecturalElement(currentX + random(-15, 15), archY, map(bass, 0, 1, 50, 150), map(bass, 0, 1, 40, 120), vol); // Much larger'''
)

# Increase pattern generation probabilities even more
improved = improved.replace(
    '''    // Organic blob clusters - MORE FREQUENT and SENSITIVE
    if (random() < 0.35 && vol > 0.08) { // Increased from 0.25, lowered vol from 0.2''',
    '''    // Organic blob clusters - VERY FREQUENT
    if (random() < 0.6 && vol > 0.02) {'''
)

improved = improved.replace(
    '''    // Scattered fields of tiny elements - MORE FREQUENT and SENSITIVE
    if (random() < 0.45 && vol > 0.05) { // Increased from 0.35, lowered vol from 0.15''',
    '''    // Scattered fields of tiny elements - VERY FREQUENT
    if (random() < 0.7 && vol > 0.02) {'''
)

improved = improved.replace(
    '''    // Cross-hatching patterns - MORE SENSITIVE
    if (random() < 0.3 && (isLoud || mid > 0.15)) { // Increased from 0.25, lowered mid from 0.3''',
    '''    // Cross-hatching patterns - VERY FREQUENT
    if (random() < 0.5 && (isLoud || mid > 0.05)) {'''
)

improved = improved.replace(
    '''    // Wave patterns - MORE FREQUENT and SENSITIVE
    if (random() < 0.4 && (treble > 0.1 || highMid > 0.1)) { // Increased from 0.3, lowered thresholds from 0.2''',
    '''    // Wave patterns - VERY FREQUENT
    if (random() < 0.6 && (treble > 0.03 || highMid > 0.03)) {'''
)

improved = improved.replace(
    '''    // Architectural elements - MORE SENSITIVE
    if (random() < 0.3 && bass > 0.12) { // Increased from 0.25, lowered bass from 0.25''',
    '''    // Architectural elements - VERY FREQUENT
    if (random() < 0.5 && bass > 0.05) {'''
)

# Make frequency band shapes larger too
improved = improved.replace(
    '''  // Generate core frequency band shapes with more variation
  let maxShapes = floor(map(vol, 0, 1, 1, 4));''',
    '''  // Generate core frequency band shapes with more variation - MORE SHAPES
  let maxShapes = floor(map(vol, 0, 1, 2, 8)); // More shapes per frame'''
)

# Increase shape sizes in the frequency band generation
improved = improved.replace(
    '''    let size = random(8, 30);''',
    '''    let size = random(20, 60); // Much larger base size'''
)

# Write the improved version
with open('sketch.js', 'w', encoding='utf-8') as f:
    f.write(improved)

print("✓ Created aggressive visual version with:")
print("  - Shapes 2-3x LARGER")
print("  - Generate on EVERY frame with audio")
print("  - Multiple shapes per frame (1-3)")
print("  - 50-70% generation probability for all patterns")
print("  - Minimum volume thresholds near zero")
print("  - Base shape sizes doubled")
print("\nVisuals will be MUCH more prominent and fast!")
