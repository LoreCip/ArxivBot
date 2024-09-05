#!/bin/bash

RESULT_DIR="/path/to/Arxiv_Daily"
TODAY=$(date +%Y_%m_%d)
FILENAME="${RESULT_DIR}/${TODAY}_Arxiv.txt"

# Check if today is Saturday (6) or Sunday (7)
DAY_OF_WEEK=$(date +%u)

if [ "$DAY_OF_WEEK" -ge 6 ]; then\
  exit 0
fi

if [ -f "$FILENAME" ]; then
  exit 0
fi

# Check if today is the first day of the month
DAY_OF_MONTH=$(date +%d)

if { [ "$DAY_OF_MONTH" -eq 1 ] && [ "$DAY_OF_WEEK" -lt 6 ]; } || \
   { [ "$DAY_OF_MONTH" -eq 2 ] && [ "$(date -d 'yesterday' +%u)" -ge 6 ]; } || \
   { [ "$DAY_OF_MONTH" -eq 3 ] && [ "$(date -d '2 days ago' +%u)" -ge 6 ] && [ "$(date -d 'yesterday' +%u)" -ge 6 ]; }; then

  # Get the previous month and year
  PREVIOUS_MONTH=$(date -d '1 month ago' +%Y_%m)

  # Create the previous month directory if it doesn't exist
  PREVIOUS_MONTH_DIR="${RESULT_DIR}/${PREVIOUS_MONTH}"
  if [ ! -d "$PREVIOUS_MONTH_DIR" ]; then
    mkdir -p "$PREVIOUS_MONTH_DIR"
  fi

  # Move all files from the previous month to the directory
  find "$RESULT_DIR" -maxdepth 1 -type f -name "${PREVIOUS_MONTH}_*_Arxiv.txt" -exec mv {} "$PREVIOUS_MONTH_DIR" \;
fi

python ./check_arxiv.py
