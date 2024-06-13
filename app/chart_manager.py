import datetime
import logging
import os
from uuid import UUID
from matplotlib.figure import Figure

PLOTS_DIRECTORY: str = "plots"
DATE_SEPARATOR: str = "_"

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def save_chart(figure: Figure, uuid: UUID):
    log.debug(f"Saving plot {uuid}")

    date = datetime.datetime.now()
    date = date.strftime("%y-%m-%d")

    figure.savefig(f"{PLOTS_DIRECTORY}/{uuid}{DATE_SEPARATOR}{date}.png")  # type: ignore[all]


def find_by_uuid(uuid: UUID) -> str | None:
    log.debug(f"Searching plot {uuid}")

    for plot in os.listdir(PLOTS_DIRECTORY):
        if str(uuid) in plot:
            return os.path.join(PLOTS_DIRECTORY, plot)

    return None
