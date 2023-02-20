import sqlite3
from sqlite3 import Error
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

def show_query_result(last_name, first_name, third_name):
    query = f"SELECT * from workers where first_name='{first_name}' and last_name ='{last_name}' and third_name = '{third_name}'"
    connection = create_connection(r"C:\Users\cyril\PycharmProjects\TelegramBots\YoutubeBot\new.db")
    data = execute_read_query(connection, query)
    data_list = []

    if data == []:
        return f'Извините, сотрудник с данным ФИО не найден'
    elif len(data)==1:
        kb = InlineKeyboardMarkup(row_width=1)
        msg = f'ФИО: {data[0][1]} {data[0][2]} {data[0][3]},\nдолжность: {data[0][6]},\nдата приема {data[0][4]}' #вынести в отдельную функцию и сделать класс
        btn = InlineKeyboardButton(text='Пользователь', callback_data=f'{{"id":"{data[0][0]}", "is_fired":"{data[0][5]}"}}')
        kb.add(btn)
        data_list.append((msg, kb))
        return data_list
    else:
        for elem in data:
            kb = InlineKeyboardMarkup(row_width=1)
            msg = f'ФИО: {elem[1]} {elem[2]} {elem[3]},\nдолжность: {elem[6]},\nдата приема {elem[4]}'
            btn = InlineKeyboardButton(text='Подтвердить', callback_data=f'{{"id":"{elem[0]}", "is_fired":"{elem[5]}"}}')
            kb.add(btn)
            data_list.append((msg, kb))
        return data_list

def insert_into_orders(user_id, last_name, first_name, third_name, current_time, category, order_sum):
    connection = create_connection(r"C:\Users\cyril\PycharmProjects\TelegramBots\YoutubeBot\new.db")
    temp_sum = check_user_sum(user_id)
    if temp_sum + order_sum>10000:
        order_sum = 10000-temp_sum
    insert_order = f"""
        INSERT INTO
          orders (user_id, last_name, first_name, third_name, date, category, order_sum)
        VALUES
          ({int(user_id)},'{last_name}', '{first_name}', '{third_name}', '{current_time}', '{category}', {int(order_sum)});
        """
    return execute_query(connection, insert_order)

def check_user_sum(user_id):
    connection = create_connection(r"C:\Users\cyril\PycharmProjects\TelegramBots\YoutubeBot\new.db")
    query = f"""SELECT user_id, sum(order_sum) from orders
                where user_id = {user_id}
                group by user_id"""
    res = execute_read_query(connection, query)
    if res != []:
        return res[0][1]
    else:
        return 0

