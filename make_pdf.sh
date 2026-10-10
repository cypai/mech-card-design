#!/usr/bin/env bash

for i in "$@"; do
  if [ "$i" == "equipment" ]; then
    echo "Generating equipment PDF"
    montage outputs/equipment/*.png -tile 3x3 -geometry 1500x2100 -background white -density 600 outputs/equipment_montages/output.png
    magick outputs/equipment_montages/*.png -gravity Center equipment.pdf
  fi
  if [ "$i" == "mechs" ]; then
    echo "Generating mechs PDF"
    montage outputs/mechs/*.png -rotate 90 -tile 1x1 -geometry 3300x4980 -background white -density 600 outputs/mechs_montages/output.png
    magick outputs/mechs_montages/*.png -units PixelsPerInch -density 600 -background white -gravity center -extent 4960x7016 mechs.pdf
  fi
  if [ "$i" == "mech-backs" ]; then
    echo "Generating mech_backs PDF"
    montage outputs/mech_backs/*.png -rotate 90 -tile 1x1 -geometry 3300x4980 -background white -density 600 outputs/mech_backs_montages/output.png
    magick outputs/mech_backs_montages/*.png -units PixelsPerInch -density 600 -background white -gravity center -extent 4960x7016 mech_backs.pdf
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
    rm -rf /tmp/maneuvers
    cp -r outputs/maneuvers /tmp/maneuvers
    # 7 copies of Airstrike (2 from the copies above + 5 extras)
    for n in 2 3 4 5 6; do
      cp outputs/maneuvers/airstrike.png /tmp/maneuvers/airstrike$n.png
    done
    montage outputs/maneuvers/*.png /tmp/maneuvers/*.png -tile 3x3 -geometry 1500x2100 -background white -density 600 outputs/maneuvers_montages/output.png
    magick outputs/maneuvers_montages/*.png -gravity Center maneuvers.pdf
  fi
  if [ "$i" == "changed" ]; then
    echo "Generating changed PDFs"
    mkdir -p outputs/changed_montages
    rm -f outputs/changed_montages/*.png
    # Split changed renders into cards (1500x2100) and mechs/mech backs (4980x3300) by size
    changed_cards=()
    changed_mechs=()
    for f in outputs/changed/*.png; do
      w=$(identify -format "%w" "$f")
      if [ "$w" == "1500" ]; then
        changed_cards+=("$f")
      else
        changed_mechs+=("$f")
      fi
    done
    if [ ${#changed_cards[@]} -gt 0 ]; then
      montage "${changed_cards[@]}" -tile 3x3 -geometry 1500x2100 -background white -density 600 outputs/changed_montages/changed_cards.png
      if ls outputs/changed_montages/changed_cards-*.png >/dev/null 2>&1; then
        magick outputs/changed_montages/changed_cards-*.png -gravity Center changed_cards.pdf
      else
        echo "ERROR: montage did not create outputs/changed_montages/changed_cards-*.png" >&2
      fi
    fi
    if [ ${#changed_mechs[@]} -gt 0 ]; then
      montage "${changed_mechs[@]}" -rotate 90 -tile 1x1 -geometry 3300x4980 -background white -density 600 outputs/changed_montages/changed_mechs.png
      if ls outputs/changed_montages/changed_mechs-*.png >/dev/null 2>&1; then
        magick outputs/changed_montages/changed_mechs-*.png -units PixelsPerInch -density 600 -background white -gravity center -extent 4960x7016 changed_mechs.pdf
      else
        echo "ERROR: montage did not create outputs/changed_montages/changed_mechs-*.png" >&2
      fi
    fi
  fi
  if [ "$i" == "tokens" ]; then
    echo "Generating tokens PDF"
    # card_rendering.py already renders the amount of copies each token asks for
    montage outputs/tokens/*_front.png outputs/tokens/*_back.png -tile 10x7 -geometry 430x430 -background white -density 600 outputs/tokens_montages/tokens.png
    magick outputs/tokens_montages/*.png -units PixelsPerInch -density 600 -background white -gravity Center tokens.pdf
  fi
  if [ "$i" == "references" ]; then
    echo "Generating references PDF"
    cp -r outputs/references /tmp/references
    montage outputs/references/*.png /tmp/references/*.png -tile 3x3 -geometry 1500x2100 -background white -density 600 /tmp/references.png
    magick /tmp/references.png -gravity Center references.pdf
  fi
done
