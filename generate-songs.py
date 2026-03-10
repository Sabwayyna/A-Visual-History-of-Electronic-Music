import os
import json
import re

# Song data from the timeline
songs = [
    {'year': '1948', 'artist': 'Pierre Schaeffer', 'track': 'Cinq Études de Bruits', 'era': 'MUSIQUE CONCRÈTE'},
    {'year': '1950', 'artist': 'Pierre Henry', 'track': 'Symphonie pour un Homme Seul', 'era': 'MUSIQUE CONCRÈTE'},
    {'year': '1952', 'artist': 'John Cage', 'track': 'Williams Mix', 'era': 'MUSIQUE CONCRÈTE'},
    {'year': '1956', 'artist': 'Karlheinz Stockhausen', 'track': 'Gesang der Jünglinge', 'era': 'MUSIQUE CONCRÈTE'},
    {'year': '1958', 'artist': 'Karlheinz Stockhausen', 'track': 'Kontakte', 'era': 'MUSIQUE CONCRÈTE'},
    {'year': '1960', 'artist': 'Daphne Oram', 'track': 'Four Aspects', 'era': 'MUSIQUE CONCRÈTE'},
    {'year': '1963', 'artist': 'Delia Derbyshire', 'track': 'Doctor Who Theme', 'era': 'MUSIQUE CONCRÈTE'},
    {'year': '1964', 'artist': 'Terry Riley', 'track': 'In C', 'era': 'MINIMALISM'},
    {'year': '1965', 'artist': 'Pauline Oliveros', 'track': 'Bye Bye Butterfly', 'era': 'MINIMALISM'},
    {'year': '1965', 'artist': 'Steve Reich', 'track': "It's Gonna Rain", 'era': 'MINIMALISM'},
    {'year': '1967', 'artist': 'Steve Reich', 'track': 'Piano Phase', 'era': 'MINIMALISM'},
    {'year': '1971', 'artist': 'Steve Reich', 'track': 'Four Organs', 'era': 'MINIMALISM'},
    {'year': '1974', 'artist': 'Kraftwerk', 'track': 'Autobahn', 'era': 'ELECTRONIC PIONEERS'},
    {'year': '1974', 'artist': 'Tangerine Dream', 'track': 'Phaedra', 'era': 'ELECTRONIC PIONEERS'},
    {'year': '1975', 'artist': 'Brian Eno', 'track': 'Discreet Music', 'era': 'ELECTRONIC PIONEERS'},
    {'year': '1978', 'artist': 'Brian Eno', 'track': 'Music for Airports 1/1', 'era': 'ELECTRONIC PIONEERS'},
    {'year': '1981', 'artist': 'Laurie Spiegel', 'track': 'The Expanding Universe', 'era': 'ELECTRONIC PIONEERS'},
    {'year': '1982', 'artist': 'Afrika Bambaataa', 'track': 'Planet Rock', 'era': 'ELECTRONIC PIONEERS'},
    {'year': '1983', 'artist': 'New Order', 'track': 'Blue Monday', 'era': 'ELECTRONIC PIONEERS'},
    {'year': '1990', 'artist': 'LFO', 'track': 'LFO', 'era': 'IDM / ELECTRONICA'},
    {'year': '1990', 'artist': 'The Orb', 'track': 'Little Fluffy Clouds', 'era': 'IDM / ELECTRONICA'},
    {'year': '1992', 'artist': 'Aphex Twin', 'track': 'Selected Ambient Works 85–92', 'era': 'IDM / ELECTRONICA'},
    {'year': '1993', 'artist': 'Autechre', 'track': 'Flutter', 'era': 'IDM / ELECTRONICA'},
    {'year': '1995', 'artist': 'Autechre', 'track': 'Tri Repetae', 'era': 'IDM / ELECTRONICA'},
    {'year': '1996', 'artist': 'Squarepusher', 'track': 'Beep Street', 'era': 'IDM / ELECTRONICA'},
    {'year': '1998', 'artist': 'Boards of Canada', 'track': 'Roygbiv', 'era': 'IDM / ELECTRONICA'},
    {'year': '2001', 'artist': 'Alva Noto', 'track': 'Transform', 'era': 'GLITCH / DIGITAL'},
    {'year': '2001', 'artist': 'Fennesz', 'track': 'Endless Summer', 'era': 'GLITCH / DIGITAL'},
    {'year': '2005', 'artist': 'Ryoji Ikeda', 'track': 'Dataplex', 'era': 'GLITCH / DIGITAL'},
    {'year': '2006', 'artist': 'Matmos', 'track': 'For the Trees', 'era': 'GLITCH / DIGITAL'},
    {'year': '2010', 'artist': 'Oneohtrix Point Never', 'track': 'Returnal', 'era': 'GLITCH / DIGITAL'},
    {'year': '2011', 'artist': 'Holly Herndon', 'track': 'Movement', 'era': 'CONTEMPORARY'},
    {'year': '2013', 'artist': 'SOPHIE', 'track': 'Bipp', 'era': 'CONTEMPORARY'},
    {'year': '2014', 'artist': 'Arca', 'track': 'Xen', 'era': 'CONTEMPORARY'},
    {'year': '2018', 'artist': 'Autechre', 'track': 'NTS Sessions', 'era': 'CONTEMPORARY'},
    {'year': '2019', 'artist': 'Caterina Barbieri', 'track': 'Fantas', 'era': 'CONTEMPORARY'},
    {'year': '2020', 'artist': 'Amnesia Scanner', 'track': 'Tearless', 'era': 'CONTEMPORARY'}
]

def generate_filename(artist, track, year):
    """Generate URL-friendly filename"""
    combined = f"{artist}-{track}-{year}"
    # Remove special characters and convert to lowercase
    combined = re.sub(r"[^\w\s-]", '', combined)
    combined = re.sub(r"\s+", '-', combined)
    combined = re.sub(r"-+", '-', combined)
    return combined.lower() + '.html'

def generate_html(song):
    """Generate HTML content for a song page"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{song['track']} - {song['artist']} ({song['year']})</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background: #ffffff;
            color: #1a1a1a;
            font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'Arial', sans-serif;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}

        .content {{
            text-align: center;
            max-width: 800px;
            padding: 40px;
        }}

        .era {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #999;
            margin-bottom: 16px;
        }}

        .year {{
            font-size: 18px;
            font-weight: 400;
            letter-spacing: 0.5px;
            color: #666;
            margin-bottom: 24px;
        }}

        .artist {{
            font-size: 32px;
            font-weight: 400;
            letter-spacing: -0.5px;
            margin-bottom: 12px;
        }}

        .track {{
            font-size: 24px;
            font-weight: 400;
            color: #666;
            font-style: italic;
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

        /* Tooltip */
        .nav-tooltip {{
            position: fixed;
            bottom: 76px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
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

        /* Back to timeline */
        .back-link {{
            position: fixed;
            top: 24px;
            left: 24px;
            font-size: 11px;
            font-weight: 400;
            letter-spacing: 2px;
            color: rgba(0, 0, 0, 0.4);
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .back-link:hover {{
            color: rgba(0, 0, 0, 1);
            letter-spacing: 3px;
            transform: translateX(-2px);
        }}

        .back-link::before {{
            content: "←";
            font-size: 14px;
            transition: transform 0.3s ease;
        }}

        .back-link:hover::before {{
            transform: translateX(-4px);
        }}
    </style>
</head>
<body>
    <!-- Back to timeline -->
    <a href="../index.html" class="back-link">
        <span>Timeline</span>
    </a>

    <!-- Main content -->
    <div class="content">
        <div class="era">{song['era']}</div>
        <div class="year">{song['year']}</div>
        <div class="artist">{song['artist']}</div>
        <div class="track">{song['track']}</div>
    </div>

    <!-- Bottom-left navigation -->
    <div class="bottom-nav">
        <!-- Visualizer Icon -->
        <a href="../visualizer.html" class="nav-link">
            <svg viewBox="0 0 42 42" xmlns="http://www.w3.org/2000/svg">
                <g stroke="black" stroke-width="1.5" fill="none">
                    <!-- Waveform-like pattern -->
                    <path d="M8 21 L14 12 L20 28 L26 15 L32 24 L38 21" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="14" cy="12" r="2" fill="black"/>
                    <circle cx="26" cy="15" r="2" fill="black"/>
                </g>
            </svg>
            <div class="nav-tooltip">Visualizer</div>
        </a>

        <!-- Alphabet Chart Icon -->
        <a href="../alphabet-chart.html" class="nav-link">
            <svg viewBox="0 0 42 42" xmlns="http://www.w3.org/2000/svg">
                <g stroke="black" stroke-width="1.5" fill="none">
                    <!-- Grid pattern -->
                    <line x1="14" y1="8" x2="14" y2="34" />
                    <line x1="28" y1="8" x2="28" y2="34" />
                    <line x1="8" y1="14" x2="34" y2="14" />
                    <line x1="8" y1="28" x2="34" y2="28" />
                    <circle cx="14" cy="14" r="2" fill="black" />
                    <circle cx="28" cy="28" r="2" fill="black" />
                    <line x1="19" y1="19" x2="23" y2="23" />
                    <line x1="23" y1="19" x2="19" y2="23" />
                </g>
            </svg>
            <div class="nav-tooltip">Alphabet</div>
        </a>
    </div>
</body>
</html>
"""

# Create songs directory if it doesn't exist
songs_dir = 'songs'
if not os.path.exists(songs_dir):
    os.makedirs(songs_dir)

# Generate all song pages
mapping = []

for index, song in enumerate(songs):
    filename = generate_filename(song['artist'], song['track'], song['year'])
    filepath = os.path.join(songs_dir, filename)
    html = generate_html(song)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    mapping.append({
        'index': index + 1,
        'year': song['year'],
        'artist': song['artist'],
        'track': song['track'],
        'filename': filename,
        'path': f'songs/{filename}'
    })

    print(f"Created: {filename}")

# Save mapping for reference
with open('song-mapping.json', 'w', encoding='utf-8') as f:
    json.dump(mapping, f, indent=2)

print(f"\nGenerated {len(songs)} song pages successfully!")
print("Mapping saved to song-mapping.json")
