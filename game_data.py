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
        copies=data.get("copies", 1),
    )


def get_all_equipment(filename: str = "data/equipment.yml") -> list[Equipment]:
    all_equipment = []
    with open(filename, "r") as equipment_file:
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
        tags=data.get("tags", []),
        copies=data.get("copies", 1),
    )


def get_all_mechs(filename: str = "data/mechs.yml") -> list[Mech]:
    all_mechs = []
    with open(filename, "r") as mechs_file:
        data = yaml.safe_load(mechs_file)
        for item in data.items():
            all_mechs.append(parse_mechs(item))
    return all_mechs


def parse_drones(drones) -> Drone:
    name, data = drones
    return Drone(
        name=name,
        ability=data.get("ability"),
        copies=data.get("copies", 2),
    )


def get_all_drones(filename: str = "data/drones.yml") -> list[Drone]:
    all_drones = []
    with open(filename, "r") as drones_file:
        data = yaml.safe_load(drones_file)
        for item in data.items():
            all_drones.append(parse_drones(item))
    return all_drones


def parse_maneuvers(maneuvers) -> Maneuver:
    name, data = maneuvers
    return Maneuver(
        name=name,
        text=data.get("text"),
        copies=data.get("copies", 2),
    )


def get_all_maneuvers(filename: str = "data/maneuvers.yml") -> list[Maneuver]:
    all_maneuvers = []
    with open(filename, "r") as maneuvers_file:
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
    spare_equipment = 0
    move_systems = 0
    total = 0
    all_equipment = get_all_equipment()
    for equipment in all_equipment:
        total += 1
        if "Spare" in equipment.tags:
            spare_equipment += 1
            continue
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
    output += f"Spare Equipment (not counted in other stats): {spare_equipment}\n"
    output += f"Total Equipment: {total}"
    return output


def get_filtered_equipment(filters: list[str]) -> list[Equipment]:
    parsed_filters = [f.lower() for f in filters]
    all_equipment = get_all_equipment()
    matching_equipment = []
    for equipment in all_equipment:
        ok = 0
        tokenized_text = re.sub(r"[^a-zA-Z0-9\s]+", " ", equipment.text.lower()).split()
        for f in parsed_filters:
            if (
                f != "move"
                and f in tokenized_text
                or f in equipment.name.lower()
                or f == equipment.type.lower()
                or f == equipment.system.lower()
                or f == equipment.size.lower()
            ):
                ok += 1
            elif f == "ammo" and equipment.ammo:
                ok += 1
            elif f == "short" and equipment.range == 1:
                ok += 1
            elif f == "mid" and equipment.range == 2:
                ok += 1
            elif f == "long" and equipment.range == 3:
                ok += 1
            elif f.startswith("size"):
                op = f[4]
                size = f[5:]
                if op == "=" and equipment.size.lower() == size:
                    ok += 1
            elif f.startswith("type"):
                op = f[4]
                the_type = f[5:]
                if op == "=" and equipment.type.lower() == the_type:
                    ok += 1
            elif f.startswith("system"):
                op = f[6]
                system = f[7:]
                if op == "=" and equipment.system.lower() == system:
                    ok += 1
            elif f.startswith("heat"):
                op = f[4]
                heat = int(f[5])
                if op == "=" and equipment.heat == heat:
                    ok += 1
                elif op == ">" and equipment.heat and equipment.heat > heat:
                    ok += 1
                elif op == "<" and equipment.heat and equipment.heat < heat:
                    ok += 1
            elif f.startswith("range"):
                op = f[5]
                the_range = int(f[6])
                if op == "=" and equipment.range == the_range:
                    ok += 1
                elif op == ">" and equipment.range and equipment.range > the_range:
                    ok += 1
                elif op == "<" and equipment.range and equipment.range < the_range:
                    ok += 1
            elif f == "move" and (
                "advance" in tokenized_text
                or "fall back" in equipment.text.lower()
                or "move" in tokenized_text
                or "reposition" in tokenized_text
                or "change position" in equipment.text.lower()
            ):
                ok += 1
            elif f in [t.lower() for t in equipment.tags]:
                ok += 1
        if ok == len(filters):
            matching_equipment.append(equipment)
    return matching_equipment


def get_filtered_mechs(filters: list[str]):
    parsed_filters = [f.lower() for f in filters]
    all_mechs = get_all_mechs()
    matching_mechs = []
    for mech in all_mechs:
        ok = 0
        for f in parsed_filters:
            if (
                f == mech.name.lower()
                or f == mech.faction.lower()
                or f in [h.lower() for h in mech.hardpoints]
                or f in mech.ability.lower()
            ):
                ok += 1
            elif f in ["feds", "terrans"] and mech.faction == "Midline":
                ok += 1
            elif f in ["ares"] and mech.faction == "Low Tech":
                ok += 1
            elif f in ["jovians", "jovian"] and mech.faction == "High Tech":
                ok += 1
            elif (
                f in ["pirates", "pirate", "belter", "belters"]
                and mech.faction == "Pirate"
            ):
                ok += 1
            elif f.startswith("heat"):
                op = f[4]
                heat = int(f[5:])
                if op == "=" and mech.hc == heat:
                    ok += 1
                elif op == ">" and mech.hc and mech.hc > heat:
                    ok += 1
                elif op == "<" and mech.hc and mech.hc < heat:
                    ok += 1
            elif f.startswith("hp"):
                op = f[2]
                hp = int(f[3:])
                if op == "=" and mech.hp == hp:
                    ok += 1
                elif op == ">" and mech.hp and mech.hp > hp:
                    ok += 1
                elif op == "<" and mech.hp and mech.hp < hp:
                    ok += 1
            elif f.startswith("armor"):
                op = f[5]
                armor = int(f[6:])
                if op == "=" and mech.armor == armor:
                    ok += 1
                elif op == ">" and mech.armor and mech.armor > armor:
                    ok += 1
                elif op == "<" and mech.armor and mech.armor < armor:
                    ok += 1
        if ok == len(filters):
            matching_mechs.append(mech)
    return matching_mechs


class GameDatabase:
    def __init__(self, changelog=False) -> None:
        if changelog:
            self.equipment = get_all_equipment("./changelog/previous_equipment.yml")
            self.mechs = get_all_mechs("./changelog/previous_mechs.yml")
            self.drones = get_all_drones("./changelog/previous_drones.yml")
            self.maneuvers = get_all_maneuvers("./changelog/previous_maneuvers.yml")
        else:
            self.equipment = get_all_equipment()
            self.mechs = get_all_mechs()
            self.drones = get_all_drones()
            self.maneuvers = get_all_maneuvers()
        self.everything = list(
            itertools.chain.from_iterable(
                [self.equipment, self.mechs, self.drones, self.maneuvers]
            )
        )

    def get_filtered_equipment(self, filters: list[str]) -> list[Equipment]:
        return get_filtered_equipment(filters)

    def get_filtered_mechs(self, filters: list[str]) -> list[Mech]:
        return get_filtered_mechs(filters)

    def get_equipment(self, name: str) -> Equipment | None:
        return next((x for x in self.equipment if x.name == name), None)

    def get_mech(self, name: str) -> Mech | None:
        return next((x for x in self.mechs if x.name == name), None)

    def get_maneuver(self, name: str) -> Maneuver | None:
        return next((x for x in self.maneuvers if x.name == name), None)

    def fuzzy_query_name(
        self, name: str, threshold: int
    ) -> list[tuple[Union[Equipment, Mech, Drone, Maneuver], int]]:
        results = [
            (x, fuzz.ratio(name.lower(), x.name.lower())) for x in self.everything
        ]
        return sorted(
            [x for x in results if x[1] > threshold], key=lambda x: x[1], reverse=True
        )
