#!/usr/bin/env python3

import argparse
import shutil
from typing import TypeVar, Union

from game_defs import *
from game_data import *
from lib import *

db = GameDatabase()
prev_db = GameDatabase(changelog=True)

T = TypeVar("T", Mech, Drone, Equipment, Maneuver)


def generate_changelog_text() -> str:
    changelog = ""
    changelog += generate_changelog_text_for(db.mechs, prev_db.mechs)
    changelog += generate_changelog_text_for(db.equipment, prev_db.equipment)
    changelog += generate_changelog_text_for(db.drones, prev_db.drones)
    changelog += generate_changelog_text_for(db.maneuvers, prev_db.maneuvers)

    if len(changelog) == 0:
        changelog = "No changes."

    return changelog


def generate_changelog_text_for(
    current_list: list[T],
    previous_list: list[T],
) -> str:
    changelog = ""
    deleted_items = []
    added_items = []
    for item in previous_list:
        current = next((x for x in current_list if x.name == item.name), None)
        if current is None:
            deleted_items.append(item)
    for item in current_list:
        prev_item = next((x for x in previous_list if x.name == item.name), None)
        if prev_item is None:
            added_items.append(item)
        else:
            is_diff, diff_str = item.diff(prev_item)
            if is_diff:
                changelog += f"{diff_str}\n"
    for item in added_items:
        similar_item = next((m for m in deleted_items if item.is_similar(m)), None)
        if similar_item is None:
            changelog += f"{item.name} was added.\n"
            changelog += str(item) + "\n"
        else:
            deleted_items.remove(similar_item)
            _, diff_str = similar_item.diff(item)
            changelog += f"{diff_str}\n"
    for item in deleted_items:
        changelog += f"{item.name} was deleted.\n"
        changelog += str(item) + "\n"
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
