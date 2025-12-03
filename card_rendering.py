import math
import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")

from gi.repository import Pango, PangoCairo

surface = cairo.SVGSurface("test.svg", 480, 480)
ctx = cairo.Context(surface)
ctx.set_source_rgb(1, 1, 1)
ctx.rectangle(0, 0, 480, 480)
ctx.fill()

layout = PangoCairo.create_layout(ctx)

font_map = PangoCairo.font_map_get_default()
font_family = font_map.get_family("Hack Nerd Font Mono")
font_face = font_family.get_face("Bold")
font_description = font_face.describe()
font_description.set_size(45 * Pango.SCALE)
layout.set_font_description(font_description)

# Set the origin a little ways into the canvas to give some margin
ctx.translate(16, 16)
# Needed whenever the Cairo context's transformation (or target surface) changes.
PangoCairo.update_layout(ctx, layout)


def draw_text_and_bounds(ctx, layout, text):
    """Returns the text's logical rectangle."""
    layout.set_text(text)

    # The ink_rect gives the bounds of the glyphs in aggregate.  The
    # logical_rect covers the total area of the font; basically the full line.
    #
    # As with all Pango measurements, these are scaled integers.  You need to
    # divide them by Pango.SCALE to get Cairo units.
    ink_rect, logical_rect = layout.get_extents()
    baseline = layout.get_baseline()

    ctx.set_line_width(2)

    # Baseline in orange.  Offset to account for stroke thickness.
    ctx.set_source_rgb(1, 0.5, 0.25)
    ctx.move_to(-8, baseline / Pango.SCALE + 1)
    ctx.line_to(
        (logical_rect.x + logical_rect.width) / Pango.SCALE + 8,
        baseline / Pango.SCALE + 1,
    )
    ctx.stroke()

    # logical rect in red
    ctx.set_source_rgb(0.75, 0, 0)
    ctx.rectangle(
        logical_rect.x / Pango.SCALE - 1,
        logical_rect.y / Pango.SCALE - 1,
        logical_rect.width / Pango.SCALE + 2,
        logical_rect.height / Pango.SCALE + 2,
    )
    ctx.stroke()

    # ink rect in blue
    ctx.set_source_rgb(0, 0, 0.75)
    ctx.rectangle(
        ink_rect.x / Pango.SCALE - 1,
        ink_rect.y / Pango.SCALE - 1,
        ink_rect.width / Pango.SCALE + 2,
        ink_rect.height / Pango.SCALE + 2,
    )
    ctx.stroke()

    # Origin in dark blue
    ctx.set_source_rgb(0, 0, 0.5)
    ctx.arc(0, 0, 2 * math.sqrt(2), 0, 2 * math.pi)
    ctx.fill()

    # Output the text
    ctx.set_source_rgb(0, 0, 0)
    # Since the origin was changed via translation, the text just goes in
    # at (0, 0).
    ctx.move_to(0, 0)
    PangoCairo.show_layout(ctx, layout)

    return logical_rect


logical_rect = draw_text_and_bounds(ctx, layout, "Aa Ee Rr 🔥")

ctx.translate(0, 16 + logical_rect.height / Pango.SCALE)
PangoCairo.update_layout(ctx, layout)

logical_rect = draw_text_and_bounds(ctx, layout, "Bb Gg Jj 🔥")

ctx.translate(0, 16 + logical_rect.height / Pango.SCALE)
PangoCairo.update_layout(ctx, layout)

surface.finish()
surface.flush()
