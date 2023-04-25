"""
interaction.py
09. January 2023

Easy Access to the database

Author:
Nilusink
"""
import typing as tp
import sqlite3
import time


class Interactor:
    __con: sqlite3.Connection = None
    _path: str = "../data/main.db"

    def __new__(cls, *args, **kwargs):
        new = super().__new__(cls)

        # only create one instance of ENGINE for all instances
        if cls.__con is None:
            cls.__con = sqlite3.connect(cls._path)

        return new

    def __init__(self):
        """
        Used to interact with the SQLite Database
        """
        self._debug = False

        if self._debug:
            self.__con.set_trace_callback(print)

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
    def connection(self) -> sqlite3.Connection:
        if self.__con is None:
            raise RuntimeError("Function called before initializing a instance")

        return self.__con

    # getters
    # noinspection Duplicates
    def get_weather_stations(
            self,
            id: int = ...,
            n_results: int = 1,
            name: str | tp.Iterable[str] = ...,
            position: str | tp.Iterable[str] = ...,
            height: float | tp.Iterable[float] = ...,
    ) -> list[dict[str, tp.Any]]:
        """
        get weather stations.


        Available Filters:


        :param id: filter by id (only one object will be returned
        :param n_results: how many results should be fetched
        :param name: str or Iterable[str], can yield multiple results
        :param position: str or Iterable[str], can yield multiple results
        :param height: float or Iterable[float], can yield multiple results
        """
        if n_results is None:
            n_results = -1

        cursor = self.__con.cursor()

        # get table info
        result = cursor.execute("PRAGMA table_info(stations);")
        t_info = result.fetchall()
        keys = [column[1] for column in t_info]

        # if id is given, there is only one possible result
        params: list = []
        if id not in (..., None):
            query = f"SELECT * FROM stations WHERE id = ?"
            params.append(id)

        else:
            query = "SELECT * FROM stations "
            if name not in (..., None):
                query += f"{'AND' if '=' in query else 'WHERE'}" \
                         f" name = ? "
                params.append(name)

            if position not in (..., None):
                query += f"{'AND' if '=' in query else 'WHERE'}" \
                         f" position = ? "
                params.append(position)

            if height not in (..., None):
                query += f"{'AND' if '=' in query else 'WHERE'}" \
                         f" height = ? "
                params.append(height)

        query += " ORDER BY id DESC;"

        # execute query
        results = cursor.execute(query, params)

        if n_results == -1:
            values = results.fetchall()

        else:
            values = results.fetchmany(n_results)

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
        """
        get all weather data

        :param id: filter by id (only one object will be returned)
        :param time: filter by time
        :param station_id: filter by station
        :param temperature: filter by temperature
        :param temperature_index: filter y temperature_index
        :param humidity: filter by humidity
        :param air_pressure: filter by air_pressure
        :param n_results: how many results should be fetched
        :return: list of dictionaries with values
        """
        if n_results is None:
            n_results = 1

        cursor = self.__con.cursor()

        # get table info
        result = cursor.execute("PRAGMA table_info(weather);")
        t_info = result.fetchall()
        keys = [column[1] for column in t_info]

        # if id is given, there is only one possible result
        params: list = []
        if id not in (..., None):
            query = "SELECT * FROM weather WHERE id = ?"
            params.append(id)

        else:
            query = "SELECT * FROM weather "

            if time not in (..., None):
                query += f"{'AND' if '=' in query else 'WHERE'}" \
                         f" time = ? "
                params.append(time)

            if station_id not in (..., None):
                query += f"{'AND' if '=' in query else 'WHERE'}" \
                         f" station_id = ? "
                params.append(station_id)

            if temperature not in (..., None):
                query += f"{'AND' if '=' in query else 'WHERE'}" \
                         f" temperature = ? "
                params.append(temperature)

            if temperature_index not in (..., None):
                query += f"{'AND' if '=' in query else 'WHERE'}" \
                         f" temperature_index = ? "
                params.append(temperature_index)

            if humidity not in (..., None):
                query += f"{'AND' if '=' in query else 'WHERE'}" \
                         f" humidity = ? "
                params.append(humidity)

            if air_pressure not in (..., None):
                query += f"{'AND' if '=' in query else 'WHERE'}" \
                         f" air_pressure = ? "
                params.append(air_pressure)

        query += " ORDER BY id DESC;"

        # execute query
        result = cursor.execute(query, params)

        if n_results == -1:
            values = result.fetchall()

        else:
            values = result.fetchmany(n_results)

        out: list[dict[str, tp.Any]] = []

        # in case list is empty
        if not values or values[0] is None:
            return out

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
        cursor = self.__con.cursor()
        _secret = cursor.execute(
            "SELECT secret FROM station_secrets WHERE "
            "station_id = ?;", (station_id,)
        ).fetchone()[0]

        # no entry
        if not _secret:
            print("station secret entry not found")
            return False

        # check if secret matches
        if not _secret == station_secret:
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
        query = f"INSERT INTO weather" \
                f" ({', '.join(to_write.keys())}) VALUES" \
                f" ({', '.join(('?',) * len(to_write))});"

        params = (*to_write.values(),)

        # execute query
        cursor.execute(query, params)
        self.__con.commit()

        return True
