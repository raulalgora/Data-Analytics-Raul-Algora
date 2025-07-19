###############################################################################
# Composer Environment (using existing service account)
###############################################################################

resource "google_composer_environment" "this" {
  name    = "composertfm"
  region  = var.gcp_region
  project = var.gcp_project_id

  config {
    # Removed node_count - not supported in Composer 2.0+
    
    software_config {
      image_version = "composer-3-airflow-2.10.5"  # Updated to supported version
    }

    node_config {
      service_account = "composer-env-sa@tfm-caixabank.iam.gserviceaccount.com"
    }

    environment_size = "ENVIRONMENT_SIZE_SMALL"
  }

  labels = {
    environment = "tfm"
  }
}

###############################################################################
# Local: Extract bucket name from gs://.../dags
###############################################################################

locals {
  composer_bucket_name = replace(
    replace(google_composer_environment.this.config[0].dag_gcs_prefix, "gs://", ""),
    "/dags", ""
  )
}

###############################################################################
# Upload DAG to Composer bucket
###############################################################################

resource "google_storage_bucket_object" "dag_upload" {
  name   = var.dag_object_name
  bucket = local.composer_bucket_name
  source = var.dag_local_path

  depends_on = [google_composer_environment.this]
}

resource "google_storage_bucket_object" "bootstrap_dag" {
  name   = var.bootstrap_dag_object_name
  bucket = local.composer_bucket_name
  source = var.bootstrap_dag_local_path
  depends_on = [google_composer_environment.this]
}

resource "google_storage_bucket_object" "json_variables" {
  name   = var.json_object_name
  bucket = local.composer_bucket_name
  source = var.json_local_path
  content_type = "application/json"
  depends_on = [google_composer_environment.this]
}