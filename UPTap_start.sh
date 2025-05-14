#!/usr/bin/env bash
# ~/start-dev-windows.sh

# — adjust these paths —
DJANGO_DIR="$HOME/Desktop/UP-Tap"
FRONTEND_DIR="$HOME/Desktop/UP-Tap/frontend"
SCRIPT_DIR="$HOME/Desktop/UP-Tap/imx500"
SCRIPT_NAME="test_ui.py"

# 1) Django in window #1
lxterminal -e bash -c "
  cd $DJANGO_DIR &&
  source venv/bin/activate &&
  python manage.py runserver
" &

sleep 1  # let Django spin up

# 2) Frontend in window #2
lxterminal -e bash -c "
  cd $FRONTEND_DIR &&
  npm run dev
" &

sleep 1  # let frontend spin up

# 3) Python script in window #3
lxterminal -e bash -c "
  cd $SCRIPT_DIR &&
  source venv/bin/activate &&
  python $SCRIPT_NAME
" &

sleep 1  # small pause

# 4) Open browser to your front‑end
xdg-open http://localhost:3000
