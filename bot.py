#!/usr/bin/env python3
import os
import sys
import argparse
import textwrap
import logging
import re
import discord
from discord import app_commands
from discord.ext import commands

from game_defs import *
from game_data import *
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
db = BotDatabase()


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

    query_groups = re.findall(r"\[\[([\w\- ]+)\]\]", message.content)
    if len(query_groups) > 0:
        await message.reply(build_query_response(query_groups))

    await bot.process_commands(message)


def build_query_response(queries: list[str]) -> str:
    message = "```\n"
    total = 0
    bad_result_message = ""
    for query in queries:
        results = db.fuzzy_query_name(query, 50)
        good_results = [x for x in results if x[1] > 95]
        if len(good_results) > 0:
            top_result = results[0]
            total += 1
            if top_result[1] == 100:
                message += f"{top_result[0]}\n"
            else:
                message += f"{top_result[0]}\n(Fuzzy match ratio of {top_result[1]} for {query})\n"
        else:
            top_3 = " or ".join(map(lambda x: f"[[{x[0].name}]]", results[:3]))
            bad_result_message += f"[[{query}]] not found. Did you mean: {top_3}?\n"

    message += f"Total matches: {total} of {len(queries)}\n"
    if total != len(queries):
        message += bad_result_message
    message += "```"
    return message


@bot.command()
async def scan_help(ctx: commands.Context):
    help_str = """
    Here's a list of specific keyword filters for equipment scans:
    ```
    Ammo
    Short, Mid, Long, Melee
    Heat[operator][number]
        Examples: Heat=3, Heat>1, Heat<4
    Move```
    You can also filter for text in these categories:
    ```
    Size: Small, Medium, Large
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
    results = get_filtered_equipment([filter_str])
    message = "```\n"
    for equipment in results:
        message += f"{equipment}\n"
    message += f"Found {len(results)} matches.```"
    await interaction.response.send_message(message)


@bot.tree.command(name="mechs")
@app_commands.rename(filter_str="filter")
@app_commands.describe(filter_str="The text to filter on. Use $scan_help for options.")
async def scan_mechs(interaction: discord.Interaction, filter_str: str):
    if filter_str is None or len(filter_str) < 2:
        await interaction.response.send_message(
            "Please provide a filter. Use $scan_help for options."
        )
        return
    results = get_filtered_mechs([filter_str])
    message = "```\n"
    for mech in results:
        message += f"{mech}\n"
    message += f"Found {len(results)} matches.```"
    await interaction.response.send_message(message)


@bot.tree.command(name="drones")
@app_commands.rename(filter_str="filter")
@app_commands.describe(filter_str="The text to filter on. Use $scan_help for options.")
async def scan_drones(interaction: discord.Interaction, filter_str: Optional[str]):
    if filter_str is None or len(filter_str) == 0:
        results = get_filtered_mechs(["Drone"])
    else:
        results = get_filtered_mechs([filter_str, "Drone"])
    message = "```\n"
    for mech in results:
        message += f"{mech}\n"
    message += f"Found {len(results)} matches.```"
    await interaction.response.send_message(message)


@bot.tree.command()
async def maneuvers(interaction: discord.Interaction):
    results = db.maneuvers
    message = "```\n"
    for maneuver in results:
        message += f"{maneuver}\n"
    message += f"Found {len(results)} matches.```"
    await interaction.response.send_message(message)


@bot.tree.command()
async def stats(interaction: discord.Interaction):
    message = f"```\n{equipment_stats()}```"
    await interaction.response.send_message(message)


if args.sync:
    logger.info("All commands:")
    for command in bot.tree.get_commands():
        logger.info(command.name)


bot.run(os.getenv("DISCORD_TOKEN", ""), log_handler=None)
