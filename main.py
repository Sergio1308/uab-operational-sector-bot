import asyncio
import logging
import sys

from bot.handlers import callback_router, message_router, group_router
from config import dp, bot, group_chat_id_is_None


async def main():
    logFormat = "%(asctime)s [%(levelname)s] [%(threadName)s] - %(name)s - %(message)s"
    logging.basicConfig(
        filename="logs",
        filemode='a',
        encoding='utf-8',
        level=logging.DEBUG,
        format=logFormat,
        datefmt='%Y-%m-%d %H:%M:%S')
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logging.Formatter(logFormat))
    logging.getLogger().addHandler(consoleHandler)

    dp.include_routers(message_router, callback_router, group_router)
    if group_chat_id_is_None():
        logging.warning('Administrator did not add this bot to the group chat for receiving applications!')
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot was turned off!")
