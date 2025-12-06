#!/usr/bin/env python3

import argparse
from abc import ABC, abstractmethod
from io import BytesIO

from pilmoji import Pilmoji
from pilmoji.source import Twemoji
from PIL import Image, ImageFont, ImageDraw, ImageText

from typing import Optional

from game_data import GameDatabase
from game_defs import Equipment
from lib import wrap_text_tagged

CARD_WIDTH = 750
CARD_HEIGHT = 1050

LARGE_FONT_SIZE = int(CARD_HEIGHT / 17.5)
TRACKER_FONT_SIZE = int(CARD_HEIGHT / 20)
SMALL_FONT_SIZE = int(CARD_HEIGHT / 28)

ICON_SIZE = int(CARD_WIDTH / 10)
SECTION_ICON_SIZE = int(SMALL_FONT_SIZE * 1.2)

TRACKER_SIZE = int(CARD_HEIGHT / 10)

MARGIN = int(CARD_WIDTH * 0.05)


class SteelVanguardSource(Twemoji):
    def get_custom_emoji(self, tag: str, /) -> Optional[BytesIO]:
        with open(f"./textures/{tag}.png", "rb") as f:
            buf = BytesIO(f.read())
        return buf


class Icons:
    def __enter__(self):
        heat = Image.open("textures/heat.png")
        melee = Image.open("textures/melee.png")
        rng = Image.open("textures/range.png")
        target = Image.open("textures/target.png")
        ammo = Image.open("textures/ammo.png")
        maxcharge = Image.open("textures/maxcharge.png")
        info = Image.open("textures/info.png")
        action = Image.open("textures/action.png")
        trigger = Image.open("textures/trigger.png")
        passive = Image.open("textures/passive.png")

        self.heat = heat.resize((ICON_SIZE, ICON_SIZE))
        self.melee = melee.resize((ICON_SIZE, ICON_SIZE))
        self.range = rng.resize((ICON_SIZE, ICON_SIZE))
        self.target = target.resize((ICON_SIZE, ICON_SIZE))
        self.ammo = ammo.resize((ICON_SIZE, ICON_SIZE))
        self.maxcharge = maxcharge.resize((ICON_SIZE, ICON_SIZE))
        self.info = info.resize((SECTION_ICON_SIZE, SECTION_ICON_SIZE))
        self.action = action.resize((SECTION_ICON_SIZE, SECTION_ICON_SIZE))
        self.trigger = trigger.resize((SECTION_ICON_SIZE, SECTION_ICON_SIZE))
        self.passive = passive.resize((SECTION_ICON_SIZE, SECTION_ICON_SIZE))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.heat.close()
        self.melee.close()
        self.range.close()
        self.ammo.close()
        self.maxcharge.close()
        self.info.close()
        self.action.close()
        self.trigger.close()


class CardRenderer(ABC):
    CARD_TEXT_Y = int(CARD_HEIGHT * 0.52)

    def __init__(self, icons: Icons, filename: str):
        self.icons = icons
        self.filename = filename
        self.large_font = ImageFont.truetype(
            "./fonts/HackNerdFont-Bold.ttf", LARGE_FONT_SIZE
        )
        self.small_font = ImageFont.truetype(
            "./fonts/HackNerdFont-Regular.ttf", SMALL_FONT_SIZE
        )
        self.icon_font = ImageFont.truetype(
            "./fonts/HackNerdFont-Regular.ttf", int(ICON_SIZE * 0.8)
        )

    def __enter__(self):
        self.image = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), (255, 255, 255))
        self.pilmoji = Pilmoji(
            self.image,
            source=SteelVanguardSource,
            render_custom_emoji=True,
            emoji_position_offset=(7, -3),
        )
        self.draw = ImageDraw.Draw(self.image)
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.image.save(self.filename)
        self.image.close()
        self.pilmoji.close()

    @abstractmethod
    def render(self):
        pass

    def draw_border(self):
        self.draw.line(
            [
                (0, 0),
                (0, CARD_HEIGHT),
                (CARD_WIDTH, CARD_HEIGHT),
                (CARD_WIDTH, 0),
                (0, 0),
            ],
            fill="#000000",
            width=2,
        )

    def draw_card_text(self, text: str):
        width_in_characters = int(CARD_WIDTH / (SMALL_FONT_SIZE * 0.6)) - 4
        wrapped_text = wrap_text_tagged(text, width_in_characters)
        self.pilmoji.text(
            (MARGIN, CardRenderer.CARD_TEXT_Y),
            wrapped_text,
            "#000000",
            font=self.small_font,
            spacing=10,
        )


class EquipmentCardRenderer(CardRenderer):
    NAME_X = int(ICON_SIZE * 2.2)
    ICON_X = int(MARGIN * 0.5)
    ICON_TEXT_X = ICON_X + ICON_SIZE
    CARD_TYPE_TEXT_Y = int(CARD_HEIGHT * 0.45)

    def __init__(self, equipment: Equipment, icons: Icons):
        super().__init__(icons, equipment.filename)
        self.equipment = equipment

    def render(self):
        self.draw_border()
        self.draw_name()
        self.draw_top_icons()
        self.draw_card_type()
        self.draw_card_text(self.equipment.text)

    def get_name_color(self) -> str:
        if self.equipment.type == "Ballistic":
            return "#ff7f00"
        elif self.equipment.type == "Energy":
            return "#ff40ff"
        elif self.equipment.type in ["Missile", "Drone", "Nanite"]:
            return "#888888"
        elif self.equipment.type == "Melee":
            return "#FF0000"
        elif self.equipment.type == "Electronics":
            return "#00f0ff"
        elif self.equipment.type == "Auxiliary":
            return "#000000"
        return "#000000"

    def draw_name(self):
        width_in_characters = int(CARD_WIDTH / (LARGE_FONT_SIZE * 0.6)) - 5
        wrapped_text = wrap_text_tagged(self.equipment.name, width_in_characters)
        text = ImageText.Text(wrapped_text, self.large_font)
        text.embed_color()
        text.stroke(1, "#000000")
        self.draw.text(
            (
                int(ICON_SIZE * 2.2),
                int(MARGIN * 1.1),
            ),
            text,
            self.get_name_color(),
            align="left",
            spacing=10,
        )

    def draw_top_icons(self):
        row = 0
        if self.equipment.heat is not None:
            self.draw_top_icon(row, self.icons.heat, str(self.equipment.heat))
            row += 1
        if self.equipment.range is not None:
            if self.equipment.range == 0:
                self.draw_top_icon(row, self.icons.melee, "")
            else:
                self.draw_top_icon(row, self.icons.range, str(self.equipment.range))
            row += 1
        if self.equipment.target is not None:
            self.draw_top_icon(row, self.icons.target, str(self.equipment.target))
            row += 1
        if self.equipment.ammo is not None:
            self.draw_top_icon(row, self.icons.ammo, str(self.equipment.ammo))
            row += 1
        if self.equipment.maxcharge is not None:
            self.draw_top_icon(row, self.icons.maxcharge, str(self.equipment.maxcharge))
            row += 1

    def draw_top_icon(self, row: int, icon: Image.Image, text: str):
        self.image.alpha_composite(
            icon, (EquipmentCardRenderer.ICON_X, int(MARGIN + row * ICON_SIZE * 1.1))
        )
        self.draw.text(
            (
                EquipmentCardRenderer.ICON_TEXT_X,
                int(MARGIN * 1.1 + row * ICON_SIZE * 1.1),
            ),
            text,
            "#000000",
            font=self.icon_font,
        )

    def draw_card_type(self):
        self.draw.text(
            (MARGIN, EquipmentCardRenderer.CARD_TYPE_TEXT_Y),
            f"{self.equipment.size} {self.equipment.type} {self.equipment.system}",
            "#000000",
            font=self.small_font,
        )

    def draw_card_text(self, text: str):
        if self.equipment.legacy_text:
            super().draw_card_text(text)
        else:
            section = 0
            if self.equipment.info is not None:
                num_lines = self.draw_card_text_section(
                    EquipmentCardRenderer.CARD_TEXT_Y,
                    self.icons.info,
                    self.equipment.info,
                )
                section += num_lines + 0.5
            for action in self.equipment.actions:
                num_lines = self.draw_card_text_section(
                    EquipmentCardRenderer.CARD_TEXT_Y
                    + int(section * (SMALL_FONT_SIZE + 10)),
                    self.icons.action,
                    action,
                )
                section += num_lines + 0.5
            for trigger in self.equipment.triggers:
                num_lines = self.draw_card_text_section(
                    EquipmentCardRenderer.CARD_TEXT_Y
                    + int(section * (SMALL_FONT_SIZE + 10)),
                    self.icons.trigger,
                    trigger,
                )
                section += num_lines + 0.5
            for passive in self.equipment.passives:
                num_lines = self.draw_card_text_section(
                    EquipmentCardRenderer.CARD_TEXT_Y
                    + int(section * (SMALL_FONT_SIZE + 10)),
                    self.icons.passive,
                    passive,
                )
                section += num_lines + 0.5

    def draw_card_text_section(self, y: int, icon: Image.Image, text: str) -> int:
        self.image.alpha_composite(icon, (MARGIN, y - 1))
        width_in_characters = int(CARD_WIDTH / (SMALL_FONT_SIZE * 0.6)) - 8
        wrapped_text = wrap_text_tagged(text, width_in_characters)
        self.pilmoji.text(
            (int(MARGIN + SMALL_FONT_SIZE * 1.5), y),
            wrapped_text,
            "#000000",
            font=self.small_font,
            spacing=10,
        )
        return len(wrapped_text.splitlines())


game_db = GameDatabase()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", "-f", action="append")
    args = parser.parse_args()
    with Icons() as icons:
        if args.filter is None:
            eq_list = game_db.equipment
        else:
            eq_list = game_db.get_filtered_equipment(args.filter)
        for equipment in eq_list:
            with EquipmentCardRenderer(equipment, icons) as card:
                card.render()


main()
