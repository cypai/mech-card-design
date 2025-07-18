#!/usr/bin/env python3

import argparse
from wand.drawing import Drawing
from wand.image import Image
from wand.color import Color

from game_defs import *
from game_data import *
from lib import *

# At 300 DPI
CARD_WIDTH = 750
CARD_HEIGHT = 1050

ICON_SIZE = int(CARD_WIDTH / 10)
LARGE_FONT_SIZE = int(CARD_HEIGHT / 17.5)
SMALL_FONT_SIZE = int(CARD_HEIGHT / 28)


class Icons:
    def __init__(self):
        pass

    def __enter__(self):
        self.heat = Image(filename="textures/heat.png")
        self.melee = Image(filename="textures/melee.png")
        self.range = Image(filename="textures/range.png")
        self.ammo = Image(filename="textures/ammo.png")

        self.heat.resize(ICON_SIZE, ICON_SIZE)
        self.melee.resize(ICON_SIZE, ICON_SIZE)
        self.range.resize(ICON_SIZE, ICON_SIZE)
        self.ammo.resize(ICON_SIZE, ICON_SIZE)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.heat.close()
        self.melee.close()
        self.range.close()
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
    move_systems = 0
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
        for key in keywords.keys():
            if key in equipment.text:
                keywords[key] += 1
        if "remove" not in equipment.text.lower() and (
            "move" in equipment.text.lower() or "reposition" in equipment.text.lower()
        ):
            move_systems += 1
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
        print(f"Range {k}: {v}")
    print("\nRanges by Type")
    for k, v in sorted(range_types.items()):
        print(f"{k[0]} {k[1]}: {v}")
    print(f"\nAmmo Equipment: {ammo_weapons}")
    for k, v in keywords.items():
        print(f"{k} Equipment: {v}")
    print(f"Move Equipment: {move_systems}")
    print(f"Total Equipment: {total}")


def generate_all():
    with Icons() as icons:
        all_equipment = get_all_equipment()
        for equipment in all_equipment:
            generate_card(icons, equipment)


def generate_card(icons: Icons, equipment: Equipment):
    with Image(width=CARD_WIDTH, height=CARD_HEIGHT) as img, Drawing() as draw_ctx:
        draw_border(draw_ctx)
        draw_ctx.font = "fonts/HackNerdFont-Regular.ttf"
        draw_name(draw_ctx, equipment)
        pad_x = int(CARD_WIDTH * 0.025)
        icon_y = int(CARD_WIDTH * 0.05)
        if equipment.heat is not None:
            add_icon(draw_ctx, icons.heat, pad_x, icon_y, str(equipment.heat))
            icon_y += icons.heat.height + pad_x
        if equipment.range is not None:
            range_icon = None
            if equipment.range == 0:
                range_icon = icons.melee
            elif equipment.range:
                range_icon = icons.range
            if range_icon is not None:
                range_num = str(equipment.range) if equipment.range > 0 else ""
                add_icon(draw_ctx, range_icon, pad_x, icon_y, range_num)
                icon_y += range_icon.height + pad_x
        if equipment.ammo is not None:
            add_icon(draw_ctx, icons.ammo, pad_x, icon_y, str(equipment.ammo))
            icon_y += icons.ammo.height + pad_x
        draw_card_type(draw_ctx, equipment)
        draw_card_text(draw_ctx, equipment)
        draw_ctx.draw(img)
        img.save(filename=f"outputs/equipment/{equipment.normalized_name}.png")


def draw_border(draw_ctx: Drawing):
    draw_ctx.push()
    draw_ctx.stroke_color = Color("#000000")
    draw_ctx.stroke_width = 2
    draw_ctx.line((0, 0), (0, CARD_HEIGHT))
    draw_ctx.line((0, 0), (CARD_WIDTH, 0))
    draw_ctx.line((CARD_WIDTH, CARD_HEIGHT), (0, CARD_HEIGHT))
    draw_ctx.line((CARD_WIDTH, CARD_HEIGHT), (CARD_WIDTH, 0))
    draw_ctx.pop()


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
    draw_ctx.font_size = LARGE_FONT_SIZE
    draw_ctx.stroke_color = Color("#000000")
    draw_ctx.stroke_width = 2
    draw_ctx.fill_color = get_color(equipment)
    wrapped_text = wrap_text(
        draw_ctx,
        equipment.name,
        int(CARD_WIDTH * 0.7),
    )
    draw_ctx.text(int(ICON_SIZE * 2.2), int(ICON_SIZE * 1.3), wrapped_text)
    draw_ctx.pop()


def draw_card_type(draw_ctx: Drawing, equipment: Equipment):
    draw_ctx.push()
    draw_ctx.font_size = SMALL_FONT_SIZE
    draw_ctx.text(
        int(CARD_WIDTH * 0.05),
        int(CARD_HEIGHT * 0.45),
        f"{equipment.size} {equipment.type} {equipment.system}",
    )
    draw_ctx.pop()


def draw_card_text(draw_ctx: Drawing, equipment: Equipment):
    draw_ctx.push()
    draw_ctx.font_size = SMALL_FONT_SIZE
    wrapped_text = wrap_text(
        draw_ctx,
        equipment.text,
        int(CARD_WIDTH * 0.9),
    )
    draw_ctx.text(int(CARD_WIDTH * 0.05), int(CARD_HEIGHT * 0.55), wrapped_text)
    draw_ctx.pop()


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
                f != "Move"
                and f.lower() in equipment.text.lower()
                or f in equipment.name
                or f == equipment.range
                or f == equipment.type
                or f == equipment.system
                or f == equipment.size
            ):
                ok += 1
            elif f == "Ammo" and equipment.ammo:
                ok += 1
            elif (
                f == "Move"
                and "remove" not in equipment.text.lower()
                and (
                    "move" in equipment.text.lower()
                    or "reposition" in equipment.text.lower()
                )
            ):
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
