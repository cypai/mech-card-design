#!/usr/bin/env python3

import argparse
import shutil

from game_defs import *
from game_data import *
from lib import *

db = GameDatabase()
prev_db = GameDatabase(changelog=True)


def generate_changelog_text():
    changelog = ""
    for mech in prev_db.mechs:
        curr_mech = next((m for m in db.mechs if m.name == mech.name), None)
        if curr_mech is None:
            changelog += f"{mech.name} was deleted.\n"
            changelog += str(mech) + "\n"
    for mech in db.mechs:
        prev_mech = next((m for m in prev_db.mechs if m.name == mech.name), None)
        if prev_mech is None:
            changelog += f"{mech.name} was added.\n"
            changelog += str(mech) + "\n"
        else:
            is_diff, diff_str = mech.diff(prev_mech)
            if is_diff:
                changelog += f"{diff_str}\n"

    for equipment in prev_db.equipment:
        curr_equipment = next(
            (m for m in db.equipment if m.name == equipment.name), None
        )
        if curr_equipment is None:
            changelog += f"{equipment.name} was deleted.\n"
            changelog += str(equipment) + "\n"
    for equipment in db.equipment:
        prev_equipment = next(
            (m for m in prev_db.equipment if m.name == equipment.name), None
        )
        if prev_equipment is None:
            changelog += f"{equipment.name} was added.\n"
            changelog += str(equipment) + "\n"
        else:
            is_diff, diff_str = equipment.diff(prev_equipment)
            if is_diff:
                changelog += f"{diff_str}\n"

    for drone in prev_db.drones:
        curr_drone = next((m for m in db.drones if m.name == drone.name), None)
        if curr_drone is None:
            changelog += f"{drone.name} was deleted.\n"
            changelog += str(drone) + "\n"
    for drone in db.drones:
        prev_drone = next((m for m in prev_db.drones if m.name == drone.name), None)
        if prev_drone is None:
            changelog += f"{drone.name} was added.\n"
            changelog += str(drone) + "\n"
        else:
            is_diff, diff_str = drone.diff(prev_drone)
            if is_diff:
                changelog += f"{diff_str}\n"

    for maneuver in prev_db.maneuvers:
        curr_maneuver = next((m for m in db.maneuvers if m.name == maneuver.name), None)
        if curr_maneuver is None:
            changelog += f"{maneuver.name} was deleted.\n"
            changelog += str(maneuver) + "\n"
    for maneuver in db.maneuvers:
        prev_maneuver = next(
            (m for m in prev_db.maneuvers if m.name == maneuver.name), None
        )
        if prev_maneuver is None:
            changelog += f"{maneuver.name} was added.\n"
            changelog += str(maneuver) + "\n"
        else:
            is_diff, diff_str = maneuver.diff(prev_maneuver)
            if is_diff:
                changelog += f"{diff_str}\n"

    if len(changelog) == 0:
        changelog = "No changes."

    return changelog


def append_to_changelog(message):
    with open("./changelog/changelog.txt", "r") as f:
        previous_data = f.read()
    with open("./changelog/changelog.txt", "w") as f:
        f.write(f"{message}\n")
        underline = "-" * len(message) + "\n\n"
        f.write(underline)
        f.write(generate_changelog_text())
        f.write("\n\n")
        f.write(previous_data)


def copy_current():
    shutil.copyfile("./data/mechs.yml", "./changelog/previous_mechs.yml")
    shutil.copyfile("./data/drones.yml", "./changelog/previous_drones.yml")
    shutil.copyfile("./data/equipment.yml", "./changelog/previous_equipment.yml")
    shutil.copyfile("./data/maneuvers.yml", "./changelog/previous_maneuvers.yml")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action")
    parser.add_argument("--message", "-m")
    args = parser.parse_args()
    if args.action == "init":
        copy_current()
    elif args.action == "sync":
        append_to_changelog(args.message)
        copy_current()
    elif args.action == "preview":
        print(generate_changelog_text())


if __name__ == "__main__":
    main()
