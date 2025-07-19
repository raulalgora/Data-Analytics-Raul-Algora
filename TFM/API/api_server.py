from fastapi import FastAPI, HTTPException
from google.cloud import storage
import pandas as pd
from io import StringIO
import os
import logging
from datetime import datetime, date

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Cursos API", description="API for managing courses data - OPTIMIZED", version="2.0.0")

# Configuration - update these values
BUCKET_NAME = os.environ.get("BUCKET_NAME", "your-bucket-name-cursos")
CSV_FILE_NAME = os.environ.get("CSV_FILE_NAME", "courses.csv")

def load_cursos_by_date_only(target_date):
    """Load ONLY courses for a specific date from Google Cloud Storage bucket - OPTIMIZED"""
    try:
        logger.info(f"Loading ONLY courses for date {target_date} from bucket: {BUCKET_NAME}")

        # Initialize the client
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(CSV_FILE_NAME)

        # Check if the blob exists
        if not blob.exists():
            logger.error(f"File {CSV_FILE_NAME} does not exist in bucket {BUCKET_NAME}")
            raise HTTPException(status_code=404, detail=f"File {CSV_FILE_NAME} not found in bucket {BUCKET_NAME}")

        # Download as string
        logger.info("Downloading CSV content...")
        content = blob.download_as_text()

        if not content.strip():
            logger.error("CSV file is empty")
            raise HTTPException(status_code=400, detail="CSV file is empty")

        # Parse CSV into pandas
        logger.info("Parsing CSV content...")
        df = pd.read_csv(StringIO(content))

        if df.empty:
            logger.warning("CSV loaded but dataframe is empty")
            raise HTTPException(status_code=400, detail="CSV file contains no data")

        # Check if loadtime column exists
        if 'loadtime' not in df.columns:
            logger.error("Column 'loadtime' not found in CSV")
            raise HTTPException(status_code=400, detail="Column 'loadtime' not found in data")

        # Convert loadtime to datetime and filter by date
        logger.info(f"Filtering courses for date: {target_date}")
        df['loadtime'] = pd.to_datetime(df['loadtime'])
        df['load_date'] = df['loadtime'].dt.date
        
        # Convert target_date string to date object
        if isinstance(target_date, str):
            target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        else:
            target_date_obj = target_date
        
        # Filter ONLY courses for the specific date
        filtered_df = df[df['load_date'] == target_date_obj]
        
        logger.info(f"Found {len(filtered_df)} courses for {target_date} out of {len(df)} total courses")
        
        return filtered_df

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading data from bucket: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading data from bucket: {str(e)}")

def get_total_count_only():
    """Get ONLY the total count without loading all data - LIGHTWEIGHT"""
    try:
        logger.info("Getting total count only...")
        
        # Initialize the client
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(CSV_FILE_NAME)

        if not blob.exists():
            raise HTTPException(status_code=404, detail=f"File {CSV_FILE_NAME} not found")

        # Download and count lines (much faster than loading all data)
        content = blob.download_as_text()
        lines = content.strip().split('\n')
        total_rows = len(lines) - 1  # Subtract header row
        
        logger.info(f"Total courses: {total_rows}")
        return total_rows

    except Exception as e:
        logger.error(f"Error getting count: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting count: {str(e)}")

@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Cursos API is running - OPTIMIZED VERSION",
        "version": "2.0.0",
        "optimization": "Only loads courses for specific dates",
        "bucket_name": BUCKET_NAME,
        "csv_file": CSV_FILE_NAME,
        "main_endpoints": {
            "get_cursos_today": "/cursos/today",
            "get_cursos_by_date": "/cursos/date/{YYYY-MM-DD}",
            "get_cursos_count_today": "/cursos/count/today",
            "health_check": "/health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "cursos-api-optimized", "version": "2.0.0"}

@app.get("/cursos/today")
def get_cursos_today():
    """Get ONLY courses added today - OPTIMIZED"""
    try:
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        
        logger.info(f"🎯 Getting courses for TODAY only: {today_str}")
        
        # Load ONLY today's courses
        today_courses_df = load_cursos_by_date_only(today_str)
        
        # Clean the dataframe
        today_courses_df = today_courses_df.replace([float('inf'), float('-inf')], None)
        today_courses_df = today_courses_df.where(pd.notnull(today_courses_df), None)
        
        courses_list = today_courses_df.to_dict('records')
        
        logger.info(f"✅ Returning {len(courses_list)} courses for today")
        
        return {
            "date": today_str,
            "total_courses_today": len(courses_list),
            "cursos": courses_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting today's courses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting today's courses: {str(e)}")

@app.get("/cursos/date/{target_date}")
def get_cursos_by_date(target_date: str):
    """Get ONLY courses for a specific date - OPTIMIZED"""
    try:
        # Validate date format
        try:
            datetime.strptime(target_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        logger.info(f"🎯 Getting courses for {target_date} only")
        
        # Load ONLY courses for this specific date
        date_courses_df = load_cursos_by_date_only(target_date)
        
        # Clean the dataframe
        date_courses_df = date_courses_df.replace([float('inf'), float('-inf')], None)
        date_courses_df = date_courses_df.where(pd.notnull(date_courses_df), None)
        
        courses_list = date_courses_df.to_dict('records')
        
        logger.info(f"✅ Returning {len(courses_list)} courses for {target_date}")
        
        return {
            "date": target_date,
            "total_courses_for_date": len(courses_list),
            "cursos": courses_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting courses for date {target_date}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting courses for date: {str(e)}")

@app.get("/cursos/count/today")
def get_cursos_count_today():
    """Get count of courses added today - OPTIMIZED"""
    try:
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        
        logger.info(f"🔢 Getting count for today: {today_str}")
        
        # Load ONLY today's courses to count them
        today_courses_df = load_cursos_by_date_only(today_str)
        today_count = len(today_courses_df)
        
        # Get total count separately (lightweight)
        total_count = get_total_count_only()
        
        logger.info(f"✅ Today: {today_count}, Total: {total_count}")
        
        return {
            "date": today_str,
            "total_cursos_today": today_count,
            "total_cursos_all": total_count
        }
        
    except Exception as e:
        logger.error(f"Error getting today's count: {str(e)}")
        return {"total_cursos_today": 0, "date": str(date.today()), "error": str(e)}

@app.get("/cursos/count/date/{target_date}")
def get_cursos_count_by_date(target_date: str):
    """Get count of courses for a specific date - OPTIMIZED"""
    try:
        # Validate date format
        try:
            datetime.strptime(target_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        logger.info(f"🔢 Getting count for {target_date}")
        
        # Load ONLY courses for this date to count them
        date_courses_df = load_cursos_by_date_only(target_date)
        date_count = len(date_courses_df)
        
        logger.info(f"✅ Found {date_count} courses for {target_date}")
        
        return {
            "date": target_date,
            "total_cursos_for_date": date_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting count for {target_date}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting count for date: {str(e)}")

# REMOVED: All endpoints that load the full CSV
# - get_cursos (full pagination)
# - get_curso_by_id 
# - search_cursos
# - get_cursos_sample
# - get_cursos_count (full count)
# These endpoints were loading the entire CSV which is inefficient

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)