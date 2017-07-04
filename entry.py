from peewee import *
import datetime


db = SqliteDatabase('workLog.db')


class Entry(Model):
    name = CharField(max_length=255)
    task = CharField(max_length=255)
    spent_minutes = IntegerField()
    notes = TextField()
    timestamp = DateField(default=datetime.datetime.now)

    class Meta:
        database = db