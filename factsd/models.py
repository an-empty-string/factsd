from peewee import Proxy, Model, CharField, DateTimeField, TextField, BooleanField
import datetime

db = Proxy()


class BaseModel(Model):
    class Meta:
        database = db


class Variable(BaseModel):
    path = CharField(1024)
    data = TextField()


class VariableHistory(BaseModel):
    ts = DateTimeField(default=datetime.datetime.now)
    path = CharField(1024)
    data = TextField()


class AccessKey(BaseModel):
    path = CharField(1024)
    url = CharField(1024, null=True)
    key = CharField(64)
    is_admin = BooleanField(default=False)
    is_writer = BooleanField(default=False)
