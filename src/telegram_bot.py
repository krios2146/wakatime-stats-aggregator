import json
import logging
import os
from typing import Any
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from api_client import get_github_languages_info, get_last_7_days_data
from data_node.github_language_data_node import GithubLanguageDataNode
from data_node.wakatime_data_node import WakatimeDataNode
from data_processor import show_pie_chart
from exception.ChatIdMissingError import ChatIdMissingError
from exception.WakatimeCredentialsMissingErrro import WakatimeCredentialsMissingError

logging.basicConfig(
    format="%(asctime)s -- %(levelname)s -- [%(module)s]: %(message)s",
    datefmt="%Y-%m-%d @ %H:%M:%S",
)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_ = load_dotenv()

token = os.getenv("TELEGRAM_API_TOKEN")


def initialize_bot():
    log.info("Initializing bot")

    if token is None:
        log.error("TELEGRAM_API_TOKEN is None, aborting starting the bot")
        return

    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler("start", start)
    languages_handler = CommandHandler("languages", languages)
    editors_handler = CommandHandler("editors", editors)
    projects_handler = CommandHandler("projects", projects)

    application.add_handler(start_handler)
    application.add_handler(languages_handler)
    application.add_handler(editors_handler)
    application.add_handler(projects_handler)

    application.run_polling()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.debug("/start command was requested")

    _ = await context.bot.set_my_commands(
        [
            ("/projects", "Projects data"),
            ("/editors", "Editors data"),
            ("/languages", "Languages data"),
            ("/start", "Start the bot"),
        ]
    )

    try:
        message = "See available commands in the menu"

        _ = await _send_message(context, update, message)

    except ChatIdMissingError as e:
        log.error(str(e))
        return


async def editors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.debug("/editors command was requested")

    try:
        editors = get_last_7_days_data()["editors"]
        show_pie_chart([WakatimeDataNode(editor) for editor in editors])
        editors = _format_to_json_code_block(editors)

        _ = await _send_message(context, update, editors)

    except ChatIdMissingError as e:
        log.error(str(e))
        return

    except WakatimeCredentialsMissingError as e:
        log.debug(
            f"Couldn't obtain editors info - ({str(e)}), responding with an error"
        )
        _ = await _send_error(context, update)


async def languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.debug("/languages command was requested")

    try:
        wakatime_languages_response: list[dict[str, Any]] = get_last_7_days_data()[
            "languages"
        ]
        github_languages_response: list[dict[str, Any]] = get_github_languages_info()

        wakatime_languages_data = [
            WakatimeDataNode(language) for language in wakatime_languages_response
        ]
        github_languages_data = [
            GithubLanguageDataNode(language) for language in github_languages_response
        ]
        github_languages_data.append(
            GithubLanguageDataNode({"name": "Vue.js", "color": "#41b883"})
        )
        github_languages_data.append(
            GithubLanguageDataNode({"name": "Bash", "color": "#89e051"})
        )

        show_pie_chart(wakatime_languages_data, langs_data=github_languages_data)
        languages: str = _format_to_json_code_block(wakatime_languages_response)

        _ = await _send_message(context, update, languages)

    except ChatIdMissingError as e:
        log.error(str(e))
        return

    except WakatimeCredentialsMissingError as e:
        log.debug(
            f"Couldn't obtain languages info - ({str(e)}), responding with an error"
        )
        _ = await _send_error(context, update)


async def projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.debug("/projects command was requested")

    try:
        projects = get_last_7_days_data()["projects"]
        show_pie_chart([WakatimeDataNode(project) for project in projects])
        projects = _format_to_json_code_block(projects)

        _ = await _send_message(context, update, projects)

    except ChatIdMissingError as e:
        log.error(str(e))
        return

    except WakatimeCredentialsMissingError as e:
        log.debug(
            f"Couldn't obtain projects info - ({str(e)}), responding with an error"
        )
        _ = await _send_error(context, update)


async def _send_message(
    context: ContextTypes.DEFAULT_TYPE, update: Update, message: str
):
    _ = await context.bot.send_message(
        chat_id=_get_chat_id(update), text=message, parse_mode="MarkdownV2"
    )


async def _send_error(context: ContextTypes.DEFAULT_TYPE, update: Update):
    error_message = (
        "There is an error occured while processing request, try again later"
    )
    _ = await _send_message(context, update, error_message)


def _format_to_json_code_block(message: Any) -> str:
    message_json = json.dumps(message, indent=2)

    message_json_block = f"```json\n{message_json}\n```"

    return message_json_block


def _get_chat_id(update: Update) -> int:
    if update.effective_chat is None:
        raise ChatIdMissingError("Couldn't obtain chat_id fot the bot response")
    else:
        return update.effective_chat.id


if __name__ == "__main__":
    initialize_bot()
