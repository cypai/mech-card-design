#!/usr/bin/env python3

import argparse
import shutil
import os
from typing import TypeVar

from game_defs import *
from game_data import *
from lib import *

db = GameDatabase()
prev_db = GameDatabase(changelog=True)

T = TypeVar("T", Mech, Drone, Equipment, Maneuver)


class Changelog:
    def __init__(
        self,
        added: list[T],
        deleted: list[T],
        renamed: list[T],
        changed: list[T],
        text: str,
    ):
        self.added = added
        self.deleted = deleted
        self.renamed = renamed
        self.changed = changed
        self.text = text


def generate_changelog_text() -> str:
    mech_changelog = generate_changelog_for(db.mechs, prev_db.mechs)
    equipment_changelog = generate_changelog_for(db.equipment, prev_db.equipment)
    drone_changelog = generate_changelog_for(db.drones, prev_db.drones)
    maneuver_changelog = generate_changelog_for(db.maneuvers, prev_db.maneuvers)
    text_changelog = (
        mech_changelog.text
        + equipment_changelog.text
        + drone_changelog.text
        + maneuver_changelog.text
    )

    if len(text_changelog) == 0:
        text_changelog = "No changes."

    return text_changelog


def generate_changelog_for(
    current_list: list[T],
    previous_list: list[T],
) -> Changelog:
    changelog = ""
    deleted_items = []
    added_items = []
    actually_added = []
    actually_deleted = []
    renamed = []
    changed = []
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
                changed.append(item)
    for item in added_items:
        similar_item = next((m for m in deleted_items if item.is_similar(m)), None)
        if similar_item is None:
            changelog += f"{item.name} was added.\n"
            changelog += str(item) + "\n"
            actually_added.append(item)
        else:
            deleted_items.remove(similar_item)
            _, diff_str = item.diff(similar_item)
            changelog += f"{diff_str}\n"
            renamed.append(item)
    for item in deleted_items:
        changelog += f"{item.name} was deleted.\n"
        changelog += str(item) + "\n"
        actually_deleted.append(item)
    return Changelog(actually_added, actually_deleted, renamed, changed, changelog)


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


def create_montage_directory():
    os.makedirs("./outputs/changed/", exist_ok=True)
    mech_changelog = generate_changelog_for(db.mechs, prev_db.mechs)
    equipment_changelog = generate_changelog_for(db.equipment, prev_db.equipment)
    drone_changelog = generate_changelog_for(db.drones, prev_db.drones)
    maneuver_changelog = generate_changelog_for(db.maneuvers, prev_db.maneuvers)
    for changelog in [
        mech_changelog,
        equipment_changelog,
        drone_changelog,
        maneuver_changelog,
    ]:
        for item in changelog.added + changelog.renamed + changelog.changed:
            for i in range(item.copies):
                shutil.copyfile(
                    item.filename, f"./outputs/changed/{item.normalized_name}_{i}.png"
                )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action")
    parser.add_argument("--message", "-m")
    args = parser.parse_args()
    if args.action == "init":
        copy_current()
    elif args.action == "sync":
        if not args.message:
            print("sync -m message is required.")
            return
        append_to_changelog(args.message)
        copy_current()
    elif args.action == "preview":
        print(generate_changelog_text())
    elif args.action == "montage":
        print("Copying changed cards into changed directory")
        create_montage_directory()


if __name__ == "__main__":
    main()
