import os

from peewee import *

global db

# if os.getenv("DEPLOYED") == "PRODUCTION":
db = SqliteDatabase("kayo.db")
# else:
#     db = SqliteDatabase(":memory:")

class BaseModel(Model):
    class Meta:
        database = db