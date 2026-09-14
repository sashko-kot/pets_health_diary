from datetime import date

#данные сущности "питомец" и "хозяин"
owner_name = "Алексей"
pet_name = "шуша"
pet_weight_kg = 4.5
recommended_weight_kg = 4.0

#данные сущности "план кормления"
base_feed_rate_grams = 20  # Норма на 1 кг веса

#данные сущности "график уборки"
last_cleaning_date = date(2026, 9, 9)
cleaning_interval_days = 5
current_date = date.today()


#расчет суточной нормы корма
def calculate_daily_feed(weight, rate):
    return weight * rate


#проверка необходимости уборки
def check_cleaning_status(last_date, interval, today):
    days_passed = (today - last_date).days
    if days_passed >= interval:
        return "Пора провести уборку!"
    return f"Уборка не требуется. Дней до следующей уборки: {interval - days_passed}"


#проверка веса питомца
def check_weight_status(current_w, target_w):
    if current_w > target_w:
        return "Есть избыточный вес, требуется корректировка рациона."
    elif current_w < target_w:
        return "Вес ниже нормы."
    return "Вес в норме!"


print(f"Владелец: {owner_name}")
print(f" Питомец: {pet_name}")

daily_feed = calculate_daily_feed(pet_weight_kg, base_feed_rate_grams)
print(f"Суточная норма корма: {daily_feed}.")

cleaning_info = check_cleaning_status(
    last_cleaning_date, cleaning_interval_days, current_date
)
print(f"Статус уборки: {cleaning_info}")

weight_info = check_weight_status(pet_weight_kg, recommended_weight_kg)
print(f"Анализ веса: {weight_info}")