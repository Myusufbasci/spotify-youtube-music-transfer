#!/usr/bin/env bash
cd "$(dirname "$0")"

echo "========================================================"
echo "  Spotify <-> YouTube Music Transfer"
echo "========================================================"

if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 is not installed. Please install Python 3 from https://www.python.org/downloads/"
    read -p "Press Enter to exit..."
    exit 1
fi

if ! python3 -c "import flask, ytmusicapi, rapidfuzz, bs4, playwright" &> /dev/null; then
    echo "[*] Installing required packages (first-time setup)..."
    python3 -m pip install --user -r requirements.txt
fi

echo "[*] Starting Web Interface at http://127.0.0.1:5050 ..."
python3 app.py --web --open --port 5050
