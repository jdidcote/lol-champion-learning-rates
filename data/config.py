from dataclasses import dataclass

from dotenv import dotenv_values


@dataclass
class Config:
    env = dotenv_values(".env")
