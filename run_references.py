#!/usr/bin/env python3

import argparse
from wand.drawing import Drawing
from wand.image import Image
from wand.color import Color
import re
import os

from game_defs import *
from game_data import *
from card_data import *
from lib import *


turn_reference = """
Turn Order:
1. Declare your Action and targets.
2. Resolve Overwatch.
3. Opponent chooses to Evade or not.
4. Resolve your Action.
5. Player Triggers.
6. Opponent Triggers.

Actions:
1. Activate equipment.
2. Play a maneuver.
3. Advance or Fall Back (1 Heat Cost).
4. Declare End of Round for yourself. Next Round, reset Heat and status, and whoever declared first goes first.
"""

keyword_reference = """
Evade: Requires discarding cards equal to your Evade Counter.
Armor: Damage taken -1.
AP: Ignores Armor.
Shred: Permanent Armor -1.
Shield: Damage reduces this before HP.
Vulnerable: Damage taken +1, then removed.
Overheat: Heat Cost +1.
Disable: Disabled equipment cannot be used.
Inert: Cannot be Disabled.
Overwatch: On opponent's next turn, target takes the effect before it acts if it acts.
Prepare: Next turn, you must perform the listed Action.
Drones: Max 2 Drones.
"""

output_dir = "./outputs/references"


def generate_all():
    os.makedirs(output_dir, exist_ok=True)
    generate_card("Turn Reference", turn_reference)
    generate_card("Keywords", keyword_reference)


def generate_card(name: str, text: str):
    with Image(width=CARD_WIDTH, height=CARD_HEIGHT) as img, Drawing() as draw_ctx:
        draw_border(draw_ctx)
        draw_ctx.font = "fonts/HackNerdFont-Regular.ttf"
        draw_name(draw_ctx, name)
        draw_text(draw_ctx, text)
        draw_ctx.draw(img)
        normalized_name = re.sub(r"\W", "", name).lower()
        img.save(filename=f"{output_dir}/{normalized_name}.png")


def draw_border(draw_ctx: Drawing):
    draw_ctx.push()
    draw_ctx.stroke_color = Color("#000000")
    draw_ctx.stroke_width = 2
    draw_ctx.line((0, 0), (0, CARD_HEIGHT))
    draw_ctx.line((0, 0), (CARD_WIDTH, 0))
    draw_ctx.line((CARD_WIDTH, CARD_HEIGHT), (0, CARD_HEIGHT))
    draw_ctx.line((CARD_WIDTH, CARD_HEIGHT), (CARD_WIDTH, 0))
    draw_ctx.pop()


def draw_name(draw_ctx: Drawing, name: str):
    draw_ctx.push()
    draw_ctx.font = "fonts/HackNerdFont-Bold.ttf"
    draw_ctx.font_size = LARGE_FONT_SIZE
    draw_ctx.stroke_color = Color("#000000")
    draw_ctx.stroke_width = 1
    draw_ctx.fill_color = Color("#aaaaaa")
    draw_ctx.text_alignment = "center"
    wrapped_text = wrap_text(
        draw_ctx,
        name,
        int(CARD_WIDTH * 0.7),
    )
    draw_ctx.text(int(CARD_WIDTH / 2), int(LARGE_FONT_SIZE * 1.2), wrapped_text)
    draw_ctx.pop()


def draw_text(draw_ctx: Drawing, text: str):
    margin = int(TRACKER_SIZE / 2)
    draw_ctx.push()
    draw_ctx.font_size = SMALL_FONT_SIZE
    draw_ctx.fill_color = Color("#000000")
    draw_ctx.text_alignment = "left"
    wrapped_text = wrap_text(draw_ctx, text, CARD_WIDTH - 2 * margin)
    draw_ctx.text(margin, int(CARD_HEIGHT * 0.05), wrapped_text)
    draw_ctx.pop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action")
    args = parser.parse_args()
    print(f"Running reference {args.action}")
    if args.action == "generate":
        generate_all()


main()
