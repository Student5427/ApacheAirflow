# Используйте официальный образ Apache Airflow
FROM apache/airflow:2.10.2

# Установите необходимые библиотеки
USER airflow
RUN pip install pandas apache-airflow-providers-telegram

# Вернуться к пользователю airflow
#USER airflow