from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BUTTONS_IN_ROW, TYPES_OF_APPEAL


def create_back_to_new_app_markup() -> InlineKeyboardMarkup:
    return create_inline_keyboard(['Повернутись назад'], ['new_application'])


def create_back_to_room_markup() -> InlineKeyboardMarkup:
    return create_inline_keyboard(['Повернутись назад'], ['back_to_room'])


def create_types_of_appeal_markup() -> InlineKeyboardMarkup:
    return create_inline_keyboard([*TYPES_OF_APPEAL])


def create_starting_new_app_markup() -> InlineKeyboardMarkup:
    return create_inline_keyboard(['Почати нове звернення'], ['new_application'])


def delete_message_app_group_markup() -> InlineKeyboardMarkup:
    return create_inline_keyboard(['Видалити повідомлення'], ['delete_msg_application'])


def create_inline_keyboard(texts: list, callbacks=None) -> InlineKeyboardMarkup:
    if callbacks is None:
        callbacks = texts
    return InlineKeyboardBuilder().add(
        *[InlineKeyboardButton(text=text, callback_data=callback) for text, callback in zip(texts, callbacks)]
    ).adjust(BUTTONS_IN_ROW).as_markup()
