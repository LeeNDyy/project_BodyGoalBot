import urllib.request
import urllib.parse
import json
from html.parser import HTMLParser
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('keys.env')
load_dotenv(dotenv_path=dotenv_path)

APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')





class Parser:
    BASE_URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"

    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "x-app-id": APP_ID,  
            "x-app-key": APP_KEY,  
        }

    def get_nutrition(self, query):
        """Получает информацию о питательных веществах для продукта.
        :param query: Запрос пользователя, например, '3 яйца'.
        :return: Словарь с данными о калориях, белках, жирах и углеводах.
        """
        
        data = json.dumps({"query": query}).encode("utf-8")
        request = urllib.request.Request(self.BASE_URL, data=data, headers=self.headers)
        
        try:
            with urllib.request.urlopen(request) as response:
                result = json.loads(response.read().decode("utf-8"))

                # Парсинг результата
                if "foods" in result:
                    food_data = result["foods"][0]  # Берём первый элемент
                    return {
                        "name": food_data["food_name"],
                        "calories": food_data["nf_calories"],
                        "protein": food_data["nf_protein"],
                        "fat": food_data["nf_total_fat"],
                        "carbs": food_data["nf_total_carbohydrate"],
                    }
                else:
                    raise ValueError("Продукт не найден")
        except Exception as e:
            raise RuntimeError(f"Ошибка при парсинге данных: {e}")
