// print-server.js
// Run with: node print-server.js
// Port 3001 → POST /print   (receives PNG, resizes, prints)
// Port 8080 → static files  (serve thesis from localhost so Chrome allows mic)
// Open: http://localhost:8080/index.html  (or 8081 if 8080 is taken)

const http     = require('http');
const { execFile } = require('child_process');
const fs       = require('fs');
const os       = require('os');
const path     = require('path');

// ── STATIC FILE SERVER (port 8080) ────────────────────────────────────────────
const STATIC_PORT = 8081;
const STATIC_ROOT = __dirname; // serve from the same folder as this script

const MIME = {
  '.html': 'text/html',
  '.js':   'application/javascript',
  '.css':  'text/css',
  '.json': 'application/json',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif':  'image/gif',
  '.svg':  'image/svg+xml',
  '.mp3':  'audio/mpeg',
  '.mp4':  'video/mp4',
  '.otf':  'font/otf',
  '.ttf':  'font/ttf',
  '.woff': 'font/woff',
  '.woff2':'font/woff2',
  '.ico':  'image/x-icon',
};

const staticServer = http.createServer((req, res) => {
  let urlPath = req.url.split('?')[0];
  if (urlPath === '/') urlPath = '/index.html';
  const filePath = path.join(STATIC_ROOT, urlPath);

  if (!filePath.startsWith(STATIC_ROOT)) {
    res.writeHead(403); res.end('Forbidden'); return;
  }

  fs.stat(filePath, (err, stat) => {
    if (err) { res.writeHead(404); res.end('Not found'); return; }

    const ext      = path.extname(filePath).toLowerCase();
    const mime     = MIME[ext] || 'application/octet-stream';
    const total    = stat.size;
    const rangeHdr = req.headers['range'];

    if (rangeHdr) {
      // Partial content — required for audio/video streaming
      const [startStr, endStr] = rangeHdr.replace('bytes=', '').split('-');
      const start = parseInt(startStr, 10);
      const end   = endStr ? parseInt(endStr, 10) : total - 1;
      const chunkSize = end - start + 1;
      res.writeHead(206, {
        'Content-Range':  `bytes ${start}-${end}/${total}`,
        'Accept-Ranges':  'bytes',
        'Content-Length': chunkSize,
        'Content-Type':   mime,
      });
      fs.createReadStream(filePath, { start, end }).pipe(res);
    } else {
      res.writeHead(200, {
        'Content-Length': total,
        'Content-Type':   mime,
        'Accept-Ranges':  'bytes',
      });
      fs.createReadStream(filePath).pipe(res);
    }
  });
});

staticServer.listen(STATIC_PORT, () => {
  console.log(`Static server  → http://localhost:${STATIC_PORT}/index.html`);
  console.log(`Song pages     → http://localhost:${STATIC_PORT}/songs/<name>.html`);
});

const PORT    = 3001;
const PRINTER = '_RP425_ZPL_203DPI_';

// 4×6 inch label at 203 DPI — landscape (6 wide × 4 tall)
const LABEL_W = 1218;
const LABEL_H = 812;

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }
  if (req.method !== 'POST' || req.url !== '/print') {
    res.writeHead(404); res.end('Not found'); return;
  }

  const chunks = [];
  req.on('data', chunk => chunks.push(chunk));
  req.on('end', () => {
    const imageBuffer = Buffer.concat(chunks);
    const stamp  = Date.now();
    const tmpPng = path.join(os.tmpdir(), `print-${stamp}.png`);
    const tmpPdf = path.join(os.tmpdir(), `print-${stamp}.pdf`);

    fs.writeFile(tmpPng, imageBuffer, err => {
      if (err) { console.error('Write error:', err); res.writeHead(500); res.end('Write error'); return; }

      // Step 1: resize PNG to label dimensions
      execFile('sips', [
        '--resampleHeightWidth', String(LABEL_H), String(LABEL_W),
        tmpPng, '--out', tmpPng
      ], (err, _so, stderr) => {
        if (err) { console.error('sips resize error:', stderr); }

        // Step 2: convert PNG → PDF (CUPS handles PDF → ZPL reliably)
        execFile('sips', [
          '-s', 'format', 'pdf',
          tmpPng, '--out', tmpPdf
        ], (err, _so, stderr) => {
          fs.unlink(tmpPng, () => {});
          if (err) {
            console.error('sips pdf error:', stderr);
            res.writeHead(500); res.end('PDF convert error'); return;
          }

          // Step 3: send PDF to printer
          execFile('lp', [
            '-d', PRINTER,
            '-o', 'fit-to-page',
            '-o', 'landscape',
            tmpPdf
          ], (err, stdout, stderr) => {
            fs.unlink(tmpPdf, () => {});
            if (err) { console.error('Print error:', stderr); res.writeHead(500); res.end('Print error'); return; }
            console.log('Printed:', stdout.trim());
            res.writeHead(200); res.end('OK');
          });
        });
      });
    });
  });
});

server.listen(PORT, () => {
  console.log(`Print server running on http://localhost:${PORT}/print`);
  console.log(`Printer: ${PRINTER} — label: ${LABEL_W}×${LABEL_H}px (4×6 in @ 203 DPI)`);
});
