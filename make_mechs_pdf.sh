#!/usr/bin/env bash

montage outputs/mechs/*.png -tile 3x3 -geometry 750x1050 -background white -density 300 outputs/mechs_montages/output.png

magick convert outputs/mechs_montages/*.png -gravity Center mechs.pdf
