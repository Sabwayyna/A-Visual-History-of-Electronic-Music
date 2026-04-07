// print-server.js
// Run with: node print-server.js
// Listens on http://localhost:3001/print
// Accepts a PNG image blob via POST, resizes to 4×6 label, prints via lp

const http     = require('http');
const { execFile } = require('child_process');
const fs       = require('fs');
const os       = require('os');
const path     = require('path');

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
