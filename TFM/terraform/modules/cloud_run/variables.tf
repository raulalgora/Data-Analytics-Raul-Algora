variable "project_id"             { type = string }
variable "region"                 { type = string }
variable "repository_name"       { type = string }
variable "service_name"          { type = string }
variable "image_tag"             { type = string }

variable "bucket_name"           { type = string }
variable "csv_file_name"         { type = string }

variable "service_account_email" { type = string }
variable "request_timeout"       { type = string }

variable "cpu_limit"             { type = string }
variable "memory_limit"          { type = string }
variable "min_instances"         { type = number }
variable "max_instances"         { type = number }

variable "allow_public_access"   { type = bool }
variable "allowed_members"       { type = list(string) }