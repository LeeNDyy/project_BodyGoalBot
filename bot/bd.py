import csv

class DishDatabase:
    """Класс для работы с локальной базой данных блюд."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.dishes = self.load_dishes()

    def load_dishes(self):
        """Загружает данные о блюдах из CSV-файла."""
        dishes = {}
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    name = row["Название"].strip().lower()
                    dishes[name] = {
                        "calories": row["Калории"],
                        "protein": row["Белки"],
                        "fat": row["Жиры"],
                        "carbs": row["Углеводы"]
                    }
        except FileNotFoundError:
            print(f"Файл {self.file_path} не найден.")
        return dishes

    def search_dish(self, query):
        """Ищет блюдо по названию."""
        query = query.strip().lower()
        return self.dishes.get(query, None)

