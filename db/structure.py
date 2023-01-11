"""
structure.py
09. January 2023

The general database Structure

Author:
Nilusink
"""
import sqlalchemy as db


META = db.MetaData()


# Table structures
WEATHER_EMP = db.Table(
    'weather', META,
    db.Column('id', db.Integer, primary_key=True),
    db.Column("time", db.String, nullable=False),
    db.Column("station_id", db.Integer, nullable=False),
    db.Column("temperature", db.Float, nullable=True),
    db.Column("temperature_index", db.Float, nullable=True),
    db.Column("humidity", db.Float, nullable=True),
    db.Column("air_pressure", db.Float, nullable=True),
)

STATIONS_EMP = db.Table(
    "stations", META,
    db.Column("id", db.Integer, primary_key=True),
    db.Column("name", db.String, nullable=False),
    db.Column("position", db.String, nullable=False),
    db.Column("height", db.Float, nullable=True),
)

STATION_SECRETS_EMP = db.Table(
    'station_secrets', META,
    db.Column("station_id", db.Integer, primary_key=True),
    db.Column("secret", db.String, nullable=False),
)

GARDEN_HOUSE_EMP = db.Table(
    "garden_house", META,
    db.Column("id", db.Integer, primary_key=True),
    db.Column("last_seen", db.Float, nullable=False),
    db.Column("online", db.Boolean, nullable=False),
    db.Column("temperature", db.Float, nullable=True),
    db.Column("cpu_temperature", db.Float, nullable=False),
    db.Column("humidity", db.Float, nullable=True),
    db.Column("heater", db.Boolean, nullable=False),
    db.Column("heater_set_temperature", db.Float, nullable=False),
    db.Column("relay1", db.Boolean, nullable=False),
    db.Column("relay2", db.Boolean, nullable=False),
)
