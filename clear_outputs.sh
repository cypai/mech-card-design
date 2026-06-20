#!/usr/bin/env bash

for i in "$@"; do
  if [ "$i" == "equipment" ]; then
    echo "Clearing equipment"
    if [ -n "$(ls -A outputs/equipment)" ]; then
      rm outputs/equipment/*
    fi
    if [ -n "$(ls -A outputs/equipment_montages)" ]; then
      rm outputs/equipment_montages/*
    fi
  fi
  if [ "$i" == "mechs" ]; then
    echo "Clearing mechs"
    if [ -n "$(ls -A outputs/mechs)" ]; then
      rm outputs/mechs/*
    fi
    if [ -n "$(ls -A outputs/mechs_montages)" ]; then
      rm outputs/mechs_montages/*
    fi
  fi
  if [ "$i" == "mech-backs" ]; then
    echo "Clearing mech-backs"
    if [ -n "$(ls -A outputs/mech_backs)" ]; then
      rm outputs/mech_backs/*
    fi
    if [ -n "$(ls -A outputs/mech_backs_montages)" ]; then
      rm outputs/mech_backs_montages/*
    fi
  fi
  if [ "$i" == "drones" ]; then
    echo "Clearing drones"
    if [ -n "$(ls -A outputs/drones)" ]; then
      rm outputs/drones/*
    fi
    if [ -n "$(ls -A outputs/drones_montages)" ]; then
      rm outputs/drones_montages/*
    fi
  fi
  if [ "$i" == "maneuvers" ]; then
    echo "Clearing maneuvers"
    if [ -n "$(ls -A outputs/maneuvers)" ]; then
      rm outputs/maneuvers/*
    fi
    if [ -n "$(ls -A outputs/maneuvers_montages)" ]; then
      rm outputs/maneuvers_montages/*
    fi
  fi
  if [ "$i" == "changed" ]; then
    echo "Clearing changed"
    if [ -n "$(ls -A outputs/changed)" ]; then
      rm outputs/changed/*
    fi
    if [ -n "$(ls -A outputs/changed_montages)" ]; then
      rm outputs/changed_montages/*
    fi
  fi
  if [ "$i" == "references" ]; then
    echo "Clearing references"
    if [ -n "$(ls -A outputs/references)" ]; then
      rm outputs/references/*
    fi
  fi
done
