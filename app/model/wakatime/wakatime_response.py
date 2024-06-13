from dataclasses import dataclass

from .wakatime_data_dto import WakatimeDataDto


@dataclass
class WakatimeResponse:
    data: WakatimeDataDto
