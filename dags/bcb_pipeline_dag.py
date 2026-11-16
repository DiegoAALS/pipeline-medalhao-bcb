"""DAG mensal: bronze -> silver -> gold."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT = "{{ var.value.get('bcb_project_path', '/opt/airflow/projeto-1-pipeline-medalhao-bcb') }}"

default_args = {
    "owner": "DiegoAALS",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="bcb_pipeline_medalhao",
    description="Pipeline medalhão com séries do Banco Central",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule="0 8 10 * *",  # dia 10 de cada mês, 08:00
    catchup=False,
    tags=["bcb", "medalhao", "portfolio"],
) as dag:
    bronze = BashOperator(task_id="bronze_ingest", bash_command=f"cd {PROJECT} && python src/bronze_ingest.py")
    silver = BashOperator(task_id="silver_transform", bash_command=f"cd {PROJECT} && python src/silver_transform.py")
    gold = BashOperator(task_id="gold_aggregate", bash_command=f"cd {PROJECT} && python src/gold_aggregate.py")

    bronze >> silver >> gold
