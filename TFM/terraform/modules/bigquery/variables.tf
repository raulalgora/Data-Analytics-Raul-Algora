###############################################################################
# variables.tf – BigQuery module (cleaned up for inline schema)
###############################################################################

variable "gcp_project_id" {
  description = "Google Cloud project ID where the dataset and table are created."
  type        = string
}

variable "bigquery_dataset_id" {
  description = "The ID of the BigQuery dataset (e.g., 'courses_dataset')."
  type        = string
}

variable "bigquery_dataset_location" {
  description = "Region where the BigQuery dataset is created."
  type        = string
  default     = "europe-west1"
}

variable "max_time_travel_hours" {
  description = "Number of hours to retain table history (time travel)."
  type        = number
  default     = 168
}