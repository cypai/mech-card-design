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
        hardpoints=data.get("hardpoints"),
        ability=data.get("ability"),
    )


def get_all_mechs() -> list[Mech]:
    all_mechs = []
    with open("data/mechs.yml", "r") as mechs_file:
        data = yaml.safe_load(mechs_file)
        for item in data.items():
            all_mechs.append(parse_mechs(item))
    return all_mechs
