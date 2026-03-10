#!/usr/bin/env python3
import os
import re

# Super aggressive debugging version
start_overlay_js = """
// DEBUG VERSION - Start overlay handler
console.log('=== START OVERLAY SCRIPT LOADED ===');

(function() {
    console.log('IIFE started');

    let audioLoaded = false;
    let startOverlay = null;
    let startText = null;

    function init() {
        console.log('init() called');
        startOverlay = document.getElementById('startOverlay');
        console.log('startOverlay element:', startOverlay);

        if (!startOverlay) {
            console.error('❌ START OVERLAY NOT FOUND IN DOM!');
            alert('ERROR: Start overlay not found in DOM');
            return;
        }

        console.log('✓ Start overlay found');
        startText = startOverlay.querySelector('.start-text');
        console.log('startText element:', startText);

        // Set initial state
        if (startText) {
            startText.textContent = 'Loading audio...';
            console.log('Set text to: Loading audio...');
        }

        // Add click handler
        console.log('Adding click event listener...');
        startOverlay.addEventListener('click', function(e) {
            console.log('CLICK DETECTED!', e);
            handleClick();
        });
        console.log('✓ Click listener added');

        // Also add to window for testing
        window.testClick = handleClick;
        console.log('✓ window.testClick() available for manual testing');

        // Check for audio every 200ms
        checkAudioReady();
    }

    function checkAudioReady() {
        console.log('Starting audio check interval...');
        let attempts = 0;

        const checkInterval = setInterval(function() {
            attempts++;
            console.log('Audio check attempt', attempts, '- typeof song:', typeof song);

            if (typeof song !== 'undefined' && song) {
                clearInterval(checkInterval);
                audioLoaded = true;
                console.log('✅ AUDIO LOADED!');
                console.log('song object:', song);

                if (startText) {
                    startText.textContent = 'Click anywhere to start';
                    console.log('Text updated to: Click anywhere to start');
                }
                if (startOverlay) {
                    startOverlay.style.cursor = 'pointer';
                    console.log('Cursor set to pointer');
                }

                alert('Audio loaded! You can click now.');
            }
        }, 200);

        // Timeout after 15 seconds
        setTimeout(function() {
            if (!audioLoaded) {
                clearInterval(checkInterval);
                console.error('❌ AUDIO LOADING TIMEOUT after', attempts, 'attempts');
                if (startText) {
                    startText.textContent = 'Error loading audio - refresh page';
                }
                alert('Audio loading timeout. Please refresh the page.');
            }
        }, 15000);
    }

    function handleClick() {
        console.log('===handleClick() called===');
        console.log('audioLoaded:', audioLoaded);

        if (!audioLoaded) {
            console.log('Audio not ready yet, ignoring click');
            alert('Please wait, audio is still loading...');
            return;
        }

        console.log('✓ Audio ready, starting playback...');

        // Hide overlay
        if (startOverlay) {
            startOverlay.style.display = 'none';
            console.log('✓ Overlay hidden');
        }

        // Start audio
        try {
            console.log('Calling userStartAudio()...');
            if (typeof userStartAudio === 'function') {
                userStartAudio();
                console.log('✓ userStartAudio() called');
            } else {
                console.warn('userStartAudio is not a function');
            }

            console.log('Starting song playback...');
            if (song) {
                song.setVolume(0.5);
                console.log('✓ Volume set');
                song.play();
                console.log('✓ song.play() called');
                if (typeof playbackSpeed !== 'undefined') {
                    song.rate(playbackSpeed);
                    console.log('✓ Playback speed set');
                }
            } else {
                console.error('song is null/undefined!');
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

            console.log('✅✅✅ PLAYBACK STARTED SUCCESSFULLY ✅✅✅');
            alert('Success! Playback started.');
        } catch (error) {
            console.error('❌ ERROR in handleClick:', error);
            alert('Error starting audio: ' + error.message);
        }
    }

    // Initialize when DOM is ready
    console.log('Setting up initialization...');
    if (document.readyState === 'loading') {
        console.log('DOM still loading, adding DOMContentLoaded listener');
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOMContentLoaded fired');
            init();
        });
    } else {
        console.log('DOM already ready, calling init immediately');
        init();
    }

    console.log('IIFE completed');
})();

console.log('=== START OVERLAY SCRIPT EXECUTION COMPLETE ===');
"""

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
songs_dir = os.path.join(script_dir, 'songs')

# Find all song HTML files
files = [f for f in os.listdir(songs_dir) if f.endswith('.html')]

print(f"Found {len(files)} song files")
print("Adding DEBUG VERSION with extensive logging and alerts...")

for file in files:
    file_path = os.path.join(songs_dir, file)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove any existing start overlay handler
    content = re.sub(
        r'// (?:DEBUG VERSION - )?(?:Handle )?[Ss]tart overlay.*?(?=</script>)',
        '',
        content,
        flags=re.DOTALL
    )

    # Clean up whitespace
    content = re.sub(r'\s+</script>', '\n</script>', content)

    # Add the debug version before the last </script>
    last_script_index = content.rfind('</script>')
    if last_script_index != -1:
        content = (content[:last_script_index] +
                  start_overlay_js + '\n' +
                  content[last_script_index:])

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ {file}")

print("\n✅ DEBUG VERSION installed!")
print("\nThis version will:")
print("- Log EVERYTHING to console")
print("- Show alerts at key points")
print("- Add window.testClick() for manual testing")
print("\nOpen a song page and:")
print("1. Open console (Cmd+Option+I)")
print("2. Watch for logs")
print("3. Try clicking the overlay")
print("4. Or type: window.testClick() in console")
