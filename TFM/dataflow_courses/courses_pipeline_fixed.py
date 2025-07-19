import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, GoogleCloudOptions
import argparse
import csv
from io import StringIO
import datetime
import sys

# --- Configuration ---
# Define your BigQuery schema explicitly.
# Ensure these names and types exactly match your target BigQuery table.
# The order here should reflect the order of columns in your CSV file.
BIGQUERY_SCHEMA = ','.join([
    'training_title:STRING',
    'training_provider:STRING',
    'training_object_id:STRING',
    'training_type:STRING',
    'training_active:STRING',
    'training_description:STRING',
    'training_subject:STRING',
    'training_hours:FLOAT',
    'area_formacion:STRING',
    'subarea_formacion:STRING',
    'keyword:STRING',
    'language:STRING',
    'tipo_formacion:STRING',
    'loadtime:STRING',
    'load_date:STRING',
    'date_processed:STRING',
    'processing_timestamp:STRING'
])

# --- DoFn for Parsing CSV Lines ---
class ParseCsvLine(beam.DoFn):
    def process(self, element):
        """
        Parses a single CSV line into a dictionary.
        Handles basic type conversion and robust error logging for malformed rows.
        """
        # Strip leading/trailing whitespace from the element first
        stripped_element = element.strip()

        # Skip completely empty or whitespace-only lines
        if not stripped_element:
            sys.stderr.write(f"Skipping empty or whitespace-only line: '{element}'\n")
            return []

        reader = csv.reader(StringIO(stripped_element))
        try:
            row = next(reader)
            
            # Additional check: if the row is empty after reading (e.g., line was just a newline)
            if not row:
                sys.stderr.write(f"Skipping line that resulted in an empty row: '{element}'\n")
                return []

            # Ensure enough columns are present
            expected_columns = 17 # Based on the number of fields in BIGQUERY_SCHEMA
            if len(row) < expected_columns:
                sys.stderr.write(f"Skipping row with insufficient columns: '{element}' "
                                 f"(Expected {expected_columns}, got {len(row)})\n")
                return []

            return [{
                'training_title': row[0].strip(),
                'training_provider': row[1].strip(),
                'training_object_id': row[2].strip(),
                'training_type': row[3].strip(),
                'training_active': row[4].strip(),
                'training_description': row[5].strip(),
                'training_subject': row[6].strip(),
                'training_hours': float(row[7].strip()) if row[7].strip() else 0.0,
                'area_formacion': row[8].strip(),
                'subarea_formacion': row[9].strip(),
                'keyword': row[10].strip(),
                'language': row[11].strip(),
                'tipo_formacion': row[12].strip(),
                'loadtime': row[13].strip(),
                'load_date': row[14].strip(),
                'date_processed': row[15].strip(),
                'processing_timestamp': row[16].strip()
            }]
        except (csv.Error, IndexError, ValueError) as e:
            sys.stderr.write(f"Skipping malformed row: '{element}' - Error: {e}\n")
            return []

def get_file_name_with_date(date_str=None):
    """
    Generate the file name with date pattern.
    If date_str is provided, use it. Otherwise, use current date.
    """
    if date_str:
        date_part = date_str
    else:
        date_part = datetime.datetime.now().strftime('%Y%m%d')
    
    file_name = f"courses_{date_part}.csv"
    return file_name

# --- Pipeline Definition ---
def run_pipeline():
    print("🚀 Starting simple pipeline...")

    parser = argparse.ArgumentParser()
    parser.add_argument('--project',
                        dest='project',
                        required=True,
                        help='Google Cloud project ID.')
    parser.add_argument('--bucket',
                        dest='bucket',
                        required=True,
                        help='GCS bucket for input and temp/staging files.')
    parser.add_argument('--dataset',
                        dest='dataset',
                        required=True,
                        help='BigQuery dataset.')
    parser.add_argument('--table',
                        dest='table',
                        required=True,
                        help='BigQuery table.')
    parser.add_argument('--date_filter',
                        dest='date_filter',
                        required=False,
                        help='Date filter for input file (YYYYMMDD). If not provided, uses current date.')
    parser.add_argument('--airflow_date',
                        dest='airflow_date',
                        required=False,
                        help='Date from Airflow DAG (YYYYMMDD format).')

    # IMPORTANT CHANGE HERE: Use parse_known_args()
    args, beam_args = parser.parse_known_args() # This will ignore Dataflow's internal arguments

    # Determine which date to use (priority: airflow_date > date_filter > current_date)
    date_to_use = None
    if args.airflow_date:
        date_to_use = args.airflow_date
        print(f"📅 Using Airflow date: {date_to_use}")
    elif args.date_filter:
        date_to_use = args.date_filter
        print(f"📅 Using provided date filter: {date_to_use}")
    else:
        date_to_use = datetime.datetime.now().strftime('%Y%m%d')
        print(f"📅 Using current date: {date_to_use}")

    # Generate file name automatically
    file_name = get_file_name_with_date(date_to_use)
    
    # Construct input and output paths
    input_file = f'gs://{args.bucket}/daily_courses/{file_name}'
    output_table = f'{args.project}:{args.dataset}.{args.table}'

    print(f"📁 Input: {input_file}")
    print(f"📊 Output: {output_table}")

    # Set up pipeline options with defaults.
    # Note: project, region, temp_location, staging_location, runner
    # are often passed by Dataflow automatically as command-line args.
    # By using parse_known_args, your script ignores them, and Beam
    # itself (when initialized with PipelineOptions()) will pick them up.
    pipeline_options = PipelineOptions()
    pipeline_options.view_as(StandardOptions).runner = 'DataflowRunner'
    pipeline_options.view_as(GoogleCloudOptions).project = args.project
    pipeline_options.view_as(GoogleCloudOptions).region = 'europe-west1' # Ensure this matches your deployment region
    pipeline_options.view_as(GoogleCloudOptions).temp_location = f'gs://{args.bucket}/temp/'
    pipeline_options.view_as(GoogleCloudOptions).staging_location = f'gs://{args.bucket}/staging/'

    with beam.Pipeline(options=pipeline_options) as p:
        (p
         | 'Read CSV' >> beam.io.ReadFromText(input_file, skip_header_lines=1)
         | 'Parse CSV Line to Dictionary' >> beam.ParDo(ParseCsvLine())
         | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
             table=output_table,
             schema=BIGQUERY_SCHEMA,
             create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
             write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE
         ))

if __name__ == '__main__':
    run_pipeline()