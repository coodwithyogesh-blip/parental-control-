#!/data/data/com.termux/files/usr/bin/bash
set -e
pkg update -y
pkg upgrade -y
pkg install python termux-api -y
python -m pip install -r requirements.txt
cp -n config.example.py config.py || true
echo "Setup complete. Edit config.py, then run: python bot.py"
