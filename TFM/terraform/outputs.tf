output "bigquery_dataset_id" {
  description = "The ID of the created BigQuery dataset."
  value       = module.bigquery.dataset_id
}

output "composer_dags_bucket" {
  value       = module.composer.dags_bucket_uri
  description = "Path to Composer bucket for DAGs"
}

output "composer_airflow_web" {
  description = "Airflow web UI URL"
  value       = module.composer.airflow_uri
}