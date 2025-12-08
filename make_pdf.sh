#!/usr/bin/env bash

for i in "$@"; do
  if [ "$i" == "equipment" ]; then
    echo "Generating equipment PDF"
    montage outputs/equipment/*.png -tile 3x3 -geometry 1500x2100 -background white -density 600 outputs/equipment_montages/output.png
    magick outputs/equipment_montages/*.png -gravity Center equipment.pdf
  fi
  if [ "$i" == "mechs" ]; then
    echo "Generating mechs PDF"
    montage outputs/mechs/*.png -tile 3x3 -geometry 1500x2100 -background white -density 600 outputs/mechs_montages/output.png
    magick outputs/mechs_montages/*.png -gravity Center mechs.pdf
  fi
  if [ "$i" == "drones" ]; then
    echo "Generating drones PDF"
    rm -rf /tmp/drones
    cp -r outputs/drones /tmp/drones
    montage outputs/drones/*.png /tmp/drones/*.png -tile 3x3 -geometry 1500x2100 -background white -density 600 outputs/drones_montages/output.png
    magick outputs/drones_montages/*.png -gravity Center drones.pdf
  fi
  if [ "$i" == "maneuvers" ]; then
    echo "Generating maneuvers PDF"
    montage outputs/maneuvers/*.png -tile 3x3 -geometry 1500x2100 -background white -density 600 outputs/maneuvers_montages/output.png
    magick outputs/maneuvers_montages/*.png -gravity Center maneuvers.pdf
  fi
  if [ "$i" == "changed" ]; then
    echo "Generating changed PDF"
    montage outputs/changed/*.png -tile 3x3 -geometry 1500x2100 -background white -density 600 outputs/changed_montages/output.png
    magick outputs/changed_montages/*.png -gravity Center changed.pdf
  fi
  if [ "$i" == "references" ]; then
    echo "Generating references PDF"
    cp -r outputs/references /tmp/references
    montage outputs/references/*.png /tmp/references/*.png -tile 3x3 -geometry 1500x2100 -background white -density 600 /tmp/references.png
    magick /tmp/references.png -gravity Center references.pdf
  fi
done
