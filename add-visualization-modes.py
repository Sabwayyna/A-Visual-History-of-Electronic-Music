"""
Add multiple visualization flow modes:
- Mode 1: Horizontal left-to-right with two-line layout
- Mode 2: Radial center-outward expansion
"""

with open('sketch.js', 'r', encoding='utf-8') as f:
    original = f.read()

improved = original

# Add visualization mode variables after other global variables
improved = improved.replace(
    '''let currentLine = 0; // Current line (0 = top, 1 = bottom)
let lineHeight = 0; // Height of each line''',
    '''let currentLine = 0; // Current line (0 = top, 1 = bottom)
let lineHeight = 0; // Height of each line

// Visualization mode system
let visualMode = 'horizontal'; // 'horizontal' or 'radial'
let currentAngle = 0; // For radial mode
let currentRadius = 0; // For radial mode
let centerX = 0; // Center point for radial mode
let centerY = 0; // Center point for radial mode'''
)

# Initialize center points in setup
improved = improved.replace(
    '''  // Calculate line height for two-line layout
  lineHeight = height / 2;
}''',
    '''  // Calculate line height for two-line layout
  lineHeight = height / 2;

  // Initialize center point for radial mode
  centerX = width / 2;
  centerY = height / 2;
}'''
)

# Replace the currentX calculation with mode-aware positioning
improved = improved.replace(
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
  }''',
    '''  // Calculate position based on current visualization mode
  let totalProgress = 0;
  if (song.duration() > 0) {
    totalProgress = song.currentTime() / song.duration();
  } else {
    // Fallback: increment based on frame count
    totalProgress = frameCounter / 6000; // Assume ~100 seconds at 60fps
    if (totalProgress > 1) totalProgress = 1;
  }

  if (visualMode === 'horizontal') {
    // HORIZONTAL MODE: Two-line left-to-right layout
    if (totalProgress <= 0.5) {
      currentLine = 0;
      currentX = map(totalProgress, 0, 0.5, 0, width);
    } else {
      currentLine = 1;
      currentX = map(totalProgress, 0.5, 1.0, 0, width);
    }
  } else if (visualMode === 'radial') {
    // RADIAL MODE: Center-outward expansion in spiral
    // Map progress to angle (0-360 degrees, multiple rotations)
    let rotations = 8; // Number of full rotations throughout the song
    currentAngle = totalProgress * 360 * rotations;

    // Map progress to radius (0 to max radius)
    let maxRadius = min(width, height) * 0.45; // Stay within bounds
    currentRadius = totalProgress * maxRadius;

    // Calculate X, Y from polar coordinates
    currentX = centerX + cos(currentAngle) * currentRadius;
    currentLine = 0; // Not used in radial mode
  }'''
)

# Update generateShapes to handle both modes
improved = improved.replace(
    '''function generateShapes(vol, subBass, bass, lowMid, mid, highMid, treble, isBeat, isLoud, isVeryLoud, isQuiet, volChange) {
  // Calculate Y offset based on current line
  let lineOffset = currentLine * lineHeight;

  // Map 6 frequency bands to vertical positions within current line
  let subBassY = map(subBass, 0, 1, lineOffset + lineHeight * 0.83, lineOffset + lineHeight);
  let bassY = map(bass, 0, 1, lineOffset + lineHeight * 0.67, lineOffset + lineHeight * 0.83);
  let lowMidY = map(lowMid, 0, 1, lineOffset + lineHeight * 0.5, lineOffset + lineHeight * 0.67);
  let midY = map(mid, 0, 1, lineOffset + lineHeight * 0.33, lineOffset + lineHeight * 0.5);
  let highMidY = map(highMid, 0, 1, lineOffset + lineHeight * 0.17, lineOffset + lineHeight * 0.33);
  let trebleY = map(treble, 0, 1, lineOffset, lineOffset + lineHeight * 0.17);''',
    '''function generateShapes(vol, subBass, bass, lowMid, mid, highMid, treble, isBeat, isLoud, isVeryLoud, isQuiet, volChange) {
  // Calculate positions based on visualization mode
  let subBassY, bassY, lowMidY, midY, highMidY, trebleY;

  if (visualMode === 'horizontal') {
    // HORIZONTAL MODE: Use line offset for two-line layout
    let lineOffset = currentLine * lineHeight;
    subBassY = map(subBass, 0, 1, lineOffset + lineHeight * 0.83, lineOffset + lineHeight);
    bassY = map(bass, 0, 1, lineOffset + lineHeight * 0.67, lineOffset + lineHeight * 0.83);
    lowMidY = map(lowMid, 0, 1, lineOffset + lineHeight * 0.5, lineOffset + lineHeight * 0.67);
    midY = map(mid, 0, 1, lineOffset + lineHeight * 0.33, lineOffset + lineHeight * 0.5);
    highMidY = map(highMid, 0, 1, lineOffset + lineHeight * 0.17, lineOffset + lineHeight * 0.33);
    trebleY = map(treble, 0, 1, lineOffset, lineOffset + lineHeight * 0.17);
  } else if (visualMode === 'radial') {
    // RADIAL MODE: Calculate Y from polar coordinates with radius variations
    // Each frequency band gets a different radius offset from current position
    let angleRad = radians(currentAngle);
    subBassY = centerY + sin(angleRad) * (currentRadius + map(subBass, 0, 1, 0, 40));
    bassY = centerY + sin(angleRad) * (currentRadius + map(bass, 0, 1, -10, 30));
    lowMidY = centerY + sin(angleRad) * (currentRadius + map(lowMid, 0, 1, -20, 20));
    midY = centerY + sin(angleRad) * (currentRadius + map(mid, 0, 1, -30, 10));
    highMidY = centerY + sin(angleRad) * (currentRadius + map(highMid, 0, 1, -40, 0));
    trebleY = centerY + sin(angleRad) * (currentRadius + map(treble, 0, 1, -50, -10));
  }'''
)

# Update pattern generation to work with both modes
improved = improved.replace(
    '''    // Organic blob clusters - more frequent
    if (random() < 0.45 && vol > 0.08) {
      let lineOffset = currentLine * lineHeight;
      let blobY = random() < 0.6 ?
        random(lineOffset + lineHeight * 0.3, lineOffset + lineHeight) :
        random(lineOffset, lineOffset + lineHeight * 0.5);
      addOrganicBlob(currentX + random(-30, 30), blobY, map(vol, 0, 1, 30, 80), vol); // Larger
    }''',
    '''    // Organic blob clusters - more frequent
    if (random() < 0.45 && vol > 0.08) {
      let blobX, blobY;
      if (visualMode === 'horizontal') {
        let lineOffset = currentLine * lineHeight;
        blobX = currentX + random(-30, 30);
        blobY = random() < 0.6 ?
          random(lineOffset + lineHeight * 0.3, lineOffset + lineHeight) :
          random(lineOffset, lineOffset + lineHeight * 0.5);
      } else {
        // Radial mode: position around current angle
        let angleOffset = random(-30, 30);
        let radiusOffset = random(-20, 20);
        let a = radians(currentAngle + angleOffset);
        blobX = centerX + cos(a) * (currentRadius + radiusOffset);
        blobY = centerY + sin(a) * (currentRadius + radiusOffset);
      }
      addOrganicBlob(blobX, blobY, map(vol, 0, 1, 30, 80), vol);
    }'''
)

# Similar updates for other pattern types
improved = improved.replace(
    '''    // Scattered fields - more frequent
    if (random() < 0.55 && vol > 0.06) {
      let lineOffset = currentLine * lineHeight;
      let fieldY = random(lineOffset, lineOffset + lineHeight);
      let fieldWidth = random(50, 120);
      let fieldHeight = random(40, 100);
      addScatteredField(currentX, fieldY, fieldWidth, fieldHeight, map(vol, 0, 1, 0.4, 1.2), vol);
    }''',
    '''    // Scattered fields - more frequent
    if (random() < 0.55 && vol > 0.06) {
      let fieldX, fieldY;
      if (visualMode === 'horizontal') {
        let lineOffset = currentLine * lineHeight;
        fieldX = currentX;
        fieldY = random(lineOffset, lineOffset + lineHeight);
      } else {
        let a = radians(currentAngle);
        fieldX = centerX + cos(a) * currentRadius;
        fieldY = centerY + sin(a) * currentRadius;
      }
      let fieldWidth = random(50, 120);
      let fieldHeight = random(40, 100);
      addScatteredField(fieldX, fieldY, fieldWidth, fieldHeight, map(vol, 0, 1, 0.4, 1.2), vol);
    }'''
)

# Add keyboard shortcut to toggle mode
improved = improved.replace(
    '''function keyPressed() {
  if (key === ' ') {''',
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

function keyPressed() {
  if (key === ' ') {'''
)

# Add M key for mode switching
improved = improved.replace(
    '''  } else if (key === 'h' || key === 'H') {
    showUI = !showUI;
  }
}''',
    '''  } else if (key === 'h' || key === 'H') {
    showUI = !showUI;
  } else if (key === 'm' || key === 'M') {
    toggleVisualizationMode();
  }
}''')

# Write the improved version
with open('sketch.js', 'w', encoding='utf-8') as f:
    f.write(improved)

print("✓ Added visualization mode system:")
print("  - HORIZONTAL mode: Left-to-right with two-line layout (default)")
print("  - RADIAL mode: Center-outward spiral expansion")
print("  - Press 'M' key to toggle between modes")
print("  - Both modes work with all audio features")
print("  - Radial mode uses spiral pattern (8 rotations)")
