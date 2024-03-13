from typing import Any
from peewee import IntegerField, ForeignKeyField
from kayo.models.base import BaseModel
from kayo.models.team import Team
from kayo.models.match import Match
import discord
from kayo import instance


class Alert(BaseModel):
    team = ForeignKeyField(Team, backref="alerts")
    channel_id = IntegerField(null=True)
    user_id = IntegerField(null=True)

    async def send_alert(self, match: Match):
        embed = discord.Embed(
            title=f":{match.flag1}: {match.team1} ⚔️ {match.team2} :{match.flag2}:",
            description=match.round_info,
            color=discord.Colour.red(),  # Pycord provides a class with default colors you can choose from
        )

        if (
            match.team1 in instance.referential["teams"]
            and instance.referential["teams"][match.team1] != ""
        ):
            embed.add_field(
                name=f"{match.team1}'s stream",
                value=f'[Link]({instance.referential["teams"][match.team1]})',
                inline=True,
            )

        embed.add_field(
            name="Check on vlr.gg",
            value=f"[Click here](https://vlr.gg{match.match_page})",
            inline=True,
        )

        if (
            match.team2 in instance.referential["teams"]
            and instance.referential["teams"][match.team2] != ""
        ):
            embed.add_field(
                name=f"{match.team2}'s stream",
                value=f'[Link]({instance.referential["teams"][match.team2]})',
                inline=True,
            )

        embed.set_author(name=match.tournament_name, icon_url=match.tournament_icon)

        if self.channel_id is not None:
            channel = await instance.bot.fetch_channel(self.channel_id)
            await channel.send(embed=embed)
        else:
            user = await instance.bot.fetch_user(self.user_id)
            await user.send(embed=embed)


async def send_alerts(match: Match):
    list_of_alerts = Alert.select().where(
        (Alert.team == match.team1) | (Alert.team == match.team2)
    )
    for alert in list_of_alerts:
        await alert.send_alert(match)
