###############################################################################
# Resource: BigQuery dataset – courses_dataset
###############################################################################

resource "google_bigquery_dataset" "this" {
  project    = var.gcp_project_id
  dataset_id = var.bigquery_dataset_id        # e.g. "courses_dataset"
  friendly_name = var.bigquery_dataset_id

  description = "Dataset para cursos diarios desde Dataflow"
  location    = "europe-west1"

  # No default table expiration
  default_table_expiration_ms = null

  # 7-day time-travel window
  max_time_travel_hours = 168

}

###############################################################################
# Resource: BigQuery table – daily_courses_fixed
###############################################################################
resource "google_bigquery_table" "daily_courses_fixed" {
  project  = var.gcp_project_id
  dataset_id = var.bigquery_dataset_id      # "courses_dataset"
  table_id   = "daily_courses_fixed"

  description = "Cleaned daily courses feed"

  schema = jsonencode([
    { name = "training_title",        type = "STRING",    mode = "NULLABLE" },
    { name = "training_provider",     type = "STRING",    mode = "NULLABLE" },
    { name = "training_object_id",    type = "STRING",    mode = "NULLABLE" },
    { name = "training_type",         type = "STRING",    mode = "NULLABLE" },
    { name = "training_active",       type = "STRING",    mode = "NULLABLE" },
    { name = "training_description",  type = "STRING",    mode = "NULLABLE" },
    { name = "training_subject",      type = "STRING",    mode = "NULLABLE" },
    { name = "training_hours",        type = "FLOAT",     mode = "NULLABLE" },
    { name = "area_formacion",        type = "STRING",    mode = "NULLABLE" },
    { name = "subarea_formacion",     type = "STRING",    mode = "NULLABLE" },
    { name = "keyword",               type = "STRING",    mode = "NULLABLE" },
    { name = "language",              type = "STRING",    mode = "NULLABLE" },
    { name = "tipo_formacion",        type = "STRING",    mode = "NULLABLE" },
    { name = "loadtime",              type = "STRING",    mode = "NULLABLE" },
    { name = "load_date",             type = "STRING",    mode = "NULLABLE" },
    { name = "date_processed",        type = "DATE",      mode = "NULLABLE" },
    { name = "processing_timestamp",  type = "TIMESTAMP", mode = "NULLABLE" }
  ])

  # Time partitioning using the DATE field
  time_partitioning {
    type  = "DAY"
    field = "date_processed"   # Now this is a DATE field
  }

  # Encryption, labels, etc. can go here if needed
}