#!/usr/bin/env python3

import os
import argparse
from enum import Enum
from abc import ABC, abstractmethod
from io import BytesIO
from textwrap import dedent

from pilmoji import Pilmoji
from pilmoji.source import Twemoji
from PIL import Image, ImageFont, ImageDraw, ImageText

from typing import Optional, Union

from game_data import GameDatabase
from game_defs import Drone, Equipment, Maneuver, Mech
from lib import wrap_text_tagged

CARD_WIDTH = 1500
CARD_HEIGHT = 2100

MECH_PADDING = int(CARD_WIDTH / 20)
MECH_WIDTH = int(CARD_WIDTH * 3) + MECH_PADDING * 2
MECH_HEIGHT = int(CARD_HEIGHT * 1.5) + MECH_PADDING * 2

HUGE_FONT_SIZE = int(CARD_HEIGHT / 12)
LARGE_FONT_SIZE = int(CARD_HEIGHT / 17.5)
NAME_FONT_SIZE = int(CARD_HEIGHT / 20)
TRACKER_FONT_SIZE = int(CARD_HEIGHT / 20)
SMALL_FONT_SIZE = int(CARD_HEIGHT / 28)
FLAVOR_FONT_SIZE = int(CARD_HEIGHT / 32)

FLAG_HEIGHT = int(HUGE_FONT_SIZE + FLAVOR_FONT_SIZE)

ICON_SIZE = int(CARD_WIDTH / 10)
SECTION_ICON_SIZE = int(SMALL_FONT_SIZE * 1.2)

TRACKER_SIZE = int(CARD_HEIGHT / 10)

MARGIN = int(CARD_WIDTH * 0.05)
BORDER_MARGIN = int(MARGIN / 3)
MECH_MARGIN = int(TRACKER_SIZE * 1.2)

SPACING = 13


class SteelVanguardSource(Twemoji):
    def get_custom_emoji(self, tag: str, /) -> Optional[BytesIO]:
        with open(f"./textures/{tag}.png", "rb") as f:
            buf = BytesIO(f.read())
        return buf


class Icons:
    def __enter__(self):
        heat = Image.open("textures/heat.png")
        engage = Image.open("textures/engage.png")
        rng = Image.open("textures/range.png")
        target = Image.open("textures/target.png")
        ammo = Image.open("textures/ammo.png")
        maxcharge = Image.open("textures/maxcharge.png")
        charge = Image.open("textures/charge.png")
        info = Image.open("textures/info.png")
        action = Image.open("textures/action.png")
        trigger = Image.open("textures/trigger.png")
        passive = Image.open("textures/passive.png")
        star = Image.open("textures/star.png")

        self.heat = heat.resize((ICON_SIZE, ICON_SIZE))
        self.engage = engage.resize((ICON_SIZE, ICON_SIZE))
        self.range = rng.resize((ICON_SIZE, ICON_SIZE))
        self.target = target.resize((ICON_SIZE, ICON_SIZE))
        self.ammo = ammo.resize((ICON_SIZE, ICON_SIZE))
        self.maxcharge = maxcharge.resize((ICON_SIZE, ICON_SIZE))
        self.charge = charge.resize((ICON_SIZE, ICON_SIZE))
        self.info = info.resize((SECTION_ICON_SIZE, SECTION_ICON_SIZE))
        self.action = action.resize((SECTION_ICON_SIZE, SECTION_ICON_SIZE))
        self.trigger = trigger.resize((SECTION_ICON_SIZE, SECTION_ICON_SIZE))
        self.passive = passive.resize((SECTION_ICON_SIZE, SECTION_ICON_SIZE))
        self.star = star.resize((int(ICON_SIZE / 2), int(ICON_SIZE / 2)))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.heat.close()
        self.engage.close()
        self.range.close()
        self.ammo.close()
        self.maxcharge.close()
        self.info.close()
        self.action.close()
        self.trigger.close()


class CardTextSectionType(Enum):
    INFO = 1
    ACTION = 2
    TRIGGER = 3
    PASSIVE = 4


class CardTextSection:
    section_type: CardTextSectionType
    text: str

    def __init__(self, section_type: CardTextSectionType, text: str):
        self.section_type = section_type
        self.text = text

    def __str__(self) -> str:
        return f"(CardTextSection {self.section_type} {self.text})"


def card_text_sections(card: Union[Equipment, Mech, Maneuver, Drone]):
    sections = []
    if card.info is not None:
        sections.append(CardTextSection(CardTextSectionType.INFO, card.info))
    for action in card.actions:
        sections.append(CardTextSection(CardTextSectionType.ACTION, action))
    for trigger in card.triggers:
        sections.append(CardTextSection(CardTextSectionType.TRIGGER, trigger))
    if not isinstance(card, Maneuver):
        for passive in card.passives:
            sections.append(CardTextSection(CardTextSectionType.PASSIVE, passive))
    return sections


class Renderer(ABC):
    def __init__(self, icons: Icons, filename: str, width: int, height: int):
        self.icons = icons
        self.filename = filename
        self.huge_font = ImageFont.truetype(
            "./fonts/HackNerdFont-Bold.ttf", HUGE_FONT_SIZE
        )
        self.large_font = ImageFont.truetype(
            "./fonts/HackNerdFont-Bold.ttf", LARGE_FONT_SIZE
        )
        self.name_font = ImageFont.truetype(
            "./fonts/HackNerdFont-Bold.ttf", NAME_FONT_SIZE
        )
        self.small_font = ImageFont.truetype(
            "./fonts/HackNerdFont-Regular.ttf", SMALL_FONT_SIZE
        )
        self.icon_font = ImageFont.truetype(
            "./fonts/HackNerdFont-Regular.ttf", int(ICON_SIZE * 0.8)
        )
        self.flavor_text_font = ImageFont.truetype(
            "./fonts/Hack-Italic.ttf", FLAVOR_FONT_SIZE
        )
        self.width = width
        self.height = height

    def __enter__(self):
        self.image = Image.new("RGBA", (self.width, self.height), (255, 255, 255))
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

    def draw_rectangle(self, x: int, y: int, width: int, height: int):
        self.draw.line(
            [
                (x, y),
                (x, y + height - 1),
                (x + width - 1, y + height - 1),
                (x + width - 1, y),
                (x, y),
            ],
            fill="#000000",
            width=2,
        )

    def draw_border(self):
        self.draw_rectangle(0, 0, self.width, self.height)

    def draw_bordered_image(
        self, image: Optional[Image.Image], x: int, y: int, width: int, height: int
    ):
        if image is not None:
            # Resize to aspect ratio
            ratio = max(width / image.width, height / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            the_image = image.resize(new_size, Image.Resampling.LANCZOS)
            # Crop box
            left = (the_image.width - width) / 2
            top = (the_image.height - height) / 2
            right = (the_image.width + width) / 2
            bottom = (the_image.height + height) / 2
            the_image = the_image.crop((left, top, right, bottom))
            self.image.paste(the_image, (x, y))
        self.draw_rectangle(x, y, width, height)

    def draw_card_text(
        self,
        card_text_sections: list[CardTextSection],
        x: int,
        y: int,
        max_chars: Optional[int] = None,
    ):
        section_num = 0
        sections = sorted(card_text_sections, key=lambda x: x.section_type.value)
        for section in sections:
            if section.section_type == CardTextSectionType.INFO:
                icon = self.icons.info
            elif section.section_type == CardTextSectionType.ACTION:
                icon = self.icons.action
            elif section.section_type == CardTextSectionType.TRIGGER:
                icon = self.icons.trigger
            else:
                icon = self.icons.passive
            num_lines = self.draw_card_text_section(
                x,
                y + int(section_num * (SMALL_FONT_SIZE + 2)),
                icon,
                section.text,
                max_chars,
            )
            section_num += num_lines + 0.5

    def draw_card_text_section(
        self,
        x: int,
        y: int,
        icon: Image.Image,
        text: str,
        max_chars: Optional[int] = None,
    ) -> int:
        self.image.alpha_composite(icon, (x, y - 1))
        if max_chars is None:
            width_in_characters = int(CARD_WIDTH / (SMALL_FONT_SIZE * 0.6)) - 8
        else:
            width_in_characters = max_chars
        wrapped_text = wrap_text_tagged(text, width_in_characters)
        self.pilmoji.text(
            (int(x + SMALL_FONT_SIZE * 1.5), y),
            wrapped_text,
            "#000000",
            font=self.small_font,
            spacing=SPACING,
        )
        return len(wrapped_text.splitlines())


class CardRenderer(Renderer):
    NAME_WIDTH = CARD_WIDTH - 2 * BORDER_MARGIN
    NAME_HEIGHT = int(NAME_FONT_SIZE * 1.3)
    ICON_X = BORDER_MARGIN
    ICON_Y = int(BORDER_MARGIN * 1.3 + NAME_HEIGHT)
    ICON_TEXT_X = BORDER_MARGIN + ICON_SIZE
    IMAGE_X = ICON_TEXT_X + int(ICON_SIZE * 0.65)
    IMAGE_Y = ICON_Y
    CARD_TYPE_TEXT_Y = int(CARD_HEIGHT * 0.5)
    IMAGE_HEIGHT = int(CARD_HEIGHT - IMAGE_Y - BORDER_MARGIN * 1.5 - CARD_TYPE_TEXT_Y)
    CARD_TEXT_Y = int(CARD_HEIGHT * 0.555)

    def __init__(self, icons: Icons, filename: str):
        super().__init__(icons, filename, CARD_WIDTH, CARD_HEIGHT)

    def draw_border(self):
        super().draw_border()
        self.draw_rectangle(
            self.ICON_X, self.ICON_Y, self.IMAGE_X - self.ICON_X, self.IMAGE_HEIGHT
        )

    def draw_name(self, name: str, color: str):
        name_width = int(len(name) * NAME_FONT_SIZE * 0.65)
        name_height = int(NAME_FONT_SIZE * 1.2)
        text = ImageText.Text(name, self.name_font)
        text.embed_color()
        text.stroke(2, "#000000")
        text.spacing = 10
        if name_width > CardRenderer.NAME_WIDTH:
            with Image.new(
                "RGBA", (name_width, name_height), (255, 255, 255)
            ) as name_image:
                name_image_draw = ImageDraw.Draw(name_image)
                name_image_draw.text(
                    (
                        int(name_width / 2),
                        int(name_height / 2),
                    ),
                    text,
                    color,
                    align="center",
                    anchor="mm",
                )
                the_image = name_image.resize((CardRenderer.NAME_WIDTH, name_height))
                self.image.paste(
                    the_image,
                    (BORDER_MARGIN, BORDER_MARGIN),
                )
        else:
            self.draw.text(
                (
                    int(self.width / 2),
                    int(BORDER_MARGIN + CardRenderer.NAME_HEIGHT / 2),
                ),
                text,
                color,
                align="center",
                anchor="mm",
            )

    def draw_top_icon(
        self, row: int, icon: Image.Image, offset: tuple[int, int] = (0, 0)
    ):
        self.image.alpha_composite(
            icon,
            (
                CardRenderer.ICON_X + offset[0],
                int(CardRenderer.ICON_Y + BORDER_MARGIN + row * ICON_SIZE * 1.1)
                + offset[1],
            ),
        )

    def draw_top_icon_with_text(
        self, row: int, icon: Image.Image, text: str, offset: tuple[int, int] = (0, 0)
    ):
        self.draw_top_icon(row, icon, offset)
        self.draw.text(
            (
                CardRenderer.ICON_TEXT_X,
                int(CardRenderer.ICON_Y * 1.05 + BORDER_MARGIN + row * ICON_SIZE * 1.1),
            ),
            text,
            "#000000",
            font=self.icon_font,
        )

    def draw_top_icon_with_icon(
        self,
        row: int,
        icon: Image.Image,
        second_icon: Image.Image,
        offset: tuple[int, int] = (0, 0),
        text_icon_offset: tuple[int, int] = (0, 0),
    ):
        self.draw_top_icon(row, icon, offset)
        self.image.alpha_composite(
            second_icon,
            (
                CardRenderer.ICON_X + ICON_SIZE + text_icon_offset[0],
                int(CardRenderer.ICON_Y + BORDER_MARGIN + row * ICON_SIZE * 1.1)
                + text_icon_offset[1],
            ),
        )

    def draw_top_icons(
        self,
        heat: Optional[int],
        rng: Optional[int],
        target: Optional[str],
        ammo: Optional[int],
        maxcharge: Optional[int],
    ):
        row = 0
        if heat is not None:
            self.draw_top_icon_with_text(row, self.icons.heat, str(heat))
            row += 1
        if rng is not None:
            if rng == 0:
                self.draw_top_icon(row, self.icons.engage)
            else:
                self.draw_top_icon_with_text(row, self.icons.range, str(rng), (0, 8))
            row += 1
        if target is not None:
            if target == "C":
                self.draw_top_icon(row, self.icons.target)
                self.draw_top_icon_with_icon(
                    row, self.icons.target, self.icons.charge, (0, 0), (-35, 10)
                )
            else:
                self.draw_top_icon_with_text(row, self.icons.target, str(target))
            row += 1
        if ammo is not None:
            self.draw_top_icon_with_text(row, self.icons.ammo, str(ammo))
            row += 1
        if maxcharge is not None:
            self.draw_top_icon_with_text(row, self.icons.maxcharge, str(maxcharge))
            row += 1

    def draw_card_image(self, image: Optional[Image.Image]):
        self.draw_bordered_image(
            image,
            CardRenderer.IMAGE_X,
            CardRenderer.IMAGE_Y,
            CARD_WIDTH - CardRenderer.IMAGE_X - BORDER_MARGIN,
            CardRenderer.IMAGE_HEIGHT,
        )

    def draw_card_type(self, text: str):
        self.draw.text(
            (MARGIN, CardRenderer.CARD_TYPE_TEXT_Y),
            text,
            "#000000",
            font=self.small_font,
        )

    def draw_flavor_text(self, text: Optional[str]):
        if text is None:
            return
        width_in_characters = int(CARD_WIDTH / (FLAVOR_FONT_SIZE * 0.6)) - 5
        wrapped_text = wrap_text_tagged(text, width_in_characters)
        num_lines = wrapped_text.count("\n") + 1
        self.draw.text(
            (
                MARGIN,
                int(
                    CARD_HEIGHT
                    - ICON_SIZE / 2
                    - num_lines * (FLAVOR_FONT_SIZE + SPACING * 0.8)
                    - SPACING
                ),
            ),
            wrapped_text,
            "#000000",
            font=self.flavor_text_font,
            align="left",
            anchor="la",
            spacing=SPACING,
        )

    def draw_card_rating(
        self,
        rating: int,
        rating_icon: Image.Image,
    ):
        star_size = int(ICON_SIZE / 2)
        star_y = int(CARD_HEIGHT - star_size * 1.2)
        if rating == 1:
            self.image.alpha_composite(
                rating_icon,
                (int(CARD_WIDTH / 2 - star_size / 2), star_y),
            )
        elif rating == 2:
            self.image.alpha_composite(
                rating_icon,
                (int(CARD_WIDTH / 2 - star_size), star_y),
            )
            self.image.alpha_composite(
                rating_icon,
                (int(CARD_WIDTH / 2), star_y),
            )
        elif rating == 3:
            self.image.alpha_composite(
                rating_icon,
                (int(CARD_WIDTH / 2 - star_size / 2), star_y),
            )
            self.image.alpha_composite(
                rating_icon,
                (int(CARD_WIDTH / 2 - 3 * star_size / 2), star_y),
            )
            self.image.alpha_composite(
                rating_icon,
                (int(CARD_WIDTH / 2 + star_size / 2), star_y),
            )


class EquipmentCardRenderer(CardRenderer):
    NAME_X = int(ICON_SIZE * 2.2)

    def __init__(self, equipment: Equipment, icons: Icons):
        super().__init__(icons, equipment.filename)
        self.equipment = equipment

    def render(self):
        self.draw_border()
        self.draw_name(
            self.equipment.name,
            self.get_name_color(),
        )
        self.draw_top_icons(
            self.equipment.heat,
            self.equipment.range,
            self.equipment.target,
            self.equipment.ammo,
            self.equipment.maxcharge,
        )
        image_path = f"textures/card-art/{self.equipment.normalized_name}.png"
        if not os.path.exists(image_path):
            image_path = f"textures/card-art/placeholder.png"
        with Image.open(image_path) as img:
            self.draw_card_image(img)
        self.draw_card_type(
            f"{self.equipment.size} {self.equipment.type} {self.equipment.form}"
        )
        self.draw_card_text(
            card_text_sections(self.equipment), MARGIN, CardRenderer.CARD_TEXT_Y
        )
        self.draw_flavor_text(self.equipment.flavor_text)
        self.draw_card_rating(self.equipment.rating_int, self.icons.star)

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


class ManeuverCardRenderer(CardRenderer):
    TEXT_Y = int(CARD_HEIGHT / 2)

    def __init__(self, maneuver: Maneuver, icons: Icons):
        super().__init__(icons, maneuver.filename)
        self.maneuver = maneuver

    def render(self):
        self.draw_border()
        self.draw_name(self.maneuver.name, "#00ff00")
        if self.maneuver.target is not None:
            self.draw_top_icon_with_text(
                0, self.icons.target, str(self.maneuver.target)
            )
        image_path = f"textures/card-art/{self.maneuver.normalized_name}.png"
        if not os.path.exists(image_path):
            image_path = f"textures/card-art/placeholder.png"
        with Image.open(image_path) as img:
            self.draw_card_image(img)
        self.draw_card_type("Maneuver")
        self.draw_card_text(
            card_text_sections(self.maneuver), MARGIN, CardRenderer.CARD_TEXT_Y
        )


class DroneCardRenderer(CardRenderer):
    TEXT_Y = int(CARD_HEIGHT / 2)

    def __init__(self, drone: Drone, icons: Icons):
        super().__init__(icons, drone.filename)
        self.drone = drone

    def render(self):
        self.draw_border()
        self.draw_name(self.drone.name, "#000000")
        row = 0
        if self.drone.range is not None:
            self.draw_top_icon_with_text(
                row, self.icons.range, str(self.drone.range), (0, 10)
            )
            row += 1
        if self.drone.target is not None:
            self.draw_top_icon_with_text(row, self.icons.target, str(self.drone.target))
            row += 1
        image_path = f"textures/card-art/{self.drone.normalized_name}.png"
        if not os.path.exists(image_path):
            image_path = f"textures/card-art/placeholder.png"
        with Image.open(image_path) as img:
            self.draw_card_image(img)
        self.draw_card_type("Drone")
        self.draw_card_text(
            card_text_sections(self.drone), MARGIN, CardRenderer.CARD_TEXT_Y
        )


class KeywordReferenceCardRenderer(CardRenderer):
    def __init__(self, icons: Icons):
        super().__init__(icons, "keywords.png")

    def render(self):
        self.draw_name("Keywords", "#000000")
        self.draw_text()

    def draw_text(self):
        text = """
        <:heat:>Heat.        <:range:>Range.
        <:target:>Target.      <:maxcharge:>Max Charge.
        <:ammo:>Ammo.        <:charge:>Charge.
        <:damage:>Damage.      <:card-rotation:>Cannot Evade.
        <:shield:>Shield: This Round, <:damage:> reduces this before HP.
        <:vulnerable:>Vulnerable: This Round, <:damage:> taken +1, then removed.
        <:overheat:>Overheat: <:heat:> Cost +1.
        <:suppression:>Suppression: This turn, take 1 <:damage:> if the mech does anything.
        Armor: HP damage taken -1.
        AP: <:damage:> ignores Armor.
        Shred: Permanent Armor -1. If no Armor, inflict 1 <:vulnerable:>.
        Disable: This Round, Equipment cannot be used.
        Inert: Cannot be Disabled.
        Prepare: Next turn, you must perform the listed Action.
        """
        text = dedent(text)
        lines = text.split("\n")
        width_in_characters = int(CARD_WIDTH / (SMALL_FONT_SIZE * 0.6)) - 4
        y = CARD_HEIGHT / 24
        for line in lines:
            wrapped_text = wrap_text_tagged(line, width_in_characters)
            newlines = len(wrapped_text.split("\n"))
            self.pilmoji.text(
                (int(CARD_WIDTH / 20), int(y)),
                wrapped_text,
                "#000000",
                font=self.small_font,
                spacing=SPACING,
            )
            y += (
                (SMALL_FONT_SIZE + SPACING) * newlines - SPACING + SMALL_FONT_SIZE * 0.3
            )


class RulesReferenceCardRenderer(CardRenderer):
    def __init__(self, icons: Icons):
        super().__init__(icons, "rules.png")

    def render(self):
        self.draw_name("Turn Reference", "#000000")
        self.draw_text()

    def draw_text(self):
        text = """
        Resolution Order:
        1. Declare your Action or <:trigger:>.
        2. Resolve <:suppression:> if applicable.
        3. Declare <:target:> if applicable.
        4. Opponent chooses to Evade or not if applicable.
        5. Your Action or <:trigger:> resolves.
        Each phase, you may activate any number of <:trigger:>, then your opponent.

        Actions (spends your turn):
        1. Activate any <:action:>.
        2. Play a Maneuver <:action:>.
        3. 1 <:heat:>: Advance or Fall Back.
        4. Declare End of Round for yourself. Next Round, reset <:heat:> and status. Whoever declared first goes first.
        """
        text = dedent(text)
        lines = text.split("\n")
        width_in_characters = int(CARD_WIDTH / (SMALL_FONT_SIZE * 0.6)) - 4
        y = CARD_HEIGHT / 24
        for line in lines:
            wrapped_text = wrap_text_tagged(line, width_in_characters)
            newlines = len(wrapped_text.split("\n"))
            self.pilmoji.text(
                (int(CARD_WIDTH / 20), int(y)),
                wrapped_text,
                "#000000",
                font=self.small_font,
                spacing=SPACING,
            )
            y += (
                (SMALL_FONT_SIZE + SPACING) * newlines - SPACING + SMALL_FONT_SIZE * 0.3
            )


class RegroupingReferenceCardRenderer(CardRenderer):
    def __init__(self, icons: Icons):
        super().__init__(icons, "regrouping.png")

    def render(self):
        self.draw_name("Regrouping", "#000000")
        self.draw_text()

    def draw_text(self):
        text = """
        You must always have at least 1 mech in the front line. If at any point, you do not, perform Regrouping immediately, then continue resolution.

        Regrouping:
        1. Choose at least 1 mech to Advance.
        2. If you cannot legally Advance any mech, choose 1 mech to Advance anyway. It loses 1 HP for each <:heat:> it could not gain.
        """
        text = dedent(text)
        lines = text.split("\n")
        width_in_characters = int(CARD_WIDTH / (SMALL_FONT_SIZE * 0.6)) - 4
        y = CARD_HEIGHT / 24
        for line in lines:
            wrapped_text = wrap_text_tagged(line, width_in_characters)
            newlines = len(wrapped_text.split("\n"))
            self.pilmoji.text(
                (int(CARD_WIDTH / 20), int(y)),
                wrapped_text,
                "#000000",
                font=self.small_font,
                spacing=SPACING,
            )
            y += (
                (SMALL_FONT_SIZE + SPACING) * newlines - SPACING + SMALL_FONT_SIZE * 0.3
            )


class MechRenderer(Renderer):
    STATS_X = MECH_PADDING
    STATS_Y = int(MECH_HEIGHT * 0.6)
    ART_X = int(MECH_PADDING * 2 + TRACKER_SIZE * 10)
    ART_Y = int(MECH_PADDING + HUGE_FONT_SIZE + LARGE_FONT_SIZE)
    ART_W = int(MECH_WIDTH - ART_X - MECH_PADDING * 0.5)
    ART_H = int(MECH_HEIGHT - ART_Y - MECH_PADDING * 4.5)

    def __init__(self, mech: Mech, icons: Icons):
        super().__init__(icons, mech.filename, MECH_WIDTH, MECH_HEIGHT)
        self.mech = mech

    def render(self):
        self.draw_border()
        self.draw_name()
        # image_path = f"textures/mech-art/{self.mech.normalized_name}.png"
        # if not os.path.exists(image_path):
        #    image_path = f"textures/mech-art/placeholder.png"
        self.draw_rectangle(
            MechRenderer.ART_X,
            MechRenderer.ART_Y,
            MechRenderer.ART_W,
            MechRenderer.ART_H,
        )
        self.draw_rectangle(
            int(MECH_PADDING / 2),
            MechRenderer.ART_Y,
            MechRenderer.ART_X - int(MECH_PADDING),
            MechRenderer.ART_H,
        )
        self.draw_flag()
        self.draw_hardpoints()
        self.draw_stats()
        self.draw_engage_circle(
            int(MechRenderer.ART_X - MECH_PADDING - 3 * TRACKER_SIZE),
            int(MechRenderer.STATS_Y - 1.5 * TRACKER_SIZE),
            int(MechRenderer.ART_X - MECH_PADDING),
            int(MechRenderer.STATS_Y + 1.5 * TRACKER_SIZE),
        )
        self.draw_card_text(
            card_text_sections(self.mech),
            int(MECH_PADDING * 1.5),
            int(MECH_HEIGHT * 0.14),
            max_chars=40,
        )

    def get_name_color(self) -> str:
        if self.mech.faction == "Martians":
            return "#ff7f00"
        elif self.mech.faction == "Jovians":
            return "#ff40ff"
        elif self.mech.faction == "Pirates":
            return "#ff0000"
        elif self.mech.faction == "Feds":
            return "#00f0ff"
        return "#000000"

    def draw_name(self):
        text = ImageText.Text(self.mech.designation_name, self.huge_font)
        text.embed_color()
        text.stroke(2, "#000000")
        text.spacing = 10
        self.draw.text(
            (
                MECH_PADDING,
                MECH_PADDING,
            ),
            text,
            self.get_name_color(),
            align="left",
        )

        faction_text = ImageText.Text(
            self.mech.faction_full_name, self.flavor_text_font
        )
        faction_text.stroke(2, "#000000")
        faction_text.spacing = 10
        self.draw.text(
            (
                MECH_PADDING,
                MECH_PADDING + HUGE_FONT_SIZE * 1.2,
            ),
            faction_text,
            "#000000",
            align="left",
        )

    def draw_flag(self):
        image_path = f"textures/flags/{self.mech.faction.lower()}.png"
        with Image.open(image_path) as img:
            ratio = FLAG_HEIGHT / img.height
            width = int(img.width * ratio)
            resized = img.resize((width, FLAG_HEIGHT))
            self.image.alpha_composite(
                resized, (MECH_WIDTH - width - MECH_PADDING, MECH_PADDING)
            )

    def draw_hardpoints(self):
        x = int(MECH_PADDING / 2)
        for hardpoint in self.mech.hardpoints:
            self.draw_hardpoint(x, MECH_HEIGHT - 2 * MECH_PADDING, hardpoint)
            x += CARD_WIDTH + int(MECH_PADDING / 2)

    def draw_hardpoint(self, x: int, y: int, text: str):
        self.draw.line(
            [
                (x, y),
                (x, y + CARD_HEIGHT - 1),
                (x + CARD_WIDTH - 1, y + CARD_HEIGHT - 1),
                (x + CARD_WIDTH - 1, y + 0),
                (x, y),
            ],
            fill="#000000",
            width=2,
        )
        self.draw.text(
            (x + CARD_WIDTH / 2, int(y - LARGE_FONT_SIZE * 0.8)),
            text,
            stroke_width=2,
            stroke_fill="#000000",
            fill="#888888",
            align="center",
            anchor="mm",
            embedded_color=True,
            font=self.large_font,
        )

    def draw_stats(self):
        stats = [
            (f"Armor: {self.mech.armor}", "#888888", 3, None, 0),
            (f"HP", "#009f00", self.mech.hp, "#00ff00", 1),
            (f"Heat", "#9f0000", self.mech.hc, "#ff0000", 0),
        ]
        y = MechRenderer.STATS_Y
        for stat in stats:
            self.draw.text(
                (MechRenderer.STATS_X, y - LARGE_FONT_SIZE * 1.2),
                stat[0],
                stroke_width=2,
                stroke_fill="#000000",
                fill=stat[1],
                align="center",
                anchor="la",
                embedded_color=True,
                font=self.large_font,
            )
            self.draw_tracker(MechRenderer.STATS_X, y, stat[2], stat[3], stat[4])
            y += int(TRACKER_SIZE * 1.75)

    def draw_engage_circle(self, x1: int, y1: int, x2: int, y2: int):
        self.draw.ellipse((x1, y1, x2, y2), outline="#000000")
        self.image.alpha_composite(
            self.icons.engage,
            (int((x1 + x2 - ICON_SIZE) / 2), int((y1 + y2 - ICON_SIZE) / 2)),
        )

    def draw_tracker(
        self, x: int, y: int, boxes: int, color: Optional[str], starting_num: int
    ):
        self.draw_rectangle(x, y, TRACKER_SIZE * boxes, TRACKER_SIZE)
        if color is not None:
            for i in range(0, boxes):
                self.draw.line(
                    [
                        (x + TRACKER_SIZE * i, y),
                        (x + TRACKER_SIZE * i, y + TRACKER_SIZE),
                    ],
                    fill="#000000",
                    width=2,
                )
                self.draw.text(
                    (
                        x + int(TRACKER_SIZE / 2) + TRACKER_SIZE * i,
                        y + int(TRACKER_SIZE / 2),
                    ),
                    str(i + starting_num),
                    stroke_width=2,
                    stroke_fill="#000000",
                    fill=color,
                    align="center",
                    anchor="mm",
                    embedded_color=True,
                    font=self.icon_font,
                )


game_db = GameDatabase()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action")
    parser.add_argument("--filter", "-f", action="append")
    args = parser.parse_args()
    with Icons() as icons:
        if args.action == "equipment" or args.action == "all":
            print("Rendering equipment...")
            if args.filter is None:
                eq_list = game_db.equipment
            else:
                eq_list = game_db.get_filtered_equipment(args.filter)
            for equipment in eq_list:
                with EquipmentCardRenderer(equipment, icons) as card:
                    card.render()
        if args.action == "mechs" or args.action == "all":
            print("Rendering mechs...")
            if args.filter is None:
                eq_list = game_db.mechs
            else:
                eq_list = game_db.get_filtered_mechs(args.filter)
            for mech in eq_list:
                with MechRenderer(mech, icons) as card:
                    card.render()
        if args.action == "maneuvers" or args.action == "all":
            print("Rendering maneuvers...")
            if args.filter is None:
                for maneuver in game_db.maneuvers:
                    with ManeuverCardRenderer(maneuver, icons) as card:
                        card.render()
            else:
                maneuver = game_db.get_maneuver(args.filter[0])
                if maneuver is not None:
                    with ManeuverCardRenderer(maneuver, icons) as card:
                        card.render()
        if args.action == "drones" or args.action == "all":
            print("Rendering drones...")
            for drone in game_db.drones:
                with DroneCardRenderer(drone, icons) as card:
                    card.render()
        if args.action == "references":
            print("Rendering references...")
            with KeywordReferenceCardRenderer(icons) as card:
                card.render()
            with RulesReferenceCardRenderer(icons) as card:
                card.render()
            with RegroupingReferenceCardRenderer(icons) as card:
                card.render()


if __name__ == "__main__":
    main()
