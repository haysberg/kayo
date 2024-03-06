import discord
from peewee import IntegerField, CharField
from kayo.models.base import BaseModel


class Team(BaseModel):
    name = CharField(primary_key=True)
    logo = CharField()
    earnings = IntegerField()

def get_team_names(ctx: discord.AutocompleteContext = None):
    return [team['name'] for team in Team.select(Team.name).order_by(Team.earnings.desc()).dicts()]