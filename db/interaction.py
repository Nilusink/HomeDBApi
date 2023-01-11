"""
interaction.py
09. January 2023

Easy Access to the database

Author:
Nilusink
"""
from .structure import *
import typing as tp
import time


class Interactor:
    __engine: db.engine.Engine = None
    _path: str = "../data/main.db"

    def __new__(cls, *args, **kwargs):
        new = super().__new__(cls)

        # only create one instance of ENGINE for all instances
        if cls.__engine is None:
            cls.__engine = db.create_engine(f'sqlite:///{cls._path}', echo=False)

        return new

    def __init__(self):
        """
        Used to interact with the SQLite Database
        """
        self._debug = True

        # create database engine
        self._connection = self.engine.connect()

    # properties
    @property
    def path(self) -> str:
        """
        :return: the location of the database file
        """
        return self._path

    @property
    def debug(self) -> bool:
        """
        :return: if the debug mode is on or off
        """
        return self._debug

    @property
    def engine(self) -> db.engine.Engine:
        if self.__engine is None:
            raise RuntimeError("Function called before initializing a instance")

        return self.__engine

    @property
    def connection(self) -> db.engine.base.Connection:
        return self._connection

    # getters
    @staticmethod
    def _query_generator(
            _table: db.Table,
            query,
            key: str,
            value: tp.Any | tp.Iterable[tp.Any],
            s_types: tuple,
    ):
        """
        :param _table: table to look up
        :param query: query to extend
        :param key: name of the key
        :param value: value to check
        :param s_types: valid types for value (singular)
        :return:
        """
        if any([isinstance(value, t) for t in s_types]):
            query = query.where(eval(f"_table.columns.{key}") == value)

        elif isinstance(value, tp.Iterable):
            query = query.where(eval(f"_table.columns.{key}").in_(value))

        else:
            raise RuntimeError(f"Argument \"{key}\" must be of type {s_types} or Iterable")

        return query

    # noinspection Duplicates
    def get_weather_stations(
            self,
            id: int = ...,
            name: str | tp.Iterable[str] = ...,
            position: str | tp.Iterable[str] = ...,
            height: float | tp.Iterable[float] = ...,
    ) -> list[dict[str, tp.Any]]:
        """
        get weather stations.


        Available Filters:


        :param id: filter by id (only one object will be returned
        :param name: str or Iterable[str], can yield multiple results
        :param position: str or Iterable[str], can yield multiple results
        :param height: float or Iterable[float], can yield multiple results
        """
        table = db.Table('stations', META, autoload=True, autoload_with=self.engine)

        # create query
        query = db.select([table])

        # if id is given, there is only one possible result
        if id not in (..., None):
            query = db.select([table]).where(table.columns.id == id)

        else:
            if name not in (..., None):
                query = self._query_generator(table, query, "name", name, (str,))

            if position not in (..., None):
                query = self._query_generator(table, query, "position", position, (str,))

            if height not in (..., None):
                query = self._query_generator(table, query, "height", height, (float, int,))

        # execute query
        result = self.connection.execute(query)
        keys = result.keys()
        values = result.fetchall()

        out: list[dict[str, tp.Any]] = []
        for value in values:
            tmp = {}
            for key, item in zip(keys, value):
                tmp[str(key)] = item

            out.append(tmp)

        return out

    # noinspection Duplicates
    def get_weather_data(
            self,
            id: int = ...,
            time: str | tp.Iterable[str] = ...,
            station_id: int | tp.Iterable[int] = ...,
            temperature: float | tp.Iterable[float] = ...,
            temperature_index: float | tp.Iterable[float] = ...,
            humidity: float | tp.Iterable[float] = ...,
            air_pressure: float | tp.Iterable[float] = ...,
            n_results: int = ...,
    ) -> list[dict[str, tp.Any]]:
        table = db.Table('weather', META, autoload=True, autoload_with=self.engine)

        # create query
        query = db.select([table])

        # if id is given, there is only one possible result
        if id not in (..., None):
            query = db.select([table]).where(table.columns.id == id)

        else:
            if time not in (..., None):
                query = self._query_generator(table, query, "time", time, (str,))

            if station_id not in (..., None):
                query = self._query_generator(table, query, "station_id", station_id, (float, int,))

            if temperature not in (..., None):
                query = self._query_generator(table, query, "temperature", temperature, (float, int,))

            if temperature_index not in (..., None):
                query = self._query_generator(table, query, "temperature_index", temperature_index, (float, int,))

            if humidity not in (..., None):
                query = self._query_generator(table, query, "humidity", humidity, (float, int,))

            if air_pressure not in (..., None):
                query = self._query_generator(table, query, "air_pressure", air_pressure, (float, int,))

        # execute query
        # reverse result to get the last n results instead of the first n results
        result = self.connection.execute(query.order_by(table.columns.id.desc()))
        keys = result.keys()

        if n_results in (..., None):
            values = result.fetchone()

        elif n_results == -1:
            values = result.fetchall()

        else:
            values = result.fetchmany(n_results)

        out: list[dict[str, tp.Any]] = []
        for value in values:
            tmp = {}
            for key, item in zip(keys, value):
                tmp[str(key)] = item

            out.append(tmp)

        return out

    def set_weather_data(
            self,
            station_id: int,
            station_secret: str,
            temperature: float | tp.Iterable[float] = ...,
            temperature_index: float | tp.Iterable[float] = ...,
            humidity: float | tp.Iterable[float] = ...,
            air_pressure: float | tp.Iterable[float] = ...,
    ) -> bool:
        """
        add an entry to a station
        """
        # get stations secret
        table = db.Table('station_secrets', META, autoload=True, autoload_with=self.engine)
        query = db.select([table]).where(table.columns.station_id == station_id)

        result = self.connection.execute(query)
        _secret = result.fetchone()

        # no entry
        if not _secret:
            print("station secret entry not found")
            return False

        # check if secret matches
        if not _secret[1] == station_secret:
            print("secret mismatch")
            return False

        # create query
        to_write: dict = {
            "time": time.strftime("%Y.%m.%d-%T"),
            "station_id": station_id,
        }

        if temperature not in (..., None):
            to_write["temperature"] = temperature

        if temperature_index not in (..., None):
            to_write["temperature_index"] = temperature_index

        if humidity not in (..., None):
            to_write["humidity"] = humidity

        if air_pressure not in (..., None):
            to_write["air_pressure"] = air_pressure

        # create query
        table = db.Table('weather', META, autoload=True, autoload_with=self.engine)
        query = db.insert(table).values(**to_write)

        # execute query
        self.connection.execute(query)

        return True
