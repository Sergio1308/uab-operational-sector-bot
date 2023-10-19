import json

from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import BasicAuth

from env_loading import load_env_variable
from aiogram import Bot
from aiogram import Dispatcher
from aiogram.enums import ParseMode


auth = BasicAuth(login='login', password='password')
session = AiohttpSession(proxy=('http://proxy.server:3128', auth))

BOT_TOKEN = load_env_variable("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, session=session, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# region bot_config.json
config_file = 'bot_config.json'
# default configuration if file not found
default_config = {
    "admins": [595033749, 372977380],
    "group_chat_id": None,
    "types_of_appeal": ["Технічний", "Господарський"],
    "buttons_in_row": 3
}

try:
    with open(config_file, 'r', encoding='utf-8') as file:
        config = json.load(file)
except FileNotFoundError:
    # Create the config file with default values
    with open(config_file, 'w', encoding='utf-8') as file:
        json.dump(default_config, file, indent=4, ensure_ascii=False)
    config = default_config

ADMINS = config["admins"]
GROUP_CHAT_ID = config["group_chat_id"]
TYPES_OF_APPEAL = config["types_of_appeal"]
BUTTONS_IN_ROW = config["buttons_in_row"]


def update_group_chat_id(new_group_chat_id):
    config["group_chat_id"] = new_group_chat_id
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def get_group_chat_id():
    return config["group_chat_id"]


def group_chat_id_is_None():
    return GROUP_CHAT_ID is None
# endregion
