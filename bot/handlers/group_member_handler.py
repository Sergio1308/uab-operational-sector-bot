import logging

from aiogram import Router, F
from aiogram.exceptions import TelegramMigrateToChat, TelegramForbiddenError
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION
from aiogram.types import ChatMemberUpdated

from bot.filters import IsAdmin
from config import bot, update_group_chat_id, get_group_chat_id

group_router = Router()
group_router.message.filter(F.chat.type.in_({"group", "supergroup"}))


@group_router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION), IsAdmin())
async def on_join_group(event: ChatMemberUpdated):
    current_chat_id = event.chat.id
    previous_chat_id = get_group_chat_id()

    if (previous_chat_id is not None) and (previous_chat_id != event.chat.id):
        try:
            await bot.send_message(
                previous_chat_id, f'Я був доданий до іншої групи адміністратором @{event.from_user.username}, '
                                  f'тепер мої повідомлення надсилатимуться туди')
            await bot.leave_chat(previous_chat_id)
        except TelegramMigrateToChat as err:
            new_chat_id = err.migrate_to_chat_id
            update_group_chat_id(new_chat_id)
            await bot.send_message(new_chat_id, f'Статус групи було змiнено на {event.chat.type}. Заявки, надіслані '
                                                f'раніше, тепер не можна буде видалити по кнопці, видаляйте вручну')
            logging.info("Status group was changed to supergroup")
            return
        except TelegramForbiddenError:
            # bot was kicked from the previous chat, do nothing
            pass
    update_group_chat_id(current_chat_id)
    welcome_message = "Привіт! Я ваш бот, і я тут, щоб допомогти вам.\nЯ надсилатиму сюди нові заявки від " \
                      "користувачів. Як тільки ви обробите одну заявку, ви зможете натиснути кнопку під моїм " \
                      "повідомленням щоб видалити її з чату, таким чином ви зможете відзначити її як оброблену. "
    await bot.send_message(current_chat_id, welcome_message)
    logging.info(f'Bot has been added to the {event.chat.type} with id={current_chat_id} '
                 f'by admin with id={event.from_user.id} and username={event.from_user.username}')


@group_router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION), ~IsAdmin())
async def on_join_group_without_permission(event: ChatMemberUpdated):
    await bot.send_message(event.chat.id, 'У вас немає прав на додавання мене до групи. Зверніться до '
                                          'адміністратора/власника бота!')
    logging.info(f'Bot has been added to the {event.chat.type} by admin with id={event.from_user.id} '
                 f'and username={event.from_user.username} but he does not have the rights to do this.')
    await bot.leave_chat(event.chat.id)


# Bot gets LEFT status instead of KICKED when group admin kicks him from group, so just check if the user is in the
# list of admins (has permission) using chat member filter
@group_router.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION), IsAdmin())
async def on_kicked_from_group(event: ChatMemberUpdated):
    if event.chat.id == get_group_chat_id():
        update_group_chat_id(None)
    logging.warning(f'Bot was kicked from the {event.chat.type} with id={event.chat.id} '
                    f'by admin with id={event.from_user.id} and username={event.from_user.username}!'
                    f'\nFull chat info=[{event.chat}]\n')


@group_router.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION), ~IsAdmin())
async def left_group(event: ChatMemberUpdated):
    chat_type = event.chat.type
    # If the admin deletes the group, the bot itself will leave it
    if event.chat.id == get_group_chat_id():
        update_group_chat_id(None)
    logging.info(f'Bot left the {chat_type} with id={event.chat.id}, title={event.chat.title}! '
                 f'\nFull chat info: [{event.chat}]\n')
