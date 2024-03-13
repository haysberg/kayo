import os
import json
import requests
import peewee

from peewee import DoesNotExist

from kayo import instance
from dotenv import load_dotenv
from kayo.models.alert import Alert, send_alerts
from kayo.models.match import Match
from kayo.models.base import db
from kayo.models.team import Team
from discord.ext import tasks

from kayo import instance
import discord
from discord.ext import commands
from kayo.models.team import get_team_names


load_dotenv()
db.create_tables([Match, Team, Alert])


@instance.bot.event
async def on_ready():
    check_matches.start()
    check_teams.start()


# ASYNC TASKS
@tasks.loop(seconds=300)
async def check_matches():
    """Checks if there is new upcoming matches."""
    instance.logger.info("Checking for matches...")
    data = json.loads(requests.get(f"{instance.vlrapi}/match/upcoming").text)
    instance.logger.info(data)
    for match in data.get("data").get("segments"):
        try:
            if (
                match["time_until_match"] == "LIVE"
                and Match()
                .get(Match.match_page == match["match_page"])
                .time_until_match
                != "LIVE"
            ):
                await send_alerts(Match().get(Match.match_page == match["match_page"]))
        except peewee.DoesNotExist:
            await send_alerts(Match(id=int(match["match_page"][1:7]), **match))
            Match.insert(
                id=int(match["match_page"][1:7]), **match
            ).on_conflict_replace().execute()
        except json.decoder.JSONDecodeError:
            instance.logger.error(data)


@tasks.loop(seconds=3600)
async def check_teams():
    """Downloads teams to put them in the database. Useful for autocomplete."""
    instance.logger.info("Checking for teams to add to the db...")
    for region in [
        "na",
        "eu",
        "ap",
        "la",
        "la-s",
        "la-n",
        "oce",
        "kr",
        "mn",
        "gc",
        "br",
        "cn",
    ]:
        data = json.loads(requests.get(f"{instance.vlrapi}/rankings/{region}").text)
        data = data.get("data")
        for team in data:
            Team.insert(
                name=team["team"],
                logo=team["logo"],
                earnings=int(team["earnings"].strip("$").replace(",", "")),
            ).on_conflict_replace().execute()


# BOT COMMANDS
@instance.subscribe.command(name="team", description="Subscribe to team alerts")
@commands.has_permissions(manage_messages=True)
async def subscribe_team(ctx: discord.ApplicationContext, team: discord.Option(str, "team", autocomplete=discord.utils.basic_autocomplete(get_team_names))):  # type: ignore
    """Subscribes the channel to a league.

    Args:
        ctx (discord.ApplicationContext): Information about the current message.
        league (discord.Option): Name of the League to follow.
        Defaults to discord.utils.basic_autocomplete(get_league_names)).
    """
    try:
        team = Team.get(Team.name == team)
        if isinstance(ctx.channel, discord.DMChannel):
            alert = Alert().insert(team=team, user_id=ctx.user.id).execute()
        else:
            alert = Alert().insert(team=team, channel_id=ctx.channel_id).execute()
        await ctx.respond(f"Successfully created an alert for {team} !")
    except commands.errors.MissingPermissions:
        await ctx.respond(
            "You need to have the 'Manage Messages' permission to run this command in a server. Feel free to send me a DM instead !"
        )


@instance.unsubscribe.command(name="team", description="Unsubscribe to team alerts")
@commands.has_permissions(manage_messages=True)
async def unsubscribe_team(ctx: discord.ApplicationContext, team: discord.Option(str, "team", autocomplete=discord.utils.basic_autocomplete(get_team_names))):  # type: ignore
    try:
        target_team = Team.get(Team.name == team)
        if isinstance(ctx.channel, discord.DMChannel):
            alert = (
                Alert.select()
                .where((Alert.user_id == ctx.user.id) & (Alert.team == target_team))
                .get()
                .delete_instance()
            )
        else:
            alert = (
                Alert.select()
                .where(
                    (Alert.channel_id == ctx.channel_id) & (Alert.team == target_team)
                )
                .get()
                .delete_instance()
            )
        await ctx.respond(f"Successfully deleted your alert for {team}.")
    except commands.errors.MissingPermissions:
        await ctx.respond(
            "You need to have the 'Manage Messages' permission to run this command in a server. Feel free to send me a DM instead !"
        )
    except DoesNotExist:
        await ctx.respond("Looks like you don't have an alert for that team.")


@instance.bot.command(name="list", description="Lists alerts in this channel")
@commands.has_permissions(manage_messages=True)
async def list_alerts(ctx: discord.ApplicationContext):
    try:
        alerts = {}
        if isinstance(ctx.channel, discord.DMChannel):
            alerts = Alert.select().where((Alert.user_id == ctx.user.id))
        else:
            alerts = Alert.select().where((Alert.channel_id == ctx.channel_id))
        if len(alerts) > 0:
            answer = "List of team alerts : "
            for alert in alerts:
                if len(f"{answer}\r- {alert.team.name}") > 1500:
                    await ctx.respond(answer)
                    answer = ""
                answer = f"{answer}\r- {alert.team.name}"
            await ctx.respond(answer)
        else:
            await ctx.respond("Looks like you don't have any alerts in that channel.")
    except commands.errors.MissingPermissions:
        await ctx.respond(
            "You need to have the 'Manage Messages' permission to run this command in a server. Feel free to send me a DM instead !"
        )
    except DoesNotExist:
        await ctx.respond("Looks like you don't have any alerts in that channel.")


@instance.bot.command(
    name="help", description="Explains the different commands on the bot."
)
async def help(ctx: discord.ApplicationContext):
    await ctx.respond(
        """Here is the list of commands you can use :
                      - /subscribe [team] to receive alerts on a team
                      - /unsubscribe [team] to stop receiving alerts
                      - /list to list the alerts configured in the current channel
                      """
    )


if os.environ.get("DEPLOYED", "DEBUG").upper() != "PRODUCTION":

    @instance.bot.command(name="testalerts", description="Debug command")
    @commands.has_permissions(manage_messages=True)
    async def testalerts(ctx: discord.ApplicationContext):
        matches = Match.select().limit(10)
        for match in matches:
            await Alert.select().limit(1).first().send_alert(match)


instance.bot.run(os.getenv("DISCORD_TOKEN"))
