#!/usr/bin/env bash

mkdir -p outputs/equipment
mkdir -p outputs/equipment_montages
mkdir -p outputs/mechs
mkdir -p outputs/mechs_montages
mkdir -p outputs/mech_backs
mkdir -p outputs/mech_backs_montages
mkdir -p outputs/drones
mkdir -p outputs/drones_montages
mkdir -p outputs/maneuvers
mkdir -p outputs/maneuvers_montages
mkdir -p outputs/changed
mkdir -p outputs/changed_montages
mkdir -p outputs/tokens
mkdir -p outputs/tokens_montages

for i in "$@"; do
  if [ "$i" == "all" ]; then
    ./clear_outputs.sh mechs equipment drones maneuvers changed
    ./card_rendering.py all
    ./run_changelog.py montage
    ./make_pdf.sh mechs equipment drones maneuvers changed
  fi
  if [ "$i" == "mechs" ]; then
    ./clear_outputs.sh mechs
    ./card_rendering.py mechs
    ./make_pdf.sh mechs
  fi
  if [ "$i" == "mech-backs" ]; then
    ./clear_outputs.sh mech-backs
    ./card_rendering.py mech-backs
    ./make_pdf.sh mech-backs
  fi
  if [ "$i" == "equipment" ]; then
    ./clear_outputs.sh equipment
    ./card_rendering.py equipment
    ./make_pdf.sh equipment
  fi
  if [ "$i" == "drones" ]; then
    ./clear_outputs.sh drones
    ./card_rendering.py drones
    ./make_pdf.sh drones
  fi
  if [ "$i" == "maneuvers" ]; then
    ./clear_outputs.sh maneuvers
    ./card_rendering.py maneuvers
    ./make_pdf.sh maneuvers
  fi
  if [ "$i" == "tokens" ]; then
    ./clear_outputs.sh tokens
    ./card_rendering.py tokens
    ./make_pdf.sh tokens
  fi
  if [ "$i" == "changed" ]; then
    ./clear_outputs.sh changed
    ./run_changelog.py montage
    ./make_pdf.sh changed
  fi
  if [ "$i" == "references" ]; then
    ./clear_outputs.sh references
    ./card_rendering.py references
    ./make_pdf.sh references
  fi
  if [ "$i" == "pngs" ]; then
    ./clear_outputs.sh mechs equipment drones maneuvers
    ./card_rendering.py all
  fi
  if [ "$i" == "mech-pngs" ]; then
    ./clear_outputs.sh mechs
    ./card_rendering.py mechs
  fi
  if [ "$i" == "mech-back-pngs" ]; then
    ./clear_outputs.sh mech_backs
    ./card_rendering.py mech_backs
  fi
  if [ "$i" == "equipment-pngs" ]; then
    ./clear_outputs.sh equipment
    ./card_rendering.py equipment
  fi
  if [ "$i" == "maneuver-pngs" ]; then
    ./clear_outputs.sh maneuvers
    ./card_rendering.py maneuvers
  fi
  if [ "$i" == "drone-pngs" ]; then
    ./clear_outputs.sh drones
    ./card_rendering.py drones
  fi
  if [ "$i" == "token-pngs" ]; then
    ./clear_outputs.sh tokens
    ./card_rendering.py tokens
  fi
done
