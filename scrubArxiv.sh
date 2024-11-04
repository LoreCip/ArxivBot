#!/bin/bash

RESULT_DIR="/home/lorenzo/Desktop/Arxiv_Daily"
TODAY=$(date +%Y_%m_%d)
FILENAME="${RESULT_DIR}/${TODAY}_Arxiv.txt"

# Check if today is Saturday (6) or Sunday (7)
DAY_OF_WEEK=$(date +%u)

if [ "$DAY_OF_WEEK" -ge 6 ]; then
  exit 0
fi

if [ -f "$FILENAME" ]; then
  exit 0
fi

MOST_RECENT_FILE=$(ls -1 "${RESULT_DIR}"/*_Arxiv.txt 2>/dev/null | sort -V | tail -n 1)
PREVIOUS_MONTH=$(basename "$MOST_RECENT_FILE" | cut -d'_' -f1,2)
CURRENT_MONTH=$(date +%Y_%m)

if [ "$CURRENT_MONTH" != "$PREVIOUS_MONTH" ]; then
  # Create the previous month directory if it doesn't exist
  PREVIOUS_MONTH_DIR="${RESULT_DIR}/${PREVIOUS_MONTH}"
  if [ ! -d "$PREVIOUS_MONTH_DIR" ]; then
    mkdir -p "$PREVIOUS_MONTH_DIR"
  fi

  # Move all files from the previous month to the directory
  find "$RESULT_DIR" -maxdepth 1 -type f -name "${PREVIOUS_MONTH}_*_Arxiv.txt" -exec mv {} "$PREVIOUS_MONTH_DIR" \;
fi

python3 /home/lorenzo/phd/VariousCodes/ArxivBot/check_arxiv.py
