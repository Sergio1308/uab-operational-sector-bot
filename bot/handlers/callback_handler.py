from aiogram import F, Router
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
        await callback.message.delete()
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
    await callback.message.delete()
    await callback.answer('Видалено')


@callback_router.callback_query()
async def process_any_form_callback(callback: CallbackQuery) -> None:
    await callback.answer()
