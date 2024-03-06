import os
import json
import requests

from kayo import instance
from dotenv import load_dotenv
from kayo.models.match import Match
from kayo.models.base import db
from kayo.models.team import Team
from discord.ext import tasks

from kayo import instance
import discord
from discord.ext import commands
from kayo.models.team import get_team_names


load_dotenv()
db.create_tables([Match, Team])

@instance.bot.event
async def on_ready():
    check_matches.start()
    check_teams.start()

# ASYNC TASKS
@tasks.loop(seconds=300)
async def check_matches():
    """Checks if there is new upcoming matches."""
    instance.logger.info("Checking for matches...")
    data = json.loads(requests.get('https://vlrggapi-q5vt9jqyz-rehkloos.vercel.app/match/upcoming').text)
    data = data.get('data').get('segments')
    instance.logger.info(data)
    for match in data:
        osef = Match().insert(id=int(match['match_page'][1:7]), **match).on_conflict_replace().execute()

@tasks.loop(seconds=3600)
async def check_teams():
    """Downloads teams to put them in the database. Useful for autocomplete."""
    instance.logger.info("Checking for teams to add to the db...")
    for region in ['na', 'eu', 'ap', 'la', 'la-s', 'la-n', 'oce', 'kr', 'mn', 'gc', 'br', 'cn']:
        data = json.loads(requests.get(f'https://vlrggapi-q5vt9jqyz-rehkloos.vercel.app/rankings/{region}').text)
        data = data.get('data')
        for team in data:
            osef = Team().insert(name=team['team'], logo=team['logo'], earnings=int(team['earnings'].strip('$').replace(',', ''))).on_conflict_replace().execute()

# BOT COMMANDS
@instance.subscribe.command(name="team", description="Subscribe to team alerts")
@commands.has_permissions(manage_messages=True)
async def subscribe_team(ctx: discord.ApplicationContext, team: discord.Option(str, "team", autocomplete=discord.utils.basic_autocomplete(get_team_names))): # type: ignore
    """Subscribes the channel to a league.

    Args:
        ctx (discord.ApplicationContext): Information about the current message.
        league (discord.Option): Name of the League to follow.
        Defaults to discord.utils.basic_autocomplete(get_league_names)).
    """
    try:
        await ctx.respond(f"Successfully created an alert for {team} !")
    except discord.ext.commands.errors.MissingPermissions:
        await ctx.respond("You need to have the 'Manage Messages' permission to run this command in a server. Feel free to send me a DM !")

instance.bot.run(os.getenv("DISCORD_TOKEN"))