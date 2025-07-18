#!/usr/bin/env bash

for i in "$@"; do
  if [ "$i" == "equipment" ]; then
    echo "Generating equipment PDF"
    montage outputs/equipment/*.png -tile 3x3 -geometry 750x1050 -background white -density 300 outputs/equipment_montages/output.png
    magick convert outputs/equipment_montages/*.png -gravity Center equipment.pdf
  fi
  if [ "$i" == "mechs" ]; then
    echo "Generating mechs PDF"
    montage outputs/mechs/*.png -tile 3x3 -geometry 750x1050 -background white -density 300 outputs/mechs_montages/output.png
    magick convert outputs/mechs_montages/*.png -gravity Center mechs.pdf
  fi
  if [ "$i" == "drones" ]; then
    echo "Generating drones PDF"
    montage outputs/mechs/*drone*.png -tile 3x3 -geometry 750x1050 -background white -density 300 outputs/drones_montages/output.png
    magick convert outputs/drones_montages/*.png -gravity Center drones.pdf
  fi
  if [ "$i" == "maneuvers" ]; then
    echo "Generating maneuvers PDF"
    montage outputs/maneuvers/*.png -tile 3x3 -geometry 750x1050 -background white -density 300 outputs/maneuvers_montages/output.png
    magick convert outputs/maneuvers_montages/*.png -gravity Center maneuvers.pdf
  fi
done
