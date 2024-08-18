from dataclasses import dataclass

from quicksettings import BaseSettings


@dataclass(init=False)
class BasicSettings(BaseSettings):
    DEBUG: bool
    WEIGHT: float
    PORT: int
    DESCRIPTION: str


@dataclass(init=False)
class BoolSettings(BaseSettings):
    DEBUG: bool
