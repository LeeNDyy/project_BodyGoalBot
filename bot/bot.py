import requests
import telebot
from telebot import types
# importing os module for environment variables
import os
from calculate_calories import calculate_calories
from bd import DishDatabase


import sys 
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from pathlib import Path
# from parser import Parser

dotenv_path = Path('keys/keys.env')
load_dotenv(dotenv_path=dotenv_path)

TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(TOKEN)


# Хранилище данных пользователей
user_data = {}


class MessagePrinter:
    """Базовый класс для вывода сообщений."""
    def __init__(self, message):
        self.message = message

    def print_message(self):
        print(f"{self.message}")


class UserWelcomePrinter(MessagePrinter):
    """Класс для приветствия пользователя, наследует MessagePrinter."""
    def __init__(self, user_name):
        super().__init__(f"Добро пожаловать, {user_name}!")
        self.user_name = user_name


class BotFarewellPrinter(MessagePrinter):
    """Класс для прощания, наследует MessagePrinter."""
    def __init__(self):
        super().__init__("Спасибо за использование бота!")

    def farewell(self):
        """Выводит прощальное сообщение."""
        return "До новых встреч!"



@bot.message_handler(commands=["start"])
def start(message):
    #Стартовая команда
    user_id = message.chat.id
    user_data[user_id] = {}
    bot.send_message(message.chat.id, "Привет! Я помогу вам рассчитать рацион питания.")
    ask_gender(message)


def ask_gender(message):
    
    #Запрашивает пол пользователя
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton("Мужской")
    item2 = types.KeyboardButton("Женский")
    markup.add(item1, item2)
    
    bot.send_message(message.chat.id, "Пожалуйста, выберите ваш пол:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in ["Мужской", "Женский"])
def handle_gender(message):

    #Обрабатывает выбор пола
    user_id = message.chat.id
    gender = message.text
    user_data[user_id]["gender"] = gender

    bot.send_message(message.chat.id, f"Вы выбрали: {gender}")
    bot.send_message(message.chat.id, "Введите ваш вес (кг):")
    
    
    bot.register_next_step_handler(message, handle_weight)

def handle_weight(message):
    #Обрабатывает ввод веса
    try:
        weight = float(message.text)
        user_id = message.chat.id
        user_data[user_id]["weight"] = weight

        bot.send_message(message.chat.id, "Введите ваш рост (см):")
        
        bot.register_next_step_handler(message, handle_height)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный рост(число).")
        bot.register_next_step_handler(message, handle_weight)


def handle_height(message):

    #Обрабатывает ввод роста
    try:
        height = float(message.text)
        user_id = message.chat.id
        user_data[user_id]["height"] = height
        bot.send_message(message.chat.id, "Введите ваш возраст:")

        bot.register_next_step_handler(message, handle_age)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный возраст (число).")
 
        bot.register_next_step_handler(message, handle_height)

def calculate_bmi(weight, height):
    """Рассчитывает индекс массы тела (ИМТ) и возвращает рекомендацию."""
    bmi = weight / (height / 100) ** 2  # ИМТ = вес (кг) / рост (м)^2
    if bmi < 18.5:
        recommendation = "У вас недостаточный вес."
        suggested_goal = "Набор массы"
    elif 18.5 <= bmi <= 24.9:
        recommendation = "У вас нормальный вес."
        suggested_goal = "Поддержание веса"
    else:
        recommendation = "У вас избыточный вес. "
        suggested_goal = "Похудение"
    return bmi, recommendation, suggested_goal

def handle_age(message):
    """Обрабатывает ввод возраста."""
    try:
        age = int(message.text)
        user_id = message.chat.id
        user_data[user_id]["age"] = age

        # Расчет ИМТ и рекомендация
        weight = user_data[user_id]["weight"]
        height = user_data[user_id]["height"]
        bmi, recommendation, suggested_goal = calculate_bmi(weight, height)
        
        # Сохраняем предложенную цель
        user_data[user_id]["suggested_goal"] = suggested_goal

        # Отправляем сообщение с результатами ИМТ и рекомендацией
        bot.send_message(
            message.chat.id,
            f"Ваш индекс массы тела (ИМТ): {bmi:.2f}.\n{recommendation}"
        )
        
        # Предлагаем пользователю выбрать программу или использовать рекомендованную
        ask_goal_with_suggestion(message, suggested_goal)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный возраст (число).")
        bot.register_next_step_handler(message, handle_age)

def ask_goal_with_suggestion(message, suggested_goal):
    """Запрашивает цель пользователя, предлагая рекомендованную программу."""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton("Похудение")
    item2 = types.KeyboardButton("Набор массы")
    item3 = types.KeyboardButton("Поддержание веса")
    markup.add(item1, item2, item3)
    
    bot.send_message(
        message.chat.id,
        f"Мы рекомендуем вам: {suggested_goal}. Вы можете выбрать другую программу, если хотите.",
        reply_markup=markup
    )


def ask_goal(message):
    #Запрашивает цель пользователя
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton("Похудение")
    item2 = types.KeyboardButton("Набор массы")
    item3 = types.KeyboardButton("Поддержание веса")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Теперь выберите вашу цель:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Похудение", "Набор массы", "Поддержание веса"])
def handle_goal(message):
    #Обрабатывает выбор цели
    user_id = message.chat.id
    goal = message.text
    user_data[user_id]["goal"] = goal
    result = calculate_calories(user_data[user_id])
    show_action_menu(message)
    try:
        bot.send_message(
            message.chat.id,
            f"Вы выбрали цель: {goal}.\n"
            f"Ваш рацион рассчитан:\n"
            f"- Калории: {result['calories']} ккал\n"
            f"- Белки: {result['protein']} \n"
            f"- Жиры: {result['fat']} \n"
            f"- Углеводы: {result['carbs']} "
        )
    finally:
        # Показать меню действий
        pass


def show_action_menu(message):
    #Показывает меню действий после выбора программы.
    user_id = message.chat.id
    user_data[user_id]["action"] = None  # Сбрасываем текущее действие
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton("Ввести еду ")
    item2 = types.KeyboardButton("Вернуться назад ")
    markup.add(item1, item2)
    bot.send_message(user_id, "Давайте продолжим", reply_markup=markup)




@bot.message_handler(func=lambda message: message.text in ["Ввести еду", "Вернуться назад"])
def handle_action_choice(message):

    #Обрабатывает выбор действия из меню.
    if message.text == "Ввести еду":
        bot.send_message(
            message.chat.id,
            "Введите блюдо, которое вы съели (например: 'Классический борщ')."
        )
        bot.register_next_step_handler(message, handle_food_query)  # Переход к обработке продукта

    elif message.text == "Вернуться назад":
        ask_goal(message)  # Возврат к выбору цели

# Инициализация базы данных
dish_db = DishDatabase("bot/dishes.csv")

@bot.message_handler(func=lambda message: True)
def handle_food_query(message):
    """Обрабатывает запросы пользователя о блюде."""
    user_id = message.chat.id
    dish_query = message.text

    # Поиск блюда в локальной базе
    dish_info = dish_db.search_dish(dish_query)
    if not dish_info:
        bot.send_message(user_id, "Такого блюда нет в списке. Попробуйте уточнить запрос.")
        return

    # Отправка информации о БЖУ пользователю
    bot.send_message(
        user_id,
        f"Информация о блюде '{dish_query}':\n"
        f"- Калорийность: {dish_info['calories']} ккал\n"
        f"- Белки: {dish_info['protein']} г\n"
        f"- Жиры: {dish_info['fat']} г\n"
        f"- Углеводы: {dish_info['carbs']} г"
    )

if __name__ == "__main__":
    # Пример использования приветственного класса
    user_printer = UserWelcomePrinter('Друг')
    user_printer.print_message()  # Печатает: Сообщение: Добро пожаловать, Алексей!

    # Пример использования класса для прощания
    bot_printer = BotFarewellPrinter()
    bot_printer.print_message()  # Печатает: Сообщение: Спасибо за использование бота!
    print(bot_printer.farewell())  # Печатает: До новых встреч!

bot.polling(non_stop=True)