import json
import re

# Read the song mapping
with open('song-mapping.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)

# Create a lookup dictionary by year, artist, and track
lookup = {}
for song in mapping:
    key = (song['year'], song['artist'], song['track'])
    lookup[key] = song['path']

# Read the current index.html
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Function to replace href for each timeline item
def replace_href(match):
    # Extract year, artist, and track from the match
    full_match = match.group(0)

    # Find year, artist, and track in the HTML block
    year_match = re.search(r'<div class="year">(\d+)</div>', full_match)
    artist_match = re.search(r'<div class="artist">([^<]+)</div>', full_match)
    track_match = re.search(r'<div class="track">([^<]+)</div>', full_match)

    if year_match and artist_match and track_match:
        year = year_match.group(1)
        artist = artist_match.group(1)
        track = track_match.group(1)

        # Look up the correct path
        key = (year, artist, track)
        if key in lookup:
            new_path = lookup[key]
            # Replace the href
            new_match = re.sub(r'href="[^"]*"', f'href="{new_path}"', full_match)
            return new_match

    return full_match

# Pattern to match each timeline item anchor tag with its content
pattern = r'<a href="visualizer\.html" class="timeline-item">.*?</a>'

# Replace all occurrences
new_content = re.sub(pattern, replace_href, content, flags=re.DOTALL)

# Write the updated content back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated index.html with individual song page links!")
