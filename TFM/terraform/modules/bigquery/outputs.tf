output "dataset_id" {
  description = "The ID of the created BigQuery dataset."
  value       = google_bigquery_dataset.this.dataset_id
}