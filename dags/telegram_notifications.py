from airflow.providers.telegram.operators.telegram import TelegramOperator

def create_telegram_operator(task_id, chat_id, message, dag):
    return TelegramOperator(
        task_id=task_id,
        telegram_conn_id='telegram_notifier',  # Убедитесь, что соединение настроено в Airflow
        chat_id=chat_id,
        text=message,
        dag=dag,
    )

def task_success_callback(context):
    task_instance = context['task_instance']
    message = f"✅ Задача *{task_instance.task_id}* выполнена успешно!"
    
    return create_telegram_operator(
        task_id=f"notify_success_{task_instance.task_id}",
        chat_id='649399722',  # Замените на ваш chat ID
        message=message,
        dag=context['dag']
    ).execute(context)

def task_failure_callback(context):
    task_instance = context['task_instance']
    message = f"❌ Задача *{task_instance.task_id}* завершилась с ошибкой!"
    
    return create_telegram_operator(
        task_id=f"notify_failure_{task_instance.task_id}",
        chat_id='649399722',  # Замените на ваш chat ID
        message=message,
        dag=context['dag']
    ).execute(context)

def dag_success_callback(context):
    message = "✅ DAG *{}* выполнен успешно!".format(context['dag'].dag_id)
    
    return create_telegram_operator(
        task_id='notify_dag_success',
        chat_id='649399722',  # Замените на ваш chat ID
        message=message,
        dag=context['dag']
    ).execute(context)

def dag_failure_callback(context):
    message = "❌ DAG *{}* завершился с ошибкой!".format(context['dag'].dag_id)
    
    return create_telegram_operator(
        task_id='notify_dag_failure',
        chat_id='649399722',  # Замените на ваш chat ID
        message=message,
        dag=context['dag']
    ).execute(context)