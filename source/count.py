import pandas as pd
import requests

# Замените 'your_file.csv' на путь к вашему CSV файлу
file_path = 'creditcard.csv'

# Считываем данные из CSV файла
data = pd.read_csv(file_path)

# Фильтруем записи с классом = 1
filtered_data = data[data['Class'] == 1]

# Считаем количество записей с классом = 1
count_class_1 = filtered_data.shape[0]

# Считаем сумму значений в столбце Amount
sum_amount_class_1 = filtered_data['Amount'].sum()

# Получаем текущий курс биткоина по API
response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
bitcoin_data = response.json()
bitcoin_rate = bitcoin_data['bpi']['USD']['rate_float']  # Получаем курс в виде числа с плавающей точкой

# Переводим сумму в биткоины
amount_in_bitcoin = sum_amount_class_1 / bitcoin_rate

# Выводим результаты
print(f"Количество записей с классом = 1: {count_class_1}")
print(f"Сумма значений Amount для записей с классом = 1: {sum_amount_class_1} USD")
print(f"Курс биткоина: {bitcoin_rate} USD")
print(f"Сумма в биткоинах: {amount_in_bitcoin:.8f} BTC")  # Форматируем вывод до 8 знаков после запятой