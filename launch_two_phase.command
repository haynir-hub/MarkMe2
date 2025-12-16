#!/bin/bash
# Two-Phase Tracking UI Launcher
# הפעלת ממשק המעקב הדו-שלבי

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to that directory
cd "$DIR"

# Run the test UI
python3 test_new_ui.py

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo ""
    echo "Press any key to close..."
    read -n 1
fi
