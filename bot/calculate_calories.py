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



