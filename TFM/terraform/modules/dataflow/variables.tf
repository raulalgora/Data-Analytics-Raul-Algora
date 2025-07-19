# modules/dataflow/variables.tf

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
}

variable "template_bucket_name" {
  description = "Name of the GCS bucket to store the Flex Template"
  type        = string
}

variable "template_name" {
  description = "Name of the template file (without .json extension)"
  type        = string
  default     = "courses-daily-load-flex-template"
}

variable "template_display_name" {
  description = "Display name for the Dataflow template"
  type        = string
  default     = "CoursesDailyLoadFlexTemplate"
}

variable "template_description" {
  description = "Description of the Dataflow template"
  type        = string
  default     = "A Dataflow Flex Template for processing daily course CSV files and loading them into BigQuery."
}

variable "container_image" {
  description = "The container image for the Dataflow Flex Template"
  type        = string
}

variable "dockerfile_context_path" {
  description = "Path to the Docker build context (where Dockerfile and code are located)"
  type        = string
  default     = "."
}

variable "dockerfile_path" {
  description = "Path to the Dockerfile relative to the context"
  type        = string
  default     = "Dockerfile"
}

variable "template_parameters" {
  description = "Template parameters configuration"
  type = list(object({
    name        = string
    label       = string
    help_text   = string
    is_optional = bool
  }))
  default = [
    {
      name        = "project"
      label       = "GCP Project ID"
      help_text   = "The Google Cloud project ID."
      is_optional = false
    },
    {
      name        = "bucket"
      label       = "GCS Bucket"
      help_text   = "GCS bucket for input and temp/staging files."
      is_optional = false
    },
    {
      name        = "dataset"
      label       = "BigQuery Dataset"
      help_text   = "The BigQuery dataset for the output table."
      is_optional = false
    },
    {
      name        = "table"
      label       = "BigQuery Table"
      help_text   = "The BigQuery table for the output."
      is_optional = false
    },
    {
      name        = "airflow_date"
      label       = "Airflow Date (YYYYMMDD)"
      help_text   = "Date passed from Airflow DAG (YYYYMMDD format)."
      is_optional = true
    }
  ]
}

variable "service_account_name" {
  description = "Name of the service account for Dataflow"
  type        = string
  default     = "dataflow-courses-sa"
}

variable "create_staging_bucket" {
  description = "Whether to create a staging bucket for Dataflow"
  type        = bool
  default     = true
}

variable "staging_bucket_name" {
  description = "Name of the staging bucket for Dataflow"
  type        = string
  default     = ""
}

variable "create_temp_bucket" {
  description = "Whether to create a temp bucket for Dataflow"
  type        = bool
  default     = true
}

variable "temp_bucket_name" {
  description = "Name of the temp bucket for Dataflow"
  type        = string
  default     = ""
}