import logging
import requests
from base64 import b64encode
import os
from dotenv import load_dotenv
from dacite import from_dict

from ..exception.WakatimeCredentialsMissingError import WakatimeCredentialsMissingError
from ..model.wakatime.wakatime_response import WakatimeResponse

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_ = load_dotenv()


def get_last_7_days(username: str) -> WakatimeResponse:
    base_url: str | None = os.getenv("WAKATIME_BASE_URL")
    api_key: str | None = os.getenv("WAKATIME_API_KEY")

    if api_key is None:
        log.error("WAKATIME_API_KEY couldn't be obtained from the .env file")
        raise WakatimeCredentialsMissingError(
            "WAKATIME_API_KEY is None, aborting API call"
        )

    if base_url is None:
        log.error("WAKATIME_BASE_URL couldn't be obtained from the .env file")
        raise WakatimeCredentialsMissingError(
            "WAKATIME_BASE_URL is None, aborting API call"
        )

    api_key_encoded = b64encode(api_key.encode())

    headers = {"Authorization": f"Basic {api_key_encoded.decode()}"}

    log.info("Requesting last 7 days data from Wakatime")

    response = requests.get(
        f"{base_url}/users/{username}/stats/last_7_days", headers=headers
    )

    log.debug(f"Response status code: {response.status_code}")

    return from_dict(data_class=WakatimeResponse, data=response.json())


if __name__ == "__main__":
    log.info("This should not be run as a module")
