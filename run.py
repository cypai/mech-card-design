#!/usr/bin/env python3

import argparse
import textwrap
from wand.drawing import Drawing
from wand.image import Image
from wand.color import Color

from game_defs import *
from game_data import *

CARD_WIDTH = 1000
CARD_HEIGHT = 1400


class Icons:
    def __init__(self):
        pass

    def __enter__(self):
        self.heat = Image(filename="textures/heat.png")
        self.melee = Image(filename="textures/melee.png")
        self.shortrange = Image(filename="textures/shortrange.png")
        self.midrange = Image(filename="textures/midrange.png")
        self.longrange = Image(filename="textures/longrange.png")
        self.ammo = Image(filename="textures/ammo.png")

        self.heat.resize(100, 100)
        self.melee.resize(100, 100)
        self.shortrange.resize(100, 100)
        self.midrange.resize(100, 100)
        self.longrange.resize(100, 100)
        self.ammo.resize(100, 100)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.heat.close()
        self.melee.close()
        self.shortrange.close()
        self.midrange.close()
        self.longrange.close()
        self.ammo.close()


def print_stats():
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
        "Melee": 0,
        "Short": 0,
        "Mid": 0,
        "Long": 0,
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
    shred_weapons = 0
    total = 0
    all_equipment = get_all_equipment()
    for equipment in all_equipment:
        total += 1
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
        if "Shred" in equipment.text:
            shred_weapons += 1
    print("Sizes")
    for k, v in sizes.items():
        print(f"{k}: {v}")
    print("\nTypes")
    for k, v in types.items():
        print(f"{k}: {v}")
    print("\nFull Types")
    for k, v in full_types.items():
        print(f"{k[0]} {k[1]}: {v}")
    print("\nRanges")
    for k, v in ranges.items():
        print(f"{k}: {v}")
    print("\nRanges by Type")
    for k, v in range_types.items():
        print(f"{k[0]} {k[1]}: {v}")
    print(f"\nAmmo Weapons: {ammo_weapons}")
    print(f"Total Weapons: {total}")


def generate_all():
    with Icons() as icons:
        all_equipment = get_all_equipment()
        for equipment in all_equipment:
            generate_card(icons, equipment)


def generate_card(icons: Icons, equipment: Equipment):
    with Image(width=CARD_WIDTH, height=CARD_HEIGHT) as img, Drawing() as draw_ctx:
        draw_ctx.font = "fonts/Comme-Regular.ttf"
        draw_name(draw_ctx, equipment)
        pad_x = int(CARD_WIDTH * 0.025)
        icon_y = int(CARD_WIDTH * 0.05)
        if equipment.heat is not None:
            add_icon(draw_ctx, icons.heat, pad_x, icon_y, str(equipment.heat))
            icon_y += icons.heat.height + pad_x
        if equipment.range is not None:
            range_icon = None
            if equipment.range == "Melee":
                range_icon = icons.melee
            elif equipment.range == "Short":
                range_icon = icons.shortrange
            elif equipment.range == "Mid":
                range_icon = icons.midrange
            elif equipment.range == "Long":
                range_icon = icons.longrange
            if range_icon is not None:
                add_icon(draw_ctx, range_icon, pad_x, icon_y, "")
                icon_y += range_icon.height + pad_x
        if equipment.ammo is not None:
            add_icon(draw_ctx, icons.ammo, pad_x, icon_y, str(equipment.ammo))
            icon_y += icons.ammo.height + pad_x
        draw_card_type(draw_ctx, equipment)
        draw_card_text(draw_ctx, equipment)
        draw_ctx.draw(img)
        img.save(filename=f"outputs/equipment/{equipment.normalized_name}.png")


def get_color(equipment: Equipment) -> Color:
    if equipment.type == "Ballistic":
        return Color("#ff7f00")
    elif equipment.type == "Energy":
        return Color("#ff00ff")
    elif equipment.type == "Missile" or equipment.type == "Drone":
        return Color("#888888")
    elif equipment.type == "Melee":
        return Color("#FF0000")
    elif equipment.type == "Electronics":
        return Color("#00f0ff")
    elif equipment.type == "Auxiliary":
        return Color("#000000")
    return Color("#000000")


def draw_name(draw_ctx: Drawing, equipment: Equipment):
    draw_ctx.push()
    draw_ctx.font_size = 80
    draw_ctx.stroke_color = Color("#000000")
    draw_ctx.stroke_width = 2
    draw_ctx.fill_color = get_color(equipment)
    wrapped_text = wrap_text(
        draw_ctx,
        equipment.name,
        int(CARD_WIDTH * 0.7),
    )
    draw_ctx.text(220, 130, wrapped_text)
    draw_ctx.pop()


def draw_card_type(draw_ctx: Drawing, equipment: Equipment):
    draw_ctx.push()
    draw_ctx.font_size = 50
    draw_ctx.text(
        int(CARD_WIDTH * 0.05),
        int(CARD_HEIGHT * 0.45),
        f"{equipment.size} {equipment.type} {equipment.system}",
    )
    draw_ctx.pop()


def draw_card_text(draw_ctx: Drawing, equipment: Equipment):
    draw_ctx.push()
    draw_ctx.font_size = 50
    wrapped_text = wrap_text(
        draw_ctx,
        equipment.text,
        int(CARD_WIDTH * 0.9),
    )
    draw_ctx.text(int(CARD_WIDTH * 0.05), int(CARD_HEIGHT * 0.55), wrapped_text)
    draw_ctx.pop()


def wrap_text(ctx: Drawing, text: str, roi_width: int):
    paragraphs = text.splitlines()
    wrapped_paras = []

    estimated_columns = int(roi_width / (ctx.font_size * 0.53))
    wrapper = textwrap.TextWrapper(width=estimated_columns, break_long_words=True)
    for para in paragraphs:
        if para.strip():
            wrapped_paras.extend(wrapper.wrap(para))
        else:
            wrapped_paras.append("\n")

    return "\n".join(wrapped_paras)


def add_icon(draw_ctx: Drawing, icon: Image, x: int, y: int, text: str):
    draw_ctx.push()
    draw_ctx.composite(
        operator="overlay",
        left=x,
        top=y,
        width=icon.width,
        height=icon.height,
        image=icon,
    )
    draw_ctx.pop()
    if text != None and len(text) > 0:
        draw_ctx.push()
        draw_ctx.font_size = int(icon.height * 0.8)
        draw_ctx.text(x + icon.width, y + icon.height - int(icon.height * 0.2), text)
        draw_ctx.pop()


def get_filtered_equipment(filters):
    all_equipment = get_all_equipment()
    matching_equipment = []
    for equipment in all_equipment:
        ok = 0
        for f in filters:
            if (
                f in equipment.text
                or f in equipment.name
                or f == equipment.range
                or f == equipment.type
                or f == equipment.size
            ):
                ok += 1
            elif f == "Ammo" and equipment.ammo:
                ok += 1
        if ok == len(filters):
            matching_equipment.append(equipment)
    return matching_equipment


def print_filtered(filters):
    matching_equipment = get_filtered_equipment(filters)
    for equipment in matching_equipment:
        print(equipment)
    print(f"Found {len(matching_equipment)} matches.")


def generate_filtered(filters):
    matching_equipment = get_filtered_equipment(filters)
    with Icons() as icons:
        for equipment in matching_equipment:
            print(f"Generating card for {equipment.name}...")
            generate_card(icons, equipment)
    print(f"Found {len(matching_equipment)} matches.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action")
    parser.add_argument("--filter", "-f", action="append")
    args = parser.parse_args()
    if args.action == "generate":
        generate_all()
    elif args.action == "genf":
        generate_filtered(args.filter)
    elif args.action == "stats":
        print_stats()
    elif args.action == "scan":
        print_filtered(args.filter)


main()
