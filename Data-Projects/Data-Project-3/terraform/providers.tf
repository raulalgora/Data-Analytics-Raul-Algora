provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

terraform {
  required_version = ">= 1.3.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.91.0"
    }
  }

}