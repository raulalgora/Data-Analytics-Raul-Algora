variable "bucket_name_treated" {
  description = "Name of the GCS bucket"
  type        = string
}

variable "bucket_name_raw" {
  description = "Name of the GCS bucket"
  type        = string
}

variable "local_csv_path" {
  description = "Local path to the CSV file to upload"
  type        = string
}