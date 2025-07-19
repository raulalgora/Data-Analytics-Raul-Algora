from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import logging
import json
import csv
import io
from google.cloud import storage
from google.oauth2 import service_account
import os

# Import Airflow Variables and other operators
from airflow import models
from airflow.models import Variable
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator

# Import pendulum for start_date
import pendulum

# Load .env file if it exists (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.getLogger(__name__).info("✅ .env file loaded successfully")
except ImportError:
    logging.getLogger(__name__).warning("⚠️ python-dotenv not installed, skipping .env file loading")
except Exception as e:
    logging.getLogger(__name__).warning(f"⚠️ Could not load .env file: {e}")

# Logging
logger = logging.getLogger(__name__)
API_BASE_URL = "https://cursos-api-v2-wn6lmzlcba-no.a.run.app"

# Service account credentials - REMOVE BEFORE COMMITTING TO GITHUB
SERVICE_ACCOUNT_INFO = {
    # TEMPORARY - Add your service account JSON here for local testing
    # REMOVE BEFORE COMMITTING TO GITHUB!
}

# --- FIXED: Proper Airflow Variables Loading ---
# These will now properly use the variables you set in Airflow UI
def get_airflow_variables():
    """
    Load all required Airflow variables with proper error handling.
    This ensures we're using the actual variables, not defaults.
    """
    try:
        variables = {
            'GCP_PROJECT_ID': Variable.get("GCP_PROJECT_ID"),
            'GCS_LANDING_BUCKET': Variable.get("GCS_LANDING_BUCKET"), 
            'GCS_PROCESSED_BUCKET': Variable.get("GCS_PROCESSED_BUCKET"),
            'GCS_FLEX_TEMPLATE_PATH': Variable.get("GCS_FLEX_TEMPLATE_PATH"),
            'DATAFLOW_JOB_NAME': Variable.get("DATAFLOW_JOB_NAME"),
            'BIGQUERY_TABLE': Variable.get("BIGQUERY_TABLE"),
            'BIGQUERY_DATASET': Variable.get("BIGQUERY_DATASET"),
            'DATAFLOW_SERVICE_ACCOUNT': Variable.get("DATAFLOW_SERVICE_ACCOUNT"),
            'GCS_DATAFLOW_BUCKET': Variable.get("GCS_DATAFLOW_BUCKET")
        }
        
        # Log the loaded variables (without sensitive data)
        logger.info("🔧 Loaded Airflow Variables:")
        for key, value in variables.items():
            if 'BUCKET' in key or 'PATH' in key:
                logger.info(f"   {key}: {value}")
            else:
                logger.info(f"   {key}: {value[:20]}..." if len(str(value)) > 20 else f"   {key}: {value}")
        
        return variables
    except Exception as e:
        logger.error(f"❌ Failed to load required Airflow Variables: {e}")
        logger.error("💡 Make sure all variables are set in Airflow UI -> Admin -> Variables")
        raise

# Load variables at DAG definition time
AIRFLOW_VARS = get_airflow_variables()

# Extract individual variables for easier use
GCP_PROJECT_ID = AIRFLOW_VARS['GCP_PROJECT_ID']
GCS_LANDING_BUCKET = AIRFLOW_VARS['GCS_LANDING_BUCKET']
GCS_PROCESSED_BUCKET = AIRFLOW_VARS['GCS_PROCESSED_BUCKET']
GCS_FLEX_TEMPLATE_PATH = AIRFLOW_VARS['GCS_FLEX_TEMPLATE_PATH']
DATAFLOW_JOB_NAME = AIRFLOW_VARS['DATAFLOW_JOB_NAME']
BIGQUERY_TABLE = AIRFLOW_VARS['BIGQUERY_TABLE']
BIGQUERY_DATASET = AIRFLOW_VARS['BIGQUERY_DATASET']
DATAFLOW_SERVICE_ACCOUNT = AIRFLOW_VARS['DATAFLOW_SERVICE_ACCOUNT']
GCS_DATAFLOW_BUCKET = AIRFLOW_VARS['GCS_DATAFLOW_BUCKET']

# Constants
GCS_SENSOR_POKE_INTERVAL = 30
GCS_SENSOR_SENSOR_TIMEOUT = 300
RETRIES = 3
BQ_CHECK_RETRIES = 5

default_args = {
    'owner': 'airflow',
    'start_date': pendulum.datetime(2025, 7, 7, tz="UTC"),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

def get_gcp_credentials():
    """
    Get GCP credentials using multiple fallback methods.
    Priority order:
    1. Airflow Variables (most secure for production)
    2. Environment variables  
    3. Default credentials (for GCP environments)
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Method 1: Airflow Variables (Recommended for production)
        try:
            from airflow.models import Variable
            service_account_json = Variable.get("gcp_service_account_json", default=None)
            if service_account_json:
                logger.info(f"🔍 Found Airflow Variable 'gcp_service_account_json': {len(service_account_json) if service_account_json else 0} characters")
                service_account_info = json.loads(service_account_json)
                credentials = service_account.Credentials.from_service_account_info(service_account_info)
                project_id = service_account_info.get('project_id', GCP_PROJECT_ID)
                return credentials, project_id, "Airflow Variables"
        except Exception as e:
            logger.warning(f"⚠️ Failed to get Airflow Variable 'gcp_service_account_json': {e}")
        
        # Method 2: Environment variable with JSON content
        gcp_json_env = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
        if gcp_json_env:
            logger.info("🔍 Found GCP_SERVICE_ACCOUNT_JSON environment variable")
            service_account_info = json.loads(gcp_json_env)
            credentials = service_account.Credentials.from_service_account_info(service_account_info)
            project_id = service_account_info.get('project_id', GCP_PROJECT_ID)
            return credentials, project_id, "Environment variable (JSON)"
        
        # Method 3: Environment variable with file path
        creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_path and os.path.exists(creds_path):
            logger.info(f"🔍 Found GOOGLE_APPLICATION_CREDENTIALS: {creds_path}")
            credentials = service_account.Credentials.from_service_account_file(creds_path)
            with open(creds_path, 'r') as f:
                service_account_info = json.load(f)
                project_id = service_account_info.get('project_id', GCP_PROJECT_ID)
            return credentials, project_id, f"Service account file: {creds_path}"
        
        # Method 4: Hardcoded credentials (ONLY for local development)
        if SERVICE_ACCOUNT_INFO and SERVICE_ACCOUNT_INFO.get('type') == 'service_account':
            logger.info("🔍 Using hardcoded credentials (REMOVE BEFORE GITHUB)")
            credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO)
            project_id = SERVICE_ACCOUNT_INFO.get('project_id', GCP_PROJECT_ID)
            return credentials, project_id, "Hardcoded credentials (REMOVE BEFORE GITHUB)"
        
        # Method 5: Default credentials (for GCP environments)
        logger.info("🔍 No explicit credentials found, trying default...")
        return None, GCP_PROJECT_ID, "Default GCP credentials"
        
    except Exception as e:
        logger.error(f"❌ Error in get_gcp_credentials: {e}")
        raise Exception(f"Failed to get GCP credentials: {e}")

def read_and_upload_today_courses_csv_only(**kwargs):
    """
    Fetches today's courses from the API and uploads ONLY CSV to airflow_daily bucket.
    FIXED: Now uploads directly to GCS_PROCESSED_BUCKET (airflow_daily)
    """
    ti = kwargs['ti']
    execution_date_str = kwargs.get('ds', datetime.now().strftime('%Y-%m-%d'))
    
    # Initialize GCS Client with secure authentication
    logger.info("🔐 Initializing GCP authentication...")
    
    try:
        credentials, project_id, auth_method = get_gcp_credentials()
        
        if credentials:
            client = storage.Client(credentials=credentials, project=project_id)
        else:
            client = storage.Client(project=project_id)
            
        logger.info(f"🔑 Authentication successful using: {auth_method}")
        logger.info(f"📁 Project: {project_id}")
        logger.info(f"🪣 Target bucket: {GCS_PROCESSED_BUCKET}")  # CHANGED: Now using processed bucket
        
    except Exception as e:
        logger.error(f"❌ Error initializing GCS client: {e}")
        logger.error("💡 Check your GCP authentication setup:")
        logger.error("   1. Set Airflow Variable 'gcp_service_account_json'")
        logger.error("   2. Set environment variable 'GCP_SERVICE_ACCOUNT_JSON'")
        logger.error("   3. Set environment variable 'GOOGLE_APPLICATION_CREDENTIALS'")
        raise
    
    logger.info(f"🗓️ === PROCESAMIENTO DE CURSOS DEL DÍA {execution_date_str} ===")
    logger.info("🚀 MODO OPTIMIZADO: Solo solicitando cursos del día actual")
    
    # 1. First check how many courses are available for today (without loading data)
    count_url = f"{API_BASE_URL}/cursos/count/today"
    logger.info(f"📊 Checking today's course count: {count_url}")
    
    try:
        count_response = requests.get(count_url, timeout=30)
        count_response.raise_for_status()
        count_data = count_response.json()
        
        total_cursos_hoy = count_data.get('total_cursos_today', 0)
        fecha_procesada = count_data.get('date', execution_date_str)
        total_cursos_general = count_data.get('total_cursos_all', 0)
        
        logger.info(f"✅ Total courses in database: {total_cursos_general}")
        logger.info(f"🎯 Courses for today ({fecha_procesada}): {total_cursos_hoy}")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 503:
            logger.error(f"❌ API temporarily unavailable (503): {e}")
            logger.info("⏳ API may be restarting - retrying later...")
            raise
        else:
            logger.error(f"❌ HTTP error getting course count: {e}")
            raise
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Connection error getting today's course count: {e}")
        logger.info("🔄 This may be temporary - task will retry automatically")
        raise
    
    # 2. Get today's courses only if there are any
    if total_cursos_hoy > 0:
        courses_url = f"{API_BASE_URL}/cursos/today"
        logger.info(f"📥 Getting ONLY the {total_cursos_hoy} courses for today: {courses_url}")
        logger.info("🚀 API will only load today's courses (optimized)")
        
        try:
            response = requests.get(courses_url)
            response.raise_for_status()
            data = response.json()
            
            today_courses = data.get('cursos', [])
            fecha_real = data.get('date', fecha_procesada)
            
            logger.info(f"✅ API processed and returned {len(today_courses)} courses for {fecha_real}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error getting today's courses: {e}")
            raise
    else:
        today_courses = []
        fecha_real = fecha_procesada
        logger.warning(f"⚠️ No new courses for {fecha_procesada}")
        logger.info("✨ Process completed - No courses to process today")
    
    # 3. Create CSV filename with date format: courses_YYYYMMDD.csv
    date_for_filename = execution_date_str.replace('-', '')
    csv_filename = f"daily_courses/courses_{date_for_filename}.csv"
    
    logger.info(f"📝 Creating CSV file: {csv_filename}")
    
    # 4. Create and upload CSV directly to airflow_daily bucket
    try:
        bucket = client.bucket(GCS_PROCESSED_BUCKET)  # CHANGED: Now using processed bucket directly
        
        # Create CSV content
        csv_output = io.StringIO()
        csv_writer = csv.writer(csv_output)
        
        # Write CSV headers
        if today_courses:
            headers = list(today_courses[0].keys())
            headers.extend(['date_processed', 'processing_timestamp'])
            csv_writer.writerow(headers)
            
            for course in today_courses:
                row = list(course.values())
                row.extend([fecha_real, datetime.now().isoformat()])
                csv_writer.writerow(row)
                
            logger.info(f"📊 CSV contains {len(today_courses)} data rows + 1 header row")
        else:
            headers = [
                'Training Title', 'Training Provider', 'Training Hours', 'Training Object ID',
                'loadtime', 'date_processed', 'processing_timestamp'
            ]
            csv_writer.writerow(headers)
            logger.info("📊 CSV contains only headers (no courses today)")
        
        # Upload CSV to GCS
        csv_blob = bucket.blob(csv_filename)
        csv_blob.upload_from_string(csv_output.getvalue(), content_type='text/csv')
        
        logger.info(f"📤 CSV uploaded to gs://{GCS_PROCESSED_BUCKET}/{csv_filename}")  # CHANGED: Updated log message
        logger.info(f"📁 File saved directly in daily_courses/ folder in airflow_daily bucket")
        
        # Store path in XCom for potential downstream tasks
        ti.xcom_push(key='gcs_csv_path', value=f"gs://{GCS_PROCESSED_BUCKET}/{csv_filename}")  # CHANGED: Updated path
        ti.xcom_push(key='gcs_csv_object', value=csv_filename)
        
        # Store summary info
        ti.xcom_push(key='courses_processed', value=len(today_courses))
        ti.xcom_push(key='processing_date', value=fecha_real)
        
    except Exception as e:
        logger.error(f"❌ Error uploading CSV to GCS: {e}")
        raise
    
    # 5. Log summary
    logger.info(f"\n🎉 PROCESSING SUMMARY:")
    logger.info(f"   📅 Date processed: {fecha_real}")
    logger.info(f"   ✅ Courses processed: {len(today_courses)}")
    logger.info(f"   📊 Total in database: {total_cursos_general}")
    logger.info(f"   🚀 API calls made: {2 if total_cursos_hoy > 0 else 1}")
    logger.info(f"   📂 CSV filename: {csv_filename}")
    logger.info(f"   📍 Location: gs://{GCS_PROCESSED_BUCKET}/{csv_filename}")  # CHANGED: Updated path
    logger.info("🎉 Process completed successfully!")
    
    return {
        'status': 'success',
        'courses_processed': len(today_courses),
        'date': fecha_real,
        'csv_filename': csv_filename,
        'gcs_path': f"gs://{GCS_PROCESSED_BUCKET}/{csv_filename}",  # CHANGED: Updated path
        'api_calls_made': 2 if total_cursos_hoy > 0 else 1
    }

# Dynamic GCS file name based on execution date and fixed prefix
GCS_FILE_NAME = "{{ task_instance.xcom_pull(task_ids='read_and_upload_today_courses_csv_task', key='gcs_csv_object') }}"

""" DAG """
with DAG(
    dag_id='TFM_daily_course_processing',
    schedule_interval='@daily',
    default_args=default_args,
    start_date=pendulum.datetime(2025, 7, 7, tz="UTC"),
    catchup=False,
    tags=['TFM', 'daily-courses', 'api', 'gcp', 'dataflow', 'bigquery'],
    is_paused_upon_creation=True 
) as dag:
    
    read_and_upload_today_courses_csv_task = PythonOperator(
        task_id='read_and_upload_today_courses_csv_task',
        python_callable=read_and_upload_today_courses_csv_only,
    )

    check_file_on_gcs = GCSObjectExistenceSensor(
        task_id="check_file_on_gcs",
        bucket=GCS_PROCESSED_BUCKET,  # CHANGED: Now checking processed bucket
        object=GCS_FILE_NAME,
        mode='reschedule',
        poke_interval=GCS_SENSOR_POKE_INTERVAL,
        timeout=GCS_SENSOR_SENSOR_TIMEOUT,        
        retries=RETRIES,
    )
    
    # CHANGED: Updated Dataflow to read from processed bucket
    run_dataflow_flex_template = DataflowStartFlexTemplateOperator(
        task_id="run_dataflow_flex_template",
        body={
            "launchParameter": {
                "containerSpecGcsPath": GCS_FLEX_TEMPLATE_PATH,
                "jobName": DATAFLOW_JOB_NAME + "-{{ ds_nodash }}",
                "parameters": {
                    "project": GCP_PROJECT_ID,
                    "bucket": GCS_PROCESSED_BUCKET,  # CHANGED: Now uses processed bucket (airflow_daily)
                    "temp_bucket": GCS_DATAFLOW_BUCKET,
                    "dataset": BIGQUERY_DATASET,
                    "table": BIGQUERY_TABLE,
                    "airflow_date": "{{ ds_nodash }}"
                },
                "environment": {
                    "tempLocation": f"gs://{GCS_DATAFLOW_BUCKET}/dataflow-temp/",
                    "stagingLocation": f"gs://{GCS_DATAFLOW_BUCKET}/dataflow-staging/",
                    "zone": "europe-west1-b"
                }
            }
        },
        location="europe-west1",
        project_id=GCP_PROJECT_ID,
        retries=RETRIES,
    )

    check_data_on_bigquery = BigQueryCheckOperator(
        task_id='check_data_on_bigquery',
        sql=f'SELECT COUNT(*) FROM `{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`',
        use_legacy_sql=False,
        retries=BQ_CHECK_RETRIES,
    )

    # REMOVED: No need to move files anymore since we upload directly to processed bucket
    # move_from_landing_to_processed = GCSToGCSOperator(...)
    
    # CHANGED: Updated task dependencies - removed file move task
    # Task Dependencies
    read_and_upload_today_courses_csv_task >> check_file_on_gcs >> run_dataflow_flex_template >> check_data_on_bigquery