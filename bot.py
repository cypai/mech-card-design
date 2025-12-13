#!/usr/bin/env python3
import os
import sys
import argparse
import textwrap
import logging
import re
import io
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands

from game_defs import *
from game_data import *
from run_changelog import generate_changelog_text
from lib import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)
logger.info("Starting discord-bot.")

parser = argparse.ArgumentParser()
parser.add_argument("--sync", "-s", action="store_true")
args = parser.parse_args()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)
db = GameDatabase()

QUERY_REGEX = re.compile(r"\[\[([\w\- :]+)\]\]")
RENDER_REGEX = re.compile(r"\{\{([\w\- :]+)\}\}")


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}.")
    if args.sync:
        logger.info("Syncing CommandTree.")
        await bot.tree.sync()


@bot.event
async def on_message(message: discord.Message):
    if bot.user is not None and message.author.id == bot.user.id:
        return

    query_groups = re.findall(QUERY_REGEX, message.content)
    if len(query_groups) > 0:
        await message.reply(build_query_response(query_groups))
    render_groups = re.findall(RENDER_REGEX, message.content)
    if len(render_groups) > 0:
        reply_msg, pngs = build_render_response(render_groups)
        await message.reply(reply_msg, files=pngs)

    await bot.process_commands(message)


def build_query_response(queries: list[str]) -> str:
    message = "```\n"
    total = 0
    bad_result_message = ""
    for query in queries:
        results = db.fuzzy_query_name(query, 50)
        good_results = [x for x in results if x[1] > 90]
        if len(good_results) > 0:
            top_result = results[0]
            total += 1
            if top_result[1] == 100:
                message += f"{top_result[0]}\n"
            else:
                message += f"(Fuzzy match ratio of {top_result[1]} for {query})\n{top_result[0]}\n"
        else:
            top_3 = " or ".join(map(lambda x: f"[[{x[0].name}]]", results[:3]))
            bad_result_message += f"[[{query}]] not found. Did you mean: {top_3}?\n"

    message += f"Total matches: {total} of {len(queries)}\n"
    if total != len(queries):
        message += bad_result_message
    message += "```"
    return message


def build_render_response(queries: list[str]) -> tuple[str, list[discord.File]]:
    message = "```\nCard PNGs for: "
    bad_result_message = ""
    cards: list[tuple[Equipment | Mech | Maneuver | Drone, int]] = []
    for query in queries:
        results = db.fuzzy_query_name(query, 50)
        good_results = [x for x in results if x[1] > 90]
        if len(good_results) > 0:
            top_result = results[0]
            cards.append(top_result)
        else:
            top_3 = " or ".join(map(lambda x: f"{{{{{x[0].name}}}}}", results[:3]))
            bad_result_message += f"{{{{{query}}}}} not found. Did you mean: {top_3}?\n"
    name_list = [
        card[0].name + ("" if card[1] == 100 else f" (fuzzy {card[1]})")
        for card in cards
    ]
    message += ", ".join(name_list) + "\n"
    if len(cards) != len(queries):
        message += bad_result_message
    message += "```"
    pngs = [discord.File(card[0].filename) for card in cards]
    return message, pngs


async def reply(
    api: Union[commands.Context, discord.Interaction],
    message: str,
    fallback_filename: str = "results.txt",
):
    discord_file = discord.File(
        io.BytesIO(message.encode("utf-8")), filename=fallback_filename
    )
    fallback_msg = "Reply too long. txt file attached."
    if isinstance(api, commands.Context):
        if len(message) >= 2000:
            await api.reply(fallback_msg, file=discord_file)
        else:
            await api.reply(f"```\n{message}```")
    elif isinstance(api, discord.Interaction):
        if len(message) >= 2000:
            await api.response.send_message(fallback_msg, file=discord_file)
        else:
            await api.response.send_message(f"```\n{message}```")


@bot.command()
async def scan_help(ctx: commands.Context):
    help_str = """
    Here's a list of specific keyword filters for equipment scans:
    ```
    Ammo
    Short, Mid, Long, Melee
    Heat[operator][number]
        Examples: Heat=3, Heat>1, Heat<4
    Range[operator][number]
        Examples: Range=3, Range>1, Range<2
    Move```
    You can also filter for text in these categories:
    ```
    Size: Small, Medium, Large
    Type: Ballistic, Energy, Missile, Electronics, Drone, Auxiliary
    System: Weapon, System
    Name
    Card Text
    Tags: AOE```
    For mechs:
    ```
    Name
    Factions: Feds, Ares, Jovians, Pirates
    Hardpoints: Large, Medium, Small
    Ability
    Heat[operator][number]
        Examples: Heat=3, Heat>1, Heat<4
    HP[operator][number]
        Examples: HP=3, HP>1, HP<4
    ```
    """
    help_str = textwrap.dedent(help_str)
    await ctx.reply(help_str, ephemeral=True)


@bot.tree.command(name="equipment")
@app_commands.rename(filter_str="filter")
@app_commands.describe(filter_str="The text to filter on. Use $scan_help for options.")
async def scan_equipment(interaction: discord.Interaction, filter_str: str):
    if filter_str is None or len(filter_str) < 2:
        await interaction.response.send_message(
            "Please provide a filter. Use $scan_help for options."
        )
        return
    filters = filter_str.split(",")
    results = get_filtered_equipment(filters)
    message = ""
    for equipment in results:
        message += f"{equipment}\n"
    message += f"Found {len(results)} matches."
    await reply(
        interaction,
        message,
        "equipment.txt",
    )


@bot.tree.command(name="mechs")
@app_commands.rename(filter_str="filter")
@app_commands.describe(filter_str="The text to filter on. Use $scan_help for options.")
async def scan_mechs(interaction: discord.Interaction, filter_str: str):
    if filter_str is None or len(filter_str) < 2:
        await interaction.response.send_message(
            "Please provide a filter. Use $scan_help for options."
        )
        return
    filters = filter_str.split(",")
    results = get_filtered_mechs(filters)
    message = ""
    for mech in results:
        message += f"{mech}\n"
    message += f"Found {len(results)} matches."
    await reply(
        interaction,
        message,
        "mechs.txt",
    )


@bot.tree.command()
async def drones(interaction: discord.Interaction):
    results = db.drones
    message = ""
    for drone in results:
        message += f"{drone}\n"
    message += f"Found {len(results)} matches."
    await reply(
        interaction,
        message,
        "drones.txt",
    )


@bot.tree.command()
async def maneuvers(interaction: discord.Interaction):
    results = db.maneuvers
    message = ""
    for maneuver in results:
        message += f"{maneuver}\n"
    message += f"Found {len(results)} matches."
    await reply(
        interaction,
        message,
        "maneuvers.txt",
    )


@bot.command()
async def changelog(ctx: commands.Context):
    message = generate_changelog_text()
    await reply(ctx, message, "changelog.txt")


@bot.tree.command()
async def stats(interaction: discord.Interaction):
    message = equipment_stats()
    await reply(interaction, message, "stats.txt")


@bot.tree.command()
async def watchlist(interaction: discord.Interaction):
    strong = db.get_filtered_equipment(["Strong-Watchlist"])
    weak = db.get_filtered_equipment(["Weak-Watchlist"])
    message = "Strong Watchlist\n"
    message += "----------------\n"
    for item in strong:
        message += f"{item}\n"
    message += "\nWeak Watchlist\n"
    message += "--------------\n"
    for item in weak:
        message += f"{item}\n"
    await reply(interaction, message, "watchlist.txt")


@bot.command()
async def strong(ctx: commands.Context):
    strong = db.get_filtered_equipment(["Strong-Watchlist"])
    message = "Strong Watchlist\n"
    message += "----------------\n"
    for item in strong:
        message += f"{item}\n"
    await reply(ctx, message, "strong_watchlist.txt")


@bot.command()
async def weak(ctx: commands.Context):
    weak = db.get_filtered_equipment(["Weak-Watchlist"])
    message = "Weak Watchlist\n"
    message += "--------------\n"
    for item in weak:
        message += f"{item}\n"
    await reply(ctx, message, "weak_watchlist.txt")


@bot.command()
async def sus(ctx: commands.Context):
    sus = db.get_filtered_equipment(["Sus"])
    message = "Sus Watchlist\n"
    message += "-------------\n"
    for item in sus:
        message += f"{item}\n"
    await reply(ctx, message, "sus_watchlist.txt")


@bot.command()
async def tutorial(ctx: commands.Context):
    message = """
    Feds
    ----
    Lancelot
    - Large: Arondight Starsword (Teaches Melee and Armor damage reduction)
    - Medium: Empty
    - Small: Shield Generator (Teaches Shield and Trigger)

    Guanyin
    - Medium: Gauss Rifle (Teaches AP and Vulnerable)
    - Medium: Empty
    - Small: Breach Missile (Teaches Ammo and Shred)
    - Small: Empty

    Ares
    ----
    Wolfblade
    - Large: Empty
    - Medium: Power Fist (Teaches Melee, forced movement, and that Larger doesn't always mean better)
    - Small: Cyberwarfare: EPIDEMIC (Teaches Charge and Do something X times)

    Mahout
    - Large: Mjolnir Railgun (Teaches Range and Disable)
    - Large: Empty
    - Small: Leading Crosshairs (Teaches Range and Trigger)

    Each player has 3 cards in hand, 1 of which is an Airstrike.
    """
    message = textwrap.dedent(message)
    await reply(ctx, message, "tutorial.txt")


@bot.command()
async def db_init(ctx: commands.Context):
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("create table usage(name, timestamp)")
        await reply(ctx, "DB Initialized.")


@bot.command()
async def db_add_usage(ctx: commands.Context, *, arg: str):
    names = arg.split(",")
    names = [name.strip() for name in names]
    actual_names = []
    bad_matches: list[
        tuple[str, list[tuple[Union[Equipment, Mech, Drone, Maneuver], int]]]
    ] = []
    for name in names:
        matches = db.fuzzy_query_name(name, 50)
        if len(matches) == 0 or matches[0][1] < 90:
            bad_matches.append((name, matches))
        else:
            actual_names.append(matches[0][0].name)
    if len(bad_matches) == 0:
        with sqlite3.connect("data.db") as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "insert into usage values(?, date())", [(x,) for x in actual_names]
            )
        message = "Added usage for the following cards:\n"
        for name in actual_names:
            message += f"{name}\n"
        await reply(ctx, message)
    else:
        message = "Not all cards were found. Bad inputs:\n"
        for match in bad_matches:
            options = [option[0].name for option in match[1][:3]]
            options_str = " or ".join(options)
            message += f"{match[0]} not found. Did you mean: {options_str}"
        await reply(ctx, message)


@bot.command()
async def db_usage(ctx: commands.Context, *, name: str):
    results = db.fuzzy_query_name(name, 50)
    if len(results) == 0 or results[0][1] < 90:
        options = [x[0].name for x in results]
        options_str = " or ".join(options)
        message = f"{name} not found. Did you mean: {options_str}"
        await reply(ctx, message)
    else:
        result = results[0][0]
        with sqlite3.connect("data.db") as conn:
            cursor = conn.cursor()
            cursor.execute("select count(*) from usage where name = ?", (result.name,))
            count = cursor.fetchall()[0][0]
            message = f"{result.name} usage: {count}\nUsage times:\n"
            cursor.execute("select timestamp from usage where name = ?", (result.name,))
            rows = cursor.fetchall()
            for row in rows:
                message += f"{row[0]}\n"
            await reply(ctx, message)


@bot.command()
async def db_clear_usage(ctx: commands.Context, *, name: str):
    results = db.fuzzy_query_name(name, 50)
    if len(results) == 0 or results[0][1] < 90:
        options = [x[0].name for x in results]
        options_str = " or ".join(options)
        message = f"{name} not found. Did you mean: {options_str}"
        await reply(ctx, message)
    else:
        result = results[0][0]
        with sqlite3.connect("data.db") as conn:
            cursor = conn.cursor()
            cursor.execute("delete from usage where name = ?", (result.name,))
            await reply(ctx, f"Usage for {result.name} cleared.")


@bot.command()
async def db_usage_distribution(ctx: commands.Context):
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "select name, count(*) from usage group by name order by count(*) desc"
        )
        results = cursor.fetchall()
        equipment_message = ""
        mechs_message = ""
        maneuvers_message = ""
        for row in results:
            name, count = row
            if db.get_equipment(name) is not None:
                equipment_message += f"{name}: {count}\n"
            elif db.get_mech(name) is not None:
                mechs_message += f"{name}: {count}\n"
            elif db.get_maneuver(name) is not None:
                maneuvers_message += f"{name}: {count}\n"
        message = f"Equipment:\n{equipment_message}\nMechs:\n{mechs_message}\nManeuvers:\n{maneuvers_message}"
        await reply(ctx, message)


@bot.command()
async def db_zero_usage(ctx: commands.Context):
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("select name, count(*) from usage group by name")
        results = cursor.fetchall()
    usage = [row[0] for row in results]
    zero_usage = [
        e for e in db.equipment + db.mechs + db.maneuvers if e.name not in usage
    ]
    message = "The following cards has 0 usage so far:\n"
    for item in zero_usage:
        message += f"{item.name}\n"
    await reply(ctx, message, "zero_usage.txt")


@bot.command()
async def db_migrate_usage(ctx: commands.Context, previous: str, current: str):
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("update usage set name = ? where name = ?", (current, previous))
    await reply(ctx, f"Updated usage from {previous} to {current}.")


if args.sync:
    logger.info("All commands:")
    for command in bot.tree.get_commands():
        logger.info(command.name)


bot.run(os.getenv("DISCORD_TOKEN", ""), log_handler=None)
