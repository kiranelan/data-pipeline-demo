output "raw_bucket_name" {
  description = "S3 bucket containing sample raw CSV data."
  value       = aws_s3_bucket.raw_data.id
}

output "raw_bucket_arn" {
  description = "ARN of the raw data S3 bucket."
  value       = aws_s3_bucket.raw_data.arn
}

output "snowflake_stage_url" {
  description = "S3 URL to use in the Snowflake external stage."
  value       = "s3://${aws_s3_bucket.raw_data.id}/${var.raw_data_prefix}/"
}

output "uploaded_sample_files" {
  description = "Sample CSV files uploaded to S3."
  value = {
    for file_name, object in aws_s3_object.sample_csv_files :
    file_name => "s3://${aws_s3_bucket.raw_data.id}/${object.key}"
  }
}

output "existing_s3_access_role_arn" {
  description = "Existing role granted read access to the sample S3 data."
  value       = var.existing_s3_access_role_arn == "" ? "No existing S3 access role configured" : var.existing_s3_access_role_arn
}
