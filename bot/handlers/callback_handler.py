import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramMigrateToChat
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from config import TYPES_OF_APPEAL
from ..inlinekeyboard import create_back_to_new_app_markup
from ..states import Form

callback_router = Router()


@callback_router.callback_query(F.data == 'new_application')
async def handle_new_application(callback: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    if (current_state is None) or (current_state == Form.room):
        await state.set_state(Form.address)
        await callback.message.delete_reply_markup()
        await callback.message.answer(f"Вітаю!\nВведіть адресу👇:")
    else:
        await callback.answer()


@callback_router.callback_query(F.data.in_(TYPES_OF_APPEAL))
async def handle_type_of_appeal(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(type_of_appeal=callback.data.title())
    await state.set_state(Form.message)
    await callback.message.delete_reply_markup()
    await callback.message.answer(f"Напишіть ваше повідомлення👇:")


@callback_router.callback_query(Form.full_name, F.data == 'back_to_room')
async def handle_hide_application(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Form.room)
    await callback.message.edit_text(f"Введіть номер кімнати або місце розташування👇:",
                                     reply_markup=create_back_to_new_app_markup())


@callback_router.callback_query(F.data == 'delete_msg_application')
async def handle_hide_application(callback: CallbackQuery) -> None:
    user = callback.from_user
    user_data = f"[id={user.id} username={user.username}]"
    application = ' '.join(callback.message.text.split())
    try:
        await callback.message.delete()
    except TelegramBadRequest:  # if trying to delete an old message
        await callback.message.edit_text("Видалено")
        logging.warning(f"User {user_data} tried to delete an old application {application}, but got "
                        f"TelegramBadRequest exception. Message text was edited.")
    except TelegramForbiddenError:
        logging.warning(f"User {user_data} tried to delete an old application, but got "
                        f"TelegramForbiddenError exception. Bot is not a member of the group chat.")
        await callback.answer()
    except TelegramMigrateToChat:
        logging.warning(f"User {user_data} tried to delete an old application [{application}],\n"
                        f"but the group status was changed to the supergroup.")
        await callback.answer()
    else:
        logging.info(f"User {user_data} successfully deleted the application "
                     f"[{application}]")


@callback_router.callback_query()
async def process_any_form_callback(callback: CallbackQuery) -> None:
    await callback.answer()
