output "service_url" {
  value       = google_cloud_run_v2_service.this.uri
  description = "The URL of the deployed Cloud Run service"
}