// clap-print.js
// Voice-triggered visualization printing.
// Say "now" to print. Say "white" or "black" to set print mode.
// Add to any song page: <script src="../clap-print.js"></script>

(function () {
  const PRINT_URL   = 'http://localhost:3001/print';
  const COOLDOWN_MS = 5000;

  let lastPrint = 0;
  let printMode = 'white'; // 'white' = inverted (white bg, black visuals) | 'black' = original

  // ── NOTIFICATION ───────────────────────────────────────────────────────────
  function showNotification(text) {
    let el = document.getElementById('__print-notification');
    if (!el) {
      el = document.createElement('div');
      el.id = '__print-notification';
      Object.assign(el.style, {
        position:       'fixed',
        top:            '50%',
        left:           '50%',
        transform:      'translate(-50%, -50%)',
        fontFamily:     'LinotypeUnivers, sans-serif',
        fontSize:       '13px',
        fontWeight:     '700',
        letterSpacing:  '0.08em',
        color:          '#fff',
        textShadow:     '0 0 8px rgba(255,255,255,0.8)',
        background:     'transparent',
        pointerEvents:  'none',
        zIndex:         '99999',
        opacity:        '0',
        transition:     'opacity 0.4s ease',
        textTransform:  'lowercase',
      });
      document.body.appendChild(el);
    }

    el.textContent = text;
    el.style.opacity = '1';
    clearTimeout(el._hideTimer);
    el._hideTimer = setTimeout(() => { el.style.opacity = '0'; }, 2000);
  }

  // ── VOICE DETECTION ────────────────────────────────────────────────────────
  function startVoiceDetection() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn('[print] Speech recognition not supported. Use Chrome.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous     = true;
    recognition.interimResults = false;
    recognition.lang           = 'en-US';

    recognition.onstart = () => console.log('[print] Listening — say "now" to print, "white" or "black" to set mode.');

    recognition.onresult = (event) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (!event.results[i].isFinal) continue;
        const transcript = event.results[i][0].transcript.trim().toLowerCase();
        console.log('[print] Heard:', transcript);

        if (transcript.includes('white')) {
          printMode = 'white';
          console.log('[print] Mode set to white');
          showNotification('print set to white');
        } else if (transcript.includes('black')) {
          printMode = 'black';
          console.log('[print] Mode set to black');
          showNotification('print set to black');
        } else if (transcript.includes('now')) {
          const now = Date.now();
          if (now - lastPrint < COOLDOWN_MS) return;
          lastPrint = now;
          captureAndPrint();
        }
      }
    };

    recognition.onerror = (e) => {
      if (e.error === 'no-speech') return;
      console.warn('[print] Speech error:', e.error);
    };

    recognition.onend = () => recognition.start();
    recognition.start();
  }

  // ── SCREEN CAPTURE ─────────────────────────────────────────────────────────
  function captureAndPrint() {
    console.log('[print] Triggered — capturing in ' + printMode + ' mode...');

    const canvases = Array.from(document.querySelectorAll('canvas')).filter(c => {
      const s = window.getComputedStyle(c);
      return s.display !== 'none' && s.visibility !== 'hidden' && c.width > 0 && c.height > 0;
    });

    // Also collect visible video elements (for pages like Doctor Who Theme)
    const videos = Array.from(document.querySelectorAll('video')).filter(v => {
      const s = window.getComputedStyle(v);
      return s.display !== 'none' && s.visibility !== 'hidden' && v.videoWidth > 0;
    });

    if (canvases.length === 0 && videos.length === 0) {
      console.warn('[print] No canvases or videos found.');
      return;
    }

    const out = document.createElement('canvas');
    out.width  = window.innerWidth;
    out.height = window.innerHeight;
    const ctx  = out.getContext('2d');

    if (printMode === 'white') {
      // White background, black visuals (inverted)
      ctx.fillStyle = '#fff';
      ctx.fillRect(0, 0, out.width, out.height);
      ctx.filter = 'invert(1) contrast(1.8)';
    } else {
      // Black background — lighten heavy fills so print reads more white than black
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, out.width, out.height);
      ctx.filter = 'contrast(1.4) brightness(3.2) saturate(1.2)';
    }

    for (const v of videos) {
      const rect = v.getBoundingClientRect();
      try {
        ctx.drawImage(v, rect.left, rect.top, rect.width, rect.height);
      } catch (e) {
        console.warn('[print] Skipping tainted video:', e);
      }
    }

    for (const c of canvases) {
      const rect = c.getBoundingClientRect();
      try {
        ctx.drawImage(c, rect.left, rect.top, rect.width, rect.height);
      } catch (e) {
        console.warn('[print] Skipping tainted canvas:', e);
      }
    }
    ctx.filter = 'none';

    // ── OPN-specific star bloom pass (print only, does not affect live view) ──
    const isOPN = window.PRINT_LABEL && window.PRINT_LABEL.artist === 'OPN';
    if (isOPN) {
      if (printMode === 'black') {
        // screen blend only adds light — tiny white star dots bloom outward
        // without darkening anything. Multiple passes: tight+bright → wide+soft.
        const passes = [
          { blur: 0.5, brightness: 18 },
          { blur: 2,   brightness: 15 },
          { blur: 5,   brightness: 12 },
          { blur: 10,  brightness: 9  },
          { blur: 20,  brightness: 7  },
          { blur: 40,  brightness: 5  },
          { blur: 70,  brightness: 3  },
        ];
        ctx.globalCompositeOperation = 'screen';
        for (const c of canvases) {
          const rect = c.getBoundingClientRect();
          try {
            for (const p of passes) {
              ctx.filter = `blur(${p.blur}px) brightness(${p.brightness})`;
              ctx.drawImage(c, rect.left, rect.top, rect.width, rect.height);
            }
          } catch (e) { /* skip */ }
        }
      } else {
        // White mode: output is white bg + tiny black star dots (already inverted).
        // For each blur level, bake invert+blur+contrast into an offscreen canvas,
        // then stamp it onto the output repeatedly with multiply — each stamp
        // compounds the darkening so halos build up into strong visible marks.
        const bloomLevels = [
          { blur: 0.5, contrast: 25, repeat: 12 },
          { blur: 2,   contrast: 20, repeat: 10 },
          { blur: 6,   contrast: 16, repeat: 8  },
          { blur: 14,  contrast: 12, repeat: 7  },
          { blur: 30,  contrast: 8,  repeat: 6  },
          { blur: 60,  contrast: 5,  repeat: 5  },
        ];
        ctx.globalCompositeOperation = 'multiply';
        for (const c of canvases) {
          const rect = c.getBoundingClientRect();
          try {
            for (const lv of bloomLevels) {
              const tmp  = document.createElement('canvas');
              tmp.width  = out.width;
              tmp.height = out.height;
              const tctx = tmp.getContext('2d');
              tctx.filter = `invert(1) blur(${lv.blur}px) contrast(${lv.contrast})`;
              tctx.drawImage(c, rect.left, rect.top, rect.width, rect.height);
              tctx.filter = 'none';
              for (let i = 0; i < lv.repeat; i++) ctx.drawImage(tmp, 0, 0);
            }
          } catch (e) { /* skip */ }
        }
      }
      ctx.filter = 'none';
      ctx.globalCompositeOperation = 'source-over';
    }

    // ── Imprint: bottom corners ───────────────────────────────────────────────
    // 'difference' blend: text inverts whatever is beneath — always legible on
    // any background, black, white, or mixed, with no manual colour decisions.
    const pad       = Math.round(out.height * 0.055);
    const isBlack   = printMode === 'black';
    const fontSize  = Math.round(out.height * (isBlack ? 0.032 : 0.024));
    const fontWeight = isBlack ? '900' : '700';
    const tracking  = isBlack ? '0.13em' : '0.04em';

    ctx.globalCompositeOperation = 'difference';
    ctx.fillStyle    = '#ffffff';
    ctx.textBaseline = 'bottom';
    ctx.letterSpacing = tracking;
    const y = out.height - pad;

    function drawLabel(text, x, align, italic) {
      ctx.textAlign = align;
      ctx.font = `${italic ? 'italic ' : ''}${fontWeight} ${fontSize}px LinotypeUnivers, sans-serif`;
      ctx.fillText(text, x, y);
      return ctx.measureText(text).width;
    }

    let label = window.PRINT_LABEL;
    if ((!label || !label.song) && new URLSearchParams(window.location.search).get('custom')) {
      const customTitle = sessionStorage.getItem('customTitle');
      if (customTitle) label = { artist: 'Custom', song: customTitle, year: new Date().getFullYear().toString() };
    }
    if (label && label.artist && label.song && label.year) {
      const prefix = label.artist + ' \u2014 ';
      const suffix = ', ' + label.year;
      let x = pad;
      x += drawLabel(prefix, x, 'left', false);
      x += drawLabel(label.song, x, 'left', true);
      drawLabel(suffix, x, 'left', false);
    }
    drawLabel('sabrinawu.me', out.width - pad, 'right', false);

    ctx.letterSpacing = '0px';
    ctx.globalCompositeOperation = 'source-over';

    // Debug preview — shows what will be sent to printer
    const preview = document.createElement('img');
    preview.src = out.toDataURL();
    Object.assign(preview.style, {
      position: 'fixed', top: '10px', left: '10px',
      width: '320px', height: 'auto',
      border: '2px solid red', zIndex: '999999',
      pointerEvents: 'none'
    });
    document.body.appendChild(preview);
    setTimeout(() => preview.remove(), 6000);

    out.toBlob(blob => {
      if (!blob) { console.warn('[print] toBlob failed'); return; }
      sendToPrinter(blob);
    }, 'image/png');
  }

  // ── SEND TO PRINTER ────────────────────────────────────────────────────────
  function sendToPrinter(blob) {
    fetch(PRINT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'image/png' },
      body: blob
    })
      .then(r => r.text())
      .then(() => console.log('[print] Printed OK'))
      .catch(e => console.error('[print] Error:', e));
  }

  // ── INIT ───────────────────────────────────────────────────────────────────
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', startVoiceDetection);
  else startVoiceDetection();

})();
