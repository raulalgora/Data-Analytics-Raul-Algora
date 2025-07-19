locals {
  dockerfile_context = "${path.module}/api"
  dockerfile_path    = "${path.module}/api/Dockerfile"
  # Build the full image path
  full_image_path = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/cursos-api:${var.image_tag}"
}

resource "google_artifact_registry_repository" "this" {
  project       = var.project_id
  location      = var.region
  repository_id = var.repository_name
  description   = "Docker repository for Cloud Run service"
  format        = "DOCKER"
}

resource "null_resource" "build_and_push_image" {
  triggers = {
    dockerfile_hash = filesha256(local.dockerfile_path)
    image_tag       = var.image_tag
  }

  provisioner "local-exec" {
    command = <<-EOT
      # Authenticate with Artifact Registry
      gcloud auth configure-docker ${var.region}-docker.pkg.dev --quiet
      
      # Build and push with explicit single platform using buildx
      cd ${local.dockerfile_context}
      docker buildx build --platform linux/amd64 --push -t ${local.full_image_path} -f Dockerfile .
    EOT
  }

  depends_on = [google_artifact_registry_repository.this]
}

resource "google_cloud_run_v2_service" "this" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = local.full_image_path  # Use the full image path

      env {
        name  = "BUCKET_NAME"
        value = var.bucket_name
      }

      env {
        name  = "CSV_FILE_NAME"
        value = var.csv_file_name
      }

      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
      }

      startup_probe {
        http_get {
          path = "/health"
        }
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
        }
        initial_delay_seconds = 30
        timeout_seconds       = 5
        period_seconds        = 30
        failure_threshold     = 3
      }
    }

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    service_account = var.service_account_email
    timeout         = var.request_timeout
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [null_resource.build_and_push_image]
}

resource "google_cloud_run_service_iam_member" "public" {
  count    = var.allow_public_access ? 1 : 0
  location = google_cloud_run_v2_service.this.location
  project  = google_cloud_run_v2_service.this.project
  service  = google_cloud_run_v2_service.this.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "specific" {
  for_each = var.allow_public_access ? toset([]) : toset(var.allowed_members)
  location = google_cloud_run_v2_service.this.location
  project  = google_cloud_run_v2_service.this.project
  service  = google_cloud_run_v2_service.this.name
  role     = "roles/run.invoker"
  member   = each.value
}