from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import logging

# Logging
logger = logging.getLogger(__name__)
API_BASE_URL = "https://api-cursos-999832391351.europe-west1.run.app"

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(days=1),
    'retries': 1,
}

def read_and_log_courses(**kwargs):
    ti = kwargs['ti']
    all_courses_data = []
    count_url = f"{API_BASE_URL}/cursos/count"
    logger.info(f"Fetching total course count from {count_url}")
    
    try:
        count_response = requests.get(count_url)
        count_response.raise_for_status()
        total_cursos = count_response.json().get('total_cursos', 0)
        logger.info(f"Total courses found: {total_cursos}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching total course count: {e}")
        raise
    
    if total_cursos == 0:
        logger.warning("No courses found in the API. Skipping course data fetch.")
        return
    
    courses_url = f"{API_BASE_URL}/cursos?limit={total_cursos}&offset=0"
    logger.info(f"Fetching all {total_cursos} courses from {courses_url}")
    
    try:
        response = requests.get(courses_url)
        response.raise_for_status()
        data = response.json()
        all_courses_data = data.get('cursos', [])
        logger.info(f"Successfully fetched {len(all_courses_data)} courses.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching course data: {e}")
        raise
    
    if all_courses_data:
        logger.info("\n--- Sample of Course Titles ---")
        for i, course in enumerate(all_courses_data[:5]):
            title = course.get('Training Title', 'N/A')
            logger.info(f"Course {i+1}: {title}")
        logger.info(f"\nSuccessfully read {len(all_courses_data)} courses in total.")
    else:
        logger.info("No course data was retrieved.")

with DAG(
    dag_id='read_all_courses_from_api',
    default_args=default_args,
    description='Fetches and logs all course titles from the FastAPI API.',
    schedule='@daily',
    catchup=False,
    tags=['courses', 'api', 'read'],
) as dag:
    read_courses_task = PythonOperator(
        task_id='read_courses_from_api',
        python_callable=read_and_log_courses,
    )