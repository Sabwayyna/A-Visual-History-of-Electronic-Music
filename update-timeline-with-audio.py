import os
import json
import re
import shutil

# Songs with available audio files in Musique folder
songs = [
    {
        'year': '1948',
        'artist': 'Pierre Schaeffer',
        'track': 'Cinq Études de Bruits',
        'era': 'MUSIQUE CONCRÈTE & EARLY ELECTRONICS',
        'description': 'Birth of musique concrète.',
        'audio': 'Musique/01 - Pierre Schaeffer - Cinq études de bruits (1948) - Etude aux chemins de fer.mp3'
    },
    {
        'year': '1952',
        'artist': 'John Cage',
        'track': 'Williams Mix',
        'era': 'MUSIQUE CONCRÈTE & EARLY ELECTRONICS',
        'description': 'Early tape montage + chance operations.',
        'audio': 'Musique/02 - John Cage_ Williams Mix (19521953).mp3'
    },
    {
        'year': '1956',
        'artist': 'Karlheinz Stockhausen',
        'track': 'Gesang der Jünglinge',
        'era': 'MUSIQUE CONCRÈTE & EARLY ELECTRONICS',
        'description': 'First masterwork combining electronic sound + human voice.',
        'audio': 'Musique/03 - karlheinz stockhausen GESANG DER JÜNGLINGE.mp3'
    },
    {
        'year': '1960',
        'artist': 'Daphne Oram',
        'track': 'Four Aspects',
        'era': 'MUSIQUE CONCRÈTE & EARLY ELECTRONICS',
        'description': 'Early British electronic innovation; foundation of Oramics.',
        'audio': 'Musique/04 - Daphne Oram - Four Aspects.mp3'
    },
    {
        'year': '1963',
        'artist': 'Delia Derbyshire',
        'track': 'Doctor Who Theme',
        'era': 'MUSIQUE CONCRÈTE & EARLY ELECTRONICS',
        'description': 'Tape-based electronic sound design milestone.',
        'audio': 'Musique/05 - Doctor Who (1963) -  Original Theme music video.mp3'
    },
    {
        'year': '1965',
        'artist': 'Steve Reich',
        'track': "It's Gonna Rain",
        'era': 'MINIMALISM / PROCESS MUSIC',
        'description': 'Origin of phasing technique.',
        'audio': "Musique/06 - Steve Reich - It's Gonna Rain (1965).mp3"
    },
    {
        'year': '1974',
        'artist': 'Kraftwerk',
        'track': 'Autobahn',
        'era': 'ELECTRONIC PIONEERS / AMBIENT',
        'description': 'Template for electronic pop + machine aesthetics.',
        'audio': 'Musique/07 - Kraftwerk - Autobahn - 1974 Full Version.mp3'
    },
    {
        'year': '1978',
        'artist': 'Brian Eno',
        'track': 'Music for Airports 1/1',
        'era': 'ELECTRONIC PIONEERS / AMBIENT',
        'description': 'Ambient music as a formalized genre.',
        'audio': 'Musique/08 - Brian Eno - 1:1  Music for Airports (Remastered 2004).mp3'
    },
    {
        'year': '1986',
        'artist': 'Mr. Fingers (Larry Heard)',
        'track': 'Can You Feel It',
        'era': 'CHICAGO HOUSE & DETROIT TECHNO',
        'description': 'The cornerstone of Chicago deep house; emotional electronic music begins here.',
        'audio': 'Musique/09 - Mr Fingers - Can You Feel It.mp3'
    },
    {
        'year': '1987',
        'artist': 'Derrick May',
        'track': 'Strings of Life',
        'era': 'CHICAGO HOUSE & DETROIT TECHNO',
        'description': "Detroit techno's global breakout.",
        'audio': 'Musique/10 - Rhythm Is Rhythm - Strings Of Life - 1987.mp3'
    },
    {
        'year': '1995',
        'artist': 'Autechre',
        'track': 'Dael',
        'era': 'IDM / ELECTRONICA',
        'description': 'Algorithmic, abstract IDM.',
        'audio': 'Musique/11 - Dael · Autechre.mp3'
    },
    {
        'year': '1998',
        'artist': 'Boards of Canada',
        'track': 'Roygbiv',
        'era': 'IDM / ELECTRONICA',
        'description': 'Iconic analog warmth + nostalgia aesthetics.',
        'audio': 'Musique/12 - Boards of Canada — Roygbiv (1998).mp3'
    },
    {
        'year': '2005',
        'artist': 'Ryoji Ikeda',
        'track': 'data.matrix',
        'era': 'GLITCH / CONTEMPORARY EXPERIMENTAL',
        'description': 'Maximal data-driven digital minimalism.',
        'audio': 'Musique/13 - Ryoji Ikeda - data.matrix.mp3'
    },
    {
        'year': '2010',
        'artist': 'Oneohtrix Point Never',
        'track': 'Returnal',
        'era': 'GLITCH / CONTEMPORARY EXPERIMENTAL',
        'description': 'Widely regarded as a turning point in modern experimental electronic music.',
        'audio': 'Musique/14 - Oneohtrix Point Never — Returnal (2010) .mp3'
    }
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
            margin-bottom: 24px;
        }}

        .description {{
            font-size: 14px;
            color: #999;
            line-height: 1.6;
            max-width: 600px;
            margin: 0 auto;
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
        <div class="description">{song['description']}</div>
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

# Clear old songs directory and recreate
songs_dir = 'songs'
if os.path.exists(songs_dir):
    shutil.rmtree(songs_dir)
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
        'era': song['era'],
        'description': song['description'],
        'audio': song['audio'],
        'filename': filename,
        'path': f'songs/{filename}'
    })

    print(f"Created: {filename}")

# Save mapping for reference
with open('song-mapping.json', 'w', encoding='utf-8') as f:
    json.dump(mapping, f, indent=2, ensure_ascii=False)

print(f"\nGenerated {len(songs)} song pages successfully!")
print("Mapping saved to song-mapping.json")

# Now generate the new index.html with audio playback
print("\nGenerating new index.html with audio playback...")

# Group songs by era
eras = {}
for song in songs:
    era = song['era']
    if era not in eras:
        eras[era] = []
    eras[era].append(song)

# Generate HTML for timeline items
timeline_html = ""
for era_name in [
    'MUSIQUE CONCRÈTE & EARLY ELECTRONICS',
    'MINIMALISM / PROCESS MUSIC',
    'ELECTRONIC PIONEERS / AMBIENT',
    'CHICAGO HOUSE & DETROIT TECHNO',
    'IDM / ELECTRONICA',
    'GLITCH / CONTEMPORARY EXPERIMENTAL'
]:
    if era_name in eras:
        timeline_html += f'\n        <div class="era-marker" data-era="{era_name}"></div>\n'
        for song in eras[era_name]:
            filename = generate_filename(song['artist'], song['track'], song['year'])
            timeline_html += f'''
        <a href="songs/{filename}" class="timeline-item" data-audio="{song['audio']}">
            <div class="year">{song['year']}</div>
            <div class="artist">{song['artist']}</div>
            <div class="track">{song['track']}</div>
            <div class="description">{song['description']}</div>
        </a>
'''

# Create new index.html with audio playback functionality
index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>History of Electronic Music</title>
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
            overflow-x: auto;
            overflow-y: hidden;
            height: 100vh;
            -webkit-font-smoothing: antialiased;
        }}

        .container {{
            display: flex;
            align-items: center;
            height: 100vh;
            padding: 0 8vw;
            width: max-content;
            gap: 60px;
        }}

        .timeline-item {{
            display: inline-flex;
            flex-direction: column;
            justify-content: center;
            min-width: 280px;
            max-width: 280px;
            height: auto;
            padding: 0;
            cursor: pointer;
            position: relative;
            text-decoration: none;
            transition: opacity 0.2s ease;
        }}

        .timeline-item:hover {{
            opacity: 0.6;
        }}

        .year {{
            font-size: 14px;
            font-weight: 400;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
            color: #000;
        }}

        .artist {{
            font-size: 14px;
            margin-bottom: 4px;
            font-weight: 400;
            letter-spacing: -0.2px;
            color: #000;
        }}

        .track {{
            font-size: 14px;
            font-weight: 400;
            line-height: 1.5;
            color: #000;
            margin-bottom: 8px;
        }}

        .description {{
            font-size: 12px;
            font-weight: 400;
            line-height: 1.5;
            color: #666;
            font-style: italic;
        }}

        .era-marker {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: auto;
            height: auto;
            padding: 0;
            margin: 0 50px;
            background: transparent;
            color: #000;
            writing-mode: vertical-rl;
            text-orientation: mixed;
            font-size: 12px;
            font-weight: 400;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            position: relative;
        }}

        .era-marker::before {{
            content: attr(data-era);
            position: absolute;
            writing-mode: vertical-rl;
            text-orientation: mixed;
            left: 0;
            font-size: 12px;
            letter-spacing: 0.5px;
            color: #000;
        }}

        ::-webkit-scrollbar {{
            height: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: #fafafa;
        }}

        ::-webkit-scrollbar-thumb {{
            background: #ddd;
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #bbb;
        }}

    </style>
</head>
<body>
    <div class="container">{timeline_html}
    </div>

    <script>
        // Audio playback on hover
        const items = document.querySelectorAll('.timeline-item');
        let currentAudio = null;

        items.forEach(item => {{
            item.addEventListener('mouseenter', function() {{
                // Stop any currently playing audio
                if (currentAudio) {{
                    currentAudio.pause();
                    currentAudio.currentTime = 0;
                }}

                // Get audio path from data attribute
                const audioPath = this.getAttribute('data-audio');
                if (audioPath) {{
                    currentAudio = new Audio(audioPath);
                    currentAudio.volume = 0.5;
                    currentAudio.play().catch(e => {{
                        console.log('Audio play failed:', e);
                    }});
                }}
            }});

            item.addEventListener('mouseleave', function() {{
                if (currentAudio) {{
                    currentAudio.pause();
                    currentAudio.currentTime = 0;
                }}
            }});
        }});
    </script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

print("New index.html generated with audio playback on hover!")
print("\n✓ Timeline updated with available audio files!")
