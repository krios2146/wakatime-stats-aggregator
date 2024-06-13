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
    github_languages: list[GithubLanguageItemDto] | None = None

    match chart_request.chart_data:
        case ChartData.LANGUAGES:
            data = response.data.languages
            github_languages = github_api_client.get_github_languages()

        case ChartData.PROJECTS:
            data = response.data.projects

        case ChartData.EDITORS:
            data = response.data.editors

    assert data is not None

    match chart_request.chart_type:
        case ChartType.PIE:
            chart_builder.create_pie_chart(data, chart_request.uuid, github_languages)

    chart_path: str | None = chart_manager.find_by_uuid(chart_request.uuid)

    if chart_path is None:
        return None

    return Chart(chart_request.uuid, chart_path)
