#!/bin/bash

usage() {
  echo "usage: $(basename $0) <screenshots directory>"
  echo ""
  echo "This script simply takes your screenshots directory, and creates"
  echo "the inverted PNG version of the png file"
}

if [ -z "$1" ]; then
  usage
  exit 1
fi

SRC_DIRECTORY="$1"
PNG_TO_CONVERT=$(find "$SRC_DIRECTORY" -type f -name '*.png' -and -not -name '*.inv.png')

while read png; do
  echo "[*] inverting '$png'"
  convert "$png" -channel RGB -negate "$png.inv.png"
done <<< $PNG_TO_CONVERT

