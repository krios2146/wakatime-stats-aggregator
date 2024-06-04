import logging
from typing import Annotated
from fastapi import FastAPI, Query, Request
from fastapi.datastructures import QueryParams


log = logging.getLogger("uvicorn.error")
log.level = logging.DEBUG

app = FastAPI()


@app.get("/api/{username}/pie/languages")
def languages(username: str, hide: str | None = None):
    languages_to_hide: set[str] | None = _parse_hide(hide)

    return {
        "username:": username,
        "hide": languages_to_hide,
    }


@app.get("/api/{username}/pie/projects")
def projects(
    username: str,
    request: Request,
    hide: Annotated[list[str] | None, Query()] = None,
    group: Annotated[list[str] | None, Query()] = None,
):
    elements_to_hide: set[str] | None = _parse_hide_list(hide)
    projects_colors: dict[str, str] | None = None

    groups: dict[str, set[str]] | None = None
    groups_colors: dict[str, str] | None = None

    parse_group_result = _parse_group(group, request.query_params)

    if parse_group_result is not None:
        (groups, groups_colors) = parse_group_result

    projects_colors = _parse_project_colors(
        request.query_params, list(groups.keys()) if groups is not None else None
    )

    return {
        "username:": username,
        "elements_to_hide": elements_to_hide,
        "groups": groups,
        "groups_colors": groups_colors,
        "projcts_colors": projects_colors,
    }


@app.get("/api/{username}/pie/editors")
def editors(username: str, hide: str | None = None):
    editors_to_hide: set[str] | None = _parse_hide(hide)

    return {"username:": username, "hide": editors_to_hide}


def _parse_hide_list(hide_query: list[str] | None) -> set[str] | None:
    if hide_query is None:
        return None

    elements_to_hide: set[str] = set()

    for hide_param in hide_query:
        elements_to_hide.update(hide_param.split(","))

    return elements_to_hide


def _parse_hide(hide_query: str | None) -> set[str] | None:
    if hide_query is None:
        return None

    elements_to_hide: set[str] = set(hide_query.split(","))

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

            groups[group] = set(projects.split(","))

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
