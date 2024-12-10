import requests
import telebot
from telebot import types

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

def calculate_calories(data):
    #Рассчитывает калорийность и БЖУ
    weight = data["weight"]
    height = data["height"]
    age = data["age"]
    gender = data["gender"]
    goal = data["goal"]

    # Основной обмен веществ (формула Миффлина-Сан Жеора)
    if gender == "Мужской":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # Калорийность в зависимости от цели
    if goal == "Похудение":
        calories = bmr * 0.8  # Уменьшаем калорийность на 20%
    elif goal == "Набор массы":
        calories = bmr * 1.2  # Увеличиваем калорийность на 20%
    else:  # Поддержание веса
        calories = bmr

    # Расчет БЖУ (примерные пропорции)
    protein = round(0.3 * calories / 4, 2)  # 30% калорий из белков
    fat = round(0.25 * calories / 9, 2)     # 25% калорий из жиров
    carbs = round(0.45 * calories / 4, 2)   # 45% калорий из углеводов

    return {
        "calories": round(calories, 2),
        "protein": protein,
        "fat": fat,
        "carbs": carbs
    }



@bot.message_handler(commands=["start"])
def start(message):
    print('Idi na')
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