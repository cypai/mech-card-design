#!/usr/bin/env bash

montage outputs/equipment/*.png -tile 3x3 -geometry 750x1050 -background white -density 300 outputs/montages/output.png

magick convert outputs/montages/*.png -gravity Center outputs/montages/output.pdf
