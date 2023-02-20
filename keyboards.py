from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
cb = CallbackData('start_kbd', 'action')

start_kbd = InlineKeyboardMarkup(row_width=1)
new_task_btn = InlineKeyboardButton(text='Создать новую заявку', callback_data=cb.new('new_task'))
check_task_btn = InlineKeyboardButton(text='Получить информацию по заявке', callback_data=cb.new('check_task'))
start_kbd.add(new_task_btn, check_task_btn)

main_kbd = InlineKeyboardMarkup(row_width = 2)
health_btn = InlineKeyboardButton(text='Медицина', callback_data='health')
sport_btn = InlineKeyboardButton(text='Спорт',callback_data='sport')
recreation_btn = InlineKeyboardButton(text='Отдых', callback_data='recreation')
hobby_btn = InlineKeyboardButton(text='Хобби', callback_data='hobby')
main_kbd.add(health_btn, sport_btn).add(recreation_btn, hobby_btn)