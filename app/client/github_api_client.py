# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false
import logging
from typing import Any
import requests
from dotenv import load_dotenv
from ruamel.yaml import YAML

from ..model.github_language_item_dto import GithubLanguageItemDto

log = logging.getLogger(__name__)

_ = load_dotenv()


def get_github_languages() -> list[GithubLanguageItemDto]:
    url = "https://raw.githubusercontent.com/github-linguist/linguist/master/lib/linguist/languages.yml"

    log.info("Requesting languages.yml from the github-linguist")

    response = requests.get(url)

    log.debug(f"Response status code: {response.status_code}")

    yaml = YAML()
    languages_yaml: dict[str, Any] = yaml.load(response.text)

    languages: list[GithubLanguageItemDto] = []

    for key in languages_yaml.keys():
        language = {"name": key, **languages_yaml.get(key)}  # type: ignore[all]
        languages.append(GithubLanguageItemDto(language))

    return languages
