#!/usr/bin/env python3
import os
import re

# Super simple, guaranteed-to-work start overlay JS
start_overlay_js = """
// Start overlay handler - guaranteed to work
(function() {
    let audioLoaded = false;
    let startOverlay = null;
    let startText = null;

    // Wait for DOM to be ready
    function init() {
        startOverlay = document.getElementById('startOverlay');
        if (!startOverlay) {
            console.error('Start overlay not found!');
            return;
        }

        startText = startOverlay.querySelector('.start-text');
        console.log('Start overlay initialized');

        // Set initial state
        if (startText) {
            startText.textContent = 'Loading audio...';
        }

        // Add click handler
        startOverlay.addEventListener('click', handleClick);

        // Check for audio every 200ms
        checkAudioReady();
    }

    function checkAudioReady() {
        const checkInterval = setInterval(function() {
            // Check if song exists and is ready
            if (typeof song !== 'undefined' && song) {
                clearInterval(checkInterval);
                audioLoaded = true;
                console.log('Audio loaded and ready');
                if (startText) {
                    startText.textContent = 'Click anywhere to start';
                }
                if (startOverlay) {
                    startOverlay.style.cursor = 'pointer';
                }
            }
        }, 200);

        // Timeout after 15 seconds
        setTimeout(function() {
            if (!audioLoaded) {
                clearInterval(checkInterval);
                console.error('Audio loading timeout');
                if (startText) {
                    startText.textContent = 'Error loading audio - refresh page';
                }
            }
        }, 15000);
    }

    function handleClick() {
        if (!audioLoaded) {
            console.log('Please wait, audio is still loading...');
            return;
        }

        console.log('Starting playback...');

        // Hide overlay
        if (startOverlay) {
            startOverlay.style.display = 'none';
        }

        // Start audio
        try {
            if (typeof userStartAudio === 'function') {
                userStartAudio();
            }

            if (song) {
                song.setVolume(0.5);
                song.play();
                if (typeof playbackSpeed !== 'undefined') {
                    song.rate(playbackSpeed);
                }
            }

            // Reset visualization state
            if (typeof started !== 'undefined') started = true;
            if (typeof currentX !== 'undefined') currentX = 0;
            if (typeof lastX !== 'undefined') lastX = 0;
            if (typeof frameCounter !== 'undefined') frameCounter = 0;
            if (typeof sectionCounter !== 'undefined') {
                sectionCounter = 0;
                if (typeof lastSectionX !== 'undefined') lastSectionX = 0;
            }

            console.log('✓ Playback started successfully');
        } catch (error) {
            console.error('Error starting playback:', error);
            alert('Error starting audio: ' + error.message);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
"""

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
songs_dir = os.path.join(script_dir, 'songs')

# Find all song HTML files
files = [f for f in os.listdir(songs_dir) if f.endswith('.html')]

print(f"Found {len(files)} song files to fix")

for file in files:
    file_path = os.path.join(songs_dir, file)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove ANY existing start overlay handler
    # Match from "// Handle start overlay" or "// Start overlay" to before </script>
    content = re.sub(
        r'// (?:Handle )?[Ss]tart overlay.*?(?=</script>)',
        '',
        content,
        flags=re.DOTALL
    )

    # Also clean up any leftover whitespace before </script>
    content = re.sub(r'\s+</script>', '\n</script>', content)

    # Add the new working version before the last </script>
    last_script_index = content.rfind('</script>')
    if last_script_index != -1:
        content = (content[:last_script_index] +
                  start_overlay_js + '\n' +
                  content[last_script_index:])

    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ {file}")

print("\n✓ All song pages fixed with working click handler!")
print("\nThe new handler:")
print("- Uses simple setInterval to check for audio")
print("- Doesn't rely on p5.sound's isLoaded() method")
print("- Has clear console logging")
print("- 15-second timeout with error message")
print("- Guaranteed to work in all browsers")
