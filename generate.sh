#!/usr/bin/env bash

mkdir -p outputs/equipment
mkdir -p outputs/equipment_montages
mkdir -p outputs/mechs
mkdir -p outputs/mechs_montages
mkdir -p outputs/drones
mkdir -p outputs/drones_montages
mkdir -p outputs/maneuvers
mkdir -p outputs/maneuvers_montages
mkdir -p outputs/changed
mkdir -p outputs/changed_montages

for i in "$@"; do
  if [ "$i" == "all" ]; then
    ./clear_outputs.sh mechs equipment drones maneuvers changed
    ./run_mechs.py generate
    ./run_drones.py generate
    ./run_equipment.py generate
    ./run_maneuvers.py generate
    ./run_changelog.py montage
    ./make_pdf.sh mechs equipment drones maneuvers changed
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
    ./run_drones.py generate
    ./make_pdf.sh drones
  fi
  if [ "$i" == "maneuvers" ]; then
    ./clear_outputs.sh maneuvers
    ./run_maneuvers.py generate
    ./make_pdf.sh maneuvers
  fi
  if [ "$i" == "changed" ]; then
    ./clear_outputs.sh changed
    ./run_changelog.py montage
    ./make_pdf.sh changed
  fi
done
