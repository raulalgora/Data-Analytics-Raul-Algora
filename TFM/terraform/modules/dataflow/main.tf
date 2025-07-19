terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Build and push the Docker image using local commands with correct platform
resource "null_resource" "build_and_push_image" {
  triggers = {
    # Rebuild when any file in the context changes
    dockerfile_hash = filesha256("${var.dockerfile_context_path}/${var.dockerfile_path}")
    image_name      = var.container_image
  }

  provisioner "local-exec" {
    command = <<-EOT
      cd ${var.dockerfile_context_path}
      docker build --platform linux/amd64 -t ${var.container_image} -f ${var.dockerfile_path} .
      docker push ${var.container_image}
    EOT
  }
}

# Create a GCS bucket for the Flex Template
resource "google_storage_bucket" "dataflow_template_bucket" {
  name          = var.template_bucket_name
  project       = var.project_id
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Upload the Flex Template JSON to GCS
resource "google_storage_bucket_object" "flex_template" {
  name   = "templates/${var.template_name}.json"
  bucket = google_storage_bucket.dataflow_template_bucket.name
  content = jsonencode({
    image = var.container_image
    sdk_info = {
      language = "PYTHON"
    }
    template_type = "FLEX"
    metadata = {
      name        = var.template_display_name
      description = var.template_description
      parameters = var.template_parameters
    }
  })
  content_type = "application/json"

  depends_on = [null_resource.build_and_push_image]
}

# Create a service account for Dataflow
resource "google_service_account" "dataflow_service_account" {
  account_id   = var.service_account_name
  project      = var.project_id
  display_name = "Dataflow Service Account for ${var.template_display_name}"
  description  = "Service account used by Dataflow jobs for ${var.template_display_name}"
}

# Grant necessary permissions to the service account
resource "google_project_iam_member" "dataflow_worker" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}

resource "google_project_iam_member" "storage_object_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}

resource "google_project_iam_member" "bigquery_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}

resource "google_project_iam_member" "bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}

# Optional: Create a staging bucket for Dataflow
resource "google_storage_bucket" "dataflow_staging_bucket" {
  count         = var.create_staging_bucket ? 1 : 0
  name          = var.staging_bucket_name
  project       = var.project_id
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "Delete"
    }
  }
}

# Optional: Create a temp bucket for Dataflow
resource "google_storage_bucket" "dataflow_temp_bucket" {
  count         = var.create_temp_bucket ? 1 : 0
  name          = var.temp_bucket_name
  project       = var.project_id
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "Delete"
    }
  }
}