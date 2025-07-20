#!/usr/bin/env bash

for i in "$@"; do
  if [ "$i" == "all" ]; then
    ./clear_outputs.sh mechs equipment drones maneuvers
    ./run_mechs.py generate
    ./run_equipment.py generate
    ./run_maneuvers.py generate
    ./make_pdf.sh mechs equipment drones maneuvers
  fi
  if [ "$i" == "mechs" ]; then
    ./clear_outputs.sh mechs
    ./run_mechs.py generate
    ./make_pdf.sh mechs
  fi
  if [ "$i" == "equipment" ]; then
    ./clear_outputs.sh equipment
    ./run_equipment.py generate
    ./make_pdf.sh equipment
  fi
  if [ "$i" == "drones" ]; then
    ./clear_outputs.sh drones
    ./run_mechs.py generate
    ./make_pdf.sh drones
  fi
  if [ "$i" == "maneuvers" ]; then
    ./clear_outputs.sh maneuvers
    ./run_maneuvers.py generate
    ./make_pdf.sh maneuvers
  fi
done
