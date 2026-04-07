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
        letterSpacing:  '0.08em',
        color:          '#fff',
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

    if (canvases.length === 0) {
      console.warn('[print] No canvases found.');
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
      // Black background, white visuals (original)
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, out.width, out.height);
      ctx.filter = 'contrast(1.8) brightness(1.4)';
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

    // Imprint: bottom corners in project font
    const pad      = Math.round(out.height * 0.055);
    const fontSize = Math.round(out.height * 0.022);
    const textColor = printMode === 'white' ? '#000' : '#fff';
    ctx.fillStyle    = textColor;
    ctx.textBaseline = 'bottom';
    const y = out.height - pad;

    // Bottom left: "Artist — Song (italic), Year" using window.PRINT_LABEL
    const label = window.PRINT_LABEL;
    if (label && label.artist && label.song && label.year) {
      const prefix = label.artist + ' \u2014 ';
      const suffix = ', ' + label.year;
      ctx.textAlign = 'left';
      ctx.font = `${fontSize}px LinotypeUnivers, sans-serif`;
      ctx.fillText(prefix, pad, y);
      const prefixW = ctx.measureText(prefix).width;
      ctx.font = `italic ${fontSize}px LinotypeUnivers, sans-serif`;
      ctx.fillText(label.song, pad + prefixW, y);
      const songW = ctx.measureText(label.song).width;
      ctx.font = `${fontSize}px LinotypeUnivers, sans-serif`;
      ctx.fillText(suffix, pad + prefixW + songW, y);
    }

    // Bottom right: website
    ctx.textAlign = 'right';
    ctx.font = `${fontSize}px LinotypeUnivers, sans-serif`;
    ctx.fillText('sabrinawu.me', out.width - pad, y);

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
