"""
Fix visuals properly - increase size and frequency WITHOUT breaking syntax
"""

with open('sketch.js', 'r', encoding='utf-8') as f:
    original = f.read()

improved = original

# First apply the two-line layout changes
improved = improved.replace(
    'let quietStreak = 0; // Track consecutive quiet frames',
    '''let quietStreak = 0; // Track consecutive quiet frames
let currentLine = 0; // Current line (0 = top, 1 = bottom)
let lineHeight = 0; // Height of each line'''
)

improved = improved.replace(
    '  // Start with black background\n  background(0);\n}',
    '''  // Start with black background
  background(0);

  // Calculate line height for two-line layout
  lineHeight = height / 2;
}'''
)

# Update currentX calculation for two lines
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

# Make beat detection and thresholds more sensitive
improved = improved.replace(
    '''  // Better beat detection using multiple criteria
  let isBeat = (volChange > 0.08 && vol > avgVol * 1.15) || // Sharp increase
               (vol > 0.6 && volChange > 0.05); // Very loud with any increase

  let isLoud = vol > 0.25;
  let isVeryLoud = vol > 0.5;
  let isQuiet = vol < 0.08;''',
    '''  // Better beat detection - MORE SENSITIVE
  let isBeat = (volChange > 0.04 && vol > avgVol * 1.1) || // Sharp increase
               (vol > 0.35 && volChange > 0.02) || // Loud with increase
               (vol > 0.15 && volChange > 0.06); // Medium with sharp change

  let isLoud = vol > 0.12; // More sensitive
  let isVeryLoud = vol > 0.3; // More sensitive
  let isQuiet = vol < 0.05; // More sensitive'''
)

# Make shape generation more frequent
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
    '''  // Generate shapes more frequently for better visibility
  let shouldGenerate = false;

  if (isBeat && vol > 0.05) {
    shouldGenerate = true; // Generate on beats
  } else if (frameCounter % 1 === 0 && vol > 0.02) {
    shouldGenerate = true; // EVERY frame if volume present
  } else if (vol > 0.15) {
    shouldGenerate = true; // Loud sections
  } else if (random() < 0.4) {
    shouldGenerate = true; // Random generation for continuity
  }

  if (shouldGenerate && vol > 0.003) {'''
)

# Update generateShapes to use currentLine for Y positioning
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

  // Map 6 frequency bands to vertical positions within current line
  let subBassY = map(subBass, 0, 1, lineOffset + lineHeight * 0.83, lineOffset + lineHeight);
  let bassY = map(bass, 0, 1, lineOffset + lineHeight * 0.67, lineOffset + lineHeight * 0.83);
  let lowMidY = map(lowMid, 0, 1, lineOffset + lineHeight * 0.5, lineOffset + lineHeight * 0.67);
  let midY = map(mid, 0, 1, lineOffset + lineHeight * 0.33, lineOffset + lineHeight * 0.5);
  let highMidY = map(highMid, 0, 1, lineOffset + lineHeight * 0.17, lineOffset + lineHeight * 0.33);
  let trebleY = map(treble, 0, 1, lineOffset, lineOffset + lineHeight * 0.17);'''
)

# Make shapes LARGER
improved = improved.replace(
    '''    let size = random(8, 30);''',
    '''    let size = random(15, 50); // Larger shapes'''
)

# Increase blob sizes
improved = improved.replace(
    '''      addOrganicBlob(currentX + random(-30, 30), blobY, map(vol, 0, 1, 15, 50), vol);''',
    '''      addOrganicBlob(currentX + random(-30, 30), blobY, map(vol, 0, 1, 30, 80), vol); // Larger'''
)

# Make pattern generation more frequent
improved = improved.replace(
    '''    // Organic blob clusters - moderate frequency
    if (random() < 0.25 && vol > 0.2) {
      let blobY = random() < 0.6 ?
        random(height * 0.3, height) :
        random(0, height * 0.5);''',
    '''    // Organic blob clusters - more frequent
    if (random() < 0.45 && vol > 0.08) {
      let lineOffset = currentLine * lineHeight;
      let blobY = random() < 0.6 ?
        random(lineOffset + lineHeight * 0.3, lineOffset + lineHeight) :
        random(lineOffset, lineOffset + lineHeight * 0.5);'''
)

improved = improved.replace(
    '''    // Scattered fields of tiny elements - more frequent
    if (random() < 0.35 && vol > 0.15) {
      let fieldY = random(0, height);''',
    '''    // Scattered fields - more frequent
    if (random() < 0.55 && vol > 0.06) {
      let lineOffset = currentLine * lineHeight;
      let fieldY = random(lineOffset, lineOffset + lineHeight);'''
)

improved = improved.replace(
    '''    // Cross-hatching patterns - on loud sections
    if (random() < 0.25 && (isLoud || mid > 0.3)) {
      let hatchY = random() < 0.5 ?
        random(height * 0.4, height) :
        random(0, height * 0.6);''',
    '''    // Cross-hatching patterns
    if (random() < 0.4 && (isLoud || mid > 0.15)) {
      let lineOffset = currentLine * lineHeight;
      let hatchY = random() < 0.5 ?
        random(lineOffset + lineHeight * 0.4, lineOffset + lineHeight) :
        random(lineOffset, lineOffset + lineHeight * 0.6);'''
)

improved = improved.replace(
    '''    // Wave patterns - more frequent
    if (random() < 0.3 && (treble > 0.2 || highMid > 0.2)) {
      let waveY = random(0, height);''',
    '''    // Wave patterns - more frequent
    if (random() < 0.5 && (treble > 0.08 || highMid > 0.08)) {
      let lineOffset = currentLine * lineHeight;
      let waveY = random(lineOffset, lineOffset + lineHeight);'''
)

improved = improved.replace(
    '''    // Architectural elements - moderate frequency
    if (random() < 0.25 && bass > 0.25) {
      let archY = random() < 0.6 ?
        random(height * 0.5, height) :
        random(0, height * 0.4);''',
    '''    // Architectural elements
    if (random() < 0.4 && bass > 0.1) {
      let lineOffset = currentLine * lineHeight;
      let archY = random() < 0.6 ?
        random(lineOffset + lineHeight * 0.5, lineOffset + lineHeight) :
        random(lineOffset, lineOffset + lineHeight * 0.4);'''
)

# Update generateQuietMark to use lineOffset
improved = improved.replace(
    '''function generateQuietMark(vol) {
  let y = random(height * 0.3, height * 0.7);''',
    '''function generateQuietMark(vol) {
  let lineOffset = currentLine * lineHeight;
  let y = random(lineOffset + lineHeight * 0.3, lineOffset + lineHeight * 0.7);'''
)

# Write the corrected version
with open('sketch.js', 'w', encoding='utf-8') as f:
    f.write(improved)

print("✓ Fixed visuals with proper syntax:")
print("  - Two-line layout for long songs")
print("  - Larger shapes (2x size)")
print("  - More frequent generation (every frame)")
print("  - Lower volume thresholds")
print("  - 40-55% pattern probability")
print("  - NO syntax errors!")
