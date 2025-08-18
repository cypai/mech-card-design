#!/usr/bin/env python3

import argparse
from wand.drawing import Drawing
from wand.image import Image
from wand.color import Color

from game_defs import *
from game_data import *
from card_data import *
from lib import *


def generate_all():
    all_mechs = get_all_mechs()
    for mech in all_mechs:
        generate_card(mech)


def generate_card(mech: Mech):
    with Image(
        width=CARD_WIDTH, height=CARD_HEIGHT
    ) as img, Icons() as icons, Drawing() as draw_ctx:
        draw_border(draw_ctx)
        draw_ctx.font = "fonts/HackNerdFont-Regular.ttf"
        draw_name(draw_ctx, mech)
        draw_stats(draw_ctx, mech)
        draw_ability(draw_ctx, mech)
        draw_heat(draw_ctx, mech)
        draw_hp(draw_ctx, mech)
        if "card_rotation_icon" in mech.tags:
            draw_card_rotation_icon(draw_ctx, icons)
        draw_ctx.draw(img)
        img.save(filename=mech.filename)


def draw_border(draw_ctx: Drawing):
    draw_ctx.push()
    draw_ctx.stroke_color = Color("#000000")
    draw_ctx.stroke_width = 2
    draw_ctx.line((0, 0), (0, CARD_HEIGHT))
    draw_ctx.line((0, 0), (CARD_WIDTH, 0))
    draw_ctx.line((CARD_WIDTH, CARD_HEIGHT), (0, CARD_HEIGHT))
    draw_ctx.line((CARD_WIDTH, CARD_HEIGHT), (CARD_WIDTH, 0))
    draw_ctx.pop()


def get_color(mech: Mech) -> Color:
    if mech.faction == "Low Tech":
        return Color("#ff7f00")
    elif mech.faction == "High Tech":
        return Color("#ff40ff")
    elif mech.faction == "Midline":
        return Color("#00f0ff")
    elif mech.faction == "Pirate":
        return Color("#FF0000")
    return Color("#000000")


def draw_name(draw_ctx: Drawing, mech: Mech):
    draw_ctx.push()
    draw_ctx.font = "fonts/HackNerdFont-Bold.ttf"
    draw_ctx.font_size = LARGE_FONT_SIZE
    draw_ctx.stroke_color = Color("#000000")
    draw_ctx.stroke_width = 1
    draw_ctx.fill_color = get_color(mech)
    draw_ctx.text_alignment = "center"
    wrapped_text = wrap_text(
        draw_ctx,
        mech.name,
        int(CARD_WIDTH * 0.7),
    )
    draw_ctx.text(int(CARD_WIDTH / 2), int(LARGE_FONT_SIZE * 1.2), wrapped_text)
    draw_ctx.pop()


def draw_hp(draw_ctx: Drawing, mech: Mech):
    draw_ctx.push()
    draw_ctx.font_size = TRACKER_FONT_SIZE
    draw_ctx.stroke_color = Color("#000000")
    draw_ctx.stroke_width = 1
    draw_ctx.fill_color = Color("#00ff00")
    draw_ctx.text_alignment = "center"
    for i in range(1, min(mech.hp + 1, 11)):
        draw_ctx.text(
            int(TRACKER_SIZE / 2), TRACKER_SIZE * i - int(TRACKER_FONT_SIZE / 2), str(i)
        )
        draw_ctx.line((0, TRACKER_SIZE * i), (TRACKER_SIZE, TRACKER_SIZE * i))
    draw_ctx.line((TRACKER_SIZE, 0), (TRACKER_SIZE, CARD_HEIGHT))
    draw_ctx.pop()


def draw_heat(draw_ctx: Drawing, mech: Mech):
    draw_ctx.push()
    draw_ctx.font_size = TRACKER_FONT_SIZE
    draw_ctx.stroke_color = Color("#000000")
    draw_ctx.stroke_width = 1
    draw_ctx.fill_color = Color("#ff0000")
    draw_ctx.text_alignment = "center"
    for i in range(0, mech.hc + 1):
        draw_ctx.text(
            CARD_WIDTH - int(TRACKER_SIZE / 2),
            TRACKER_SIZE * (i + 1) - int(TRACKER_FONT_SIZE / 2),
            str(i),
        )
        draw_ctx.line(
            (CARD_WIDTH - TRACKER_SIZE, TRACKER_SIZE * (i + 1)),
            (CARD_WIDTH, TRACKER_SIZE * (i + 1)),
        )
    draw_ctx.line(
        (CARD_WIDTH - TRACKER_SIZE, 0), (CARD_WIDTH - TRACKER_SIZE, CARD_HEIGHT)
    )
    draw_ctx.pop()


def draw_stats(draw_ctx: Drawing, mech: Mech):
    margin = int(TRACKER_SIZE * 1.2)
    draw_ctx.push()
    draw_ctx.font_size = LARGE_FONT_SIZE
    draw_ctx.fill_color = Color("#000000")
    draw_ctx.push()
    draw_ctx.text_alignment = "left"
    draw_ctx.text(margin, int(LARGE_FONT_SIZE * 3), f"HP:{mech.hp}")
    draw_ctx.text(margin, int(LARGE_FONT_SIZE * 4.5), f"Armor:{mech.armor}")
    # This draws armor pips, commented out for now
    # if mech.armor > 0:
    #     for a in range(mech.armor):
    #         draw_ctx.composite(
    #             operator="overlay",
    #             left=int(CARD_WIDTH * 0.47 + a * icons.armor.width * 1.4),
    #             top=int(LARGE_FONT_SIZE * 4.5 - icons.armor.height * 0.9),
    #             width=icons.armor.width,
    #             height=icons.armor.height,
    #             image=icons.armor,
    #         )
    draw_ctx.pop()
    if len(mech.hardpoints_str) > 0:
        draw_ctx.push()
        draw_ctx.text_alignment = "center"
        draw_ctx.text(
            int(CARD_WIDTH / 2), int(LARGE_FONT_SIZE * 6), mech.hardpoints_str
        )
        draw_ctx.pop()
    draw_ctx.push()
    draw_ctx.text_alignment = "right"
    draw_ctx.text(CARD_WIDTH - margin, int(LARGE_FONT_SIZE * 3), f"Heat:{mech.hc}")
    draw_ctx.pop()
    draw_ctx.pop()


def draw_ability(draw_ctx: Drawing, mech: Mech):
    margin = int(TRACKER_SIZE * 1.2)
    draw_ctx.push()
    draw_ctx.font_size = SMALL_FONT_SIZE
    draw_ctx.fill_color = Color("#000000")
    draw_ctx.text_alignment = "left"
    wrapped_text = wrap_text(draw_ctx, mech.ability, CARD_WIDTH - 2 * margin)
    draw_ctx.text(margin, int(CARD_HEIGHT * 0.5), wrapped_text)
    draw_ctx.pop()


def draw_card_rotation_icon(draw_ctx: Drawing, icons: Icons):
    icon = icons.card_rotation
    draw_ctx.push()
    draw_ctx.composite(
        operator="overlay",
        left=int(CARD_WIDTH / 2 - icon.width / 2),
        top=int(CARD_HEIGHT - icon.height * 1.1),
        width=icon.width,
        height=icon.height,
        image=icon,
    )
    draw_ctx.pop()


def print_filtered(filters):
    matching_mechs = get_filtered_mechs(filters)
    for mech in matching_mechs:
        print(mech)
    print(f"Found {len(matching_mechs)} matches.")


def generate_filtered(filters):
    matching_mechs = get_filtered_mechs(filters)
    for mech in matching_mechs:
        print(f"Generating card for {mech.name}...")
        generate_card(mech)
    print(f"Found {len(matching_mechs)} matches.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action")
    parser.add_argument("--filter", "-f", action="append")
    args = parser.parse_args()
    print(f"Running mechs {args.action}")
    if args.action == "generate":
        generate_all()
    elif args.action == "genf":
        generate_filtered(args.filter)
    elif args.action == "scan":
        print_filtered(args.filter)


main()
