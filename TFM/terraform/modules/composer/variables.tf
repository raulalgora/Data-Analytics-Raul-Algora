variable "gcp_project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "gcp_region" {
  description = "Region for Composer and storage"
  type        = string
  default     = "europe-west1"
}

variable "dag_local_path" {
  description = "Local path to the DAG file to upload"
  type        = string
}

variable "dag_object_name" {
  description = "Path inside the GCS bucket where the DAG will be stored"
  type        = string
}

variable "bootstrap_dag_local_path"  { type = string }
variable "bootstrap_dag_object_name" { type = string }

variable "json_local_path"        { type = string }
variable "json_object_name"       { type = string }