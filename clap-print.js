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
    recognition.maxAlternatives = 5;

    // Bias the recognizer toward the three command words
    const SpeechGrammarList = window.SpeechGrammarList || window.webkitSpeechGrammarList;
    if (SpeechGrammarList) {
      const grammar = '#JSGF V1.0; grammar commands; public <command> = black | white | now ;';
      const list = new SpeechGrammarList();
      list.addFromString(grammar, 1);
      recognition.grammars = list;
    }

    // Words the ASR commonly returns instead of "black"
    const BLACK_ALTS = ['black', 'blank', 'bloc', 'blacks', 'blake', 'blac', 'back'];

    function matchesBlack(t) { return BLACK_ALTS.some(w => t.includes(w)); }

    recognition.onstart = () => console.log('[print] Listening — say "now" to print, "white" or "black" to set mode.');

    recognition.onresult = (event) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (!event.results[i].isFinal) continue;

        // Collect all alternatives into one pool for matching
        const alts = [];
        for (let a = 0; a < event.results[i].length; a++) {
          alts.push(event.results[i][a].transcript.trim().toLowerCase());
        }
        console.log('[print] Heard:', alts);

        // Check every alternative — first match wins
        let matched = false;
        for (const transcript of alts) {
          if (transcript.includes('white')) {
            printMode = 'white';
            console.log('[print] Mode set to white');
            showNotification('print set to white');
            matched = true; break;
          } else if (matchesBlack(transcript)) {
            printMode = 'black';
            console.log('[print] Mode set to black');
            showNotification('print set to black');
            matched = true; break;
          } else if (transcript.includes('now')) {
            const now = Date.now();
            if (now - lastPrint < COOLDOWN_MS) { matched = true; break; }
            lastPrint = now;
            captureAndPrint();
            matched = true; break;
          }
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

  // ── BUILD PRINT CANVAS ────────────────────────────────────────────────────
  // Shared by both the real print path and the preview path.
  // Returns a composed canvas (with thermal processing + imprint) or null.
  // Pass an optional mode ('white'|'black') to override the current printMode.
  function buildPrintCanvas(modeOverride) {
    const mode = modeOverride || printMode;
    const canvases = Array.from(document.querySelectorAll('canvas')).filter(c => {
      const s = window.getComputedStyle(c);
      return s.display !== 'none' && s.visibility !== 'hidden' && c.width > 0 && c.height > 0;
    });

    const videos = Array.from(document.querySelectorAll('video')).filter(v => {
      const s = window.getComputedStyle(v);
      return s.display !== 'none' && s.visibility !== 'hidden' && v.videoWidth > 0;
    });

    if (canvases.length === 0 && videos.length === 0) {
      console.warn('[print] No canvases or videos found.');
      return null;
    }

    const out = document.createElement('canvas');
    out.width  = window.innerWidth;
    out.height = window.innerHeight;
    const ctx  = out.getContext('2d');

    // ── Thermal colour processing ─────────────────────────────────────────────
    if (mode === 'white') {
      ctx.fillStyle = '#fff';
      ctx.fillRect(0, 0, out.width, out.height);
      ctx.filter = 'invert(1) contrast(1.8)';
    } else {
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, out.width, out.height);
      ctx.filter = 'contrast(1.4) brightness(3.2) saturate(1.2)';
    }

    for (const v of videos) {
      const rect = v.getBoundingClientRect();
      try { ctx.drawImage(v, rect.left, rect.top, rect.width, rect.height); }
      catch (e) { console.warn('[print] Skipping tainted video:', e); }
    }
    for (const c of canvases) {
      const rect = c.getBoundingClientRect();
      try { ctx.drawImage(c, rect.left, rect.top, rect.width, rect.height); }
      catch (e) { console.warn('[print] Skipping tainted canvas:', e); }
    }
    ctx.filter = 'none';

    // ── OPN-specific star bloom pass ──────────────────────────────────────────
    const isOPN = window.PRINT_LABEL && window.PRINT_LABEL.artist === 'OPN';
    if (isOPN) {
      if (mode === 'black') {
        const passes = [
          { blur: 0.5, brightness: 18 }, { blur: 2,  brightness: 15 },
          { blur: 5,   brightness: 12 }, { blur: 10, brightness: 9  },
          { blur: 20,  brightness: 7  }, { blur: 40, brightness: 5  },
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
        const bloomLevels = [
          { blur: 0.5, contrast: 25, repeat: 12 }, { blur: 2,  contrast: 20, repeat: 10 },
          { blur: 6,   contrast: 16, repeat: 8  }, { blur: 14, contrast: 12, repeat: 7  },
          { blur: 30,  contrast: 8,  repeat: 6  }, { blur: 60, contrast: 5,  repeat: 5  },
        ];
        ctx.globalCompositeOperation = 'multiply';
        for (const c of canvases) {
          const rect = c.getBoundingClientRect();
          try {
            for (const lv of bloomLevels) {
              const tmp  = document.createElement('canvas');
              tmp.width  = out.width; tmp.height = out.height;
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
    const pad      = Math.round(out.height * 0.055);
    const fontSize = Math.round(out.height * 0.026);
    const xShift   = Math.round(out.width  * 0.018);

    ctx.globalCompositeOperation = 'difference';
    ctx.fillStyle    = '#ffffff';
    ctx.textBaseline = 'bottom';
    const y = out.height - pad;

    function drawLabel(text, x, align, italic, weight, tracking) {
      ctx.textAlign     = align;
      ctx.letterSpacing = tracking || '0.08em';
      ctx.font = `${italic ? 'italic ' : ''}${weight} ${fontSize}px LinotypeUnivers, sans-serif`;
      ctx.fillText(text, x, y);
      return ctx.measureText(text).width;
    }

    const label = window.PRINT_LABEL;
    if (label && label.artist && label.song && label.year) {
      const prefix = label.artist + ' \u2014 ';
      const suffix = ', ' + label.year;
      let x = pad + xShift;
      x += drawLabel(prefix,     x,            'left',  false, '900', '0.08em');
      x += drawLabel(label.song, x,            'left',  true,  '900', '0.08em');
             drawLabel(suffix,   x,            'left',  false, '900', '0.08em');
    }
    drawLabel('sabrinawu.me', out.width - pad, 'right', false, '400', '0.08em');

    ctx.letterSpacing = '0px';
    ctx.globalCompositeOperation = 'source-over';

    return out;
  }

  // ── PRINT PREVIEW OVERLAY (p = current mode, b = black mode) ───────────
  function showPrintPreview(modeOverride) {
    // Toggle off if already open
    const existing = document.getElementById('__print-preview-overlay');
    if (existing) { existing.remove(); return; }

    const out = buildPrintCanvas(modeOverride);
    if (!out) { console.warn('[print] buildPrintCanvas returned null'); return; }
    const mode = modeOverride || printMode;

    let dataURL;
    try {
      dataURL = out.toDataURL('image/png');
    } catch (e) {
      console.warn('[print] toDataURL failed (tainted canvas?):', e);
      return;
    }

    const overlay = document.createElement('div');
    overlay.id = '__print-preview-overlay';
    Object.assign(overlay.style, {
      position:       'fixed',
      inset:          '0',
      background:     'rgba(0,0,0,0.88)',
      zIndex:         '999998',
      display:        'flex',
      flexDirection:  'column',
      alignItems:     'center',
      justifyContent: 'center',
      gap:            '14px',
      cursor:         'pointer',
    });

    // Hint label
    const hint = document.createElement('div');
    Object.assign(hint.style, {
      fontFamily:    'LinotypeUnivers, sans-serif',
      fontSize:      '10px',
      letterSpacing: '0.18em',
      textTransform: 'uppercase',
      color:         'rgba(255,255,255,0.3)',
      userSelect:    'none',
      flexShrink:    '0',
    });
    hint.textContent = (mode === 'white' ? 'white' : 'black') + ' mode — click or esc to close';

    // Preview image — fills as much screen as possible
    const img = document.createElement('img');
    img.src = dataURL;
    Object.assign(img.style, {
      display:      'block',
      width:        '96vw',
      maxHeight:    '88vh',
      objectFit:    'contain',
      flexShrink:   '1',
      boxShadow:    '0 4px 80px rgba(0,0,0,1)',
      outline:      mode === 'white' ? '1px solid rgba(0,0,0,0.15)' : '1px solid rgba(255,255,255,0.05)',
    });

    overlay.appendChild(hint);
    overlay.appendChild(img);
    document.body.appendChild(overlay);

    function close() {
      overlay.remove();
      document.removeEventListener('keydown', onCloseKey);
    }
    function onCloseKey(e) {
      if (e.key === 'Escape' || e.code === 'KeyP') close();
    }
    overlay.addEventListener('click', close);
    document.addEventListener('keydown', onCloseKey);
  }

  // ── SCREEN CAPTURE + PRINT ────────────────────────────────────────────────
  function captureAndPrint() {
    console.log('[print] Triggered — capturing in ' + printMode + ' mode...');
    const out = buildPrintCanvas();
    if (!out) return;
    showNotification('printing…');
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

  // ── P → preview current mode  |  B → preview black mode ─────────────────
  document.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.code === 'KeyP') { e.preventDefault(); showPrintPreview(); }
    if (e.code === 'KeyB') { e.preventDefault(); showPrintPreview('black'); }
  });

  // ── INIT ───────────────────────────────────────────────────────────────────
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', startVoiceDetection);
  else startVoiceDetection();

})();
