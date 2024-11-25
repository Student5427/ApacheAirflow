from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 11, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('backup_files_dag', default_args=default_args, schedule_interval='@daily')

backup_task = BashOperator(
    task_id='backup_files',
    bash_command='cp -r /opt/airflow/source* /opt/airflow/backup',
    dag=dag,
)