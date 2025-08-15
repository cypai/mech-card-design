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
    all_maneuvers = get_all_maneuvers()
    for maneuver in all_maneuvers:
        generate_card(maneuver)


def generate_card(maneuver: Maneuver):
    with Image(width=CARD_WIDTH, height=CARD_HEIGHT) as img, Drawing() as draw_ctx:
        draw_border(draw_ctx)
        draw_ctx.font = "fonts/HackNerdFont-Regular.ttf"
        draw_name(draw_ctx, maneuver)
        draw_ability(draw_ctx, maneuver)
        draw_ctx.draw(img)
        img.save(filename=f"outputs/maneuvers/{maneuver.normalized_name}.png")


def draw_border(draw_ctx: Drawing):
    draw_ctx.push()
    draw_ctx.stroke_color = Color("#000000")
    draw_ctx.stroke_width = 2
    draw_ctx.line((0, 0), (0, CARD_HEIGHT))
    draw_ctx.line((0, 0), (CARD_WIDTH, 0))
    draw_ctx.line((CARD_WIDTH, CARD_HEIGHT), (0, CARD_HEIGHT))
    draw_ctx.line((CARD_WIDTH, CARD_HEIGHT), (CARD_WIDTH, 0))
    draw_ctx.pop()


def draw_name(draw_ctx: Drawing, maneuver: Maneuver):
    draw_ctx.push()
    draw_ctx.font = "fonts/HackNerdFont-Bold.ttf"
    draw_ctx.font_size = LARGE_FONT_SIZE
    draw_ctx.stroke_color = Color("#000000")
    draw_ctx.stroke_width = 1
    draw_ctx.fill_color = Color("#00ff00")
    draw_ctx.text_alignment = "center"
    wrapped_text = wrap_text(
        draw_ctx,
        maneuver.name,
        int(CARD_WIDTH * 0.7),
    )
    draw_ctx.text(int(CARD_WIDTH / 2), int(LARGE_FONT_SIZE * 1.2), wrapped_text)
    draw_ctx.pop()


def draw_ability(draw_ctx: Drawing, maneuver: Maneuver):
    margin = int(TRACKER_SIZE * 1.2)
    draw_ctx.push()
    draw_ctx.font_size = SMALL_FONT_SIZE
    draw_ctx.fill_color = Color("#000000")
    draw_ctx.text_alignment = "left"
    wrapped_text = wrap_text(draw_ctx, maneuver.text, CARD_WIDTH - 2 * margin)
    draw_ctx.text(margin, int(CARD_HEIGHT * 0.5), wrapped_text)
    draw_ctx.pop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action")
    args = parser.parse_args()
    print(f"Running maneuvers {args.action}")
    if args.action == "generate":
        generate_all()


main()
