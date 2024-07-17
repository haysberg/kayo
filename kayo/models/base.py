
from peewee import SqliteDatabase, Model

global db

# if os.getenv("DEPLOYED") == "PRODUCTION":
db = SqliteDatabase("data/kayo.db")
# else:
#     db = SqliteDatabase(":memory:")


class BaseModel(Model):
    class Meta:
        database = db
