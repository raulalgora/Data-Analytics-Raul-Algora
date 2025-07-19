terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# main.tf
resource "google_project_service" "apis" {
  for_each = toset([
    "composer.googleapis.com",
    "bigquery.googleapis.com",
    "run.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "container.googleapis.com", # Required for Composer
    "compute.googleapis.com",   # Required for Composer
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "storage.googleapis.com",
    "dataflow.googleapis.com",  # Added for Dataflow
  ])
  project                    = var.gcp_project_id
  service                    = each.key
  disable_on_destroy         = false # Set to true to disable API on terraform destroy
  disable_dependent_services = true
}

# 1. BUCKETS MODULE - FIRST
module "buckets" {
  source = "./modules/buckets"

  bucket_name_treated = var.bucket_name_treated
  bucket_name_raw     = var.bucket_name_raw
  local_csv_path      = var.local_csv_path

  depends_on = [google_project_service.apis]
}

# 2. CLOUD RUN MODULE - SECOND (depends on buckets)
module "cloud_run" {
  source = "./modules/cloud_run"

  project_id             = var.gcp_project_id
  region                 = var.gcp_region
  repository_name        = var.cloud_run_repository_name
  service_name           = var.cloud_run_service_name
  image_tag              = var.cloud_run_image_tag

  bucket_name            = var.bucket_name_raw  # Usamos la misma
  csv_file_name          = var.cloud_run_csv_file_name
  service_account_email  = var.cloud_run_service_account_email
  request_timeout        = var.cloud_run_request_timeout

  cpu_limit              = var.cloud_run_cpu_limit
  memory_limit           = var.cloud_run_memory_limit
  min_instances          = var.cloud_run_min_instances
  max_instances          = var.cloud_run_max_instances

  allow_public_access    = var.cloud_run_allow_public_access
  allowed_members        = var.cloud_run_allowed_members

  depends_on = [google_project_service.apis, module.buckets]
}

# 3. BIGQUERY MODULE - THIRD (depends on cloud run)
module "bigquery" {
  source = "./modules/bigquery"

  gcp_project_id        = var.gcp_project_id
  bigquery_dataset_id   = var.bigquery_dataset_id
  bigquery_dataset_location = var.gcp_region
  max_time_travel_hours = 168

  depends_on = [google_project_service.apis, module.cloud_run]
}

# 4. DATAFLOW MODULE - FOURTH (depends on bigquery)
module "dataflow" {
  source = "./modules/dataflow"

  project_id                = var.gcp_project_id
  region                    = var.gcp_region
  template_bucket_name      = var.dataflow_template_bucket_name
  template_name             = var.dataflow_template_name
  template_display_name     = var.dataflow_template_display_name
  template_description      = var.dataflow_template_description
  container_image           = var.dataflow_container_image
  dockerfile_context_path   = var.dataflow_dockerfile_context_path
  dockerfile_path           = var.dataflow_dockerfile_path
  template_parameters       = var.dataflow_template_parameters
  service_account_name      = var.dataflow_service_account_name
  create_staging_bucket     = var.dataflow_create_staging_bucket
  staging_bucket_name       = var.dataflow_staging_bucket_name
  create_temp_bucket        = var.dataflow_create_temp_bucket
  temp_bucket_name          = var.dataflow_temp_bucket_name

  depends_on = [google_project_service.apis, module.bigquery]
}

# 5. COMPOSER MODULE - LAST (depends on dataflow)
module "composer" {
  source = "./modules/composer"

  gcp_project_id = var.gcp_project_id
  gcp_region     = var.gcp_region

  dag_local_path             = "${path.module}/modules/composer/dags/airflow_final_funcional.py"
  dag_object_name            = "dags/airflow_final_funcional.py"
  bootstrap_dag_local_path   = "${path.module}/modules/composer/dags/bootstrap_variables_from_json.py"
  bootstrap_dag_object_name  = "dags/bootstrap_variables_from_json.py"
  json_local_path            = "${path.module}/modules/composer/configs/airflow_variables.json"
  json_object_name           = "configs/airflow_variables.json"

  depends_on = [google_project_service.apis, module.dataflow]
}

# COMENTADO TEMPORALMENTE - Para que lo maneje tu compañero
# module "composer" {
#   source           = "./modules/composer"
#   project_id       = var.gcp_project_id
#   region           = var.gcp_region
#   zone             = var.gcp_zone
#   environment_name = var.composer_environment_name
#   machine_type     = var.composer_machine_type
#   node_count       = var.composer_node_count
#   depends_on       = [google_project_service.apis]
# }

# COMENTADO TEMPORALMENTE - Para que lo maneje tu compañero
# module "bigquery" {
#   source     = "./modules/bigquery"
#   project_id = var.gcp_project_id
#   region     = var.gcp_region
#   dataset_id = var.bigquery_dataset_id
#   tables     = var.bigquery_tables
#   depends_on = [google_project_service.apis]
# }

# COMENTADO TEMPORALMENTE - Para que lo maneje tu compañero
# module "cloud_run" {
#   source = "./modules/cloud_run"
#
#   project_id            = var.gcp_project_id
#   region                = var.gcp_region
#   service_name          = var.cloud_run_service_name
#   container_image       = var.cloud_run_image
#   bucket_name           = var.cloud_run_bucket_name
#   csv_file_name         = var.cloud_run_csv_file_name
#   service_account_email = var.cloud_run_service_account_email
#   
#   # Configuración de recursos
#   cpu_limit     = var.cloud_run_cpu_limit
#   memory_limit  = var.cloud_run_memory_limit
#   min_instances = var.cloud_run_min_instances
#   max_instances = var.cloud_run_max_instances
#   
#   # Configuración de acceso
#   allow_public_access = var.cloud_run_allow_public_access
#   allowed_members     = var.cloud_run_allowed_members
#   
#   # Dependencia en APIs habilitadas
#   apis_enabled = google_project_service.apis
#   depends_on   = [google_project_service.apis]
# }

# COMENTADO TEMPORALMENTE - Para que lo maneje tu compañero
# output "composer_environment_web_server_url" {
#   description = "The URL of the Composer environment's Airflow UI."
#   value       = module.composer.web_server_url
# }

# COMENTADO TEMPORALMENTE - Para que lo maneje tu compañero  
# output "bigquery_dataset_id" {
#   description = "The ID of the created BigQuery dataset."
#   value       = module.bigquery.dataset_id
# }

# COMENTADO TEMPORALMENTE - Para que lo maneje tu compañero
# output "cloud_run_service_url" {
#   description = "The URL of the Cloud Run service."
#   value       = module.cloud_run.service_url
# }