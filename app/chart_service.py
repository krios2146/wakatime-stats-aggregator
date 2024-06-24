from functools import reduce
import logging
from . import chart_builder
from . import chart_manager
from .client import github_api_client
from .model.chart_data import ChartData
from .model.chart_request import ChartRequest
from .model.chart import Chart
from .client import wakatime_api_client
from .model.chart_type import ChartType
from .model.github_language_item_dto import GithubLanguageItemDto
from .model.wakatime.wakatime_item_dto import WakatimeItemDto
from .model.wakatime.wakatime_response import WakatimeResponse

log = logging.getLogger(__name__)
log.level = logging.DEBUG


def create_chart(chart_request: ChartRequest) -> Chart | None:
    log.info(f"Creating chart {chart_request.uuid}")

    response: WakatimeResponse = wakatime_api_client.get_last_7_days(
        chart_request.username
    )

    data: list[WakatimeItemDto] | None = None
    colors: dict[str, str] | None = chart_request.colors

    match chart_request.chart_data:
        case ChartData.LANGUAGES:
            data = response.data.languages
            github_languages = github_api_client.get_github_languages()
            colors = _merge_github_lang_colors(colors, github_languages)

        case ChartData.PROJECTS:
            data = response.data.projects

        case ChartData.EDITORS:
            data = response.data.editors

    colors = _merge_group_colors(colors, chart_request.group_colors)

    assert data is not None

    data = _hide(data, chart_request.hide)
    data = _group(data, chart_request.groups)

    match chart_request.chart_type:
        case ChartType.PIE:
            chart_builder.create_pie_chart(data, chart_request.uuid, colors)

    chart_path: str | None = chart_manager.find_by_uuid(chart_request.uuid)

    if chart_path is None:
        return None

    return Chart(chart_request.uuid, chart_path)


def _merge_github_lang_colors(
    colors: dict[str, str] | None, github_languages: list[GithubLanguageItemDto]
) -> dict[str, str] | None:
    default_colors: dict[str, str] = {
        github_language.name: github_language.color
        for github_language in github_languages
    }

    if colors is None:
        return default_colors

    for default_color in default_colors:
        for color in colors:
            if default_color.lower() == color:
                default_colors[color] = colors[color]


def _merge_group_colors(
    colors: dict[str, str] | None, group_colors: dict[str, str] | None
) -> dict[str, str] | None:
    if colors is None:
        return group_colors

    if group_colors is None:
        return colors

    return colors | group_colors


def _hide(data: list[WakatimeItemDto], hide: set[str] | None) -> list[WakatimeItemDto]:
    if hide is None:
        return data

    return list(filter(lambda x: x.name.lower() not in hide, data))


def _group(
    data: list[WakatimeItemDto], groups: dict[str, set[str]] | None
) -> list[WakatimeItemDto]:
    if groups is None:
        return data

    grouped_items: list[WakatimeItemDto] = list()

    for group_name, group_item_names in groups.items():
        group_items = list(filter(lambda x: x.name in group_item_names, data))

        if len(group_items) == 0:
            continue

        grouped_item = reduce(_combine_items, group_items)
        grouped_item.name = group_name
        grouped_items.append(grouped_item)

    non_grouped_items = list(filter(lambda x: x.name not in groups.values(), data))

    grouped_data = grouped_items + non_grouped_items

    grouped_data.sort(key=lambda x: x.total_seconds, reverse=True)

    return grouped_data


def _combine_items(
    item_one: WakatimeItemDto, item_two: WakatimeItemDto
) -> WakatimeItemDto:
    combined_total_seconds: float = item_one.total_seconds + item_two.total_seconds
    combined_percent: float = item_one.percent + item_two.percent
    combined_hours: int = item_one.hours + item_two.hours
    combined_minutes: int = item_one.minutes + item_two.minutes

    if combined_minutes >= 60:
        hours = combined_minutes // 60
        minutes = combined_minutes % 60

        combined_hours += hours
        combined_minutes = minutes

    combined_digital = f"{combined_hours}:{combined_minutes}"
    combined_decimal = f"{combined_hours}.{combined_minutes // 0.6}"
    combined_text = f"{f"{combined_hours} hrs" if combined_hours != 0 else ""} {combined_minutes} mins"

    return WakatimeItemDto(
        total_seconds=combined_total_seconds,
        name=item_one.name,
        percent=combined_percent,
        digital=combined_digital,
        decimal=combined_decimal,
        text=combined_text,
        hours=combined_hours,
        minutes=combined_minutes,
    )
