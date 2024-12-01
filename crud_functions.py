import sqlite3
from distutils.util import execute

from django.template.defaultfilters import title
from numpy.ma.core import append

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

#Создаем функцию для создания двух таблиц: "Продукты", содержащую столбцы
# id, title, description, price и "Пользователи", содержащую столбцы is,
# username, email, age, balance
def initiate_db():
    cursor.execute('''
CREATE TABLE IF NOT EXISTS Products(
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
description TEXT,
price INT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT NOT NULL,
email TEXT NOT NULL,
age INT NOT NULL,
balance INT NOT NULL
);
''')

# Вызываем функцию создания таблиц
initiate_db()

#Создаем курсор для управления базой данных
cursor.execute("CREATE INDEX IF NOT EXISTS id ON Products (id)")

#Добавляем данные в таблицу "Продукты"
#for i in range(1, 5):
#    cursor.execute("INSERT INTO Products (title, description, price)"
#                     " VALUES (?, ?, ?)", (f"Продукт {i}", f"Описание {i}",
#                                           f"{i * 100}"))
#Удаляем данные из таблицы "Продукты"
# for i in range (21, 25):
#     cursor.execute("DELETE FROM Products WHERE id = ?", (f"{i}",))

#Создаем функцию, достающую из таблицы "Продукты" данные о названии,
# описании и цене, упаковывающую эти данные в списки
def get_all_products():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Products")

    rows = cursor.fetchmany(4)
    titles = []
    for title in rows:
        titles.append(title[1])

    descriptions = []
    for description in rows:
        descriptions.append(description[2])

    prices = []
    for price in rows:
        prices.append(price[3])

    return titles, descriptions, prices

get_all_products()


#Создаем функцию, добавляющую данные в таблицу "Пользователи"
def add_user(username, email, age):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Users (username, email, age, balance)"
                       " VALUES (?, ?, ?, ?)", (f"{username}", f"{email}",
                                             f"{age}", f"{1000}"))
    connection.commit()
    connection.close()
    print('Я добавил в базу данных пользователя')

#add_user('user1', 'user1@mail.ru', 28)
# for i in range (100):
#     cursor.execute("DELETE FROM Users WHERE id = ?", (f"{i}",))


#Создаем функцию, проверяющую наличие пользователя с указанным username в таблице
# "Пользователи"
def is_included(username):
    import sqlite3
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    check_user = cursor.execute("SELECT * FROM Users WHERE username=?", (username,))
    if check_user.fetchone() is None:
        return False
    else:
        return True


connection.commit()
connection.close()