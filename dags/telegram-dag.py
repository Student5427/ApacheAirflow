from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import requests
from telegram_notifications import task_success_callback, task_failure_callback

def send_currency_rate():
    # Получение курса валют
    response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
    rates = response.json()
    message = "Курсы валют:\n"
    for currency, rate in rates.items():
        message += f"{currency}: {rate}\n"
    # Отправка в Telegram
    requests.post(f'https://api.telegram.org/bot7891446819:AAEGULObbcnCnd-J60AxChFllx8pM5Qbp5A/sendMessage', 
                  data={'chat_id': '649399722', 'text': str(message)})

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 11, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('currency_rate_dag', default_args=default_args, schedule_interval='0 0,12 * * *')

task = PythonOperator(task_id='send_currency_rate', python_callable=send_currency_rate, dag=dag, on_success_callback=task_success_callback,
        on_failure_callback=task_failure_callback,)