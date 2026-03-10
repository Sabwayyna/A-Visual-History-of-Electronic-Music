# Music Visualizer

An interactive electronic music visualization platform.

## Structure

```
/visualizer/
  ├── index.html                  # Main timeline landing page
  ├── visualizer.html             # Custom file upload visualizer
  ├── alphabet-chart.html         # Visual-sonic alphabet reference
  ├── timeline-horizontal.html    # Alternative timeline view
  ├── sketch.js                   # Main visualization engine (p5.js)
  │
  ├── /assets/
  │   ├── kiki.png               # UI icon (spiky/angular shape)
  │   ├── bouda.png              # UI icon (soft/rounded shape)
  │   └── visual-sonic-alphabet.json  # Design system data
  │
  ├── /audio/
  │   └── [14 mp3 files]         # Curated electronic music tracks (1948-2010)
  │
  └── /songs/
      └── [14 html files]        # Individual song visualization pages
```

## How to Run

1. **Using Python:**
   ```bash
   python3 -m http.server 8000
   ```

2. **Using Node.js (http-server):**
   ```bash
   npx http-server -p 8000
   ```

3. **Using PHP:**
   ```bash
   php -S localhost:8000
   ```

Then open your browser to `http://localhost:8000`

## Features

- **Timeline View** - Browse 14 seminal electronic music compositions from 1948-2010
- **Real-time Visualization** - Audio-reactive visuals generated from frequency analysis
- **Custom Upload** - Visualize any audio file using the visualizer.html page
- **Visual-Sonic Alphabet** - Interactive reference chart of the design system
- **Dual Modes** - Radial (spiral) and Horizontal visualization layouts
- **Keyboard Controls** - Play/pause, speed control, save frames, toggle modes

## Notes

- All file paths have been organized and updated
- The visualizer uses p5.js and p5.sound libraries (loaded via CDN)
- Audio files are preloaded on the timeline page for smooth playback
- All visualizations are cumulative (shapes persist throughout the track)
