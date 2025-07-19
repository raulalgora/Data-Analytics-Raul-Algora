###############################
# Project & GCP Basics
###############################

variable "gcp_project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "gcp_region" {
  description = "The GCP region for resources."
  type        = string
}

variable "gcp_zone" {
  description = "The GCP zone for resources like Composer."
  type        = string
}

###############################
# Composer Configuration
###############################

variable "dag_local_path" {
  description = "Local path to the main DAG file"
  type        = string
}

variable "dag_object_name" {
  description = "Object name to upload the DAG to in GCS"
  type        = string
}

variable "bootstrap_dag_local_path" {
  description = "Path to DAG for bootstrapping Airflow Variables"
  type        = string
}

variable "bootstrap_dag_object_name" {
  description = "Object name for bootstrap DAG in Composer bucket"
  type        = string
}

variable "json_local_path" {
  description = "Path to local JSON file with Airflow Variables"
  type        = string
}

variable "json_object_name" {
  description = "Object name for JSON file in GCS Composer bucket"
  type        = string
}

###############################
# Buckets
###############################

variable "bucket_name_treated" {
  description = "Name of the treated GCS bucket (e.g. airflow_daily)"
  type        = string
}

variable "bucket_name_raw" {
  description = "Name of the raw GCS bucket (used by Cloud Run and CSV ingestion)"
  type        = string
}

variable "local_csv_path" {
  description = "Path to local CSV file to upload initially"
  type        = string
}

###############################
# BigQuery
###############################

variable "bigquery_dataset_id" {
  description = "ID of the BigQuery dataset."
  type        = string
}

###############################
# Dataflow Flex Template
###############################

variable "dataflow_template_bucket_name" {
  type        = string
  description = "Bucket to store Dataflow Flex Template JSON"
}

variable "dataflow_template_name" {
  type        = string
  description = "Name of the Dataflow template"
}

variable "dataflow_template_display_name" {
  type        = string
  description = "Display name for the template"
}

variable "dataflow_template_description" {
  type        = string
  description = "Description for the template"
}

variable "dataflow_container_image" {
  type        = string
  description = "Container image used by Dataflow Flex Template"
}

variable "dataflow_dockerfile_context_path" {
  type        = string
  description = "Context path for Docker build"
}

variable "dataflow_dockerfile_path" {
  type        = string
  description = "Path to Dockerfile relative to context"
}

variable "dataflow_template_parameters" {
  type = list(object({
    name        = string
    label       = string
    help_text   = string
    is_optional = bool
  }))
  description = "Parameters accepted by the Flex Template"
}

variable "dataflow_service_account_name" {
  type        = string
  description = "Name of the service account for Dataflow"
}

variable "dataflow_create_staging_bucket" {
  type        = bool
  description = "Whether to create staging bucket"
}

variable "dataflow_staging_bucket_name" {
  type        = string
  description = "Staging bucket name"
}

variable "dataflow_create_temp_bucket" {
  type        = bool
  description = "Whether to create temp bucket"
}

variable "dataflow_temp_bucket_name" {
  type        = string
  description = "Temp bucket name"
}

###############################
# Cloud Run
###############################

variable "cloud_run_service_name" {
  type        = string
  description = "Name of the Cloud Run service"
}

variable "cloud_run_repository_name" {
  type        = string
  description = "Artifact Registry repo to push Docker image"
}

variable "cloud_run_image_tag" {
  type        = string
  description = "Tag name for the Docker image"
}

variable "cloud_run_service_account_email" {
  type        = string
  description = "Service account to run Cloud Run API"
}

variable "cloud_run_csv_file_name" {
  type        = string
  description = "CSV file name expected in the bucket"
}

variable "cloud_run_request_timeout" {
  type        = string
  description = "Timeout per request (e.g. 30s)"
}

variable "cloud_run_cpu_limit" {
  type        = string
  description = "CPU limit for Cloud Run container"
}

variable "cloud_run_memory_limit" {
  type        = string
  description = "Memory limit for Cloud Run container"
}

variable "cloud_run_min_instances" {
  type        = number
  description = "Minimum instances for Cloud Run"
}

variable "cloud_run_max_instances" {
  type        = number
  description = "Maximum instances for Cloud Run"
}

variable "cloud_run_allow_public_access" {
  type        = bool
  description = "Whether to allow unauthenticated access"
}

variable "cloud_run_allowed_members" {
  type        = list(string)
  description = "List of IAM members allowed to invoke Cloud Run"
}