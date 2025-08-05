from game_defs import *
import yaml


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


def get_filtered_equipment(filters) -> list[Equipment]:
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


def get_filtered_mechs(filters):
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
