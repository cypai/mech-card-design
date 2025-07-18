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
    if [ -n "$(ls -A outputs/drones_montages)" ]; then
      rm outputs/drones_montages/*
    fi
  fi
  if [ "$i" == "drones" ]; then
    echo "Clearing drones"
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
done
