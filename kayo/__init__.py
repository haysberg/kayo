"""KAY/O Initialization module."""
import json
import logging
import os
import sys

import aiohttp
import discord
import dotenv
from peewee import *

dotenv.load_dotenv()
LOGLEVEL = os.environ.get('LOGLEVEL', 'info').upper()


class BotContext:
    """Contains all the useful objects to interact with the database and the logger."""

    def __init__(self):
        """Creates all the objects."""
        LOGFORMAT = '%(asctime)s:%(levelname)s:%(message)s'
        logging.basicConfig(filename='./kayo.log', encoding='utf-8', level=LOGLEVEL, format=LOGFORMAT)
        self.logger = logging.getLogger('discord')
        self.logger = logging.getLogger('peewee')
        self.logger.setLevel(level=LOGLEVEL)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
        self.logger.addHandler(handler)
        self.http_client = aiohttp.ClientSession()

        # Initializing core objects
        if os.environ.get('DEPLOYED', 'DEBUG').upper() == "PRODUCTION":
            self.bot = discord.Bot()
        else:
            self.bot = discord.Bot(debug_guilds=[int(os.environ.get('DEBUG_GUILD'))])

        # Opening JSON file
        with open('./referential.json') as json_file:
            self.referential = json.load(json_file)
        
        self.subscribe = self.bot.create_group("subscribe", "Subscribes you to teams")

        self.vlrapi = os.environ.get('VLR_GG_API')


global instance
instance = BotContext()
