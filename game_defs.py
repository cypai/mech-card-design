from functools import reduce
from typing import Optional, Self
import re
from thefuzz import fuzz


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

    def is_similar(self, other: Self) -> bool:
        """
        Determines likelihood that this was a rename
        """
        if self.name == other.name:
            return True
        diffs = 0
        if self.size != other.size:
            diffs += 1
        if self.type != other.type:
            diffs += 1
        if self.system != other.system:
            diffs += 1
        if self.heat != other.heat:
            diffs += 1
        if self.ammo != other.ammo:
            diffs += 1
        if self.range != other.range:
            diffs += 1
        text_ratio = fuzz.token_set_ratio(self.text, other.text)
        if text_ratio < 100:
            if text_ratio > 90:
                diffs += 1
            else:
                diffs += 2
        return diffs <= 2

    def diff(self, other: Self) -> tuple[bool, str]:
        is_diff = False
        if self.name == other.name:
            diffs = f"{self.name}\n"
        else:
            diffs = f"{other.name} -> {self.name}\n"
        if self.size != other.size:
            is_diff = True
            diffs += f"Size: {other.size} -> {self.size}\n"
        if self.type != other.type:
            is_diff = True
            diffs += f"Type: {other.type} -> {self.type}\n"
        if self.system != other.system:
            is_diff = True
            diffs += f"{other.system} -> {self.system}\n"
        if self.heat != other.heat:
            is_diff = True
            diffs += f"Heat: {other.heat} -> {self.heat}\n"
        if self.ammo != other.ammo:
            is_diff = True
            diffs += f"Ammo: {other.ammo} -> {self.ammo}\n"
        if self.range != other.range:
            is_diff = True
            diffs += f"Range: {other.range} -> {self.range}\n"
        if self.text != other.text:
            is_diff = True
            diffs += f"{other.text}|->\n{self.text}"
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
    tags: list[str]

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
        self.tags = kwargs.get("tags", [])

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

    def is_similar(self, other: Self) -> bool:
        """
        Determines likelihood that this was a rename
        """
        if self.name == other.name:
            return True
        diffs = 0
        if self.hp != other.hp:
            diffs += 1
        if self.armor != other.armor:
            diffs += 1
        if self.hc != other.hc:
            diffs += 1
        if self.hardpoints_str != other.hardpoints_str:
            diffs += 1
        text_ratio = fuzz.token_set_ratio(self.ability, other.ability)
        if text_ratio < 100:
            if text_ratio > 90:
                diffs += 1
            else:
                diffs += 2
        return diffs <= 2

    def diff(self, other: Self) -> tuple[bool, str]:
        is_diff = False
        if self.name == other.name:
            diffs = f"{self.name}\n"
        else:
            diffs = f"{other.name} -> {self.name}\n"
        if self.hp != other.hp:
            is_diff = True
            diffs += f"HP: {other.hp} -> {self.hp}\n"
        if self.armor != other.armor:
            is_diff = True
            diffs += f"Armor: {other.armor} -> {self.armor}\n"
        if self.hc != other.hc:
            is_diff = True
            diffs += f"Heat Capacity: {other.hc} -> {self.hc}\n"
        if self.hardpoints_str != other.hardpoints_str:
            is_diff = True
            diffs += f"Hardpoints: {other.hardpoints_str} -> {self.hardpoints_str}\n"
        if self.ability != other.ability:
            is_diff = True
            diffs += f"{other.ability}|->\n{self.ability}"
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

    def is_similar(self, other: Self) -> bool:
        """
        Determines likelihood that this was a rename
        """
        if self.name == other.name:
            return True
        text_ratio = fuzz.ratio(self.ability, other.ability)
        return text_ratio > 80

    def diff(self, other: Self) -> tuple[bool, str]:
        is_diff = False
        if self.name == other.name:
            diffs = f"{self.name}\n"
        else:
            diffs = f"{other.name} -> {self.name}\n"
        if self.ability != other.ability:
            is_diff = True
            diffs += f"{other.ability}|->\n{self.ability}"
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

    def is_similar(self, other: Self) -> bool:
        """
        Determines likelihood that this was a rename
        """
        if self.name == other.name:
            return True
        text_ratio = fuzz.ratio(self.text, other.text)
        return text_ratio > 80

    def diff(self, other: Self) -> tuple[bool, str]:
        is_diff = False
        if self.name == other.name:
            diffs = f"{self.name}\n"
        else:
            diffs = f"{other.name} -> {self.name}\n"
        if self.text != other.text:
            is_diff = True
            diffs += f"{other.text}|->\n{self.text}"
        return (is_diff, diffs)
