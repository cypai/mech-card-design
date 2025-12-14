from functools import reduce
from typing import Optional, Self
import re
from thefuzz import fuzz


class Equipment:
    name: str
    size: str
    type: str
    form: str
    heat: Optional[int]
    range: Optional[int]
    target: Optional[str]
    ammo: Optional[int]
    maxcharge: Optional[int]
    text: str
    info: Optional[str]
    actions: list[str]
    triggers: list[str]
    passives: list[str]
    tags: list[str]
    alias: list[str]
    copies: int
    legacy_text: bool
    rating: Optional[str]

    def __init__(self, **kwargs):
        self.name = str(kwargs.get("name"))
        self.size = str(kwargs.get("size"))
        self.type = str(kwargs.get("type"))
        self.form = str(kwargs.get("form"))
        self.heat = kwargs.get("heat", None)
        self.range = kwargs.get("range", None)
        self.target = kwargs.get("target", None)
        self.ammo = kwargs.get("ammo", None)
        self.maxcharge = kwargs.get("maxcharge", None)
        self.info = kwargs.get("info", None)
        self.actions = kwargs.get("actions", [])
        self.triggers = kwargs.get("triggers", [])
        self.passives = kwargs.get("passives", [])
        self.tags = kwargs.get("tags", [])
        self.alias = kwargs.get("alias", [])
        self.copies = kwargs.get("copies", 1)
        self.rating = kwargs.get("rating", None)

        self.normalized_name = re.sub(r"\W", "", self.name)
        self.normalized_name = self.normalized_name.lower()
        self.filename = f"outputs/equipment/{self.normalized_name}.png"
        self.legacy_text = (
            self.info is None
            and len(self.actions) == 0
            and len(self.triggers) == 0
            and len(self.passives) == 0
        )
        if self.legacy_text:
            self.text = kwargs.get("text", "")
        else:
            self.text = self.pretty_text()

    def pretty_text(self):
        if self.info is None:
            text = ""
        else:
            text = f"Info: {self.info}"
        for action in self.actions:
            text += f"Action: {action}"
        for trigger in self.triggers:
            text += f"Trigger: {trigger}"
        for passive in self.passives:
            text += f"Passive: {passive}"
        return text

    def __str__(self):
        text = self.name + "\n"
        text += f"{self.size} {self.type} {self.form}\n"
        if self.heat is not None:
            text += f"Heat: {self.heat}\n"
        if self.range is not None:
            text += f"Range: {self.range}\n"
        if self.target is not None:
            text += f"Target: {self.target}\n"
        if self.ammo is not None:
            text += f"Ammo: {self.ammo}\n"
        if self.maxcharge is not None:
            text += f"Max Charge: {self.maxcharge}\n"
        if len(self.tags) > 0:
            text += f"Tags: {self.tags}\n"
        if self.rating is not None:
            text += f"Rating: {self.rating}\n"
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
        if self.form != other.form:
            diffs += 1
        if self.heat != other.heat:
            diffs += 1
        if self.range != other.range:
            diffs += 1
        if self.target != other.target:
            diffs += 1
        if self.ammo != other.ammo:
            diffs += 1
        if self.maxcharge != other.maxcharge:
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
        if self.form != other.form:
            is_diff = True
            diffs += f"{other.form} -> {self.form}\n"
        if self.heat != other.heat:
            is_diff = True
            diffs += f"Heat: {other.heat} -> {self.heat}\n"
        if self.range != other.range:
            is_diff = True
            diffs += f"Range: {other.range} -> {self.range}\n"
        if self.target != other.target:
            is_diff = True
            diffs += f"Target: {other.target} -> {self.target}\n"
        if self.ammo != other.ammo:
            is_diff = True
            diffs += f"Ammo: {other.ammo} -> {self.ammo}\n"
        if self.maxcharge != other.maxcharge:
            is_diff = True
            diffs += f"Max Charge: {other.maxcharge} -> {self.maxcharge}\n"
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
    info: Optional[str]
    actions: list[str]
    triggers: list[str]
    passives: list[str]
    tags: list[str]
    copies: int
    legacy_text: bool

    def __init__(self, **kwargs):
        self.name = str(kwargs.get("name"))
        self.faction = str(kwargs.get("faction"))
        self.hp = kwargs.get("hp", 10)
        self.armor = kwargs.get("armor", 10)
        self.hc = kwargs.get("hc", 10)
        self.hardpoints = kwargs.get("hardpoints", [])
        self.hardpoints_str = reduce(lambda x, y: x + y[0] + " ", self.hardpoints, "")
        self.hardpoints_str = self.hardpoints_str[:-1]
        self.info = kwargs.get("info", None)
        self.actions = kwargs.get("actions", [])
        self.triggers = kwargs.get("triggers", [])
        self.passives = kwargs.get("passives", [])
        self.tags = kwargs.get("tags", [])
        self.copies = kwargs.get("copies", 1)

        self.normalized_name = re.sub(r"\W", "", self.name)
        self.normalized_name = self.normalized_name.lower()
        self.filename = f"outputs/mechs/{self.normalized_name}.png"
        self.legacy_text = (
            self.info is None
            and len(self.actions) == 0
            and len(self.triggers) == 0
            and len(self.passives) == 0
        )
        if self.legacy_text:
            self.ability = kwargs.get("ability", "")
        else:
            self.ability = self.pretty_text()

    def __str__(self):
        text = self.name + "\n"
        text += f"HP: {self.hp}\n"
        text += f"Armor: {self.armor}\n"
        text += f"Heat: {self.hc}\n"
        text += f"Hardpoints: {self.hardpoints_str}\n"
        text += f"Ability: \n{self.ability}"
        return text

    def pretty_text(self):
        text = ""
        if self.info is not None:
            text += f"Info: {self.info}"
        for action in self.actions:
            text += f"Action: {action}"
        for trigger in self.triggers:
            text += f"Trigger: {trigger}"
        for passive in self.passives:
            text += f"Passive: {passive}"
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
    copies: int
    info: Optional[str]
    actions: list[str]
    triggers: list[str]
    passives: list[str]
    legacy_text: bool

    def __init__(self, **kwargs):
        self.name = str(kwargs.get("name"))
        self.ability = str(kwargs.get("ability"))
        self.info = kwargs.get("info", None)
        self.actions = kwargs.get("actions", [])
        self.triggers = kwargs.get("triggers", [])
        self.passives = kwargs.get("passives", [])
        self.copies = kwargs.get("copies", 2)

        self.normalized_name = re.sub(r"\W", "", self.name)
        self.normalized_name = self.normalized_name.lower()
        self.filename = f"outputs/drones/{self.normalized_name}.png"

        self.legacy_text = (
            self.info is None
            and len(self.actions) == 0
            and len(self.triggers) == 0
            and len(self.passives) == 0
        )
        if self.legacy_text:
            self.ability = kwargs.get("ability", "")
        else:
            self.ability = self.pretty_text()

    def pretty_text(self):
        text = ""
        if self.info is not None:
            text += f"Info: {self.info}"
        for action in self.actions:
            text += f"Action: {action}"
        for trigger in self.triggers:
            text += f"Trigger: {trigger}"
        for passive in self.passives:
            text += f"Passive: {passive}"
        return text

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
    copies: int

    def __init__(self, **kwargs):
        self.name = str(kwargs.get("name"))
        self.text = str(kwargs.get("text"))
        self.copies = kwargs.get("copies", 2)

        self.normalized_name = re.sub(r"\W", "", self.name)
        self.normalized_name = self.normalized_name.lower()
        self.filename = f"outputs/maneuvers/{self.normalized_name}.png"

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
