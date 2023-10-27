import logging

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest, TelegramMigrateToChat, TelegramForbiddenError
from aiogram.filters import Command, ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ErrorEvent
from aiogram.utils.markdown import hbold

from bot.filters import IsAdmin
from bot.inlinekeyboard import create_back_to_new_app_markup, create_back_to_room_markup, \
    create_types_of_appeal_markup, create_starting_new_app_markup, delete_message_app_group_markup
from bot.models import Application
from bot.states import Form
from config import bot, get_group_chat_id, update_group_chat_id

message_router = Router()
message_router.message.filter(F.chat.type == "private")


@message_router.message(Command("start"))
async def start_command(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.address)
    await message.answer(f"Вітаю!\nВведіть адресу👇:")


@message_router.message(Command("cancel"))
async def cancel_operation(message: Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        await message.answer("Ви ще не створювали нового звернення")
    else:
        await state.clear()
        await message.answer("Скасовано")


@message_router.message(Form.address)
async def process_address(message: Message, state: FSMContext) -> None:
    await state.update_data(address=message.text)
    await state.set_state(Form.room)
    await message.answer(f"Введіть номер кімнати або місце розташування👇:",
                         reply_markup=create_back_to_new_app_markup())


@message_router.message(Form.room)
async def process_room(message: Message, state: FSMContext) -> None:
    await state.update_data(room=message.text)
    await state.set_state(Form.full_name)
    await message.answer(f"Введіть ПIБ (Прізвище Ім'я По-батькові)👇:", reply_markup=create_back_to_room_markup())


@message_router.message(Form.full_name)
async def process_full_name(message: Message, state: FSMContext) -> None:
    await state.update_data(full_name=message.text)
    await state.set_state(Form.phone_number)
    await message.answer(f"Введіть номер телефону👇:")


@message_router.message(Form.phone_number)
async def process_phone_number(message: Message, state: FSMContext) -> None:
    # don't need a phone number validation. User is supposed to enter a custom number
    await state.update_data(phone_number=message.text)
    await state.set_state(Form.type_of_appeal)
    await message.answer(f"Оберіть характер звернення👇:", reply_markup=create_types_of_appeal_markup())


@message_router.message(Form.message)
async def process_appeal_message(message: Message, state: FSMContext) -> None:
    await state.update_data(message=message.text)
    user = message.from_user
    try:
        user_data = await state.get_data()
        app = Application(
            user_data['address'], user_data['room'], user_data['full_name'],
            user_data['phone_number'], user_data['type_of_appeal'], user_data['message']
        )
        await state.update_data(application_model=app)
        group_chat_id = get_group_chat_id()
        if group_chat_id:
            await send_application_to_group_chat(message, group_chat_id, app)
        else:
            logging.warning(f"Failed to send application from user {user.username} id={user.id} ."
                            f"\nAdministrator did not add this bot to the group chat for receiving applications."
                            f"\nApplication not sent: {app}")
            await message.answer("Не вдалося надіслати заявку. Зв'яжіться з адміністратором, оскільки він не "
                                 "налаштував груповий чат для їх отримання")
    except TelegramMigrateToChat as err:
        new_chat_id = err.migrate_to_chat_id
        update_group_chat_id(new_chat_id)
        logging.warning(f"Group chat was upgraded to a supergroup chat! Group chat id was changed to {new_chat_id}")
        user_data = await state.get_data()
        app = user_data['application_model']
        await send_application_to_group_chat(message, new_chat_id, app)
    except Exception as err:
        user_data = await state.get_data()
        logging.error(f"Error when trying to send an application from user @{user.username} id={user.id}.\n{err}"
                      f"\nApplication not sent: {user_data['application_model']}")
        await message.answer(f"Упс, щось пішло не так! Залиште звернення знову, для цього введiть команду /start")
    await state.clear()


async def send_application_to_group_chat(message: Message, chat_id: int, app: Application) -> None:
    await bot.send_message(
        chat_id,
        f"Нова заявка за адресою: {hbold(app.address)}"
        f"\n\nКімната: {hbold(app.cabinet)}"
        f"\n\nЗаявка від: {hbold(app.full_name)}"
        f"\n\nКонтактний номер: {hbold(app.contact_number)}"
        f"\n\nХарактер звернення: {hbold(app.type_of_appeal)}"
        f"\n\nТекст заявки: '{hbold(app.text_message)}'",
        reply_markup=delete_message_app_group_markup()
    )
    await message.answer(f"Заявка відправлена. Дякую за звернення!",
                         reply_markup=create_starting_new_app_markup())


@message_router.message(Command("check"), IsAdmin())
async def check_sending_to_group_chat(message: Message) -> None:
    chat_id = get_group_chat_id()
    if chat_id is None:
        await message.answer('Я ще не був доданий до групового чату для прийому заявок! '
                             'Заявки від користувачів не надсилатимуться!')
        return
    await message.answer(f'Вітаю, адміне! На даний момент я перебуваю в групі з ID=[{chat_id}], '
                         f'зараз я спробую надіслати туди тестове повідомлення!')
    try:
        await bot.send_message(chat_id,
                               'Це тестове повідомлення. Адміністратор/власник бота запросив перевірку, '
                               'щоб дізнатися, куди я надсилатиму заявки.\nЗаявки будуть надсилатися сюди.')
    except (TelegramBadRequest, TelegramForbiddenError, TelegramMigrateToChat):
        await message.answer('Помилка! Не вдалося вiдправити повiдомлення.'
                             '\nДодайте мене в потрібну групу ще раз (якщо я там вже є, '
                             'тоді видаліть і додайте заново)')


@message_router.message()
async def process_other_messages(message: Message) -> None:
    try:
        await message.answer("Невідома команда/повідомлення.\nДля створення нового звернення введіть команду "
                             "/start,\nабо /cancel для скасування")
    except TypeError:
        await message.answer("Упс, щось пішло не так! Залиште звернення знову, для цього введіть команду /start")


@message_router.error(ExceptionTypeFilter(Exception))
async def handle_private_chat_errors(event: ErrorEvent):
    logging.exception("Exception caused by %s", event.exception, exc_info=True)


@message_router.errors
async def handle_private_chat_errors(event: ErrorEvent):
    logging.critical("Critical error caused by %s", event.exception, exc_info=True)
