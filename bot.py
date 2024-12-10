import requests
import telebot
from telebot import types
import logging 
from calculate_calories import calculate_calories


# importing os module for environment variables
import os
import sys 
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from pathlib import Path
from parser import Parser

dotenv_path = Path('keys.env')
load_dotenv(dotenv_path=dotenv_path)

TOKEN = os.getenv('TOKEN')
APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')

bot = telebot.TeleBot(TOKEN)


# Хранилище данных пользователей
user_data = {}


class BotLogger:
    def __init__(self, log_file):
        self.logger = logging.getLogger("bot_logger")
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def log(self, level, message):
        if level == 'info':
            self.logger.info(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'debug':
            self.logger.debug(message)


logger = BotLogger('bot.log')

@bot.message_handler(commands=['start'])
def handle_start(message):
    # Обработка команды /start
    user_id = message.from_user.id
    logger.log_info(f"Пользователь {user_id} запустил бота с командой /start")
    bot.send_message(message.chat.id, "Добро пожаловать в нашего бота!")


def ask_gender(message):
    #Запрашивает пол пользователя
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton("Мужской")
    item2 = types.KeyboardButton("Женский")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Пожалуйста, выберите ваш пол:", reply_markup=markup)
    
    user_id = message.from_user.id
    logger.log_info(f"Пользователь {user_id} выбрал кнопку {'/Мужской' if user_id else '/Женский'}")


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
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный вес (число).")
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
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный рост (число).")
        bot.register_next_step_handler(message, handle_height)


def handle_age(message):
    #Обрабатывает ввод возраста
    try:
        age = int(message.text)
        user_id = message.chat.id
        user_data[user_id]["age"] = age
        ask_goal(message)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный возраст (число).")
        bot.register_next_step_handler(message, handle_age)


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
    bot.send_message(user_id, "Что вы хотите сделать?", reply_markup=markup)




@bot.message_handler(func=lambda message: message.text in ["Ввести еду", "Вернуться назад"])
def handle_action_choice(message):
    #Обрабатывает выбор действия из меню.
    if message.text == "Ввести еду":
        bot.send_message(
            message.chat.id,
            "Введите продукт и количество, которое вы съели (например: '3 яйца')."
        )
        bot.register_next_step_handler(message, handle_food_input)  # Переход к обработке продукта
    elif message.text == "Вернуться назад":
        ask_goal(message)  # Возврат к выбору цели


def handle_food_input(message):
    #Обрабатывает ввод продукта.
    user_id = message.chat.id
    query = message.text

    parser = Parser()
    try:
        # Передаем данные в парсер
        nutrition_data = parser.get_nutrition(query)
        if nutrition_data:
            response = (
                f"Информация о продукте \"{nutrition_data['name']}\":\n"
                f"- Калории: {nutrition_data['calories']} ккал\n"
                f"- Белки: {nutrition_data['protein']} г\n"
                f"- Жиры: {nutrition_data['fat']} г\n"
                f"- Углеводы: {nutrition_data['carbs']} г\n"
            )
            bot.send_message(message.chat.id, response)

         # Предлагаем записать в дневник
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            item1 = types.KeyboardButton("Записать в дневник ")
            item2 = types.KeyboardButton("Назад ")
            markup.add(item1, item2)
            bot.send_message(user_id, "Хотите записать это в дневник или вернуться назад?", reply_markup=markup)
        else:
            bot.send_message(user_id, "Не удалось найти информацию о продукте. Попробуйте еще раз.")
    except Exception as e:
        bot.send_message(user_id, f"Ошибка при получении данных о продукте: {e}")

#if __name__ == "__main__":
    # parser = Parser()
    # try:
    #     result = parser.get_nutrition(query)
    #     print(f"Продукт: {result['name']}")
    #     print(f"Калории: {result['calories']} ккал")
    #     print(f"Белки: {result['protein']} г")
    #     print(f"Жиры: {result['fat']} г")
    #     print(f"Углеводы: {result['carbs']} г")
    # except Exception as e:
    #     print(f"Ошибка: {e}")

bot.polling(non_stop=True)