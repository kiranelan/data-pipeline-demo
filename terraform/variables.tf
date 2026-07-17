variable "aws_region" {
  description = "AWS region where the S3 bucket will be created."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for S3 bucket naming."
  type        = string
  default     = "telecom-warehouse-demo"
}

variable "environment" {
  description = "Environment name."
  type        = string
  default     = "dev"
}

variable "terraform_assume_role_arn" {
  description = "Optional existing IAM role ARN that Terraform should assume while creating AWS resources. Leave empty if using AWS_PROFILE or default credentials."
  type        = string
  default     = ""
}

variable "existing_s3_access_role_arn" {
  description = "Existing IAM role ARN that should be allowed to read the uploaded S3 sample data. This can be your Snowflake S3 access role or another existing AWS role."
  type        = string
  default     = ""
}

variable "force_destroy_bucket" {
  description = "If true, Terraform can delete the bucket even when it contains uploaded sample data. Keep true for demo projects."
  type        = bool
  default     = true
}

variable "raw_data_prefix" {
  description = "S3 prefix where sample CSV files will be uploaded."
  type        = string
  default     = "raw"
}
