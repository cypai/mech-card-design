#!/usr/bin/env bash

montage outputs/mechs/*drone*.png -tile 3x3 -geometry 750x1050 -background white -density 300 outputs/drones_montages/output.png

magick convert outputs/drones_montages/*.png -gravity Center drones.pdf
