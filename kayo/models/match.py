from peewee import IntegerField, CharField
from kayo.models.base import BaseModel


class Match(BaseModel):
    id = IntegerField(primary_key=True)
    team1 = CharField()
    team2 = CharField()
    flag1 = CharField()
    flag2 = CharField()
    score1 = CharField()
    score2 = CharField()
    time_until_match = CharField()
    round_info = CharField()
    tournament_name = CharField()
    match_page = CharField()
    tournament_icon = CharField()
