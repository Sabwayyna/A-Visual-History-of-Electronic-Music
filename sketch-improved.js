let song, fft, amp;
let started = false;
let shapes = []; // Array to store all permanent shapes
let waveform;
let time = 0;
let frameCounter = 0;
let currentX = 0; // Current horizontal position (left to right progression)
let lastVol = 0;
let volHistory = []; // Track volume over time
let lastX = 0; // Track last X position to create breaks
let quietStreak = 0; // Track consecutive quiet frames
let currentLine = 0; // Current line (0 = top, 1 = bottom)
let lineHeight = 0; // Height of each line

// Simplified - grayscale only
let showUI = true;

// Playback speed control
let playbackSpeed = 1.0; // 1.0 = normal speed

// Section tracking for annotations
let sectionCounter = 0;
let lastSectionX = 0;
let sectionMinDistance = 200; // Minimum pixels between sections

function setup() {
  createCanvas(windowWidth, windowHeight);
  angleMode(DEGREES);
  fft = new p5.FFT(0.8, 1024);
  amp = new p5.Amplitude(0.8);
  
  // File input handler
  let fileInput = select('#fileInput');
  if (fileInput) {
    fileInput.changed(handleFile);
  }
  
  // Start with black background
  background(0);

  // Calculate line height for two-line layout
  lineHeight = height / 2;
}

function handleFile() {
  let fileInput = select('#fileInput');
  if (!fileInput) return;
  
  let file = fileInput.elt.files[0];
  if (file) {
    if (song && song.isPlaying()) {
      song.stop();
    }
    started = false;
    shapes = [];
    currentX = 0;
    lastX = 0;
    volHistory = [];
    lastVol = 0;
    quietStreak = 0;
    sectionCounter = 0;
    lastSectionX = 0;
    background(0);
    
    // Use FileReader to create object URL for p5.sound
    let reader = new FileReader();
    reader.onload = function(e) {
      let fileURL = e.target.result;
      song = loadSound(fileURL, () => {
        console.log("File loaded successfully");
        // Auto-start playback
        userStartAudio();
        song.play();
        song.rate(playbackSpeed);
        started = true;
        currentX = 0;
        lastX = 0;
        frameCounter = 0;
        background(0);
        console.log('Auto-started playback');
      }, (error) => {
        console.error("Error loading file:", error);
      });
    };
    reader.readAsDataURL(file);
  }
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}

function draw() {
  // Keep black background - no clearing after start
  if (frameCount === 1 || !started) {
  background(0);
  }

  // Only show text before starting - and only if no song is loaded
  if (!started) {
    // HTML music selector handles UI, no canvas text needed
    return;
  }

  // Once started, no text should ever appear - just visuals
  if (!song || !song.isPlaying()) {
    if (started && frameCounter < 10) {
      console.log('Waiting for playback...', {
        hasSong: !!song,
        isPlaying: song ? song.isPlaying() : false,
        frameCounter: frameCounter
      });
    }
    return;
  }

  frameCounter++;
  
  // Calculate current X position based on song progress (left to right with two-line support)
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
  }

  let spectrum = fft.analyze();
  let vol = amp.getLevel();

  waveform = fft.waveform();
  
  // Extract 6 frequency bands from spectrum for more layers
  let spectrumLength = spectrum.length;
  
  // Calculate energy in different frequency ranges from spectrum array
  // Spectrum is typically 1024 bins, each representing a frequency range
  let subBassStart = floor(spectrumLength * 0.0);
  let subBassEnd = floor(spectrumLength * 0.05);
  let bassStart = floor(spectrumLength * 0.05);
  let bassEnd = floor(spectrumLength * 0.15);
  let lowMidStart = floor(spectrumLength * 0.15);
  let lowMidEnd = floor(spectrumLength * 0.3);
  let midStart = floor(spectrumLength * 0.3);
  let midEnd = floor(spectrumLength * 0.5);
  let highMidStart = floor(spectrumLength * 0.5);
  let highMidEnd = floor(spectrumLength * 0.75);
  let trebleStart = floor(spectrumLength * 0.75);
  let trebleEnd = spectrumLength;
  
  // Calculate average energy for each band
  let subBass = 0;
  let subBassCount = subBassEnd - subBassStart;
  if (subBassCount > 0) {
    for (let i = subBassStart; i < subBassEnd; i++) {
      subBass += spectrum[i];
    }
    subBass = subBass / subBassCount;
  }
  
  let bass = 0;
  let bassCount = bassEnd - bassStart;
  if (bassCount > 0) {
    for (let i = bassStart; i < bassEnd; i++) {
      bass += spectrum[i];
    }
    bass = bass / bassCount;
  }
  
  let lowMid = 0;
  let lowMidCount = lowMidEnd - lowMidStart;
  if (lowMidCount > 0) {
    for (let i = lowMidStart; i < lowMidEnd; i++) {
      lowMid += spectrum[i];
    }
    lowMid = lowMid / lowMidCount;
  }
  
  let mid = 0;
  let midCount = midEnd - midStart;
  if (midCount > 0) {
    for (let i = midStart; i < midEnd; i++) {
      mid += spectrum[i];
    }
    mid = mid / midCount;
  }
  
  let highMid = 0;
  let highMidCount = highMidEnd - highMidStart;
  if (highMidCount > 0) {
    for (let i = highMidStart; i < highMidEnd; i++) {
      highMid += spectrum[i];
    }
    highMid = highMid / highMidCount;
  }
  
  let treble = 0;
  let trebleCount = trebleEnd - trebleStart;
  if (trebleCount > 0) {
    for (let i = trebleStart; i < trebleEnd; i++) {
      treble += spectrum[i];
    }
    treble = treble / trebleCount;
  }
  
  // Track volume history
  volHistory.push(vol);
  if (volHistory.length > 20) {
    volHistory.shift();
  }
  
  // IMPROVED beat detection - more sensitive and accurate
  let volChange = vol - lastVol;
  let avgVol = volHistory.length > 0 ? volHistory.reduce((a, b) => a + b, 0) / volHistory.length : vol;

  // Better beat detection using multiple criteria - MORE SENSITIVE
  let isBeat = (volChange > 0.03 && vol > avgVol * 1.08) || // Sharp increase (lowered from 0.08)
               (vol > 0.4 && volChange > 0.02) || // Loud with any increase (lowered from 0.6)
               (vol > 0.15 && volChange > 0.05); // Medium volume with sharp change

  let isLoud = vol > 0.15; // Lowered from 0.25
  let isVeryLoud = vol > 0.35; // Lowered from 0.5
  let isQuiet = vol < 0.05; // Lowered from 0.08
  
  // Track quiet streaks for breaks
  if (isQuiet) {
    quietStreak++;
  } else {
    quietStreak = 0;
  }
  
  // Normalize frequency values (0-255 to 0-1)
  let subBassNorm = map(subBass, 0, 255, 0, 1);
  let bassNorm = map(bass, 0, 255, 0, 1);
  let lowMidNorm = map(lowMid, 0, 255, 0, 1);
  let midNorm = map(mid, 0, 255, 0, 1);
  let highMidNorm = map(highMid, 0, 255, 0, 1);
  let trebleNorm = map(treble, 0, 255, 0, 1);
  
  // Generate shapes with balanced frequency - MORE SENSITIVE FOR QUIET SOUNDS
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

  if (shouldGenerate && vol > 0.005) { // Lowered from 0.01
    // Generate shapes based on audio with 6 frequency bands
    generateShapes(vol, subBassNorm, bassNorm, lowMidNorm, midNorm, highMidNorm, trebleNorm, isBeat, isLoud, isVeryLoud, isQuiet, volChange);
    lastX = currentX;
  } else if (isQuiet && quietStreak > 30) {
    // Sparse marks during extended quiet sections
    if (random() < 0.1) { // Balanced - some marks in quiet areas
      generateQuietMark(vol);
    }
  }
  
  // Always draw all accumulated shapes
  drawShapes();

  lastVol = vol;
  time += 0.1;
}

// Simplified - grayscale only
function getShapeColor(vol, frequencyType, isVeryLoud, isLoud, isQuiet, frequencyValue = 0) {
  return getGrayscaleColor(vol, frequencyType, isVeryLoud, isLoud, isQuiet);
}

// Helper function to calculate grayscale color based on audio properties
function getGrayscaleColor(vol, frequencyType, isVeryLoud, isLoud, isQuiet) {
  let baseGray;

  // Base gray value based on volume
  if (isVeryLoud) {
    baseGray = map(vol, 0.5, 1, 220, 255); // Bright white for very loud
  } else if (isLoud) {
    baseGray = map(vol, 0.3, 0.5, 180, 220); // Light gray for loud
  } else if (isQuiet) {
    baseGray = map(vol, 0, 0.1, 40, 100); // Dark gray for quiet
  } else {
    baseGray = map(vol, 0.1, 0.3, 100, 180); // Medium gray for normal
  }

  // Adjust based on frequency type
  if (frequencyType === 'bass') {
    baseGray -= 15; // Slightly darker for bass
  } else if (frequencyType === 'treble') {
    baseGray += 10; // Slightly brighter for treble
  }
  // Mid frequencies stay at base gray

  // Constrain to valid grayscale range
  return constrain(baseGray, 30, 255);
}


function generateShapes(vol, subBass, bass, lowMid, mid, highMid, treble, isBeat, isLoud, isVeryLoud, isQuiet, volChange) {
  // Calculate Y offset based on current line
  let lineOffset = currentLine * lineHeight;

  // Map 6 frequency bands to vertical positions within the current line (from bottom to top)
  let subBassY = map(subBass, 0, 1, lineOffset + lineHeight * 0.83, lineOffset + lineHeight);        // Bottom layer
  let bassY = map(bass, 0, 1, lineOffset + lineHeight * 0.67, lineOffset + lineHeight * 0.83);     // Second from bottom
  let lowMidY = map(lowMid, 0, 1, lineOffset + lineHeight * 0.5, lineOffset + lineHeight * 0.67);  // Lower middle
  let midY = map(mid, 0, 1, lineOffset + lineHeight * 0.33, lineOffset + lineHeight * 0.5);         // Middle
  let highMidY = map(highMid, 0, 1, lineOffset + lineHeight * 0.17, lineOffset + lineHeight * 0.33); // Upper middle
  let trebleY = map(treble, 0, 1, lineOffset, lineOffset + lineHeight * 0.17);               // Top layer

  // SECTION DETECTION - Add structured dividers and annotations on major changes
  if ((currentX - lastSectionX) > sectionMinDistance && isBeat && isVeryLoud) {
    addSectionDivider(currentX, sectionCounter, vol);
    lastSectionX = currentX;
    sectionCounter++;
  }

  // INTRICATE PATTERNS - Add varied textural elements with better balance
  if (vol > 0.05) {
    // Organic blob clusters - MORE FREQUENT and SENSITIVE
    if (random() < 0.35 && vol > 0.08) { // Increased from 0.25, lowered vol from 0.2
      let lineOffset = currentLine * lineHeight;
      let blobY = random() < 0.6 ?
        random(lineOffset + lineHeight * 0.3, lineOffset + lineHeight) :
        random(lineOffset, lineOffset + lineHeight * 0.5);
      addOrganicBlob(currentX + random(-30, 30), blobY, map(vol, 0, 1, 10, 50), vol); // Lowered min size from 15
    }

    // Scattered fields of tiny elements - MORE FREQUENT and SENSITIVE
    if (random() < 0.45 && vol > 0.05) { // Increased from 0.35, lowered vol from 0.15
      let lineOffset = currentLine * lineHeight;
      let fieldY = random(lineOffset, lineOffset + lineHeight);
      let fieldWidth = random(50, 120);
      let fieldHeight = random(40, 100);
      addScatteredField(currentX, fieldY, fieldWidth, fieldHeight, map(vol, 0, 1, 0.3, 1.2), vol); // Lowered min from 0.4
    }

    // Cross-hatching patterns - MORE SENSITIVE
    if (random() < 0.3 && (isLoud || mid > 0.15)) { // Increased from 0.25, lowered mid from 0.3
      let lineOffset = currentLine * lineHeight;
      let hatchY = random() < 0.5 ?
        random(lineOffset + lineHeight * 0.4, lineOffset + lineHeight) :
        random(lineOffset, lineOffset + lineHeight * 0.6);
      addCrossHatch(currentX, hatchY, map(vol, 0, 1, 15, 60), map(vol, 0, 1, 20, 80), map(vol, 0, 1, 3, 12), vol); // Lowered mins
    }

    // Wave patterns - MORE FREQUENT and SENSITIVE
    if (random() < 0.4 && (treble > 0.1 || highMid > 0.1)) { // Increased from 0.3, lowered thresholds from 0.2
      let lineOffset = currentLine * lineHeight;
      let waveY = random(lineOffset, lineOffset + lineHeight);
      addWavePattern(currentX + random(-20, 20), waveY, map(treble, 0, 1, 25, 100), map(treble, 0, 1, 3, 18), vol); // Lowered mins
    }

    // Architectural elements - MORE SENSITIVE
    if (random() < 0.3 && bass > 0.12) { // Increased from 0.25, lowered bass from 0.25
      let lineOffset = currentLine * lineHeight;
      let archY = random() < 0.6 ?
        random(lineOffset + lineHeight * 0.5, lineOffset + lineHeight) :
        random(0, height * 0.7);
      addArchitecturalElement(currentX + random(-25, 25), archY, map(bass, 0, 1, 35, 100), vol);
    }

    // Dense grid patterns - moderate frequency
    if (random() < 0.25 && mid > 0.25) {
      let gridY = random() < 0.5 ?
        random(height * 0.3, height) :
        random(0, height * 0.6);
      addDenseGrid(currentX, gridY, map(mid, 0, 1, 25, 70), map(mid, 0, 1, 25, 70), map(mid, 0, 1, 5, 12), vol);
    }
  }

  // Add textural noise - more frequently for density
  if (vol > 0.08 && random() < 0.5) {
    addTexturalNoise(vol, currentX);
  }
  
  // VERY LOUD / BEAT DROPS - VARIED PILLARS with HORIZONTAL VARIANCE
  if ((isVeryLoud || (isBeat && isLoud)) && random() < 0.8) {
    // Create 2-4 varied pillar structures
    let numPillars = floor(random(2, 5));

    for (let p = 0; p < numPillars; p++) {
      // HORIZONTAL VARIANCE - each pillar at different X position
      let pillarOffsetX = random(-40, 40);
      let pillarX = currentX + pillarOffsetX;

      // VARIED WIDTHS for each pillar
      let pillarWidth = random(15, 50);
      let pillarHeight = map(vol, 0.55, 1, height * 0.2, height * 0.6);
      let pillarY = height - pillarHeight;

      // Choose pillar type based on frequency
      let pillarType = random();

      if (pillarType < 0.3 && bass > 0.3) {
        // SOLID BLOCK PILLAR (bass-aligned)
        let blockWidth = pillarWidth;
        let blockHeight = map(bass, 0, 1, height * 0.15, height * 0.5);

        // Create fragmented elements with Y-variation
        let numFragments = floor(random(12, 30)); // Balanced density

        for (let f = 0; f < numFragments; f++) {
          // Random Y position across entire canvas, with bias toward bottom
          let yBias = random();
          let fragmentY = yBias < 0.6 ?
            random(height * 0.5, height) : // 60% chance lower half
            random(0, height);              // 40% chance anywhere

          let fragmentX = pillarX + random(-blockWidth/2, blockWidth/2);
          let fragmentType = floor(random(6));

          if (fragmentType === 0) {
            // Dense horizontal stripes
            shapes.push({
              type: 'horizontalLine',
              x: fragmentX - random(10, 25),
              y: fragmentY,
              length: random(15, 40),
              weight: random(0.5, 2),
              color: map(bass, 0, 1, 120, 255)
            });
          } else if (fragmentType === 1) {
            // Small filled rectangles
            shapes.push({
              type: 'rectangle',
              x: fragmentX,
              y: fragmentY,
              w: random(8, 25),
              h: random(5, 20),
              weight: random(0.8, 2),
              color: map(bass, 0, 1, 100, 240)
            });
          } else if (fragmentType === 2) {
            // Circles - mix of filled and outline
            shapes.push({
              type: 'circle',
              x: fragmentX,
              y: fragmentY,
              size: random(4, 15),
              filled: random() < 0.3,
              weight: random(0.4, 1.2),
              color: map(bass, 0, 1, 150, 255)
            });
          } else if (fragmentType === 3) {
            // Vertical line fragments
            shapes.push({
              type: 'verticalLine',
              x: fragmentX,
              y: fragmentY,
              length: random(10, 40),
              weight: random(0.5, 2),
              color: map(bass, 0, 1, 100, 230)
            });
          } else if (fragmentType === 4) {
            // Cross marks
            shapes.push({
              type: 'cross',
              x: fragmentX,
              y: fragmentY,
              size: random(5, 12),
              weight: random(0.4, 1),
              color: map(bass, 0, 1, 140, 255)
            });
          } else {
            // Small squares (no X inside)
            shapes.push({
              type: 'square',
              x: fragmentX,
              y: fragmentY,
              size: random(5, 15),
              filled: random() < 0.25,
              weight: random(0.5, 1.5),
              color: map(bass, 0, 1, 130, 250)
            });
          }
        }

      } else if (pillarType < 0.6 && mid > 0.3) {
        // FRAGMENTED LINE CLUSTER - scattered across Y-axis
        let numFragments = floor(random(8, 20)); // Balanced

        for (let i = 0; i < numFragments; i++) {
          // Random Y positioning across canvas
          let fragmentY = random() < 0.6 ?
            random(height * 0.3, height) :  // 60% middle-to-bottom
            random(0, height * 0.5);        // 40% top-to-middle

          let fragmentX = pillarX + random(-pillarWidth, pillarWidth);
          let fragmentChoice = random();

          if (fragmentChoice < 0.4) {
            // Vertical line fragments of varied lengths
            shapes.push({
              type: 'verticalLine',
              x: fragmentX + random(-3, 3),
              y: fragmentY,
              length: random(10, 50),
              weight: random(0.4, 2),
              color: map(mid, 0, 1, 120, 240)
            });
          } else if (fragmentChoice < 0.7) {
            // Horizontal connecting bars scattered around
            shapes.push({
              type: 'horizontalLine',
              x: fragmentX - random(10, 25),
              y: fragmentY,
              length: random(20, 50),
              weight: random(0.3, 1.2),
              color: map(mid, 0, 1, 100, 230)
            });
          } else {
            // Small rectangles at various angles
            shapes.push({
              type: 'rectangle',
              x: fragmentX,
              y: fragmentY,
              w: random(8, 30),
              h: random(5, 20),
              weight: random(0.5, 1.5),
              color: map(mid, 0, 1, 110, 235)
            });
          }
        }

        // Add scattered marks and dots throughout
        let numMarks = floor(random(10, 20));
        for (let c = 0; c < numMarks; c++) {
          let markY = random() < 0.5 ?
            random(height * 0.4, height) :
            random(0, height);

          if (random() < 0.6) {
            shapes.push({
              type: 'cross',
              x: pillarX + random(-pillarWidth * 1.5, pillarWidth * 1.5),
              y: markY,
              size: random(3, 10),
              weight: random(0.3, 0.8),
              color: map(mid, 0, 1, 140, 255)
            });
          } else {
            shapes.push({
              type: 'circle',
              x: pillarX + random(-pillarWidth, pillarWidth),
              y: markY,
              size: random(2, 8),
              filled: random() < 0.4,
              weight: random(0.3, 0.7),
              color: map(mid, 0, 1, 150, 255)
            });
          }
        }

      } else if (treble > 0.2) {
        // SCATTERED TEXTURE ELEMENTS (treble-aligned) - fragmented across Y
        let numElements = floor(random(12, 35)); // Balanced

        for (let e = 0; e < numElements; e++) {
          // Scatter elements across Y-axis with bias toward middle/upper
          let elementY = random() < 0.5 ?
            random(0, height * 0.6) :     // 50% upper-to-middle
            random(height * 0.4, height); // 50% middle-to-bottom

          let elementX = pillarX + random(-pillarWidth * 1.2, pillarWidth * 1.2);
          let elementType = floor(random(7));

          if (elementType === 0) {
            // Small circles scattered
            shapes.push({
              type: 'circle',
              x: elementX,
              y: elementY,
              size: random(2, 10),
              filled: random() < 0.35,
              weight: random(0.3, 0.8),
              color: map(treble, 0, 1, 140, 255)
            });
          } else if (elementType === 1) {
            // Cross marks
            shapes.push({
              type: 'cross',
              x: elementX,
              y: elementY,
              size: random(3, 10),
              weight: random(0.3, 0.7),
              color: map(treble, 0, 1, 150, 255)
            });
          } else if (elementType === 2) {
            // Tiny rectangles
            shapes.push({
              type: 'rectangle',
              x: elementX,
              y: elementY,
              w: random(4, 15),
              h: random(3, 10),
              weight: random(0.3, 0.9),
              color: map(treble, 0, 1, 130, 245)
            });
          } else if (elementType === 3) {
            // Small squares
            shapes.push({
              type: 'square',
              x: elementX,
              y: elementY,
              size: random(3, 12),
              filled: random() < 0.3,
              weight: random(0.3, 0.8),
              color: map(treble, 0, 1, 140, 250)
            });
          } else if (elementType === 4) {
            // Horizontal dashes
            shapes.push({
              type: 'horizontalLine',
              x: elementX - random(5, 12),
              y: elementY,
              length: random(10, 25),
              weight: random(0.3, 0.9),
              color: map(treble, 0, 1, 150, 255)
            });
          } else if (elementType === 5) {
            // Vertical dashes
            shapes.push({
              type: 'verticalLine',
              x: elementX,
              y: elementY,
              length: random(8, 25),
              weight: random(0.3, 0.9),
              color: map(treble, 0, 1, 140, 250)
            });
          } else {
            // Diagonal marks
            shapes.push({
              type: 'diagonalLine',
              x: elementX,
              y: elementY,
              length: random(6, 20),
              angle: random() < 0.5 ? 45 : -45,
              weight: random(0.3, 0.7),
              color: map(treble, 0, 1, 145, 255)
            });
          }
        }
      }

      // Add scattered overlapping textures across canvas
      if (random() < 0.6) {
        // Position textures randomly across Y-axis
        let overlayY = random() < 0.5 ?
          random(height * 0.5, height) :  // 50% lower half
          random(0, height * 0.6);        // 50% upper-middle

        let overlayX = pillarX + random(-40, 40);
        let overlayWidth = random(30, 80);

        // Add wave pattern overlay
        if (random() < 0.5) {
          addWavePattern(overlayX, overlayY, overlayWidth, random(5, 20), vol);
        } else {
          // Add varied stripe patterns at different orientations
          let numStripes = floor(random(5, 15));
          let stripeOrientation = random();

          for (let s = 0; s < numStripes; s++) {
            if (random() < 0.7) {
              if (stripeOrientation < 0.6) {
                // Horizontal stripes
                shapes.push({
                  type: 'horizontalLine',
                  x: overlayX - overlayWidth/2,
                  y: overlayY + s * random(2, 5),
                  length: random(overlayWidth * 0.5, overlayWidth),
                  weight: random(0.3, 1),
                  color: map(vol, 0, 1, 120, 250)
                });
              } else {
                // Vertical stripes
                shapes.push({
                  type: 'verticalLine',
                  x: overlayX - overlayWidth/2 + s * random(3, 6),
                  y: overlayY,
                  length: random(15, 40),
                  weight: random(0.3, 0.8),
                  color: map(vol, 0, 1, 130, 245)
                });
              }
            }
          }
        }
      }
    }

    // Add scattered fragmented elements across canvas
    if (random() < 0.5) { // Balanced
      let numSymbols = floor(random(6, 18)); // Balanced
      for (let s = 0; s < numSymbols; s++) {
        let symbolX = currentX + random(-60, 60);
        // Scatter across entire Y-axis with some clustering
        let symbolY = random() < 0.5 ?
          random(height * 0.4, height) : // 50% lower portion
          random(0, height * 0.7);        // 50% upper-middle portion
        let symbolType = floor(random(8));

        if (symbolType === 0) {
          // Small circles with varied fills
          shapes.push({
            type: 'circle',
            x: symbolX,
            y: symbolY,
            size: random(2, 10),
            filled: random() < 0.4,
            weight: random(0.3, 0.8),
            color: map(vol, 0, 1, 120, 255)
          });
        } else if (symbolType === 1) {
          // Crosses of various sizes
          shapes.push({
            type: 'cross',
            x: symbolX,
            y: symbolY,
            size: random(3, 12),
            weight: random(0.3, 0.9),
            color: map(vol, 0, 1, 140, 255)
          });
        } else if (symbolType === 2) {
          // Small squares
          shapes.push({
            type: 'square',
            x: symbolX,
            y: symbolY,
            size: random(3, 10),
            filled: random() < 0.35,
            weight: random(0.3, 0.9),
            color: map(vol, 0, 1, 130, 250)
          });
        } else if (symbolType === 3) {
          // Short horizontal lines
          shapes.push({
            type: 'horizontalLine',
            x: symbolX - random(5, 15),
            y: symbolY,
            length: random(10, 30),
            weight: random(0.4, 1.2),
            color: map(vol, 0, 1, 110, 240)
          });
        } else if (symbolType === 4) {
          // Short vertical lines
          shapes.push({
            type: 'verticalLine',
            x: symbolX,
            y: symbolY,
            length: random(8, 30),
            weight: random(0.4, 1.2),
            color: map(vol, 0, 1, 120, 235)
          });
        } else if (symbolType === 5) {
          // Diagonal marks
          shapes.push({
            type: 'diagonalLine',
            x: symbolX,
            y: symbolY,
            length: random(8, 25),
            angle: random() < 0.5 ? 45 : -45,
            weight: random(0.3, 0.8),
            color: map(vol, 0, 1, 130, 245)
          });
        } else if (symbolType === 6) {
          // Small rectangles with varied orientations
          shapes.push({
            type: 'rectangle',
            x: symbolX,
            y: symbolY,
            w: random(5, 20),
            h: random(3, 12),
            weight: random(0.4, 1),
            color: map(vol, 0, 1, 110, 230)
          });
        } else {
          // Tiny dots/particles
          shapes.push({
            type: 'circle',
            x: symbolX,
            y: symbolY,
            size: random(1, 4),
            filled: true,
            weight: 0.3,
            color: map(vol, 0, 1, 150, 255)
          });
        }
      }
    }
  }

  // LOUD SECTIONS - Reduced density with glitch
  else if (isLoud) {
    // Create vertical structure with fewer lines
    let structureWidth = map(vol, 0.35, 0.55, 8, 25);
    let numLines = floor(map(vol, 0.35, 0.55, 2, 6)); // Much fewer
    let lineSpacing = structureWidth / numLines;

    for (let i = 0; i < numLines; i++) {
      if (random() < 0.6) { // Skip some lines
        let lineX = currentX - structureWidth/2 + i * lineSpacing;
        let lineHeight = map(vol, 0.35, 0.55, height * 0.15, height * 0.5);
        let lineY = height - lineHeight;

        shapes.push({
          type: 'verticalLine',
          x: lineX + random(-1, 1), // Slight glitch displacement
          y: lineY,
          length: lineHeight,
          weight: map(vol, 0.35, 0.55, 0.4, 1),
          color: getShapeColor(vol, 'mid', isVeryLoud, isLoud, isQuiet, mid)
        });
      }
    }

    // Add some rectangles for bass - less often
    if (bass > 0.3 && random() < 0.4) {
      shapes.push({
        type: 'rectangle',
        x: currentX,
        y: bassY,
        w: map(bass, 0, 1, 6, 20),
        h: map(bass, 0, 1, 10, 50),
        weight: map(bass, 0, 1, 0.5, 1.2),
        color: getShapeColor(vol, 'bass', isVeryLoud, isLoud, isQuiet, bass)
      });
    }
  }
  
  // NORMAL SECTIONS - Sparse, distinct patterns
  else {
    // Frequency-based shapes - selective generation for distinct marks

    // Only generate main shape sometimes
    if (vol > 0.02 && random() < 0.5) {
      shapes.push({
        type: 'verticalLine',
        x: currentX,
        y: height - map(vol, 0, 1, 10, 80),
        length: map(vol, 0, 1, 10, 80),
        weight: map(vol, 0, 1, 0.3, 0.8),
        color: getShapeColor(vol, 'mid', isVeryLoud, isLoud, isQuiet, mid)
      });
    }

    if (vol > 0.02) {
      // SUB-BASS - Very bottom layer: large rectangles (reduced)
      if (subBass > 0.1) {
        if (random() < 0.25) { // Lower probability
          shapes.push({
            type: 'rectangle',
            x: currentX,
            y: subBassY,
            w: map(subBass, 0, 1, 8, 30),
            h: map(subBass, 0, 1, 12, 50),
            weight: map(subBass, 0, 1, 0.5, 1.5),
            color: getShapeColor(vol, 'bass', isVeryLoud, isLoud, isQuiet, bass)
          });
        }
      }
      
      // BASS - Second from bottom: rectangles and vertical lines (reduced)
      if (bass > 0.1) {
        if (random() < 0.3) { // Much lower probability
          let lineHeight = map(bass, 0, 1, 15, 60);
          shapes.push({
            type: 'verticalLine',
            x: currentX,
            y: height - lineHeight,
            length: lineHeight,
            weight: map(bass, 0, 1, 0.4, 1),
            color: getShapeColor(vol, 'bass', isVeryLoud, isLoud, isQuiet, bass)
          });
        } else if (random() < 0.3) {
          shapes.push({
            type: 'rectangle',
            x: currentX,
            y: bassY,
            w: map(bass, 0, 1, 5, 20),
            h: map(bass, 0, 1, 10, 40),
            weight: map(bass, 0, 1, 0.4, 0.9),
            color: getShapeColor(vol, 'bass', isVeryLoud, isLoud, isQuiet, bass)
          });
        }
      }

      // LOW-MID - Lower middle: horizontal lines and small rectangles (reduced)
      if (lowMid > 0.1) {
        if (random() < 0.3) {
          shapes.push({
            type: 'horizontalLine',
            x: currentX - 15,
            y: lowMidY,
            length: 30,
            weight: map(lowMid, 0, 1, 0.3, 0.9),
            color: getShapeColor(vol, 'mid', isVeryLoud, isLoud, isQuiet, mid)
          });
        } else {
          shapes.push({
            type: 'rectangle',
            x: currentX,
            y: lowMidY,
            w: map(lowMid, 0, 1, 5, 18),
            h: map(lowMid, 0, 1, 6, 30),
            weight: map(lowMid, 0, 1, 0.3, 0.8),
            color: getShapeColor(vol, 'mid', isVeryLoud, isLoud, isQuiet, mid)
          });
        }
      }
      
      // MID - Middle: horizontal bands, grids, circles (reduced)
      if (mid > 0.1) {
        let choice = random();
        if (choice < 0.2 && random() < 0.4) { // Lower overall probability
          shapes.push({
            type: 'horizontalLine',
            x: currentX - 20,
            y: midY,
            length: 40,
            weight: map(mid, 0, 1, 0.3, 1),
            color: getShapeColor(vol, 'mid', isVeryLoud, isLoud, isQuiet, mid)
          });
        } else if (choice < 0.45) {
          // Small grid of squares and circles
          let gridSize = floor(map(mid, 0, 1, 2, 5));
          let squareSize = map(mid, 0, 1, 3, 8);
          for (let i = 0; i < gridSize; i++) {
            for (let j = 0; j < gridSize; j++) {
              if (random() < 0.7) {
                let shapeChoice = random();
                if (shapeChoice < 0.4) {
                  shapes.push({
                    type: 'square',
                    x: currentX - (gridSize * squareSize)/2 + i * squareSize,
                    y: midY - (gridSize * squareSize)/2 + j * squareSize,
                    size: squareSize * 0.8,
                    filled: random() < 0.3,
                    weight: map(mid, 0, 1, 0.3, 0.7),
                    color: getShapeColor(vol, 'mid', isVeryLoud, isLoud, isQuiet, mid)
                  });
                } else {
                  shapes.push({
                    type: 'circle',
                    x: currentX - (gridSize * squareSize)/2 + i * squareSize,
                    y: midY - (gridSize * squareSize)/2 + j * squareSize,
                    size: squareSize * 0.7,
                    filled: random() < 0.2,
                    weight: map(mid, 0, 1, 0.3, 0.7),
                    color: getShapeColor(vol, 'mid', isVeryLoud, isLoud, isQuiet, mid)
                  });
                }
              }
            }
          }
        } else if (choice < 0.7) {
          // Circles
          shapes.push({
            type: 'circle',
            x: currentX,
            y: midY,
            size: map(mid, 0, 1, 8, 25),
            filled: false,
            weight: map(mid, 0, 1, 0.3, 0.9),
            color: getShapeColor(vol, 'mid', isVeryLoud, isLoud, isQuiet, mid)
          });
        } else {
          shapes.push({
            type: 'rectangle',
            x: currentX,
            y: midY,
            w: map(mid, 0, 1, 6, 20),
            h: map(mid, 0, 1, 8, 35),
            weight: map(mid, 0, 1, 0.3, 0.9),
            color: getShapeColor(vol, 'mid', isVeryLoud, isLoud, isQuiet, mid)
          });
        }
      }
      
      // HIGH-MID - Upper middle: small squares, circles, lines, crosses
      if (highMid > 0.05 || vol > 0.05) {
        let choice = random();
        if (choice < 0.3) {
          shapes.push({
            type: 'square',
            x: currentX,
            y: highMidY,
            size: map(highMid, 0, 1, 3, 10),
            filled: random() < 0.2,
            weight: map(highMid, 0, 1, 0.3, 0.7),
            color: getShapeColor(vol, 'treble', isVeryLoud, isLoud, isQuiet, treble)
          });
        } else if (choice < 0.5) {
          shapes.push({
            type: 'circle',
            x: currentX,
            y: highMidY,
            size: map(highMid, 0, 1, 4, 12),
            filled: false,
            weight: map(highMid, 0, 1, 0.2, 0.6),
            color: getShapeColor(vol, 'treble', isVeryLoud, isLoud, isQuiet, treble)
          });
        } else if (choice < 0.7) {
          shapes.push({
            type: 'cross',
            x: currentX,
            y: highMidY,
            size: map(highMid, 0, 1, 3, 8),
            weight: map(highMid, 0, 1, 0.2, 0.5),
            color: getShapeColor(vol, 'treble', isVeryLoud, isLoud, isQuiet, treble)
          });
        } else {
          shapes.push({
            type: 'horizontalLine',
            x: currentX - 12,
            y: highMidY,
            length: 24,
            weight: map(highMid, 0, 1, 0.2, 0.6),
            color: getShapeColor(vol, 'treble', isVeryLoud, isLoud, isQuiet, treble)
          });
        }
      }

      // TREBLE - Top layer: dots, small circles, crosses, thin lines
      if (treble > 0.05 || vol > 0.05) {
        let choice = random();
        if (choice < 0.35) {
          // Small dots
          shapes.push({
            type: 'circle',
            x: currentX + random(-2, 2),
            y: trebleY,
            size: map(treble, 0, 1, 1, 4),
            filled: true,
            weight: map(treble, 0, 1, 0.2, 0.5),
            color: getShapeColor(vol, 'treble', isVeryLoud, isLoud, isQuiet, treble)
          });
        } else if (choice < 0.6) {
          shapes.push({
            type: 'cross',
            x: currentX,
            y: trebleY,
            size: map(treble, 0, 1, 2, 6),
            weight: map(treble, 0, 1, 0.2, 0.4),
            color: getShapeColor(vol, 'treble', isVeryLoud, isLoud, isQuiet, treble)
          });
        } else if (choice < 0.8) {
          shapes.push({
            type: 'square',
            x: currentX,
            y: trebleY,
            size: map(treble, 0, 1, 2, 8),
            filled: random() < 0.3,
            weight: map(treble, 0, 1, 0.2, 0.5),
            color: getShapeColor(vol, 'treble', isVeryLoud, isLoud, isQuiet, treble)
          });
        } else {
          shapes.push({
            type: 'horizontalLine',
            x: currentX - 8,
            y: trebleY,
            length: 16,
            weight: map(treble, 0, 1, 0.2, 0.5),
            color: getShapeColor(vol, 'treble', isVeryLoud, isLoud, isQuiet, treble)
          });
        }
      }
    }
  }

  // LARGE THIN CIRCLE OVERLAYS - MUCH LARGER like in revised version
  if (isBeat && vol > 0.5 && random() < 0.35) {
    // HUGE compositional circles - 60-80% of screen height
    let circleSize = random(height * 0.5, height * 0.85);
    let circleY = random() < 0.5 ?
      random(height * 0.2, height * 0.5) :
      random(height * 0.5, height * 0.8);

    shapes.push({
      type: 'largeCircle',
      x: currentX + random(-80, 80),
      y: circleY,
      size: circleSize,
      weight: random(0.8, 2),
      color: map(vol, 0, 1, 180, 255),
      blendMode: 'difference'
    });

    // Frequently add overlapping circles for depth
    if (random() < 0.6) {
      shapes.push({
        type: 'largeCircle',
        x: currentX + random(-100, 100),
        y: circleY + random(-120, 120),
        size: circleSize * random(0.5, 1.2),
        weight: random(0.6, 1.8),
        color: map(vol, 0, 1, 150, 230),
        blendMode: 'exclusion'
      });
    }
  }

  // Medium-large circles more frequently
  if (isLoud && random() < 0.25) {
    let circleSize = random(height * 0.3, height * 0.6);
    let circleY = random(height * 0.15, height * 0.85);

    shapes.push({
      type: 'largeCircle',
      x: currentX + random(-60, 60),
      y: circleY,
      size: circleSize,
      weight: random(0.5, 1.5),
      color: map(mid, 0, 1, 140, 220),
      blendMode: random() < 0.5 ? 'difference' : 'exclusion'
    });

    // Add curved arcs near circles more often
    if (random() < 0.5) {
      let arcRadius = circleSize * random(0.6, 1.3);
      let startAng = random(360);
      let endAng = startAng + random(90, 270);
      addCurvedArc(currentX + random(-80, 80), circleY + random(-80, 80), arcRadius, startAng, endAng, vol);
    }
  }

  // Standalone curved arcs more frequently
  if (vol > 0.25 && random() < 0.15) {
    let arcY = random(height * 0.1, height * 0.9);
    let arcRadius = random(height * 0.1, height * 0.4);
    let startAng = random(360);
    let endAng = startAng + random(60, 200);
    addCurvedArc(currentX + random(-60, 60), arcY, arcRadius, startAng, endAng, vol);
  }

  // BRIGHT WHITE VERTICAL FOCAL BARS - MUCH THICKER like in revised version
  if (isVeryLoud && random() < 0.3) {
    let barHeight = random(height * 0.4, height * 0.9);
    let barY = random(0, height * 0.3);
    let numBars = floor(random(1, 3));

    for (let b = 0; b < numBars; b++) {
      let barX = currentX + random(-40, 40);
      let barWidth = random(25, 60); // MUCH thicker - was 8-25

      // Main bright thick bar
      shapes.push({
        type: 'focalBar',
        x: barX,
        y: barY,
        width: barWidth,
        height: barHeight,
        color: 255,
        blendMode: 'normal'
      });

      // Add gradient-like effect with overlapping bars
      if (random() < 0.7) {
        shapes.push({
          type: 'focalBar',
          x: barX + random(-15, 15),
          y: barY + random(-30, 30),
          width: barWidth * random(0.6, 1.3),
          height: barHeight * random(0.8, 1.1),
          color: map(vol, 0, 1, 140, 220),
          blendMode: 'difference'
        });
      }
    }
  }

  // MEDIUM WHITE BARS at loud sections - more frequent
  if (isLoud && random() < 0.25) {
    let barHeight = random(height * 0.3, height * 0.7);
    let barY = random(0, height * 0.5);
    let barWidth = random(20, 50);

    shapes.push({
      type: 'focalBar',
      x: currentX + random(-30, 30),
      y: barY,
      width: barWidth,
      height: barHeight,
      color: map(vol, 0, 1, 200, 255),
      blendMode: 'normal'
    });
  }

  // GRADIENT-LIKE SOFT BARS - Create depth with blend modes
  if (vol > 0.35 && random() < 0.15) {
    let softBarHeight = random(height * 0.25, height * 0.6);
    let softBarY = random(0, height - softBarHeight);

    // Create overlapping bars with blend modes for gradient effect
    for (let layer = 0; layer < 3; layer++) {
      shapes.push({
        type: 'focalBar',
        x: currentX + random(-20, 20),
        y: softBarY + layer * 15,
        width: random(20, 50), // Thicker
        height: softBarHeight - layer * 30,
        color: map(vol, 0, 1, 120 + layer * 30, 220 + layer * 15),
        blendMode: layer === 0 ? 'normal' : 'exclusion'
      });
    }
  }

  // BEAT DETECTION - Add DISTINCTIVE vertical marker
  if (isBeat && vol > 0.25 && random() < 0.7) { // More frequent beats
    // Main beat line - broken/glitched
    let numSegments = floor(random(2, 5)); // Balanced
    let segmentHeight = height / numSegments;

    for (let i = 0; i < numSegments; i++) {
      if (random() < 0.6) { // More segments missing for glitch
        shapes.push({
          type: 'verticalLine',
          x: currentX + random(-1, 1), // Slight displacement
          y: i * segmentHeight,
          length: segmentHeight * random(0.6, 0.9),
          weight: map(vol, 0, 1, 0.6, 2),
          color: map(vol, 0, 1, 180, 255)
        });
      }
    }

    // Add distinctive crosses at beat points
    if (random() < 0.7) {
      let numCrosses = floor(random(3, 6));
      for (let i = 0; i < numCrosses; i++) {
        shapes.push({
          type: 'cross',
          x: currentX + random(-15, 15),
          y: random(height),
          size: random(4, 14),
          weight: random(0.5, 1.2),
          color: map(vol, 0, 1, 180, 255)
        });
      }
    }

    // Occasional spiral pattern on strong beats
    if (vol > 0.7 && random() < 0.3) {
      addSpiralPattern(currentX, random(height * 0.3, height * 0.7), random(15, 35), floor(random(3, 6)), vol);
    }

    // Add architectural bracket on very strong beats
    if (vol > 0.8 && random() < 0.25) {
      addArchitecturalElement(currentX, random(height * 0.4, height * 0.6), random(40, 80), vol);
    }
  }
}

function generateQuietMark(vol) {
  // Very sparse marks during quiet sections - very dark gray
  let quietColor = map(vol, 0, 0.08, 30, 60); // Very dark gray for quiet
  if (random() < 0.3) {
    shapes.push({
      type: 'horizontalLine',
      x: currentX,
      y: random(height),
      length: map(vol, 0, 0.08, 2, 8),
      weight: 0.2,
      color: quietColor
    });
  } else if (random() < 0.5) {
    shapes.push({
      type: 'square',
      x: currentX,
      y: random(height),
      size: map(vol, 0, 0.08, 2, 6),
      weight: 0.2,
      color: quietColor
    });
  }
}

// ENHANCED: Add intricate textural noise with varied complex symbols
function addTexturalNoise(vol, x) {
  // More varied density based on volume
  let numParticles = floor(map(vol, 0, 1, 3, 12));

  for (let i = 0; i < numParticles; i++) {
    let y = random(height);
    let markType = random();
    // Vary size more dramatically
    let sizeVariation = map(vol, 0, 1, 0.5, 1.5);

    if (markType < 0.25) {
      // Small dots/circles - more variety in size and fill
      shapes.push({
        type: 'circle',
        x: x + random(-12, 12),
        y: y,
        size: random(0.5, 4) * sizeVariation,
        filled: random() < 0.4,
        weight: random(0.2, 0.5),
        color: getShapeColor(vol, 'mid', false, false, false, 0.5)
      });
    } else if (markType < 0.45) {
      // Tiny crosses with more size variation
      shapes.push({
        type: 'cross',
        x: x + random(-10, 10),
        y: y,
        size: random(1, 6) * sizeVariation,
        weight: random(0.2, 0.5),
        color: getShapeColor(vol, 'mid', false, false, false, 0.5)
      });
    } else if (markType < 0.6) {
      // Horizontal dashes - more length variation
      shapes.push({
        type: 'horizontalLine',
        x: x + random(-10, 10),
        y: y,
        length: random(2, 12) * sizeVariation,
        weight: random(0.2, 0.6),
        color: getShapeColor(vol, 'mid', false, false, false, 0.5)
      });
    } else if (markType < 0.75) {
      // Vertical dashes
      shapes.push({
        type: 'verticalLine',
        x: x + random(-10, 10),
        y: y,
        length: random(2, 10) * sizeVariation,
        weight: random(0.2, 0.6),
        color: getShapeColor(vol, 'mid', false, false, false, 0.5)
      });
    } else if (markType < 0.85) {
      // Diagonal marks - more variety
      shapes.push({
        type: 'diagonalLine',
        x: x + random(-10, 10),
        y: y,
        length: random(3, 12) * sizeVariation,
        angle: random([45, -45, 30, -30, 60, -60]),
        weight: random(0.2, 0.5),
        color: getShapeColor(vol, 'mid', false, false, false, 0.5)
      });
    } else if (markType < 0.92) {
      // Tiny filled rectangles with more variation
      shapes.push({
        type: 'rectangle',
        x: x + random(-10, 10),
        y: y,
        w: random(2, 8) * sizeVariation,
        h: random(1, 5) * sizeVariation,
        weight: random(0.2, 0.6),
        color: getShapeColor(vol, 'mid', false, false, false, 0.5)
      });
    } else {
      // Small squares (without X) - reduced from squareWithX
      shapes.push({
        type: 'square',
        x: x + random(-10, 10),
        y: y,
        size: random(2, 6) * sizeVariation,
        filled: random() < 0.4,
        weight: random(0.2, 0.5),
        color: getShapeColor(vol, 'mid', false, false, false, 0.5)
      });
    }
  }

  // Add occasional cluster patterns
  if (random() < 0.3) {
    addSymbolCluster(x, random(height), vol);
  }
}

// NEW: Add clusters of symbols for dense texture
function addSymbolCluster(x, y, vol) {
  let clusterSize = floor(random(3, 7));
  let clusterSpread = random(10, 20);
  let symbolType = floor(random(3));
  let baseColor = getShapeColor(vol, 'mid', false, false, false, 0.5);

  for (let i = 0; i < clusterSize; i++) {
    let offsetX = random(-clusterSpread, clusterSpread);
    let offsetY = random(-clusterSpread, clusterSpread);

    if (symbolType === 0) {
      // Circle cluster
      shapes.push({
        type: 'circle',
        x: x + offsetX,
        y: y + offsetY,
        size: random(1, 3),
        filled: random() < 0.4,
        weight: 0.3,
        color: baseColor
      });
    } else if (symbolType === 1) {
      // Cross cluster
      shapes.push({
        type: 'cross',
        x: x + offsetX,
        y: y + offsetY,
        size: random(2, 5),
        weight: 0.3,
        color: baseColor
      });
    } else {
      // Square cluster
      shapes.push({
        type: 'square',
        x: x + offsetX,
        y: y + offsetY,
        size: random(2, 4),
        filled: random() < 0.3,
        weight: 0.3,
        color: baseColor
      });
    }
  }
}

// NEW: Spiral/radial pattern for complex moments
function addSpiralPattern(x, y, radius, numArms, vol) {
  let baseColor = getShapeColor(vol, 'mid', false, false, false, 0.5);
  let numPoints = floor(numArms * 8);

  for (let i = 0; i < numPoints; i++) {
    let angle = (i / numPoints) * 360 * 2; // Two full rotations
    let r = (i / numPoints) * radius;
    let px = x + cos(angle) * r;
    let py = y + sin(angle) * r;

    if (i % 3 === 0) {
      shapes.push({
        type: 'circle',
        x: px,
        y: py,
        size: random(1, 3),
        filled: random() < 0.4,
        weight: 0.3,
        color: baseColor
      });
    }

    // Connect with lines occasionally
    if (i > 0 && i % 4 === 0) {
      let prevAngle = ((i - 4) / numPoints) * 360 * 2;
      let prevR = ((i - 4) / numPoints) * radius;
      let prevX = x + cos(prevAngle) * prevR;
      let prevY = y + sin(prevAngle) * prevR;

      shapes.push({
        type: 'customLine',
        x1: prevX,
        y1: prevY,
        x2: px,
        y2: py,
        weight: 0.3,
        color: baseColor
      });
    }
  }

  // Add center mark
  shapes.push({
    type: 'cross',
    x: x,
    y: y,
    size: 6,
    weight: 0.5,
    color: baseColor
  });
}

// NEW: Section divider with annotations
function addSectionDivider(x, sectionNum, vol) {
  let baseColor = 200;

  // Strong vertical divider line
  shapes.push({
    type: 'verticalLine',
    x: x,
    y: 0,
    length: height,
    weight: 2,
    color: baseColor
  });

  // Add tick marks along divider
  let numTicks = floor(height / 20);
  for (let i = 0; i < numTicks; i++) {
    if (i % 2 === 0) {
      shapes.push({
        type: 'horizontalLine',
        x: x - 8,
        y: i * 20,
        length: 16,
        weight: 0.6,
        color: baseColor
      });
    }
  }

  // Add section label/annotation
  let labelY = height * 0.1;

  // Section number box
  shapes.push({
    type: 'rectangle',
    x: x,
    y: labelY,
    w: 30,
    h: 20,
    weight: 1,
    color: baseColor
  });

  // Add "PART" text annotation above
  shapes.push({
    type: 'text',
    x: x,
    y: labelY - 15,
    text: 'PART',
    size: 8,
    color: baseColor
  });

  // Add section number
  shapes.push({
    type: 'text',
    x: x,
    y: labelY,
    text: sectionNum.toString(),
    size: 10,
    color: baseColor
  });

  // Add decorative brackets around the section marker
  shapes.push({
    type: 'horizontalLine',
    x: x - 20,
    y: labelY - 25,
    length: 40,
    weight: 0.8,
    color: baseColor
  });

  shapes.push({
    type: 'horizontalLine',
    x: x - 20,
    y: labelY + 15,
    length: 40,
    weight: 0.8,
    color: baseColor
  });
}

// INTRICATE: Dense cross-hatch pattern with multiple angles
function addCrossHatch(x, y, width, height, density, vol) {
  let numLines = floor(density);
  let spacing = height / numLines;
  let baseColor = getShapeColor(vol, 'mid', false, false, false, 0.5);

  for (let i = 0; i < numLines; i++) {
    let yPos = y + i * spacing;

    // Primary diagonal lines (45 degrees)
    if (random() < 0.8) {
      shapes.push({
        type: 'diagonalLine',
        x: x - width/2,
        y: yPos,
        length: width,
        angle: 45,
        weight: random(0.3, 0.6),
        color: baseColor
      });
    }

    // Counter diagonal lines (-45 degrees) - denser
    if (random() < 0.7) {
      shapes.push({
        type: 'diagonalLine',
        x: x - width/2,
        y: yPos,
        length: width,
        angle: -45,
        weight: random(0.3, 0.6),
        color: baseColor
      });
    }

    // Add horizontal accent lines
    if (i % 3 === 0 && random() < 0.5) {
      shapes.push({
        type: 'horizontalLine',
        x: x - width/2,
        y: yPos,
        length: width,
        weight: random(0.4, 0.8),
        color: baseColor
      });
    }

    // Add small perpendicular marks for density
    if (random() < 0.4) {
      shapes.push({
        type: 'verticalLine',
        x: x + random(-width/2, width/2),
        y: yPos,
        length: spacing * random(0.5, 1.5),
        weight: 0.3,
        color: baseColor
      });
    }
  }
}

// NEW: Wave/oscillation pattern generator
function addWavePattern(x, y, length, amplitude, vol) {
  let numPoints = floor(length / 3);
  let baseColor = getShapeColor(vol, 'treble', false, false, false, 0.5);

  // Create smooth wave using connected line segments
  for (let i = 0; i < numPoints - 1; i++) {
    let x1 = x - length/2 + (i / numPoints) * length;
    let x2 = x - length/2 + ((i + 1) / numPoints) * length;
    let y1 = y + sin(i * 20 + time) * amplitude;
    let y2 = y + sin((i + 1) * 20 + time) * amplitude;

    shapes.push({
      type: 'customLine',
      x1: x1,
      y1: y1,
      x2: x2,
      y2: y2,
      weight: random(0.4, 0.8),
      color: baseColor
    });

    // Add perpendicular tick marks along wave
    if (i % 2 === 0 && random() < 0.6) {
      shapes.push({
        type: 'verticalLine',
        x: x1,
        y: y1 - amplitude * 0.5,
        length: amplitude,
        weight: 0.3,
        color: baseColor
      });
    }
  }

  // Add parallel wave lines for density
  if (random() < 0.7) {
    let offset = amplitude * 1.5;
    for (let i = 0; i < numPoints - 1; i++) {
      let x1 = x - length/2 + (i / numPoints) * length;
      let x2 = x - length/2 + ((i + 1) / numPoints) * length;
      let y1 = y + offset + sin(i * 20 + time) * amplitude * 0.7;
      let y2 = y + offset + sin((i + 1) * 20 + time) * amplitude * 0.7;

      shapes.push({
        type: 'customLine',
        x1: x1,
        y1: y1,
        x2: x2,
        y2: y2,
        weight: random(0.3, 0.6),
        color: baseColor
      });
    }
  }
}

// NEW: Architectural elements (brackets, dividers, structural marks)
function addArchitecturalElement(x, y, size, vol) {
  let baseColor = getShapeColor(vol, 'bass', false, false, false, 0.5);
  let elementType = floor(random(4));

  if (elementType === 0) {
    // Bracket structure
    let bracketWidth = size * 0.3;
    let bracketHeight = size;

    // Left vertical
    shapes.push({
      type: 'verticalLine',
      x: x - bracketWidth/2,
      y: y - bracketHeight/2,
      length: bracketHeight,
      weight: 0.8,
      color: baseColor
    });

    // Right vertical
    shapes.push({
      type: 'verticalLine',
      x: x + bracketWidth/2,
      y: y - bracketHeight/2,
      length: bracketHeight,
      weight: 0.8,
      color: baseColor
    });

    // Top horizontal
    shapes.push({
      type: 'horizontalLine',
      x: x - bracketWidth/2,
      y: y - bracketHeight/2,
      length: bracketWidth,
      weight: 0.8,
      color: baseColor
    });

    // Bottom horizontal
    shapes.push({
      type: 'horizontalLine',
      x: x - bracketWidth/2,
      y: y + bracketHeight/2,
      length: bracketWidth,
      weight: 0.8,
      color: baseColor
    });

    // Add internal structural marks
    for (let i = 0; i < 3; i++) {
      shapes.push({
        type: 'horizontalLine',
        x: x - bracketWidth/2,
        y: y - bracketHeight/2 + (i + 1) * (bracketHeight / 4),
        length: bracketWidth,
        weight: 0.3,
        color: baseColor
      });
    }
  } else if (elementType === 1) {
    // Stacked rectangles (like a tower)
    let numRects = floor(random(3, 6));
    let rectHeight = size / numRects;
    let rectWidth = size * 0.4;

    for (let i = 0; i < numRects; i++) {
      if (random() < 0.8) {
        shapes.push({
          type: 'rectangle',
          x: x,
          y: y - size/2 + i * rectHeight + rectHeight/2,
          w: rectWidth * random(0.7, 1),
          h: rectHeight * 0.8,
          weight: 0.6,
          color: baseColor
        });

        // Add internal pattern
        if (random() < 0.5) {
          let numDots = floor(random(2, 5));
          for (let j = 0; j < numDots; j++) {
            shapes.push({
              type: 'circle',
              x: x - rectWidth/4 + (j / numDots) * rectWidth/2,
              y: y - size/2 + i * rectHeight + rectHeight/2,
              size: 2,
              filled: true,
              weight: 0.3,
              color: baseColor
            });
          }
        }
      }
    }
  } else if (elementType === 2) {
    // Divider with tick marks
    shapes.push({
      type: 'verticalLine',
      x: x,
      y: y - size/2,
      length: size,
      weight: 1.2,
      color: baseColor
    });

    // Add perpendicular ticks
    let numTicks = floor(size / 8);
    for (let i = 0; i < numTicks; i++) {
      shapes.push({
        type: 'horizontalLine',
        x: x - 6,
        y: y - size/2 + i * (size / numTicks),
        length: 12,
        weight: 0.4,
        color: baseColor
      });
    }
  } else {
    // Dense vertical bar with texture
    let barWidth = size * 0.25;
    let barHeight = size;

    // Outline
    shapes.push({
      type: 'rectangle',
      x: x,
      y: y,
      w: barWidth,
      h: barHeight,
      weight: 0.8,
      color: baseColor
    });

    // Fill with dense horizontal lines
    let numLines = floor(barHeight / 3);
    for (let i = 0; i < numLines; i++) {
      if (random() < 0.7) {
        shapes.push({
          type: 'horizontalLine',
          x: x - barWidth/2,
          y: y - barHeight/2 + i * (barHeight / numLines),
          length: barWidth,
          weight: 0.3,
          color: baseColor
        });
      }
    }
  }
}

// NEW: Dense grid with intricate internal patterns
function addDenseGrid(x, y, gridWidth, gridHeight, cellSize, vol) {
  let cols = floor(gridWidth / cellSize);
  let rows = floor(gridHeight / cellSize);
  let baseColor = getShapeColor(vol, 'mid', false, false, false, 0.5);

  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      if (random() < 0.85) { // Most cells filled for density
        let cellX = x - gridWidth/2 + i * cellSize + cellSize/2;
        let cellY = y - gridHeight/2 + j * cellSize + cellSize/2;

        let patternType = random();
        if (patternType < 0.2) {
          // Filled square
          shapes.push({
            type: 'square',
            x: cellX,
            y: cellY,
            size: cellSize * 0.9,
            filled: true,
            weight: 0.4,
            color: baseColor
          });
        } else if (patternType < 0.35) {
          // Circle outline
          shapes.push({
            type: 'circle',
            x: cellX,
            y: cellY,
            size: cellSize * 0.8,
            filled: false,
            weight: 0.4,
            color: baseColor
          });
        } else if (patternType < 0.5) {
          // Cross
          shapes.push({
            type: 'cross',
            x: cellX,
            y: cellY,
            size: cellSize * 0.8,
            weight: 0.4,
            color: baseColor
          });
        } else if (patternType < 0.65) {
          // Square with X inside
          shapes.push({
            type: 'squareWithX',
            x: cellX,
            y: cellY,
            size: cellSize * 0.8,
            weight: 0.4,
            color: baseColor
          });
        } else if (patternType < 0.8) {
          // Mini cross-hatch
          shapes.push({
            type: 'diagonalLine',
            x: cellX - cellSize/2,
            y: cellY - cellSize/2,
            length: cellSize,
            angle: 45,
            weight: 0.3,
            color: baseColor
          });
          shapes.push({
            type: 'diagonalLine',
            x: cellX - cellSize/2,
            y: cellY - cellSize/2,
            length: cellSize,
            angle: -45,
            weight: 0.3,
            color: baseColor
          });
        } else {
          // Multiple small dots
          let numDots = floor(random(2, 5));
          for (let k = 0; k < numDots; k++) {
            shapes.push({
              type: 'circle',
              x: cellX + random(-cellSize/3, cellSize/3),
              y: cellY + random(-cellSize/3, cellSize/3),
              size: random(1, 2),
              filled: true,
              weight: 0.3,
              color: baseColor
            });
          }
        }
      }
    }
  }

  // Add grid outline for structure
  shapes.push({
    type: 'rectangle',
    x: x,
    y: y,
    w: gridWidth,
    h: gridHeight,
    weight: 0.8,
    color: baseColor
  });
}

// NEW: Add organic irregular blob/cluster
function addOrganicBlob(x, y, size, vol) {
  let numPoints = floor(random(8, 20));
  let baseColor = getShapeColor(vol, 'mid', false, false, false, 0.5);

  // Create irregular shape with varied radii
  for (let i = 0; i < numPoints; i++) {
    let angle = (i / numPoints) * 360;
    let radius = size * random(0.4, 1.2); // Irregular radius
    let px = x + cos(angle) * radius;
    let py = y + sin(angle) * radius;

    // Draw various marks at each point
    let markType = floor(random(5));
    if (markType === 0) {
      shapes.push({
        type: 'circle',
        x: px,
        y: py,
        size: random(1, 4),
        filled: random() < 0.5,
        weight: random(0.2, 0.5),
        color: baseColor
      });
    } else if (markType === 1) {
      shapes.push({
        type: 'cross',
        x: px,
        y: py,
        size: random(2, 6),
        weight: random(0.2, 0.5),
        color: baseColor
      });
    } else if (markType === 2) {
      shapes.push({
        type: 'horizontalLine',
        x: px - random(3, 8),
        y: py,
        length: random(5, 15),
        weight: random(0.2, 0.5),
        color: baseColor
      });
    } else if (markType === 3) {
      shapes.push({
        type: 'verticalLine',
        x: px,
        y: py,
        length: random(4, 12),
        weight: random(0.2, 0.5),
        color: baseColor
      });
    } else {
      shapes.push({
        type: 'square',
        x: px,
        y: py,
        size: random(2, 5),
        filled: random() < 0.3,
        weight: random(0.2, 0.5),
        color: baseColor
      });
    }
  }

  // Add center density
  let centerDensity = floor(random(3, 8));
  for (let c = 0; c < centerDensity; c++) {
    shapes.push({
      type: 'circle',
      x: x + random(-size * 0.3, size * 0.3),
      y: y + random(-size * 0.3, size * 0.3),
      size: random(1, 3),
      filled: true,
      weight: 0.3,
      color: baseColor
    });
  }
}

// NEW: Add irregular scattered field of elements
function addScatteredField(x, y, width, height, density, vol) {
  let numElements = floor(density * 15);
  let baseColor = getShapeColor(vol, 'mid', false, false, false, 0.5);

  for (let e = 0; e < numElements; e++) {
    let ex = x + random(-width/2, width/2);
    let ey = y + random(-height/2, height/2);
    let elementType = floor(random(6));

    if (elementType === 0) {
      // Tiny dots
      shapes.push({
        type: 'circle',
        x: ex,
        y: ey,
        size: random(0.5, 2),
        filled: true,
        weight: 0.2,
        color: baseColor
      });
    } else if (elementType === 1) {
      // Small crosses
      shapes.push({
        type: 'cross',
        x: ex,
        y: ey,
        size: random(1, 4),
        weight: 0.3,
        color: baseColor
      });
    } else if (elementType === 2) {
      // Short dashes
      shapes.push({
        type: 'horizontalLine',
        x: ex - random(2, 5),
        y: ey,
        length: random(3, 10),
        weight: 0.3,
        color: baseColor
      });
    } else if (elementType === 3) {
      // Diagonal marks
      shapes.push({
        type: 'diagonalLine',
        x: ex,
        y: ey,
        length: random(2, 8),
        angle: random([-60, -45, -30, 30, 45, 60]),
        weight: 0.3,
        color: baseColor
      });
    } else if (elementType === 4) {
      // Tiny rectangles
      shapes.push({
        type: 'rectangle',
        x: ex,
        y: ey,
        w: random(2, 6),
        h: random(1, 4),
        weight: 0.3,
        color: baseColor
      });
    } else {
      // Small vertical marks
      shapes.push({
        type: 'verticalLine',
        x: ex,
        y: ey,
        length: random(2, 8),
        weight: 0.3,
        color: baseColor
      });
    }
  }
}

// NEW: Add curved arc elements for compositional interest
function addCurvedArc(x, y, radius, startAngle, endAngle, vol) {
  let baseColor = getShapeColor(vol, 'mid', false, false, false, 0.5);
  let numPoints = 20;

  // Draw arc using connected line segments
  for (let i = 0; i < numPoints - 1; i++) {
    let angle1 = map(i, 0, numPoints - 1, startAngle, endAngle);
    let angle2 = map(i + 1, 0, numPoints - 1, startAngle, endAngle);

    let x1 = x + cos(angle1) * radius;
    let y1 = y + sin(angle1) * radius;
    let x2 = x + cos(angle2) * radius;
    let y2 = y + sin(angle2) * radius;

    shapes.push({
      type: 'customLine',
      x1: x1,
      y1: y1,
      x2: x2,
      y2: y2,
      weight: random(0.4, 1.2),
      color: baseColor
    });
  }
}

// NEW: Add grid/lattice pattern
function addGridPattern(x, y, gridWidth, gridHeight, cellSize, vol) {
  let cols = floor(gridWidth / cellSize);
  let rows = floor(gridHeight / cellSize);

  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      if (random() < 0.6) { // Not all cells filled
        let cellX = x + i * cellSize;
        let cellY = y + j * cellSize;

        let patternType = random();
        if (patternType < 0.3) {
          // Small filled square
          shapes.push({
            type: 'square',
            x: cellX,
            y: cellY,
            size: cellSize * 0.8,
            filled: true,
            color: getShapeColor(vol, 'mid', false, false, false, 0.5)
          });
        } else if (patternType < 0.6) {
          // Circle
          shapes.push({
            type: 'circle',
            x: cellX,
            y: cellY,
            size: cellSize * 0.7,
            filled: false,
            color: getShapeColor(vol, 'mid', false, false, false, 0.5)
          });
        } else {
          // Cross
          shapes.push({
            type: 'cross',
            x: cellX,
            y: cellY,
            size: cellSize * 0.8,
            weight: 0.4,
            color: getShapeColor(vol, 'mid', false, false, false, 0.5)
          });
        }
      }
    }
  }
}

function drawShapes() {
  for (let shape of shapes) {
    if (!shape) continue; // Skip invalid shapes

    // Apply blend mode if specified
    if (shape.blendMode) {
      if (shape.blendMode === 'difference') {
        blendMode(DIFFERENCE);
      } else if (shape.blendMode === 'exclusion') {
        blendMode(EXCLUSION);
      } else if (shape.blendMode === 'multiply') {
        blendMode(MULTIPLY);
      } else if (shape.blendMode === 'screen') {
        blendMode(SCREEN);
      } else {
        blendMode(BLEND);
      }
    } else {
      blendMode(BLEND); // Default blend mode
    }

    // Handle both color objects and grayscale values
    if (shape.color !== undefined) {
      if (typeof shape.color === 'number') {
        stroke(shape.color);
        fill(shape.color);
      } else {
        stroke(shape.color);
        fill(shape.color);
      }
    } else {
      stroke(255);
      fill(255);
    }

    strokeWeight(shape.weight || 0.5);

    switch (shape.type) {
      case 'rectangle':
        noFill();
        if (shape.x !== undefined && shape.y !== undefined && shape.w && shape.h) {
          rect(shape.x - shape.w/2, shape.y - shape.h/2, shape.w, shape.h);
        }
        break;

      case 'square':
        if (shape.filled) {
          // Filled square
          if (shape.x !== undefined && shape.y !== undefined && shape.size) {
            rect(shape.x - shape.size/2, shape.y - shape.size/2, shape.size, shape.size);
          }
        } else {
          // Outlined square
          noFill();
          if (shape.x !== undefined && shape.y !== undefined && shape.size) {
            rect(shape.x - shape.size/2, shape.y - shape.size/2, shape.size, shape.size);
          }
        }
        break;

      case 'circle':
        if (shape.filled) {
          // Filled circle
          if (shape.x !== undefined && shape.y !== undefined && shape.size) {
            ellipse(shape.x, shape.y, shape.size, shape.size);
          }
        } else {
          // Outlined circle
          noFill();
          if (shape.x !== undefined && shape.y !== undefined && shape.size) {
            ellipse(shape.x, shape.y, shape.size, shape.size);
          }
        }
        break;

      case 'cross':
        noFill();
        if (shape.x !== undefined && shape.y !== undefined && shape.size) {
          let halfSize = shape.size / 2;
          // Horizontal line of cross
          line(shape.x - halfSize, shape.y, shape.x + halfSize, shape.y);
          // Vertical line of cross
          line(shape.x, shape.y - halfSize, shape.x, shape.y + halfSize);
        }
        break;

      case 'horizontalLine':
        noFill();
        if (shape.x !== undefined && shape.y !== undefined && shape.length) {
          line(shape.x, shape.y, shape.x + shape.length, shape.y);
        }
        break;

      case 'verticalLine':
        noFill();
        if (shape.x !== undefined && shape.y !== undefined && shape.length) {
          line(shape.x, shape.y, shape.x, shape.y + shape.length);
        }
        break;

      case 'diagonalLine':
        noFill();
        if (shape.x !== undefined && shape.y !== undefined && shape.length && shape.angle !== undefined) {
          let rad = radians(shape.angle);
          let endX = shape.x + shape.length * cos(rad);
          let endY = shape.y + shape.length * sin(rad);
          line(shape.x, shape.y, endX, endY);
        }
        break;

      case 'squareWithX':
        noFill();
        if (shape.x !== undefined && shape.y !== undefined && shape.size) {
          // Draw square
          rect(shape.x - shape.size/2, shape.y - shape.size/2, shape.size, shape.size);
          // Draw X inside
          line(shape.x - shape.size/2, shape.y - shape.size/2, shape.x + shape.size/2, shape.y + shape.size/2);
          line(shape.x + shape.size/2, shape.y - shape.size/2, shape.x - shape.size/2, shape.y + shape.size/2);
        }
        break;

      case 'customLine':
        noFill();
        if (shape.x1 !== undefined && shape.y1 !== undefined && shape.x2 !== undefined && shape.y2 !== undefined) {
          line(shape.x1, shape.y1, shape.x2, shape.y2);
        }
        break;

      case 'text':
        noStroke();
        if (shape.x !== undefined && shape.y !== undefined && shape.text && shape.size) {
          fill(shape.color || 255);
          textAlign(CENTER, CENTER);
          textSize(shape.size);
          text(shape.text, shape.x, shape.y);
        }
        break;

      case 'largeCircle':
        noFill();
        if (shape.x !== undefined && shape.y !== undefined && shape.size) {
          ellipse(shape.x, shape.y, shape.size, shape.size);
        }
        break;

      case 'focalBar':
        // Bright white vertical bar with gradient-like effect
        if (shape.x !== undefined && shape.y !== undefined && shape.width && shape.height) {
          // Draw filled white rectangle
          fill(shape.color || 255);
          noStroke();
          rect(shape.x - shape.width/2, shape.y, shape.width, shape.height);

          // Add outline for definition
          noFill();
          stroke(shape.color || 255);
          strokeWeight(shape.weight || 1);
          rect(shape.x - shape.width/2, shape.y, shape.width, shape.height);
        }
        break;
    }
  }

  // Reset blend mode after drawing all shapes
  blendMode(BLEND);
}

function mousePressed() {
  if (!started && song && song.isLoaded()) {
    console.log('Starting audio playback...');
    userStartAudio();

    // Try to play and log any errors
    try {
      song.play();
      console.log('Song playing:', song.isPlaying());
      started = true;
      currentX = 0;
      lastX = 0;
      frameCounter = 0;
      // Clear background to remove any text
      background(0);
    } catch (e) {
      console.error('Error playing song:', e);
    }
  } else {
    console.log('Cannot start:', {
      started: started,
      hasSong: !!song,
      isLoaded: song ? song.isLoaded() : false
    });
  }
}

// Simplified keyboard controls
function keyPressed() {
  // Toggle UI with 'h' key (hide/show)
  if (key === 'h' || key === 'H') {
    showUI = !showUI;
    // Toggle HTML elements visibility
    const controlsBtn = document.getElementById('controlsBtn');
    const controlsPanel = document.getElementById('controlsPanel');
    const musicSelector = document.getElementById('musicSelector');
    const saveConfirm = document.getElementById('saveConfirmation');

    if (showUI) {
      // Only show controls if music is loaded, otherwise show music selector
      if (started && song && song.isLoaded()) {
        controlsBtn.style.display = 'flex';
      } else {
        musicSelector.classList.remove('hidden');
      }
      // Reset panel to allow hover to work again
      controlsPanel.style.opacity = '';
      controlsPanel.style.pointerEvents = '';
    } else {
      controlsBtn.style.display = 'none';
      controlsPanel.style.opacity = '0';
      controlsPanel.style.pointerEvents = 'none';
      musicSelector.classList.add('hidden');
      saveConfirm.classList.remove('show');
    }
  }

  // Export current frame for book documentation
  if (key === 's' || key === 'S') {
    let timestamp = year() + '' + nf(month(), 2) + nf(day(), 2) + '_' + nf(hour(), 2) + nf(minute(), 2) + nf(second(), 2);
    let filename = 'music-viz_' + timestamp + '.png';
    saveCanvas(filename, 'png');
    console.log('Saved: ' + filename);
    showSaveConfirmation();
  }

  // Clear and restart
  if (key === 'c' || key === 'C') {
    shapes = [];
    currentX = 0;
    lastX = 0;
    frameCounter = 0;
    sectionCounter = 0;
    lastSectionX = 0;
    background(0);
    console.log('Cleared visualization');
  }

  // Restart song
  if (key === ' ') { // Spacebar
    if (song && song.isLoaded()) {
      if (song.isPlaying()) {
        song.pause();
        console.log('Paused');
      } else {
        song.play();
        console.log('Playing');
      }
    }
  }

  // Speed controls with arrow keys
  if (keyCode === RIGHT_ARROW) {
    // Speed up by 1x (max 10x)
    playbackSpeed = Math.min(playbackSpeed + 1.0, 10.0);
    if (song && song.isLoaded()) {
      song.rate(playbackSpeed);
    }
    showSpeedIndicator();
    console.log('Speed:', playbackSpeed.toFixed(1) + 'x');
  }

  if (keyCode === LEFT_ARROW) {
    // Slow down by 1x (min 1x)
    playbackSpeed = Math.max(playbackSpeed - 1.0, 1.0);
    if (song && song.isLoaded()) {
      song.rate(playbackSpeed);
    }
    showSpeedIndicator();
    console.log('Speed:', playbackSpeed.toFixed(1) + 'x');
  }
}

// Save confirmation using HTML overlay
function showSaveConfirmation() {
  const saveConfirm = document.getElementById('saveConfirmation');
  saveConfirm.classList.add('show');

  // Hide after 2 seconds
  setTimeout(() => {
    saveConfirm.classList.remove('show');
  }, 2000);
}

// Speed indicator using HTML overlay
function showSpeedIndicator() {
  const speedIndicator = document.getElementById('speedIndicator');
  speedIndicator.textContent = playbackSpeed.toFixed(1) + 'x';
  speedIndicator.classList.add('show');

  // Hide after 1.5 seconds
  setTimeout(() => {
    speedIndicator.classList.remove('show');
  }, 1500);
}
