from dataclasses import dataclass

import pytest

from quicksettings import BaseSettings


@pytest.fixture()
def basic_settings() -> type[BaseSettings]:
    @dataclass(init=False)
    class Settings(BaseSettings):
        DEBUG: bool
        WEIGHT: float
        PORT: int
        DESCRIPTION: str

    return Settings


@pytest.fixture()
def bool_settings() -> type[BaseSettings]:
    @dataclass(init=False)
    class Settings(BaseSettings):
        DEBUG: bool

    return Settings
