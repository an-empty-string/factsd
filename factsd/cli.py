from . import app, models
from peewee import SqliteDatabase
import click


@click.group()
def base():
    pass


@base.command()
@click.option("--database", default="app.db")
def initdb(database):
    models.db.initialize(SqliteDatabase(database))
    for model in [models.Variable, models.VariableHistory, models.AccessKey]:
        model.create_table(True)

    click.secho("Database tables created.", bold=True)


@base.command()
@click.option("--database", default="app.db")
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=8091)
def serve(database, host, port):
    models.db.initialize(SqliteDatabase(database))
    app.app.run(host=host, port=port)


if __name__ == "__main__":
    base()
