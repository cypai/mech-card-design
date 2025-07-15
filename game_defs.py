from typing import Optional
import re


class Equipment:
    name: str
    normalized_name: str
    size: str
    type: str
    heat: Optional[int]
    ammo: Optional[int]
    range: Optional[str]
    text: str

    def __init__(self, **kwargs):
        self.name = str(kwargs.get("name"))
        self.size = str(kwargs.get("size"))
        self.type = str(kwargs.get("type"))
        self.system = str(kwargs.get("system"))
        self.heat = kwargs.get("heat", None)
        self.ammo = kwargs.get("ammo", None)
        self.range = kwargs.get("range", None)
        self.text = str(kwargs.get("text"))

        self.normalized_name = re.sub(r"\W", "", self.name)
        self.normalized_name = self.normalized_name.lower()

    def __str__(self):
        text = self.name + "\n"
        text += f"{self.size} {self.type}\n"
        if self.range is not None:
            text += f"Range: {self.range}\n"
        if self.heat is not None:
            text += f"Heat: {self.heat}\n"
        if self.ammo is not None:
            text += f"Ammo: {self.ammo}\n"
        text += f"{self.text}"
        return text
