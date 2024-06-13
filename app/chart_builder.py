import logging
from uuid import UUID
import matplotlib
import matplotlib.pyplot as plt

from . import chart_manager
from .model.github_language_item_dto import GithubLanguageItemDto
from .model.wakatime.wakatime_item_dto import WakatimeItemDto

matplotlib.use("TkAgg")
custom_font = {
    "font.family": "sans-serif",
    "font.serif": ["Segoe UI"],
}

matplotlib.rcParams.update(custom_font)

GITHUB_BG_COLOR: str = "#0D1117"
GITHUB_FG_COLOR: str = "#C3D1D9"

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def create_pie_chart(
    data_list: list[WakatimeItemDto],
    uuid: UUID,
    langs_data: list[GithubLanguageItemDto] | None = None,
) -> None:
    log.info(f"Creating pie chart {uuid}")
    box, (left_plot, right_plot) = plt.subplots(1, 2)  # type: ignore[all]

    percents: list[float] = [data.percent for data in data_list[:5]]
    names: list[str] = [data.name for data in data_list[:5]]
    hours: list[str] = [data.text for data in data_list[:5]]

    colors = _get_colors(langs_data, names)

    # creating pie based on percents, shape it with wedgeprops
    wedges, autotext = right_plot.pie(
        percents, colors=colors, wedgeprops=dict(width=0.2, radius=0.95)
    )

    # building left side legend
    labels = [
        f"{name} {percent}% - {hour}"
        for name, percent, hour in zip(names, percents, hours)
    ]

    # hiding legend text on the pie
    for text in autotext:
        text.set_alpha(0)

    # associate data from the pie (wedges) to the labels
    legend = left_plot.legend(wedges, labels, loc="center", frameon=False)
    left_plot.axis("off")

    for text in legend.get_texts():
        text.set_color(GITHUB_FG_COLOR)

    # setting background for the entire box (figure)
    box.patch.set_facecolor(GITHUB_BG_COLOR)

    chart_manager.save_chart(box, uuid)


def _get_colors(
    github_langs_data: list[GithubLanguageItemDto] | None, languages: list[str]
) -> list[str | tuple[float, float, float, float]] | None:
    if github_langs_data is None:
        return None

    colors: list[str | tuple[float, float, float, float]] = []
    defaultColors = plt.get_cmap("tab10")

    for index, language in enumerate(languages):
        found = False
        for github_language in github_langs_data:

            if github_language.name.lower() == language.lower():
                _ = colors.append(github_language.color)
                found = True
                break

        # use default colors for missing langs
        if not found:
            _ = colors.append(defaultColors(index))

    return colors
