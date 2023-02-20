from aiogram.dispatcher.filters.state import StatesGroup, State

TOKEN_API = '6106870243:AAH6v7GkpC40cPARtxMa2Xmj8DbSJLC2N6U'


class ClientStatesGroup(StatesGroup):
    last_name = State()
    first_name = State()
    third_name = State()
    user_id = State()
    category = State()
    order_sum = State()