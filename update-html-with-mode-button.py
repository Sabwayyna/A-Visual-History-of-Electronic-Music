"""
Update the HTML template generator to include mode toggle button
"""

import os
import json

# Load song mapping
with open('song-mapping.json', 'r', encoding='utf-8') as f:
    songs = json.load(f)

# Read the complete sketch.js
with open('sketch.js', 'r', encoding='utf-8') as f:
    sketch_js = f.read()

def generate_song_visualizer_html(song):
    """Generate HTML page with integrated visualizer and mode switching for a song"""

    # Create modified sketch that auto-loads the song
    modified_sketch = f"""
// Auto-load audio path
const AUTO_LOAD_AUDIO = '../{song['audio']}';

{sketch_js}
"""

    # Replace the handleFile function to support auto-loading
    modified_sketch = modified_sketch.replace(
        'function setup() {',
        '''function preload() {
  // Auto-load the song if AUTO_LOAD_AUDIO is defined
  if (typeof AUTO_LOAD_AUDIO !== 'undefined' && AUTO_LOAD_AUDIO) {
    song = loadSound(AUTO_LOAD_AUDIO,
      () => {
        console.log("Song loaded successfully");
      },
      (error) => {
        console.error("Error loading song:", error);
      }
    );
  }
}

function setup() {'''
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{song['track']} - {song['artist']} ({song['year']})</title>
    <link rel="stylesheet" href="https://use.typekit.net/hdx3amb.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.6.0/p5.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.6.0/addons/p5.sound.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #000000;
            font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'Arial', sans-serif;
            font-weight: 400;
            font-size: 14px;
        }}

        /* Hidden file input */
        #fileInput {{
            display: none;
        }}

        /* Controls button - minimalist top right */
        #controlsBtn {{
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            background: transparent;
            cursor: pointer;
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        #controlsBtn img {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
            height: 100%;
            object-fit: contain;
        }}

        #controlsBtn .soft-shape {{
            transition: opacity 0.3s ease;
            opacity: 1;
        }}

        #controlsBtn .spiky-shape {{
            transition: opacity 0.3s ease;
            opacity: 0;
        }}

        #controlsBtn:hover .soft-shape {{
            opacity: 0;
        }}

        #controlsBtn:hover .spiky-shape {{
            opacity: 1;
        }}

        /* Controls panel - minimalist style */
        #controlsPanel {{
            position: fixed;
            top: 80px;
            right: 20px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px 24px;
            color: #000000;
            font-size: 14px;
            z-index: 99;
            min-width: 180px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
            line-height: 2;
        }}

        #controlsBtn:hover + #controlsPanel,
        #controlsPanel:hover {{
            opacity: 1;
            pointer-events: auto;
        }}

        #controlsPanel .title {{
            font-weight: 700;
            margin-bottom: 16px;
            font-size: 14px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }}

        #controlsPanel .control-item {{
            margin: 4px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        #controlsPanel .key {{
            font-weight: 600;
            padding: 2px 6px;
            margin-right: 12px;
            font-size: 14px;
            letter-spacing: 0.5px;
        }}

        /* Mode indicator overlay */
        #modeIndicator {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #ffffff;
            border: 3px solid #000000;
            padding: 20px 40px;
            font-size: 14px;
            font-weight: 700;
            box-shadow: 6px 6px 0px #000000;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
            letter-spacing: 2px;
        }}

        #modeIndicator.show {{
            opacity: 1;
        }}

        /* Save confirmation overlay */
        #saveConfirmation {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #ffffff;
            border: 3px solid #000000;
            padding: 20px 40px;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 6px 6px 0px #000000;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        }}

        #saveConfirmation.show {{
            opacity: 1;
        }}

        /* Speed indicator overlay */
        #speedIndicator {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #ffffff;
            border: 3px solid #000000;
            padding: 20px 40px;
            font-size: 14px;
            font-weight: 700;
            box-shadow: 6px 6px 0px #000000;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
            letter-spacing: 2px;
        }}

        #speedIndicator.show {{
            opacity: 1;
        }}

        /* Back to timeline link */
        #backLink {{
            position: fixed;
            top: 24px;
            left: 24px;
            font-size: 11px;
            font-weight: 400;
            letter-spacing: 2px;
            color: rgba(255, 255, 255, 0.4);
            cursor: pointer;
            z-index: 100;
            transition: all 0.3s ease;
            text-transform: uppercase;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        #backLink:hover {{
            color: rgba(255, 255, 255, 1);
            letter-spacing: 3px;
            transform: translateX(-2px);
        }}

        #backLink::before {{
            content: "←";
            font-size: 14px;
            transition: transform 0.3s ease;
        }}

        #backLink:hover::before {{
            transform: translateX(-4px);
        }}

        /* Bottom-left navigation */
        .bottom-nav {{
            position: fixed;
            bottom: 24px;
            left: 24px;
            display: flex;
            gap: 16px;
            z-index: 100;
        }}

        .nav-link {{
            width: 42px;
            height: 42px;
            cursor: pointer;
            opacity: 0.4;
            transition: opacity 0.3s ease, transform 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
        }}

        .nav-link:hover {{
            opacity: 1;
            transform: translateY(-2px);
        }}

        .nav-link svg {{
            width: 100%;
            height: 100%;
        }}

        .nav-tooltip {{
            position: fixed;
            bottom: 76px;
            background: rgba(255, 255, 255, 0.9);
            color: black;
            padding: 8px 16px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
            white-space: nowrap;
        }}

        .nav-link:hover .nav-tooltip {{
            opacity: 1;
        }}

        /* Mode toggle button - bottom right */
        #modeToggleBtn {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 50px;
            height: 50px;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.3);
            cursor: pointer;
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }}

        #modeToggleBtn:hover {{
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.6);
            transform: scale(1.05);
        }}

        #modeToggleBtn svg {{
            width: 60%;
            height: 60%;
        }}
    </style>
</head>
<body>
    <!-- Hidden file input for compatibility -->
    <input type="file" id="fileInput" accept="audio/*" />

    <!-- Back to timeline -->
    <a href="../index.html" id="backLink">
        <span>Timeline</span>
    </a>

    <!-- Minimalist controls button (top right) -->
    <div id="controlsBtn">
        <img src="../bouda.png" class="soft-shape" alt="Controls">
        <img src="../kiki.png" class="spiky-shape" alt="Controls">
    </div>
    <div id="controlsPanel">
        <div class="title">Controls</div>
        <div class="control-item">
            <span class="key">SPACE</span>
            <span>Play / Pause</span>
        </div>
        <div class="control-item">
            <span class="key">← →</span>
            <span>Speed</span>
        </div>
        <div class="control-item">
            <span class="key">M</span>
            <span>Toggle Mode</span>
        </div>
        <div class="control-item">
            <span class="key">S</span>
            <span>Save Frame</span>
        </div>
        <div class="control-item">
            <span class="key">C</span>
            <span>Clear Canvas</span>
        </div>
        <div class="control-item">
            <span class="key">H</span>
            <span>Hide UI</span>
        </div>
    </div>

    <!-- Mode indicator -->
    <div id="modeIndicator">RADIAL MODE</div>

    <!-- Save confirmation -->
    <div id="saveConfirmation">✓ FRAME SAVED</div>

    <!-- Speed indicator -->
    <div id="speedIndicator">1.0x</div>

    <!-- Mode toggle button (bottom right) -->
    <div id="modeToggleBtn" onclick="toggleVisualizationMode()">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <g stroke="white" stroke-width="2" fill="none">
                <!-- Arrows showing transformation -->
                <line x1="4" y1="12" x2="10" y2="12" />
                <line x1="14" y1="12" x2="20" y2="12" />
                <circle cx="12" cy="12" r="2" fill="white"/>
            </g>
        </svg>
        <div class="nav-tooltip" style="bottom: 76px; right: 24px; left: auto;">Toggle Mode (M)</div>
    </div>

    <!-- Bottom-left navigation -->
    <div class="bottom-nav">
        <!-- Visualizer Icon -->
        <a href="../visualizer.html" class="nav-link">
            <svg viewBox="0 0 42 42" xmlns="http://www.w3.org/2000/svg">
                <g stroke="white" stroke-width="1.5" fill="none">
                    <path d="M8 21 L14 12 L20 28 L26 15 L32 24 L38 21" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="14" cy="12" r="2" fill="white"/>
                    <circle cx="26" cy="15" r="2" fill="white"/>
                </g>
            </svg>
            <div class="nav-tooltip">Visualizer</div>
        </a>

        <!-- Alphabet Chart Icon -->
        <a href="../alphabet-chart.html" class="nav-link">
            <svg viewBox="0 0 42 42" xmlns="http://www.w3.org/2000/svg">
                <g stroke="white" stroke-width="1.5" fill="none">
                    <line x1="14" y1="8" x2="14" y2="34" />
                    <line x1="28" y1="8" x2="28" y2="34" />
                    <line x1="8" y1="14" x2="34" y2="14" />
                    <line x1="8" y1="28" x2="34" y2="28" />
                    <circle cx="14" cy="14" r="2" fill="white" />
                    <circle cx="28" cy="28" r="2" fill="white" />
                    <line x1="19" y1="19" x2="23" y2="23" />
                    <line x1="23" y1="19" x2="19" y2="23" />
                </g>
            </svg>
            <div class="nav-tooltip">Alphabet</div>
        </a>
    </div>

    <script>
{modified_sketch}
    </script>
</body>
</html>
"""
    return html

# Generate all song visualizer pages
print("Generating song pages with mode switching...")

for song in songs:
    html = generate_song_visualizer_html(song)
    filepath = os.path.join('songs', song['filename'])

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Created: {song['filename']}")

print(f"\n✓ Generated {len(songs)} song pages with mode switching!")
print("Features:")
print("  - Mode toggle button (bottom right)")
print("  - Press M key or click button to switch")
print("  - Horizontal mode (default): Left-to-right")
print("  - Radial mode: Center-outward spiral")
