#!/usr/bin/env bash

./clear_outputs.sh mechs equipment drones maneuvers
./run_mechs.py generate
./run_equipment.py generate
./run_maneuvers.py generate
./make_pdf.sh mechs equipment drones maneuvers
