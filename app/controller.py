import logging
from typing import Annotated
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.datastructures import QueryParams
from fastapi.responses import FileResponse

from . import chart_service
from .model.chart import Chart
from .model.chart_data import ChartData
from .model.chart_type import ChartType
from .model.chart_request import ChartRequest


log = logging.getLogger(__name__)

app = FastAPI()


@app.get("/api/{username}/pie/languages")
def languages(username: str, request: Request, hide: str | None = None) -> FileResponse:
    languages_to_hide: set[str] | None = _parse_hide(hide)
    language_colors: dict[str, str] | None = _parse_colors(request.query_params)

    chart_request: ChartRequest = ChartRequest(
        ChartType.PIE,
        ChartData.LANGUAGES,
        username,
        hide=languages_to_hide,
        colors=language_colors,
    )

    chart: Chart | None = chart_service.create_chart(chart_request)

    if chart is None:
        raise HTTPException(
            status_code=500, detail="Couldn't create a pie chart for some reason"
        )

    return FileResponse(chart.path)


@app.get("/api/{username}/pie/projects")
def projects(
    username: str,
    request: Request,
    hide: Annotated[list[str] | None, Query()] = None,
    group: Annotated[list[str] | None, Query()] = None,
):
    elements_to_hide: set[str] | None = _parse_hide_list(hide)
    project_colors: dict[str, str] | None = None

    groups: dict[str, set[str]] | None = None
    group_colors: dict[str, str] | None = None

    parse_group_result = _parse_group(group, request.query_params)

    if parse_group_result is not None:
        (groups, group_colors) = parse_group_result

    project_colors = _parse_project_colors(
        request.query_params, list(groups.keys()) if groups is not None else None
    )

    chart_request: ChartRequest = ChartRequest(
        ChartType.PIE,
        ChartData.PROJECTS,
        username,
        hide=elements_to_hide,
        colors=project_colors,
        groups=groups,
        group_colors=group_colors,
    )

    chart: Chart | None = chart_service.create_chart(chart_request)

    if chart is None:
        raise HTTPException(
            status_code=500, detail="Couldn't create a pie chart for some reason"
        )

    return FileResponse(chart.path)


@app.get("/api/{username}/pie/editors")
def editors(username: str, request: Request, hide: str | None = None):
    editors_to_hide: set[str] | None = _parse_hide(hide)
    editor_colors: dict[str, str] | None = _parse_colors(request.query_params)

    chart_request: ChartRequest = ChartRequest(
        ChartType.PIE,
        ChartData.EDITORS,
        username,
        hide=editors_to_hide,
        colors=editor_colors,
    )

    chart: Chart | None = chart_service.create_chart(chart_request)

    if chart is None:
        raise HTTPException(
            status_code=500, detail="Couldn't create a pie chart for some reason"
        )

    return FileResponse(chart.path)


def _parse_hide_list(hide_query: list[str] | None) -> set[str] | None:
    if hide_query is None:
        return None

    elements_to_hide: set[str] = set()

    for hide_param in hide_query:
        elements_to_hide.update(map(str.lower, hide_param.split(",")))

    return elements_to_hide


def _parse_hide(hide_query: str | None) -> set[str] | None:
    if hide_query is None:
        return None

    elements_to_hide: set[str] = set(map(str.lower, hide_query.split(",")))

    return elements_to_hide if len(elements_to_hide) != 0 else None


def _parse_group(
    group_query: list[str] | None, query: QueryParams
) -> tuple[dict[str, set[str]] | None, dict[str, str] | None] | None:
    """
    Return a tuple where:
    - the first element is a dict from group name to set of projects in this group;
    - the second element is a dict from group name to the color of this group.

    Both elements of the tuple are optional and may be None.
    If the element is present in the tuple is guaranteed to be non empty.
    """

    if group_query is None:
        return None

    groups: dict[str, set[str]] | None = None
    colors: dict[str, str] | None = None

    for group in set(group_query):
        projects: str | None = query.get(group)
        color: str | None = query.get(f"{group}_color")

        if projects is not None:
            if groups is None:
                groups = dict()

            groups[group] = set(map(str.lower, projects.split(",")))

        if color is not None:
            if colors is None:
                colors = dict()

            colors[group] = color

    return (groups, colors)


def _parse_project_colors(
    query: QueryParams, groups: list[str] | None
) -> dict[str, str] | None:
    project_colors: dict[str, str] | None = None

    for query_item in query.items():
        key = query_item[0]
        if key == "hide":
            continue
        if key == "group":
            continue
        if key.endswith("_color"):
            continue
        if groups is not None and key in groups:
            continue

        if project_colors is None:
            project_colors = dict()

        project_colors[key] = query_item[1]

    return project_colors


def _parse_colors(query: QueryParams | None) -> dict[str, str] | None:
    if query is None:
        return None

    colors: dict[str, str] | None = None

    for query_item in query.items():
        key = query_item[0]

        if key == "hide":
            continue

        if colors is None:
            colors = dict()

        colors[key] = query_item[1]

    return colors
