resource "google_storage_bucket" "airflow_daily" {
  name          = var.bucket_name_treated
  location      = "europe-southwest1"
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  force_destroy = true  # Set to true if you want Terraform to delete non-empty buckets
}

resource "google_storage_bucket" "bucket-courses" {
  name          = var.bucket_name_raw
  location      = "europe-west1"
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  force_destroy = true  # Set to true if you want Terraform to delete non-empty buckets
}

resource "google_storage_bucket_object" "upload_csv_to_raw" {
  name   = "courses.csv"                                 # path inside the bucket
  bucket = google_storage_bucket.bucket-courses.name
  source = var.local_csv_path                                # local file path

  content_type = "text/csv"
}