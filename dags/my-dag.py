from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 31),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'my_dag',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
)

task = BashOperator(
    task_id='my_task',
    bash_command='echo "Hello World!"',
    dag=dag,
)