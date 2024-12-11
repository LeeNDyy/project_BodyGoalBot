import urllib.request
from bs4 import BeautifulSoup


class Parser:
    """Парсер для раздела 'Вторые блюда' сайта health-diet.ru."""

    BASE_URL = "https://health-diet.ru"

    def search_dish(self, query):
        """
        Ищет блюдо на сайте по запросу пользователя.
        :param query: Название блюда
        :return: URL найденного блюда или сообщение об ошибке
        """
        try:
            search_url = f"{self.BASE_URL}/base_of_meals/?search={urllib.parse.quote(query)}"
            headers = {"User-Agent": "Mozilla/5.0"}
            req = urllib.request.Request(search_url, headers=headers)

            # Получаем HTML страницы поиска
            with urllib.request.urlopen(req) as response:
                html = response.read()

            # Парсим HTML с помощью BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            # Находим первую ссылку на блюдо
            dish_link = soup.find("a", class_="mzr-tc-group-item-href")
            if not dish_link:
                return {"error": "Блюдо не найдено. Попробуйте уточнить запрос."}

            return {"url": f"{self.BASE_URL}{dish_link['href']}"}
        except Exception as e:
            return {"error": f"Ошибка поиска блюда: {e}"}

    def get_nutrition(self, dish_url):
        """
        Получает БЖУ и калорийность блюда по URL.
        :param dish_url: URL страницы рецепта
        :return: Словарь с БЖУ и калорийностью или сообщение об ошибке
        """
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            req = urllib.request.Request(dish_url, headers=headers)

            # Получаем HTML страницы
            with urllib.request.urlopen(req) as response:
                html = response.read()

            # Парсим HTML с помощью BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            # Находим таблицу с БЖУ
            nutrition_table = soup.find("table", class_="mzr-calorie-table")
            if not nutrition_table:
                return {"error": "Информация о БЖУ и калориях не найдена."}

            # Ищем строки таблицы
            rows = nutrition_table.find_all("tr")
            if len(rows) < 2:
                return {"error": "Не удалось извлечь данные о БЖУ и калориях."}

            # Извлекаем заголовки и значения
            headers = [th.text.strip() for th in rows[0].find_all("th")]
            values = [td.text.strip() for td in rows[1].find_all("td")]

            nutrition_info = {header: value for header, value in zip(headers, values)}

            return {
                "calories": nutrition_info.get("Калорийность (ккал)"),
                "protein": nutrition_info.get("Белки (г)"),
                "fat": nutrition_info.get("Жиры (г)"),
                "carbs": nutrition_info.get("Углеводы (г)"),
            }
        except Exception as e:
            return {"error": f"Ошибка парсинга: {e}"}
