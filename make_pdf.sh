#!/usr/bin/env bash

montage outputs/equipment/*.png -tile 3x3 -geometry 750x1050 -background white -density 300 outputs/equipment_montages/output.png

magick convert outputs/equipment_montages/*.png -gravity Center equipment.pdf

montage outputs/mechs/*.png -tile 3x3 -geometry 750x1050 -background white -density 300 outputs/mechs_montages/output.png

magick convert outputs/mechs_montages/*.png -gravity Center mechs.pdf
