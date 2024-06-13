from dataclasses import dataclass


@dataclass
class WakatimeItemDto:
    total_seconds: float
    name: str
    percent: float
    digital: str
    decimal: str
    text: str
    hours: int
    minutes: int
