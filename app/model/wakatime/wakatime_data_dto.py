from dataclasses import dataclass

from .wakatime_item_dto import WakatimeItemDto


@dataclass
class WakatimeDataDto:
    projects: list[WakatimeItemDto]
    languages: list[WakatimeItemDto]
    editors: list[WakatimeItemDto]
