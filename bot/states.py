from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    address = State()
    room = State()
    full_name = State()
    phone_number = State()
    type_of_appeal = State()
    message = State()

    application_data: dict = State()
