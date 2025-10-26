#!/usr/bin/env python3

import argparse
from wand.drawing import Drawing
from wand.color import Color

from game_defs import *
from game_data import *
from card_data import *
from lib import *


def generate_all():
    with Icons() as icons:
        all_equipment = get_all_equipment()
        for equipment in all_equipment:
            generate_card(icons, equipment)


def generate_card(icons: Icons, equipment: Equipment):
    with Image(
        width=CARD_WIDTH, height=CARD_HEIGHT, background=Color("white")
    ) as img, Drawing() as draw_ctx:
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
        if equipment.range == 0:
            add_icon(
                draw_ctx,
                icons.card_rotation,
                int(CARD_WIDTH / 2 - LARGE_ICON_SIZE / 2),
                int(CARD_HEIGHT - LARGE_ICON_SIZE * 1.1),
                "",
            )
        draw_card_type(draw_ctx, equipment)
        draw_card_text(draw_ctx, equipment)
        draw_ctx.draw(img)
        img.save(filename=equipment.filename)


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
        return Color("#ff40ff")
    elif equipment.type in ["Missile", "Drone", "Nanite"]:
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
    draw_ctx.font = "fonts/HackNerdFont-Bold.ttf"
    draw_ctx.font_size = LARGE_FONT_SIZE
    draw_ctx.stroke_color = Color("#000000")
    draw_ctx.stroke_width = 1
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
        operator="multiply",
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
    print(f"Running equipment {args.action}")
    if args.action == "generate":
        generate_all()
    elif args.action == "genf":
        generate_filtered(args.filter)
    elif args.action == "stats":
        print(equipment_stats())
    elif args.action == "scan":
        print_filtered(args.filter)


main()
