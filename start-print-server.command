#!/bin/bash
cd "$(dirname "$0")"
echo "Starting print server..."
echo "Printer: _RP425_ZPL_203DPI_"
echo "Listening on http://localhost:3001/print"
echo "----------------------------------------"
node print-server.js
