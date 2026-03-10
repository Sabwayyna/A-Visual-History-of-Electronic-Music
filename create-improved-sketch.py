"""
Read the original sketch.js and create an improved version with:
1. Better sensitivity for quiet/unique sounds
2. Two-line horizontal layout support
3. Better shape generation for subtle audio
"""

with open('sketch.js', 'r', encoding='utf-8') as f:
    original = f.read()

# Create the improved version with modifications
improved = original

# Add currentLine variable after the other declarations
improved = improved.replace(
    'let quietStreak = 0; // Track consecutive quiet frames',
    '''let quietStreak = 0; // Track consecutive quiet frames
let currentLine = 0; // Current line (0 = top, 1 = bottom)
let lineHeight = 0; // Height of each line'''
)

# Update setup to calculate lineHeight
improved = improved.replace(
    '  // Start with black background\n  background(0);\n}',
    '''  // Start with black background
  background(0);

  // Calculate line height for two-line layout
  lineHeight = height / 2;
}'''
)

# Update the currentX calculation in draw() to support wrapping and two lines
improved = improved.replace(
    '''  // Calculate current X position based on song progress (left to right)
  if (song.duration() > 0 && song.duration() > 0) {
    currentX = map(song.currentTime(), 0, song.duration(), 0, width);
  } else {
    // Fallback: increment based on frame count
    currentX = map(frameCounter, 0, 6000, 0, width); // Assume ~100 seconds at 60fps
    if (currentX > width) {
      currentX = width;
    }
  }''',
    '''  // Calculate current X position based on song progress (left to right with two-line support)
  let totalProgress = 0;
  if (song.duration() > 0) {
    totalProgress = song.currentTime() / song.duration();
  } else {
    // Fallback: increment based on frame count
    totalProgress = frameCounter / 6000; // Assume ~100 seconds at 60fps
    if (totalProgress > 1) totalProgress = 1;
  }

  // Map to two lines: 0-0.5 = line 0, 0.5-1.0 = line 1
  if (totalProgress <= 0.5) {
    currentLine = 0;
    currentX = map(totalProgress, 0, 0.5, 0, width);
  } else {
    currentLine = 1;
    currentX = map(totalProgress, 0.5, 1.0, 0, width);
  }'''
)

# Lower the volume thresholds for better quiet sound detection
improved = improved.replace(
    '''  // Better beat detection using multiple criteria
  let isBeat = (volChange > 0.08 && vol > avgVol * 1.15) || // Sharp increase
               (vol > 0.6 && volChange > 0.05); // Very loud with any increase

  let isLoud = vol > 0.25;
  let isVeryLoud = vol > 0.5;
  let isQuiet = vol < 0.08;''',
    '''  // Better beat detection using multiple criteria - MORE SENSITIVE
  let isBeat = (volChange > 0.03 && vol > avgVol * 1.08) || // Sharp increase (lowered from 0.08)
               (vol > 0.4 && volChange > 0.02) || // Loud with any increase (lowered from 0.6)
               (vol > 0.15 && volChange > 0.05); // Medium volume with sharp change

  let isLoud = vol > 0.15; // Lowered from 0.25
  let isVeryLoud = vol > 0.35; // Lowered from 0.5
  let isQuiet = vol < 0.05; // Lowered from 0.08'''
)

# Make shape generation more sensitive and frequent
improved = improved.replace(
    '''  // Generate shapes with balanced frequency - concentrated areas with breathing room
  let shouldGenerate = false;

  if (isBeat && vol > 0.2) {
    shouldGenerate = true; // Generate on beats with reasonable volume
  } else if (frameCounter % 3 === 0 && vol > 0.1) {
    shouldGenerate = true; // Every 3rd frame if volume is present
  } else if (vol > 0.4) {
    shouldGenerate = true; // Loud sections generate more
  }

  if (shouldGenerate && vol > 0.01) {''',
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

  if (shouldGenerate && vol > 0.005) { // Lowered from 0.01'''
)

# Update the generateShapes function to use currentLine for Y positioning
improved = improved.replace(
    '''function generateShapes(vol, subBass, bass, lowMid, mid, highMid, treble, isBeat, isLoud, isVeryLoud, isQuiet, volChange) {
  // Map 6 frequency bands to vertical positions (from bottom to top)
  let subBassY = map(subBass, 0, 1, height * 0.83, height);        // Bottom layer
  let bassY = map(bass, 0, 1, height * 0.67, height * 0.83);     // Second from bottom
  let lowMidY = map(lowMid, 0, 1, height * 0.5, height * 0.67);  // Lower middle
  let midY = map(mid, 0, 1, height * 0.33, height * 0.5);         // Middle
  let highMidY = map(highMid, 0, 1, height * 0.17, height * 0.33); // Upper middle
  let trebleY = map(treble, 0, 1, 0, height * 0.17);               // Top layer''',
    '''function generateShapes(vol, subBass, bass, lowMid, mid, highMid, treble, isBeat, isLoud, isVeryLoud, isQuiet, volChange) {
  // Calculate Y offset based on current line
  let lineOffset = currentLine * lineHeight;

  // Map 6 frequency bands to vertical positions within the current line (from bottom to top)
  let subBassY = map(subBass, 0, 1, lineOffset + lineHeight * 0.83, lineOffset + lineHeight);        // Bottom layer
  let bassY = map(bass, 0, 1, lineOffset + lineHeight * 0.67, lineOffset + lineHeight * 0.83);     // Second from bottom
  let lowMidY = map(lowMid, 0, 1, lineOffset + lineHeight * 0.5, lineOffset + lineHeight * 0.67);  // Lower middle
  let midY = map(mid, 0, 1, lineOffset + lineHeight * 0.33, lineOffset + lineHeight * 0.5);         // Middle
  let highMidY = map(highMid, 0, 1, lineOffset + lineHeight * 0.17, lineOffset + lineHeight * 0.33); // Upper middle
  let trebleY = map(treble, 0, 1, lineOffset, lineOffset + lineHeight * 0.17);               // Top layer'''
)

# Update quiet mark generation to also use lineOffset
improved = improved.replace(
    '''function generateQuietMark(vol) {
  let y = random(height * 0.3, height * 0.7);''',
    '''function generateQuietMark(vol) {
  let lineOffset = currentLine * lineHeight;
  let y = random(lineOffset + lineHeight * 0.3, lineOffset + lineHeight * 0.7);'''
)

# Update all the pattern generation functions that use random(height) or random(0, height)
# For addOrganicBlob
improved = improved.replace(
    '''    // Organic blob clusters - moderate frequency
    if (random() < 0.25 && vol > 0.2) {
      let blobY = random() < 0.6 ?
        random(height * 0.3, height) :
        random(0, height * 0.5);
      addOrganicBlob(currentX + random(-30, 30), blobY, map(vol, 0, 1, 15, 50), vol);
    }''',
    '''    // Organic blob clusters - MORE FREQUENT and SENSITIVE
    if (random() < 0.35 && vol > 0.08) { // Increased from 0.25, lowered vol from 0.2
      let lineOffset = currentLine * lineHeight;
      let blobY = random() < 0.6 ?
        random(lineOffset + lineHeight * 0.3, lineOffset + lineHeight) :
        random(lineOffset, lineOffset + lineHeight * 0.5);
      addOrganicBlob(currentX + random(-30, 30), blobY, map(vol, 0, 1, 10, 50), vol); // Lowered min size from 15
    }'''
)

# For addScatteredField
improved = improved.replace(
    '''    // Scattered fields of tiny elements - more frequent
    if (random() < 0.35 && vol > 0.15) {
      let fieldY = random(0, height);
      let fieldWidth = random(50, 120);
      let fieldHeight = random(40, 100);
      addScatteredField(currentX, fieldY, fieldWidth, fieldHeight, map(vol, 0, 1, 0.4, 1.2), vol);
    }''',
    '''    // Scattered fields of tiny elements - MORE FREQUENT and SENSITIVE
    if (random() < 0.45 && vol > 0.05) { // Increased from 0.35, lowered vol from 0.15
      let lineOffset = currentLine * lineHeight;
      let fieldY = random(lineOffset, lineOffset + lineHeight);
      let fieldWidth = random(50, 120);
      let fieldHeight = random(40, 100);
      addScatteredField(currentX, fieldY, fieldWidth, fieldHeight, map(vol, 0, 1, 0.3, 1.2), vol); // Lowered min from 0.4
    }'''
)

# For addCrossHatch
improved = improved.replace(
    '''    // Cross-hatching patterns - on loud sections
    if (random() < 0.25 && (isLoud || mid > 0.3)) {
      let hatchY = random() < 0.5 ?
        random(height * 0.4, height) :
        random(0, height * 0.6);
      addCrossHatch(currentX, hatchY, map(vol, 0, 1, 20, 60), map(vol, 0, 1, 25, 80), map(vol, 0, 1, 4, 12), vol);
    }''',
    '''    // Cross-hatching patterns - MORE SENSITIVE
    if (random() < 0.3 && (isLoud || mid > 0.15)) { // Increased from 0.25, lowered mid from 0.3
      let lineOffset = currentLine * lineHeight;
      let hatchY = random() < 0.5 ?
        random(lineOffset + lineHeight * 0.4, lineOffset + lineHeight) :
        random(lineOffset, lineOffset + lineHeight * 0.6);
      addCrossHatch(currentX, hatchY, map(vol, 0, 1, 15, 60), map(vol, 0, 1, 20, 80), map(vol, 0, 1, 3, 12), vol); // Lowered mins
    }'''
)

# For addWavePattern
improved = improved.replace(
    '''    // Wave patterns - more frequent
    if (random() < 0.3 && (treble > 0.2 || highMid > 0.2)) {
      let waveY = random(0, height);
      addWavePattern(currentX + random(-20, 20), waveY, map(treble, 0, 1, 35, 100), map(treble, 0, 1, 4, 18), vol);
    }''',
    '''    // Wave patterns - MORE FREQUENT and SENSITIVE
    if (random() < 0.4 && (treble > 0.1 || highMid > 0.1)) { // Increased from 0.3, lowered thresholds from 0.2
      let lineOffset = currentLine * lineHeight;
      let waveY = random(lineOffset, lineOffset + lineHeight);
      addWavePattern(currentX + random(-20, 20), waveY, map(treble, 0, 1, 25, 100), map(treble, 0, 1, 3, 18), vol); // Lowered mins
    }'''
)

# For architectural elements
improved = improved.replace(
    '''    // Architectural elements - moderate frequency
    if (random() < 0.25 && bass > 0.25) {
      let archY = random() < 0.6 ?
        random(height * 0.5, height) :''',
    '''    // Architectural elements - MORE SENSITIVE
    if (random() < 0.3 && bass > 0.12) { // Increased from 0.25, lowered bass from 0.25
      let lineOffset = currentLine * lineHeight;
      let archY = random() < 0.6 ?
        random(lineOffset + lineHeight * 0.5, lineOffset + lineHeight) :'''
)

# Update the continuation of architectural elements
improved = improved.replace(
    '''        random(height * 0.5, height) :
        random(0, height * 0.4);
      addArchitecturalElement(currentX + random(-15, 15), archY, map(bass, 0, 1, 30, 90), map(bass, 0, 1, 20, 70), vol);
    }''',
    '''        random(lineOffset + lineHeight * 0.5, lineOffset + lineHeight) :
        random(lineOffset, lineOffset + lineHeight * 0.4);
      addArchitecturalElement(currentX + random(-15, 15), archY, map(bass, 0, 1, 25, 90), map(bass, 0, 1, 18, 70), vol); // Lowered mins
    }'''
)

# Write the improved version
with open('sketch-improved.js', 'w', encoding='utf-8') as f:
    f.write(improved)

print("✓ Created improved sketch.js with:")
print("  - Better sensitivity for quiet/unique sounds")
print("  - Two-line horizontal layout for long songs")
print("  - More frequent shape generation")
print("  - Lower volume thresholds")
print("\nFile saved as: sketch-improved.js")
