#!/usr/bin/env python3
import os
import sys
import argparse
import textwrap
import logging
import re
import io
import csv
import sqlite3
import discord
from discord import ForumChannel, ForumTag, Thread, app_commands
from discord.ext import commands

from game_defs import *
from game_data import *
from card_rendering import EquipmentCardRenderer, Icons
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
MANEUVER_STRING_REGEX = re.compile(r"\s*([^,]+?)\s*(?:,|$)")


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
        results = db.fuzzy_query_name(query, 90)
        if results.ok:
            top_result = results.actual
            total += 1
            if results.threshold == 100:
                message += f"{top_result}\n"
            else:
                message += f"(Fuzzy match ratio of {results.threshold} for {query})\n{top_result}\n"
        else:
            top_3 = " or ".join(map(lambda x: f"[[{x.name}]]", results.options))
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
        results = db.fuzzy_query_name(query, 90)
        if results.ok:
            cards.append((results.actual, results.threshold))
        else:
            top_3 = " or ".join(map(lambda x: f"{{{{{x.name}}}}}", results.options))
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
    Factions: Feds, Martians, Jovians, Pirates
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
async def aka(ctx: commands.Context, *, query: str):
    matches = db.fuzzy_query_name(query, 90)
    if not matches.ok:
        options = [opt.name for opt in matches.options]
        options_str = " or ".join(options)
        message = f"{query} not found. Did you mean: {options_str}"
        await reply(ctx, message)
        return
    actual = matches.actual
    if matches.threshold == 100:
        message = f"Aliases for {actual.name}:\n"
    else:
        message = f"Aliases for {actual.name} (fuzzy {matches.threshold}):\n"
    if isinstance(actual, Equipment):
        for alias in actual.alias:
            message += f"{alias}\n"
    await reply(ctx, message)


@bot.command()
async def render(ctx: commands.Context, query: str, flavor_text: str):
    matches = db.fuzzy_query_name(query, 90)
    if not matches.ok:
        options = [opt.name for opt in matches.options]
        options_str = " or ".join(options)
        message = f"{query} not found. Did you mean: {options_str}"
        await reply(ctx, message)
        return
    actual = matches.actual
    if isinstance(actual, Equipment):
        if matches.threshold == 100:
            message = f"Running live render for {actual.name}."
        else:
            message = (
                f"Running live render for {actual.name} (fuzzy {matches.threshold})."
            )
        await reply(ctx, message)
        processed_flavor_text = flavor_text.replace("\\n", "\n")
        actual.flavor_text = processed_flavor_text
        actual.filename = f"outputs/live_render.png"
        with Icons() as icons, EquipmentCardRenderer(actual, icons) as card:
            card.render()
        await ctx.reply(f"Rendered result:", file=discord.File(actual.filename))
    else:
        await reply(ctx, f"Live render not yet supported for non-Equipment.")


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

    Martians
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
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute("""
        create table if not exists battles(
            id integer primary key,
            winner integer not null,
            player1 text not null,
            player2 text not null,
            timestamp datetime default current_timestamp
        );
        """)
        cursor.execute("""
        create table if not exists mech_drafts(
            id integer primary key,
            battle_id integer not null,
            player integer not null,
            name text not null,
            foreign key(battle_id) references battles(id) on delete cascade
        );
        """)
        cursor.execute("""
        create table if not exists equipment_drafts(
            id integer primary key,
            mech_draft_id integer not null,
            name text not null,
            foreign key(mech_draft_id) references mech_drafts(id) on delete cascade
        );
        """)
        cursor.execute("""
        create table if not exists maneuver_drafts(
            id integer primary key,
            battle_id integer not null,
            player integer not null,
            name text not null,
            foreign key(battle_id) references battles(id) on delete cascade
        );
        """)
        await reply(ctx, "DB Initialized.")


@bot.command()
async def db_add_battle(
    ctx: commands.Context,
    player1: str,
    player2: str,
    winner: int,
    timestamp: str | None = None,
):
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        if timestamp is None:
            cursor.execute(
                "insert into battles(winner, player1, player2) values (?, ?, ?)",
                (winner, player1, player2),
            )
        else:
            cursor.execute(
                "insert into battles(winner, player1, player2, timestamp) values (?, ?, ?, ?)",
                (winner, player1, player2, timestamp),
            )
        rowid = cursor.lastrowid
    await reply(ctx, f"Created new battle with id {rowid}.")


@db_add_battle.error
async def db_add_battle_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await reply(ctx, "winner (1 or 2) is a required argument.")
    else:
        logger.error(error)
        await reply(ctx, str(error))


@bot.command()
async def db_add_draft(ctx: commands.Context, battle_id: int, player: int, *args):
    """
    $db_add_draft 12 2 "Jolly Roger@Reserved Rifle,Drone Command Nexus" "Cockroach@Heavy Assault Cannon" "Airstrike"
    """
    if player not in [1, 2]:
        message = f"Player {player} should be 1 or 2"
        await reply(ctx, message)
        return

    with sqlite3.connect("data.db") as conn:
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()

        cursor.execute("select * from battles where id = ?", (battle_id,))
        if len(cursor.fetchall()) == 0:
            message = f"Battle {battle_id} not found."
            await reply(ctx, message)
            return

        mech_rows: list[tuple[str, list[str]]] = []
        maneuver_rows: list[str] = []
        bad_matches: list[
            tuple[str, list[tuple[Union[Equipment, Mech, Drone, Maneuver], int]]]
        ] = []

        def handle_match(name: str):
            matches = db.fuzzy_query_name(name, 90)
            if matches.ok:
                return matches.actual
            else:
                bad_matches.append((name, matches.raw_results))
                return None

        for draft_string in args:
            if "@" in draft_string:
                splitted = draft_string.split("@")
                mech_name = splitted[0].strip()
                equipment_str = splitted[1].split(",")
                equipment_names = [
                    x.strip() for x in equipment_str if len(x.strip()) > 0
                ]
                mech = handle_match(mech_name)
                if (
                    isinstance(mech, Maneuver)
                    or isinstance(mech, Equipment)
                    or isinstance(mech, Drone)
                ):
                    message = f"Found non-mech specified as mech: {mech.name}"
                    await reply(ctx, message)
                    return

                equipments = [handle_match(x) for x in equipment_names]
                actual_equipments = [
                    x.name for x in equipments if isinstance(x, Equipment)
                ]
                non_equipments = [
                    x.name
                    for x in equipments
                    if isinstance(x, Mech)
                    or isinstance(x, Maneuver)
                    or isinstance(x, Drone)
                ]
                if len(non_equipments) > 0:
                    message = (
                        f"Found non-equipment attached to a mech: {non_equipments}"
                    )
                    await reply(ctx, message)
                    return
                if isinstance(mech, Mech) and all(
                    isinstance(equipment, Equipment) for equipment in equipments
                ):
                    mech_rows.append((mech.name, actual_equipments))
            else:
                maneuver_groups = re.findall(MANEUVER_STRING_REGEX, draft_string)
                maneuver_names = [
                    x.strip() for x in maneuver_groups if len(x.strip()) > 0
                ]
                for name in maneuver_names:
                    maneuver = handle_match(name)
                    if isinstance(maneuver, Maneuver):
                        maneuver_rows.append(maneuver.name)
                    elif (
                        isinstance(maneuver, Mech)
                        or isinstance(maneuver, Equipment)
                        or isinstance(maneuver, Drone)
                    ):
                        message = (
                            f"Found non-maneuver specified as maneuver: {maneuver.name}"
                        )
                        await reply(ctx, message)
                        return

        if len(bad_matches) == 0:
            cursor.execute(
                "delete from mech_drafts where battle_id = ? and player = ?",
                (battle_id, player),
            )
            cursor.execute(
                "delete from maneuver_drafts where battle_id = ? and player = ?",
                (battle_id, player),
            )
            message = "Added usage for the following:"
            for m in mech_rows:
                cursor.execute(
                    "insert into mech_drafts(battle_id, player, name) values (?, ?, ?)",
                    (battle_id, player, m[0]),
                )
                mech_rowid = cursor.lastrowid
                message += f"\n{m[0]}"
                for eq in m[1]:
                    cursor.execute(
                        "insert into equipment_drafts(mech_draft_id, name) values (?, ?)",
                        (mech_rowid, eq),
                    )
                    message += f"\n- {eq}"

            cursor.executemany(
                "insert into maneuver_drafts(battle_id, player, name) values(?, ?, ?)",
                [(battle_id, player, x) for x in maneuver_rows],
            )
            for m in maneuver_rows:
                message += f"\n{m}"
            await reply(ctx, message)
        else:
            message = "Not all cards were found. Bad inputs:"
            for match in bad_matches:
                options = [option[0].name for option in match[1][:3]]
                options_str = " or ".join(options)
                message += f"\n{match[0]} not found. Did you mean: {options_str}"
            await reply(ctx, message)


@bot.command()
async def db_battle(ctx: commands.Context, battle_id: int):
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "select winner, player1, player2, timestamp from battles where id = ?",
            (battle_id,),
        )
        row = cursor.fetchone()
        winner, player1, player2, timestamp = row
        message = f"Battle {battle_id} on {timestamp}:\n{player1} vs {player2}\nWinner was Player {winner} ({player1 if winner == 1 else player2})"
        cursor.execute(
            "select m.name, m.player from maneuver_drafts m where battle_id = ? order by m.player asc",
            (battle_id,),
        )
        maneuver_rows = cursor.fetchall()
        cursor.execute(
            """
            select m.player, m.name, e.name
            from mech_drafts m
            join equipment_drafts e
            on e.mech_draft_id = m.id
            where m.battle_id = ?
            order by m.player asc, m.name asc, e.name asc""",
            (battle_id,),
        )
        mech_draft_rows = cursor.fetchall()
        prev_player, prev_mech = (None, None)
        for row in mech_draft_rows:
            curr_player, curr_mech, equipment = row
            if curr_player != prev_player:
                if curr_player == 2:
                    for maneuver in [m for m in maneuver_rows if m[1] == 1]:
                        message += f"\n{maneuver[0]}"
                message += f"\n\nPlayer {curr_player}"
                prev_player = curr_player
            if curr_mech != prev_mech:
                message += f"\n{curr_mech}"
                prev_mech = curr_mech
            message += f"\n- {equipment}"
        for maneuver in [m for m in maneuver_rows if m[1] == 2]:
            message += f"\n{maneuver[0]}"
        await reply(ctx, message)


@bot.command()
async def db_zero_usage(ctx: commands.Context):
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("select name, count(*) from mech_drafts group by name")
        results = cursor.fetchall()
        cursor.execute("select name, count(*) from equipment_drafts group by name")
        results += cursor.fetchall()
        cursor.execute("select name, count(*) from maneuver_drafts group by name")
        results += cursor.fetchall()
    usage = [row[0] for row in results]
    zero_usage = [
        e for e in db.equipment + db.mechs + db.maneuvers if e.name not in usage
    ]
    message = "The following cards has 0 usage so far:\n"
    for item in zero_usage:
        message += f"{item.name}\n"
    await reply(ctx, message, "zero_usage.txt")


@bot.command()
async def db_query(ctx: commands.Context, *, query: str):
    matches = db.fuzzy_query_name(query, 90)
    if not matches.ok:
        options = [opt.name for opt in matches.options]
        options_str = " or ".join(options)
        message = f"{query} not found. Did you mean: {options_str}"
        await reply(ctx, message)
        return
    actual = matches.actual
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        message = f"Stats for {actual.name}:"
        if isinstance(actual, Mech):
            cursor.execute(
                """
                select m.battle_id, m.player, b.winner, b.timestamp
                from mech_drafts m
                join battles b
                on m.battle_id = b.id
                where m.name = ?
                order by b.timestamp desc
            """,
                (actual.name,),
            )
        elif isinstance(actual, Equipment):
            cursor.execute(
                """
                select m.battle_id, m.player, b.winner, b.timestamp
                from equipment_drafts e
                join mech_drafts m
                on e.mech_draft_id = m.id
                join battles b
                on m.battle_id = b.id
                where e.name = ?
                order by b.timestamp desc
            """,
                (actual.name,),
            )
        elif isinstance(actual, Maneuver):
            cursor.execute(
                """
                select m.battle_id, m.player, b.winner, b.timestamp
                from maneuver_drafts m
                join battles b
                on m.battle_id = b.id
                where m.name = ?
                order by b.timestamp desc
            """,
                (actual.name,),
            )
        battle_messages = ""
        wins = 0
        wins_going_first = 0
        wins_going_second = 0
        going_first = 0
        going_second = 0
        rows = cursor.fetchall()
        total = len(rows)
        for row in rows:
            battle_id, player, winner, timestamp = row
            won = "won" if player == winner else "lost"
            if player == winner:
                wins += 1
                if player == 1:
                    wins_going_first += 1
                else:
                    wins_going_second += 1
            if player == 1:
                going_first += 1
            else:
                going_second += 1
            battle_messages += f"\nBattle {battle_id} {won} on {timestamp}"
        if total > 0:
            message += f"\nTotal usage: {total}"
            message += f"\nOverall win rate: {wins}/{total}: {int(wins/total*100)}%"
            if going_first > 0:
                message += f"\nOverall win rate going first: {wins_going_first}/{going_first}: {int(wins_going_first/going_first*100)}%"
            else:
                message += f"\nNever went first yet."
            if going_second > 0:
                message += f"\nOverall win rate going second: {wins_going_second}/{going_second}: {int(wins_going_second/going_second*100)}%"
            else:
                message += f"\nNever went second yet."
            message += f"\n{battle_messages}"
        else:
            message += "\nNo data found."
    await reply(ctx, message)


@bot.command()
async def db_stats(ctx: commands.Context):
    message = "Overall stats"
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        select winner, count(*) * 100 / sum(count(*)) over()
        from battles
        group by winner
        order by winner asc
        """)
        rows = cursor.fetchall()
        for row in rows:
            player, winrate = row
            message += f"\nPlayer {player} win rate: {winrate}%"
        cursor.execute("select count(*) from battles")
        message += f"\nTotal battles: {cursor.fetchone()[0]}"
    await reply(ctx, message)


def get_equipment_usage() -> dict[str, tuple[int, int]]:
    """
    Maps equipment name -> (wins, total usages) from the battle database.
    Only includes cards that exist in equipment.yml.
    """
    equipment_names = {e.name for e in db.equipment}
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            select e.name,
                   count(*),
                   sum(case when m.player = b.winner then 1 else 0 end)
            from equipment_drafts e
            join mech_drafts m on e.mech_draft_id = m.id
            join battles b on m.battle_id = b.id
            group by e.name
            """)
        rows = cursor.fetchall()
    return {
        name: (wins, total) for name, total, wins in rows if name in equipment_names
    }


@bot.command()
async def equipment_winrates(ctx: commands.Context):
    usage = get_equipment_usage()
    stats = []
    for equipment in db.equipment:
        wins, total = usage.get(equipment.name, (0, 0))
        stats.append((equipment.name, wins, total))
    stats.sort(
        key=lambda s: (
            s[2] == 0,
            -(s[1] / s[2]) if s[2] > 0 else 0,
            -s[2],
            s[0],
        )
    )
    if all(s[2] == 0 for s in stats):
        await reply(
            ctx,
            "No equipment usage data found. Log battles with $db_add_battle and $db_add_draft first.",
        )
        return
    message = "Equipment win rates"
    for i, (name, wins, total) in enumerate(stats, start=1):
        if total > 0:
            message += f"\n{i}. {name}: {wins}/{total} ({int(wins / total * 100)}%)"
        else:
            message += f"\n{i}. {name}: 0/0 (n/a)"
    await reply(ctx, message, "winrates.txt")


@bot.command()
async def equipment_usage(ctx: commands.Context):
    usage = get_equipment_usage()
    stats = [
        (equipment.name, *usage.get(equipment.name, (0, 0)))
        for equipment in db.equipment
    ]
    stats.sort(key=lambda s: (-s[2], s[0]))
    message = "Equipment usage"
    for i, (name, wins, total) in enumerate(stats, start=1):
        message += f"\n{i}. {name}: {total}"
    await reply(ctx, message, "equipment_usage.txt")


FACTIONS = ["Feds", "Martians", "Jovians", "Pirates"]
FACTION_ABBR = {"Feds": "Feds", "Martians": "Mart", "Jovians": "Jov", "Pirates": "Pir"}


def get_battle_factions() -> dict[int, dict[int, set[str]]]:
    """
    Maps battle_id -> {player: set of factions drafted by that player}.
    A player's factions are the factions of all their drafted mechs.
    """
    mech_faction = {mech.name: mech.faction for mech in db.mechs}
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("select battle_id, player, name from mech_drafts")
        draft_rows = cursor.fetchall()
    factions_by_battle: dict[int, dict[int, set[str]]] = {}
    for battle_id, player, name in draft_rows:
        faction = mech_faction.get(name)
        if faction is None:
            continue
        factions_by_battle.setdefault(battle_id, {}).setdefault(player, set()).add(
            faction
        )
    return factions_by_battle


def get_faction_matchups() -> tuple[dict[tuple[str, str], list[int]], int, int]:
    """
    Aggregates battles into faction-vs-faction results.

    Returns (results, total_battles, skipped_battles) where results maps
    (faction_a, faction_b) to a list of winners (1 or 2, from the battles
    table) for every battle where faction_a and faction_b faced each other.
    A player's factions are the factions of all their drafted mechs, so a
    mixed-faction draft counts towards each of its faction pairings.
    """
    results: dict[tuple[str, str], list[int]] = {}
    total_battles = 0
    skipped_battles = 0
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("select id, winner from battles order by id asc")
        battles = cursor.fetchall()
    factions_by_battle = get_battle_factions()
    for battle_id, winner in battles:
        battle_factions = factions_by_battle.get(battle_id, {})
        factions1 = battle_factions.get(1, set())
        factions2 = battle_factions.get(2, set())
        if not factions1 or not factions2:
            skipped_battles += 1
            continue
        total_battles += 1
        for faction1 in factions1:
            for faction2 in factions2:
                results.setdefault((faction1, faction2), []).append(winner)
    return results, total_battles, skipped_battles


def get_faction_head_to_head(
    faction1: str, faction2: str
) -> list[tuple[int, str, bool]]:
    """
    Returns (battle_id, timestamp, won_by_faction1) for every battle where
    the two players played exactly faction1 and faction2, in either order.
    Wins are always reported from faction1's perspective, so
    "Feds vs Martians" and "Martians vs Feds" cover the same battles.
    """
    factions_by_battle = get_battle_factions()
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "select id, winner, timestamp from battles order by timestamp desc"
        )
        battles = cursor.fetchall()
    results = []
    for battle_id, winner, timestamp in battles:
        player_factions = factions_by_battle.get(battle_id, {})
        f1 = player_factions.get(1)
        f2 = player_factions.get(2)
        if f1 == {faction1} and f2 == {faction2}:
            results.append((battle_id, timestamp, winner == 1))
        elif f1 == {faction2} and f2 == {faction1}:
            results.append((battle_id, timestamp, winner == 2))
    return results


def format_matchup_matrix(
    results: dict[tuple[str, str], list[int]], total_battles: int, skipped_battles: int
) -> str:
    lines = ["Faction matchup winrates (row faction's win rate vs column faction)"]
    header = f"Battles: {total_battles}"
    if skipped_battles > 0:
        header += f" ({skipped_battles} skipped: no faction data)"
    lines.append(header)
    lines.append("")

    def cell(faction_a: str, faction_b: str) -> str:
        if faction_a == faction_b:
            return "-"
        # results is keyed (player 1 faction, player 2 faction), so battles
        # where faction_a was player 2 live under (faction_b, faction_a).
        # Winners are player ids, so swap them to keep faction_a's view.
        winners = results.get((faction_a, faction_b), []) + [
            2 if w == 1 else 1 for w in results.get((faction_b, faction_a), [])
        ]
        if not winners:
            return "n/a"
        total = len(winners)
        wins = sum(1 for winner in winners if winner == 1)
        return f"{round(wins / total * 100)}%({wins}/{total})"

    rows = [[cell(a, b) for b in FACTIONS] for a in FACTIONS]
    widths = [len(FACTION_ABBR[f]) for f in FACTIONS]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))

    lines.append(
        "      "
        + " ".join(FACTION_ABBR[f].ljust(widths[i]) for i, f in enumerate(FACTIONS))
    )
    for faction, row in zip(FACTIONS, rows):
        lines.append(
            FACTION_ABBR[faction].ljust(6)
            + " ".join(value.ljust(widths[i]) for i, value in enumerate(row))
        )
    return "\n".join(lines)


@bot.command()
async def matchups(ctx: commands.Context):
    results, total_battles, skipped_battles = get_faction_matchups()
    if total_battles == 0:
        await reply(
            ctx,
            "No battle data with faction information yet. Log battles with $db_add_battle and $db_add_draft first.",
        )
        return
    message = format_matchup_matrix(results, total_battles, skipped_battles)
    await reply(ctx, message, "matchups.txt")


@bot.command()
async def matchup(ctx: commands.Context, faction1: str, faction2: str):
    f1 = next((f for f in FACTIONS if f.lower() == faction1.strip().lower()), None)
    if f1 is None:
        message = (
            f"{faction1} is not a known faction. Valid factions: {', '.join(FACTIONS)}"
        )
        await reply(ctx, message)
        return
    f2 = next((f for f in FACTIONS if f.lower() == faction2.strip().lower()), None)
    if f2 is None:
        message = (
            f"{faction2} is not a known faction. Valid factions: {', '.join(FACTIONS)}"
        )
        await reply(ctx, message)
        return
    if f1 == f2:
        message = f"{f1} vs {f2} is not a valid matchup. Pick two different factions."
        await reply(ctx, message)
        return
    rows = get_faction_head_to_head(f1, f2)
    message = f"Stats for {f1} vs {f2}:"
    if len(rows) > 0:
        wins = sum(1 for _, _, won in rows if won)
        total = len(rows)
        message += f"\nTotal battles: {total}"
        message += f"\nOverall win rate: {wins}/{total}: {int(wins/total*100)}%"
        for battle_id, timestamp, won in rows:
            message += f"\nBattle {battle_id} {'won' if won else 'lost'} on {timestamp}"
    else:
        message += "\nNo data found."
    await reply(ctx, message, "matchup.txt")


@bot.command()
async def db_rename(ctx: commands.Context, original: str, new_name: str):
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        update mech_drafts
        set name = ?
        where name = ?
        """,
            (new_name, original),
        )
        cursor.execute(
            """
        update equipment_drafts
        set name = ?
        where name = ?
        """,
            (new_name, original),
        )
        cursor.execute(
            """
        update maneuver_drafts
        set name = ?
        where name = ?
        """,
            (new_name, original),
        )
    await reply(ctx, f"{original} was renamed to {new_name}.")


def list_to_csv_value(items: list) -> str:
    return "; ".join(str(item) for item in items if item is not None)


@bot.command()
async def equipment_csv(ctx: commands.Context):
    output = io.StringIO()
    fieldnames = [
        "name",
        "size",
        "type",
        "form",
        "heat",
        "range",
        "target",
        "ammo",
        "maxcharge",
        "text",
        "info",
        "actions",
        "triggers",
        "passives",
        "flavor_text",
        "tags",
        "alias",
        "copies",
        "rating",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for equipment in db.equipment:
        writer.writerow(
            {
                "name": equipment.name,
                "size": equipment.size,
                "type": equipment.type,
                "form": equipment.form,
                "heat": equipment.heat,
                "range": equipment.range,
                "target": equipment.target,
                "ammo": equipment.ammo,
                "maxcharge": equipment.maxcharge,
                "text": equipment.text,
                "info": equipment.info,
                "actions": list_to_csv_value(equipment.actions),
                "triggers": list_to_csv_value(equipment.triggers),
                "passives": list_to_csv_value(equipment.passives),
                "flavor_text": equipment.flavor_text,
                "tags": list_to_csv_value(equipment.tags),
                "alias": list_to_csv_value(equipment.alias),
                "copies": equipment.copies,
                "rating": equipment.rating,
            }
        )
    await reply(ctx, output.getvalue(), "equipment.csv")


@bot.command()
async def mech_csv(ctx: commands.Context):
    output = io.StringIO()
    fieldnames = [
        "name",
        "designation_name",
        "faction",
        "hp",
        "heat",
        "armor",
        "hardpoints",
        "ability",
        "info",
        "actions",
        "triggers",
        "passives",
        "tags",
        "copies",
        "rating",
        "lore",
        "how_to_play",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for mech in db.mechs:
        writer.writerow(
            {
                "name": mech.name,
                "designation_name": mech.designation_name,
                "faction": mech.faction,
                "hp": mech.hp,
                "heat": mech.hc,
                "armor": mech.armor,
                "hardpoints": mech.hardpoints_str,
                "ability": mech.ability,
                "info": mech.info,
                "actions": list_to_csv_value(mech.actions),
                "triggers": list_to_csv_value(mech.triggers),
                "passives": list_to_csv_value(mech.passives),
                "tags": list_to_csv_value(mech.tags),
                "copies": mech.copies,
                "rating": mech.rating,
                "lore": list_to_csv_value(mech.lore),
                "how_to_play": mech.how_to_play,
            }
        )
    await reply(ctx, output.getvalue(), "mechs.csv")


@bot.command()
async def maneuvers_csv(ctx: commands.Context):
    output = io.StringIO()
    fieldnames = [
        "name",
        "target",
        "text",
        "info",
        "actions",
        "triggers",
        "copies",
        "rating",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for maneuver in db.maneuvers:
        writer.writerow(
            {
                "name": maneuver.name,
                "target": maneuver.target,
                "text": maneuver.text,
                "info": maneuver.info,
                "actions": list_to_csv_value(maneuver.actions),
                "triggers": list_to_csv_value(maneuver.triggers),
                "copies": maneuver.copies,
                "rating": maneuver.rating,
            }
        )
    await reply(ctx, output.getvalue(), "maneuvers.csv")


@bot.command()
async def drones_csv(ctx: commands.Context):
    output = io.StringIO()
    fieldnames = [
        "name",
        "range",
        "target",
        "ability",
        "info",
        "actions",
        "triggers",
        "passives",
        "copies",
        "rating",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for drone in db.drones:
        writer.writerow(
            {
                "name": drone.name,
                "range": drone.range,
                "target": drone.target,
                "ability": drone.ability,
                "info": drone.info,
                "actions": list_to_csv_value(drone.actions),
                "triggers": list_to_csv_value(drone.triggers),
                "passives": list_to_csv_value(drone.passives),
                "copies": drone.copies,
                "rating": drone.rating,
            }
        )
    await reply(ctx, output.getvalue(), "drones.csv")


def get_todo_forum(bot: commands.Bot) -> ForumChannel:
    TODO_FORUM_ID = 1457611085728190688
    todo_forum = bot.get_channel(TODO_FORUM_ID)
    if not isinstance(todo_forum, ForumChannel):
        raise RuntimeError("todo-list forum channel not found.")
    return todo_forum


def get_resolved_tag(bot: commands.Bot) -> ForumTag:
    RESOLVED_TAG_ID = 1457611312594026566
    resolved_tag = get_todo_forum(bot).get_tag(RESOLVED_TAG_ID)
    if not isinstance(resolved_tag, ForumTag):
        raise RuntimeError("resolved forum tag not found.")
    return resolved_tag


def get_unresolved_tag(bot: commands.Bot) -> ForumTag:
    UNRESOLVED_TAG_ID = 1457612610051641470
    unresolved_tag = get_todo_forum(bot).get_tag(UNRESOLVED_TAG_ID)
    if not isinstance(unresolved_tag, ForumTag):
        raise RuntimeError("unresolved forum tag not found.")
    return unresolved_tag


@bot.event
async def on_thread_create(thread: Thread):
    resolved_tag = get_resolved_tag(bot)
    unresolved_tag = get_unresolved_tag(bot)
    if thread.parent == get_todo_forum(bot):
        if (
            resolved_tag not in thread.applied_tags
            and unresolved_tag not in thread.applied_tags
        ):
            await thread.add_tags(unresolved_tag)


@bot.command()
async def resolve(ctx: commands.Context):
    resolved_tag = get_resolved_tag(bot)
    unresolved_tag = get_unresolved_tag(bot)
    channel = ctx.channel
    if isinstance(channel, Thread) and channel.parent == get_todo_forum(bot):
        if unresolved_tag in channel.applied_tags:
            await channel.remove_tags(unresolved_tag)
        if resolved_tag not in channel.applied_tags:
            await channel.add_tags(resolved_tag)


if args.sync:
    logger.info("All commands:")
    for command in bot.tree.get_commands():
        logger.info(command.name)


bot.run(os.getenv("DISCORD_TOKEN", ""), log_handler=None)
