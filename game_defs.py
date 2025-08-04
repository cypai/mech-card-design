from functools import reduce
from typing import Optional
import re


class Equipment:
    name: str
    normalized_name: str
    size: str
    type: str
    heat: Optional[int]
    ammo: Optional[int]
    range: Optional[int]
    text: str
    tags: list[str]

    def __init__(self, **kwargs):
        self.name = str(kwargs.get("name"))
        self.size = str(kwargs.get("size"))
        self.type = str(kwargs.get("type"))
        self.system = str(kwargs.get("system"))
        self.heat = kwargs.get("heat", None)
        self.ammo = kwargs.get("ammo", None)
        self.range = kwargs.get("range", None)
        self.text = str(kwargs.get("text"))
        self.tags = kwargs.get("tags", [])

        self.normalized_name = re.sub(r"\W", "", self.name)
        self.normalized_name = self.normalized_name.lower()

    def __str__(self):
        text = self.name + "\n"
        text += f"{self.size} {self.type} {self.system}\n"
        if self.range is not None:
            text += f"Range: {self.range}\n"
        if self.heat is not None:
            text += f"Heat: {self.heat}\n"
        if self.ammo is not None:
            text += f"Ammo: {self.ammo}\n"
        if len(self.tags) > 0:
            text += f"Tags: {self.tags}\n"
        text += f"{self.text}"
        return text


class Mech:
    name: str
    faction: str
    hp: int
    armor: int
    hc: int
    hardpoints: list[str]
    hardpoints_str: str
    ability: str

    def __init__(self, **kwargs):
        self.name = str(kwargs.get("name"))
        self.faction = str(kwargs.get("faction"))
        self.hp = kwargs.get("hp", 10)
        self.armor = kwargs.get("armor", 10)
        self.hc = kwargs.get("hc", 10)
        self.hardpoints = kwargs.get("hardpoints", [])
        self.hardpoints_str = reduce(lambda x, y: x + y[0] + " ", self.hardpoints, "")
        self.hardpoints_str = self.hardpoints_str[:-1]
        self.ability = str(kwargs.get("ability"))

        self.normalized_name = re.sub(r"\W", "", self.name)
        self.normalized_name = self.normalized_name.lower()

    def __str__(self):
        text = self.name + "\n"
        text += f"HP: {self.hp}\n"
        text += f"Armor: {self.armor}\n"
        text += f"Heat: {self.hc}\n"
        text += f"Hardpoints: {self.hardpoints_str}\n"
        text += f"Ability: {self.ability}"
        return text


class Maneuver:
    name: str
    text: str

    def __init__(self, **kwargs):
        self.name = str(kwargs.get("name"))
        self.text = str(kwargs.get("text"))

        self.normalized_name = re.sub(r"\W", "", self.name)
        self.normalized_name = self.normalized_name.lower()

    def __str__(self):
        text = self.name + "\n" + self.text
        return text
