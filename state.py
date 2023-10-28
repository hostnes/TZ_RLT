from aiogram.dispatcher.filters.state import State, StatesGroup


class SendMessage(StatesGroup):
    get_message = State()

