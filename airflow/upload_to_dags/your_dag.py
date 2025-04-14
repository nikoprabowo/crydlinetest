import os
import time
from datetime import timedelta
from google.cloud import storage
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# ============================
# === CONFIGURABLE SECTION ===
# ============================

# Your GCP project ID
PROJECT_ID = 'your-gcp-project-id'

# Your Dataproc cluster name
DATAPROC_CLUSTER = 'your-dataproc-cluster'

# Your GCS bucket for data (not the Composer bucket)
DATA_BUCKET = 'your-data-bucket'

# Path to the spark job file inside Composer bucket
SPARK_LOCAL_PATH = '/home/airflow/gcs/data/spark/spark_job.py'
SPARK_GCS_PATH = 'scripts/spark_job.py'

# DBT paths
DBT_DIR = '/home/airflow/gcs/data/dbt'
DBT_PROFILES_DIR = DBT_DIR
DBT_PROFILE_NAME = 'your_dbt'

# Path to GCP service account key file (inside Composer bucket)
GOOGLE_CREDENTIALS_PATH = '/home/airflow/gcs/data/auth/your-sa-key.json'

# ============================
# === DEFAULT ARGS & DAG ===
# ============================

default_args = {
    'owner': 'niko',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='crypipe_daily_dag_v1',
    default_args=default_args,
    description='Daily DAG for Crypipe project',
    schedule_interval=None,  # set to '0 0 * * *' for daily run at 00:00 UTC
    start_date=days_ago(0),
    catchup=False,
    tags=['crypto', 'datapipeline', 'gcp'],
)

# =====================
# === PYTHON TASK ===
# =====================

def wait_60_seconds():
    time.sleep(60)

def upload_to_gcs(local_file_path, bucket_name, blob_path):
    """Uploads a local file to a GCS bucket."""
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(local_file_path)
        print(f"✅ Uploaded {local_file_path} to gs://{bucket_name}/{blob_path}")
    except Exception as e:
        print(f"❌ Failed to upload file: {e}")
        raise

# =====================
# === DAG TASKS ===
# =====================

with dag:

    # Step 1 - Ingest indicator data
    ingest_indicator = BashOperator(
        task_id='ingest_indicator',
        bash_command='python3 /home/airflow/gcs/data/ingest/ingest_indicator.py',
    )

    # Step 2 - Wait 60 secs (free API delay)
    wait_task = PythonOperator(
        task_id='wait_60_seconds',
        python_callable=wait_60_seconds,
    )

    # Step 3 - Ingest coin price data
    ingest_coin = BashOperator(
        task_id='ingest_coin',
        bash_command='python3 /home/airflow/gcs/data/ingest/ingest_coin.py',
    )

    # Step 4 - Upload Spark script to project bucket
    upload_spark_script = PythonOperator(
        task_id='upload_spark_script',
        python_callable=upload_to_gcs,
        op_kwargs={
            'local_file_path': SPARK_LOCAL_PATH,
            'bucket_name': DATA_BUCKET,
            'blob_path': SPARK_GCS_PATH,
        },
    )

    # Step 5 - Submit Spark job to Dataproc
    run_spark_script = BashOperator(
        task_id='run_spark_script',
        bash_command=f"""
            echo "Submitting Spark job to Dataproc..."
            gcloud dataproc jobs submit pyspark gs://{DATA_BUCKET}/{SPARK_GCS_PATH} \
              --cluster={DATAPROC_CLUSTER} \
              --region=asia-southeast1 \
              --properties=spark.hadoop.fs.gs.system.bucket={DATA_BUCKET},spark.bigquery.temp.gcs.bucket={DATA_BUCKET}
            echo "✅ Spark job submitted."
        """,
        env={'GOOGLE_CLOUD_PROJECT': PROJECT_ID}
    )

    # Step 6 - Install dbt dependencies
    dbt_deps = BashOperator(
        task_id='dbt_deps',
        bash_command=f"""
        export DBT_PROFILES_DIR={DBT_PROFILES_DIR} &&
        dbt deps --project-dir {DBT_DIR}
        """
    )

    # Step 7 - Seed dbt data
    dbt_seed = BashOperator(
        task_id='dbt_seed',
        bash_command=f"""
        export GOOGLE_APPLICATION_CREDENTIALS={GOOGLE_CREDENTIALS_PATH} &&
        export DBT_PROFILES_DIR={DBT_PROFILES_DIR} &&
        dbt seed --project-dir {DBT_DIR} --target dev
        """
    )

    # Step 8 - Run dbt models
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=f"""
        export GOOGLE_APPLICATION_CREDENTIALS={GOOGLE_CREDENTIALS_PATH} &&
        export DBT_PROFILES_DIR={DBT_PROFILES_DIR} &&
        dbt run --project-dir {DBT_DIR} --target dev
        """
    )

    # ========================
    # === TASK DEPENDENCIES ===
    # ========================
    ingest_indicator >> wait_task >> ingest_coin >> upload_spark_script
    upload_spark_script >> run_spark_script >> dbt_deps
    dbt_deps >> dbt_seed >> dbt_run