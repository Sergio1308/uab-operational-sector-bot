import asyncio
import logging
import sys

from bot.handlers import callback_router, message_router, group_router
from config import dp, bot, group_chat_id_is_None


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        stream=sys.stdout)
    dp.include_routers(message_router, callback_router, group_router)
    if group_chat_id_is_None():
        logging.warning('Administrator did not add this bot to the group chat for receiving applications!')
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot was turned off!")
