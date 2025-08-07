from functools import reduce
from typing import Optional, Self
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

    def diff(self, other: Self) -> tuple[bool, str]:
        is_diff = False
        diffs = f"{self.name}\n"
        if self.size != other.size:
            is_diff = True
            diffs += f"{other.size} -> {self.size}\n"
        if self.type != other.type:
            is_diff = True
            diffs += f"{other.type} -> {self.type}\n"
        if self.system != other.system:
            is_diff = True
            diffs += f"{other.system} -> {self.system}\n"
        if self.heat != other.heat:
            is_diff = True
            diffs += f"{other.heat} -> {self.heat}\n"
        if self.ammo != other.ammo:
            is_diff = True
            diffs += f"{other.ammo} -> {self.ammo}\n"
        if self.range != other.range:
            is_diff = True
            diffs += f"{other.range} -> {self.range}\n"
        if self.text != other.text:
            is_diff = True
            diffs += f"{other.text}\n->\n{self.text}\n"
        return (is_diff, diffs)


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

    def diff(self, other: Self) -> tuple[bool, str]:
        is_diff = False
        diffs = f"{self.name}\n"
        if self.hp != other.hp:
            is_diff = True
            diffs += f"{other.hp} -> {self.hp}\n"
        if self.armor != other.armor:
            is_diff = True
            diffs += f"{other.armor} -> {self.armor}\n"
        if self.hc != other.hc:
            is_diff = True
            diffs += f"{other.hc} -> {self.hc}\n"
        if self.hardpoints_str != other.hardpoints_str:
            is_diff = True
            diffs += f"{other.hardpoints_str} -> {self.hardpoints_str}\n"
        if self.ability != other.ability:
            is_diff = True
            diffs += f"{other.ability} -> {self.ability}\n"
        return (is_diff, diffs)


class Drone:
    name: str
    ability: str

    def __init__(self, **kwargs):
        self.name = str(kwargs.get("name"))
        self.ability = str(kwargs.get("ability"))

        self.normalized_name = re.sub(r"\W", "", self.name)
        self.normalized_name = self.normalized_name.lower()

    def __str__(self):
        text = self.name + "\n"
        text += f"Ability: {self.ability}"
        return text

    def diff(self, other: Self) -> tuple[bool, str]:
        is_diff = False
        diffs = f"{self.name}\n"
        if self.ability != other.ability:
            is_diff = True
            diffs += f"{other.ability} -> {self.ability}\n"
        return (is_diff, diffs)


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

    def diff(self, other: Self) -> tuple[bool, str]:
        is_diff = False
        diffs = f"{self.name}\n"
        if self.text != other.text:
            is_diff = True
            diffs += f"{other.text} -> {self.text}\n"
        return (is_diff, diffs)
