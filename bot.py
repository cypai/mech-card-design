#!/usr/bin/env python3
import os
import argparse
import textwrap
import discord
from discord import app_commands
from discord.ext import commands

from game_defs import *
from game_data import *
from lib import *

parser = argparse.ArgumentParser()
parser.add_argument("--sync", "-s", action="store_true")
args = parser.parse_args()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}.")
    if args.sync:
        print("Syncing CommandTree.")
        await bot.tree.sync()


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
    message = "```"
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
    message = "```"
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
    message = "```"
    for mech in results:
        message += f"{mech}\n"
    message += f"Found {len(results)} matches.```"
    await interaction.response.send_message(message)


@bot.tree.command()
async def maneuvers(interaction: discord.Interaction):
    results = get_all_maneuvers()
    message = "```"
    for maneuver in results:
        message += f"{maneuver}\n"
    message += f"Found {len(results)} matches.```"
    await interaction.response.send_message(message)


@bot.tree.command()
async def stats(interaction: discord.Interaction):
    message = f"```{equipment_stats()}```"
    await interaction.response.send_message(message)


if args.sync:
    print("All commands:")
    for command in bot.tree.get_commands():
        print(command.name)

bot.run(os.getenv("DISCORD_TOKEN", ""))
