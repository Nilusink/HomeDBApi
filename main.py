"""
main.py
09. January 2023

Enables the Database to be reachable from outside

Author:
Nilusink
"""
from db import *
import typing as tp
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from extra import *


# types
class WeatherDataResult(BaseModel):
    id: int
    time: str
    station_id: int
    temperature: float | None
    temperature_index: float | None
    humidity: float | None
    air_pressure: float | None


class WeatherStationResult(BaseModel):
    id: int
    name: str
    position: str
    height: str | None


class WeatherStationRequest(BaseModel):
    id: int = None
    name: str | tp.Iterable[str] = None
    position: str | tp.Iterable[str] = None
    height: float | tp.Iterable[float] = None


class WeatherDataRequest(BaseModel):
    id: int = None
    time: str | tp.Iterable[str] = None
    station_id: int | tp.Iterable[int] = None
    temperature: float | tp.Iterable[float] = None
    temperature_index: float | tp.Iterable[float] = None
    humidity: float | tp.Iterable[float] = None
    air_pressure: float | tp.Iterable[float] = None
    n_results: int = None


# post hints
class WeatherPush(BaseModel):
    station_id: int
    station_secret: str
    temperature: float | None = None
    temperature_index: float | None = None
    humidity: float | None = None
    air_pressure: float | None = None


# create FastApi app
app = FastAPI()

# allow CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hi": "You've reached my Api!"}


@app.get("/stations/")
def read_weather_stations(item: WeatherStationRequest) -> list[WeatherStationResult]:
    """
    Get available Stations.
    """
    with catch_error():
        i = Interactor()
        result = i.get_weather_stations(**dict(item))

        return result


@app.get("/simple/stations/")
def read_weather_stations_simple(
        id: int = None,
        name: str = None,
        position: str = None,
        height: float = None,
) -> list[WeatherStationResult]:
    """
    Get available Stations. URI-only version because JavaScript cant add a body to a GET request.
    """
    with catch_error():
        i = Interactor()
        result = i.get_weather_stations(id, name, position, height)

        return result


@app.get("/weather/")
def read_weather_data(item: WeatherDataRequest) -> list[WeatherDataResult]:
    """
    Browse available weather data
    """
    with catch_error():
        i = Interactor()
        result = i.get_weather_data(**dict(item))

        return result


@app.get("/simple/weather/")
def read_weather_data_simple(
        id: int = None,
        time: str = None,
        station_id: int = None,
        temperature: float = None,
        temperature_index: float = None,
        humidity: float = None,
        air_pressure: float = None,
        n_results: int = None,
) -> list[WeatherDataResult]:
    """
    Browse available weather data. URI-only version because JavaScript cant add a body to a GET request.
    """
    with catch_error():
        i = Interactor()
        result = i.get_weather_data(
            id,
            time,
            station_id,
            temperature,
            temperature_index,
            humidity,
            air_pressure,
            n_results,
        )

        return result

@app.post("/weather/")
def write_weather_data(item: WeatherPush):
    i = Interactor()
    res = i.set_weather_data(**dict(item))

    return {"success": res}
