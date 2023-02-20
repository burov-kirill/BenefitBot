import ast
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN_API, ClientStatesGroup
from aiogram import executor, Bot, Dispatcher, types
from keyboards import start_kbd, main_kbd
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
import sql_scripts
import datetime


bot = Bot(TOKEN_API)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
cb = CallbackData('start_kbd', 'action')

# @dp.message_handler(content_types=[types.ContentType.NEW_CHAT_MEMBERS])
# async def new_members_handler(message: types.Message):
#     new_member = message.new_chat_members[0]
#     await bot.send_message(message.chat.id, f"Добро пожаловать, {new_member.mention}")

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message) -> None:
    await message.answer('Вас приветствует Кафетерий Бот.\nС помощью меня вы можете создать новую заявку '
                         'или узнать дату выплаты по текущей заявке',
                         reply_markup=start_kbd)
@dp.callback_query_handler(cb.filter(action='new_task'))  # single responsibility principle
async def push_first_cb_handler(callback: types.CallbackQuery) -> None:
    # await callback.answer()
    await callback.answer()
    await callback.message.answer('Пожалуйста, отправьте вашу фамилию')
    await ClientStatesGroup.last_name.set()

@dp.message_handler(state=ClientStatesGroup.last_name)
async def load_last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text

    await ClientStatesGroup.next()
    await message.reply('А теперь, отправьте нам ваше имя!')

@dp.message_handler(state=ClientStatesGroup.first_name)
async def load_first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text

    await ClientStatesGroup.next()
    await message.reply('И наконец, отправьте пожалуйста отчество')

@dp.message_handler(state=ClientStatesGroup.third_name)
async def load_third_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['third_name'] = message.text
        await message.answer('Ваши данные получены и обработаны')
        result = sql_scripts.show_query_result(data["last_name"],
                               data["first_name"], data["third_name"])
        if type(result)==list:
            await message.answer(text='Пожалуйста, подтвердите ваши данные')
            for elem in result:
                await bot.send_message(chat_id=message.chat.id, text = elem[0], reply_markup=elem[1])
        else:
            await bot.send_message(chat_id=message.chat.id, text = result)
            await bot.send_message(chat_id=message.chat.id, text='Попробуйте ввести заново данные',reply_markup=start_kbd)

    await ClientStatesGroup.next()

@dp.callback_query_handler(state = ClientStatesGroup.user_id)
async def check_user_answer(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        callback_dict = ast.literal_eval(callback.data)
        data['user_id'] = int(callback_dict['id'])
    #Добавить проверку на то, что сумма меньше 10 000
        if callback_dict['is_fired'] == 'yes':
            await callback.answer()
            await callback.message.answer(text=f'Извините, но данный сотрудник уволен\n'
                                               f'Попробуйте снова оформить заявку', reply_markup=start_kbd)
        else:
            await callback.answer()

            await callback.message.answer(text=f'Вы можете оформить заявку\n'
                                               f'Пожалуйста, выберите один из 4 вариантов кафетерия льгот', reply_markup=main_kbd)
    await ClientStatesGroup.next()
@dp.callback_query_handler(state=ClientStatesGroup.category)
async def load_category(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = callback.data

    await callback.answer()
    await callback.message.answer(f"Введите сумму заявки")
    await callback.message.answer(text='Обращаем ваше внимание на то что максимальная сумма для возмещения составляет 10 000 рублей за текущий год')
    await ClientStatesGroup.next()

@dp.message_handler(state=ClientStatesGroup.order_sum)
async def load_order_sum(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['order_sum'] = int(message.text)
    if sql_scripts.check_user_sum(data['user_id'])>=10000:
        await message.answer('Извиние, но за текущий год вы исчерпали лимит возмещения', reply_markup=start_kbd)
        await bot.send_sticker(chat_id=message.chat.id, sticker='CAACAgIAAxkBAAEHx3Bj709_8txbUAehgnDeXeNTac5T_QACmhQAAsnkkUnqr1sH9YtLZi4E')
    else:
        current_time = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        res = sql_scripts.insert_into_orders(data['user_id'], data['last_name'],
                                             data['first_name'], data['third_name'],
                                             current_time, data['category'], data['order_sum'])
        await message.reply(f"Заявка оформлена")
        await bot.send_sticker(chat_id=message.chat.id, sticker='CAACAgIAAxkBAAEHx2Rj70bMRo6gVhFcwu1kDBMX_pEjDgACfRMAAqN3qEvCWDsDiG_N4C4E')
    await state.finish()



if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True)

