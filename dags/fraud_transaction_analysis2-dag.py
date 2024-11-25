from datetime import datetime
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.telegram.operators.telegram import TelegramOperator
from telegram_notifications import task_success_callback, task_failure_callback, dag_success_callback, dag_failure_callback

# Функция для обработки данных из CSV файла
def process_data():
    file_path = '/opt/airflow/source/creditcard.csv'
    data = pd.read_csv(file_path)
    filtered_data = data[data['Class'] == 1]
    
    transaction_count = filtered_data.shape[0]
    total_amount_usd = filtered_data['Amount'].sum()
    
    return transaction_count, total_amount_usd

# Функция для конвертации суммы в биткоины
def convert_to_btc(total_amount_usd, bitcoin_rate):
    return float(total_amount_usd) / float(bitcoin_rate)

# Функция для формирования сообщения для Telegram
def create_telegram_message(transaction_count, total_amount_usd, total_amount_btc, bitcoin_rate):
    transaction_count = int(transaction_count)
    total_amount_usd = float(total_amount_usd)
    total_amount_btc = float(total_amount_btc)
    bitcoin_rate = float(bitcoin_rate)
    message = (
        f"Количество мошеннических транзакций: {int(transaction_count)}\n"
        f"Сумма в долларах: {total_amount_usd} USD\n"
        f"Сумма в биткоинах: {total_amount_btc:.8f} BTC\n"
        f"Курс биткоина: {bitcoin_rate} USD\n"
        f"Дата получения курса: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    return message

# DAG определение
with DAG(
    'fraud_transaction_analysis2',
    schedule_interval='@daily',
    start_date=datetime(2024, 11, 1),
    catchup=False,
    on_success_callback=dag_success_callback,
    on_failure_callback=dag_failure_callback
) as dag:

    # Задача для обработки данных из CSV файла
    process_task = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
        provide_context=True,
        do_xcom_push=True,
    )

    # Задача для получения курса биткоина через HTTP API
    get_bitcoin_price = HttpOperator(
        task_id='get_bitcoin_price',
        http_conn_id='coindesk_api',
        endpoint='v1/bpi/currentprice.json',
        method='GET',
        response_filter=lambda response: response.json()['bpi']['USD']['rate_float'],
        log_response=True,
        do_xcom_push=True,
    )

    # Задача для конвертации суммы в биткоины
    convert_task = PythonOperator(
        task_id='convert_to_btc',
        python_callable=convert_to_btc,
        op_kwargs={
            'total_amount_usd': '{{ task_instance.xcom_pull(task_ids="process_data")[1] }}',
            'bitcoin_rate': '{{ task_instance.xcom_pull(task_ids="get_bitcoin_price") }}'
        },
        provide_context=True,
        do_xcom_push=True,
    )

    # Задача для формирования сообщения для Telegram
    create_message_task = PythonOperator(
        task_id='create_telegram_message',
        python_callable=create_telegram_message,
        op_kwargs={
            'transaction_count': '{{ task_instance.xcom_pull(task_ids="process_data")[0] }}',
            'total_amount_usd': '{{ task_instance.xcom_pull(task_ids="process_data")[1] }}',
            'total_amount_btc': '{{ task_instance.xcom_pull(task_ids="convert_to_btc") }}',
            'bitcoin_rate': '{{ task_instance.xcom_pull(task_ids="get_bitcoin_price") }}'
        },
        provide_context=True,
        do_xcom_push=True,
    )

    # Задача для записи данных в таблицу fraud_transactions
    insert_task = PostgresOperator(
        task_id='insert_data',
        postgres_conn_id='postgres_default',
        sql="""
            INSERT INTO fraud_transactions (transaction_count, total_amount_usd, total_amount_btc, bitcoin_rate)
            VALUES (
                {{ task_instance.xcom_pull(task_ids='process_data')[0] }},
                {{ task_instance.xcom_pull(task_ids='process_data')[1] }},
                {{ task_instance.xcom_pull(task_ids='convert_to_btc') }},
                {{ task_instance.xcom_pull(task_ids='get_bitcoin_price') }}
            );
        """,
    )

    # Задача для отправки сообщения в Telegram
    send_telegram_task = TelegramOperator(
        task_id='send_telegram_message',
        telegram_conn_id='telegram_default',
        chat_id='649399722',  # Укажите ваш ID чата
        text="{{ task_instance.xcom_pull(task_ids='create_telegram_message') }}",  # Получаем сообщение из предыдущей задачи
    )

    # Определяем порядок выполнения задач
    [process_task,get_bitcoin_price] >> convert_task >> create_message_task >> [insert_task, send_telegram_task] #>> insert_task >> send_telegram_task