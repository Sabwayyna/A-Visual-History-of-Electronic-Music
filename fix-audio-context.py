#!/usr/bin/env python3
import os
import re

# Fixed version that properly handles audio context
start_overlay_js = """
// Start overlay with proper audio context handling
console.log('=== START OVERLAY SCRIPT (Audio Context Fix) ===');

(function() {
    let audioLoaded = false;
    let startOverlay = null;
    let startText = null;

    function init() {
        console.log('Initializing start overlay...');
        startOverlay = document.getElementById('startOverlay');

        if (!startOverlay) {
            console.error('Start overlay not found');
            return;
        }

        console.log('✓ Start overlay found');
        startText = startOverlay.querySelector('.start-text');

        if (startText) {
            startText.textContent = 'Loading audio...';
        }

        // Add click handler
        startOverlay.addEventListener('click', handleClick, false);
        console.log('✓ Click listener added');

        // Check for audio
        checkAudioReady();
    }

    function checkAudioReady() {
        console.log('Checking for audio...');
        let attempts = 0;

        const checkInterval = setInterval(function() {
            attempts++;

            if (typeof song !== 'undefined' && song) {
                clearInterval(checkInterval);
                audioLoaded = true;
                console.log('✅ Audio loaded after', attempts, 'attempts');

                if (startText) {
                    startText.textContent = 'Click anywhere to start';
                }
                if (startOverlay) {
                    startOverlay.style.cursor = 'pointer';
                }
            }
        }, 200);

        setTimeout(function() {
            if (!audioLoaded) {
                clearInterval(checkInterval);
                console.error('Audio loading timeout');
                if (startText) {
                    startText.textContent = 'Error loading - refresh page';
                }
            }
        }, 15000);
    }

    function handleClick(e) {
        console.log('=== CLICK DETECTED ===');

        if (!audioLoaded) {
            console.log('Audio not ready yet');
            return;
        }

        // CRITICAL: Resume audio context FIRST
        console.log('Resuming audio context...');
        try {
            // p5.sound uses getAudioContext()
            if (typeof getAudioContext === 'function') {
                const audioContext = getAudioContext();
                console.log('Audio context state:', audioContext.state);

                if (audioContext.state === 'suspended') {
                    console.log('Audio context is suspended, resuming...');
                    audioContext.resume().then(function() {
                        console.log('✓ Audio context resumed');
                        startPlayback();
                    }).catch(function(err) {
                        console.error('Failed to resume audio context:', err);
                        alert('Error: Could not resume audio context');
                    });
                } else {
                    console.log('Audio context already running');
                    startPlayback();
                }
            } else {
                console.warn('getAudioContext not available, trying direct play');
                startPlayback();
            }
        } catch (err) {
            console.error('Error in handleClick:', err);
            alert('Error: ' + err.message);
        }
    }

    function startPlayback() {
        console.log('=== STARTING PLAYBACK ===');

        // Hide overlay
        if (startOverlay) {
            startOverlay.style.display = 'none';
            console.log('✓ Overlay hidden');
        }

        try {
            // Call userStartAudio (p5.sound function)
            if (typeof userStartAudio === 'function') {
                userStartAudio();
                console.log('✓ userStartAudio() called');
            }

            // Start the song
            if (song) {
                console.log('Starting song...');
                song.setVolume(0.5);

                // Use .play() which returns a promise
                const playPromise = song.play();

                if (playPromise !== undefined) {
                    playPromise.then(function() {
                        console.log('✅ Song playing successfully');
                        if (typeof playbackSpeed !== 'undefined') {
                            song.rate(playbackSpeed);
                        }
                    }).catch(function(error) {
                        console.error('Play failed:', error);
                        alert('Play failed: ' + error.message);
                    });
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

            console.log('✓ Visualization state reset');
            console.log('✅ Playback initialized');

        } catch (error) {
            console.error('Error in startPlayback:', error);
            alert('Playback error: ' + error.message);
        }
    }

    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

console.log('=== START OVERLAY SCRIPT COMPLETE ===');
"""

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
songs_dir = os.path.join(script_dir, 'songs')

# Find all song HTML files
files = [f for f in os.listdir(songs_dir) if f.endswith('.html')]

print(f"Fixing {len(files)} song files with proper audio context handling...")

for file in files:
    file_path = os.path.join(songs_dir, file)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove existing start overlay handler
    content = re.sub(
        r'// (?:DEBUG VERSION - )?(?:Start overlay|Handle start overlay).*?(?=</script>)',
        '',
        content,
        flags=re.DOTALL
    )

    # Clean up whitespace
    content = re.sub(r'\s+</script>', '\n</script>', content)

    # Add the fixed version
    last_script_index = content.rfind('</script>')
    if last_script_index != -1:
        content = (content[:last_script_index] +
                  start_overlay_js + '\n' +
                  content[last_script_index:])

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ {file}")

print("\n✅ Fixed with proper audio context handling!")
print("\nThe fix:")
print("- Explicitly calls getAudioContext().resume()")
print("- Checks if context is suspended")
print("- Waits for resume to complete before playing")
print("- Handles play() promise properly")
print("- Has detailed error logging")
