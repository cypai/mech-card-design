from game_defs import *
import yaml
import itertools
from thefuzz import fuzz
from typing import Union


def parse_equipment(equipment) -> Equipment:
    name, data = equipment
    return Equipment(
        name=name,
        size=data.get("size"),
        type=data.get("type"),
        system=data.get("system"),
        heat=data.get("heat", None),
        ammo=data.get("ammo", None),
        range=data.get("range", None),
        text=data.get("text"),
        tags=data.get("tags", []),
    )


def get_all_equipment() -> list[Equipment]:
    all_equipment = []
    with open("data/equipment.yml", "r") as equipment_file:
        data = yaml.safe_load(equipment_file)
        for item in data.items():
            all_equipment.append(parse_equipment(item))
    return all_equipment


def parse_mechs(mechs) -> Mech:
    name, data = mechs
    return Mech(
        name=name,
        faction=data.get("faction"),
        hp=data.get("hp"),
        armor=data.get("armor"),
        hc=data.get("hc"),
        hardpoints=data.get("hardpoints", []),
        ability=data.get("ability"),
    )


def get_all_mechs() -> list[Mech]:
    all_mechs = []
    with open("data/mechs.yml", "r") as mechs_file:
        data = yaml.safe_load(mechs_file)
        for item in data.items():
            all_mechs.append(parse_mechs(item))
    return all_mechs


def parse_maneuvers(maneuvers) -> Maneuver:
    name, data = maneuvers
    return Maneuver(
        name=name,
        text=data.get("text"),
    )


def get_all_maneuvers() -> list[Maneuver]:
    all_maneuvers = []
    with open("data/maneuvers.yml", "r") as maneuvers_file:
        data = yaml.safe_load(maneuvers_file)
        for item in data.items():
            all_maneuvers.append(parse_maneuvers(item))
    return all_maneuvers


def equipment_stats():
    output = ""
    sizes = {
        "Small": 0,
        "Medium": 0,
        "Large": 0,
    }
    types = {
        "Ballistic": 0,
        "Energy": 0,
        "Melee": 0,
        "Missile": 0,
        "Electronics": 0,
        "Drone": 0,
        "Auxiliary": 0,
    }
    ranges = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
    }
    range_types = {}
    for r in ranges.keys():
        if r != "Melee":
            range_types[("Ballistic", r)] = 0
            range_types[("Energy", r)] = 0
    full_types = {}
    for size in sizes.keys():
        for t in types.keys():
            full_types[(size, t)] = 0
    ammo_weapons = 0
    keywords = {
        "Shred": 0,
        "AP": 0,
        "Charge": 0,
        "Shield": 0,
        "Vulnerable": 0,
        "Overheat": 0,
        "Disable": 0,
        "Overwatch": 0,
    }
    move_systems = 0
    total = 0
    all_equipment = get_all_equipment()
    for equipment in all_equipment:
        total += 1
        sizes[equipment.size] += 1
        types[equipment.type] += 1
        full_types[(equipment.size, equipment.type)] += 1
        if equipment.range is not None:
            ranges[equipment.range] += 1
            range_type_key = (equipment.type, equipment.range)
            if range_type_key in range_types:
                range_types[range_type_key] += 1
        if equipment.ammo:
            ammo_weapons += 1
        for key in keywords.keys():
            if key in equipment.text:
                keywords[key] += 1
        text = equipment.text.lower()
        if "remove" not in text and (
            "move" in text
            or "reposition" in text
            or "fall back" in text
            or "advance" in text
        ):
            move_systems += 1
        for tag in equipment.tags:
            if tag not in keywords:
                keywords[tag] = 1
            else:
                keywords[tag] += 1
    output += "Sizes\n"
    for k, v in sizes.items():
        output += f"{k}: {v}\n"
    output += "\nTypes\n"
    for k, v in types.items():
        output += f"{k}: {v}\n"
    output += "\nFull Types\n"
    for k, v in full_types.items():
        output += f"{k[0]} {k[1]}: {v}\n"
    output += "\nRanges\n"
    for k, v in ranges.items():
        output += f"Range {k}: {v}\n"
    output += "\nRanges by Type\n"
    for k, v in sorted(range_types.items()):
        output += f"{k[0]} {k[1]}: {v}\n"
    output += f"\nAmmo Equipment: {ammo_weapons}\n"
    for k, v in keywords.items():
        output += f"{k} Equipment: {v}\n"
    output += f"Move Equipment: {move_systems}\n"
    output += f"Total Equipment: {total}"
    return output


def get_filtered_equipment(filters: list[str]) -> list[Equipment]:
    all_equipment = get_all_equipment()
    matching_equipment = []
    for equipment in all_equipment:
        ok = 0
        for f in filters:
            if (
                f != "Move"
                and f.lower() in equipment.text.lower()
                or f in equipment.name
                or f == equipment.type
                or f == equipment.system
                or f == equipment.size
            ):
                ok += 1
            elif f == "Ammo" and equipment.ammo:
                ok += 1
            elif f == "Short" and equipment.range == 1:
                ok += 1
            elif f == "Mid" and equipment.range == 2:
                ok += 1
            elif f == "Long" and equipment.range == 3:
                ok += 1
            elif f.startswith("Heat"):
                op = f[4]
                heat = int(f[5])
                if op == "=" and equipment.heat == heat:
                    ok += 1
                elif op == ">" and equipment.heat and equipment.heat > heat:
                    ok += 1
                elif op == "<" and equipment.heat and equipment.heat < heat:
                    ok += 1
            elif (
                f == "Move"
                and "remove" not in equipment.text.lower()
                and (
                    "advance" in equipment.text.lower()
                    or "fall back" in equipment.text.lower()
                    or "move" in equipment.text.lower()
                    or "reposition" in equipment.text.lower()
                )
            ):
                ok += 1
            elif f in equipment.tags:
                ok += 1
        if ok == len(filters):
            matching_equipment.append(equipment)
    return matching_equipment


def get_filtered_mechs(filters: list[str]):
    all_mechs = get_all_mechs()
    matching_mechs = []
    for mech in all_mechs:
        ok = 0
        for f in filters:
            if (
                f in mech.name
                or f == mech.faction
                or f in mech.hardpoints
                or f in mech.ability
            ):
                ok += 1
            elif f == "Feds" and mech.faction == "Midline":
                ok += 1
            elif f == "Ares" and mech.faction == "Low Tech":
                ok += 1
            elif f == "Jovians" and mech.faction == "High Tech":
                ok += 1
            elif f == "Pirates" and mech.faction == "Pirate":
                ok += 1
            elif f.startswith("Heat"):
                op = f[4]
                heat = int(f[5:])
                if op == "=" and mech.hc == heat:
                    ok += 1
                elif op == ">" and mech.hc and mech.hc > heat:
                    ok += 1
                elif op == "<" and mech.hc and mech.hc < heat:
                    ok += 1
            elif f.startswith("HP"):
                op = f[2]
                hp = int(f[3:])
                if op == "=" and mech.hp == hp:
                    ok += 1
                elif op == ">" and mech.hp and mech.hp > hp:
                    ok += 1
                elif op == "<" and mech.hp and mech.hp < hp:
                    ok += 1
        if ok == len(filters):
            matching_mechs.append(mech)
    return matching_mechs


class BotDatabase:
    equipment = get_all_equipment()
    mechs = get_all_mechs()
    maneuvers = get_all_maneuvers()
    everything = list(itertools.chain.from_iterable([equipment, mechs, maneuvers]))

    def get_filtered_equipment(self, filters: list[str]) -> list[Equipment]:
        return get_filtered_equipment(filters)

    def get_filtered_mechs(self, filters: list[str]) -> list[Mech]:
        return get_filtered_mechs(filters)

    def fuzzy_query_name(
        self, name: str, threshold: int
    ) -> list[tuple[Union[Equipment, Mech, Maneuver], int]]:
        results = [
            (x, fuzz.ratio(name.lower(), x.name.lower())) for x in self.everything
        ]
        return sorted(
            [x for x in results if x[1] > threshold], key=lambda x: x[1], reverse=True
        )
