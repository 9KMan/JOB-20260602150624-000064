################################################################################
# S3 Module Outputs
################################################################################

################################################################################
# Assets Bucket
################################################################################

output "assets_bucket_name" {
  description = "Name of the assets S3 bucket"
  value       = aws_s3_bucket.assets.id
}

output "assets_bucket_arn" {
  description = "ARN of the assets S3 bucket"
  value       = aws_s3_bucket.assets.arn
}

output "assets_bucket_domain_name" {
  description = "Domain name of the assets S3 bucket"
  value       = aws_s3_bucket.assets.bucket_domain_name
}

################################################################################
# Logs Bucket
################################################################################

output "logs_bucket_name" {
  description = "Name of the logs S3 bucket"
  value       = aws_s3_bucket.logs.id
}

output "logs_bucket_arn" {
  description = "ARN of the logs S3 bucket"
  value       = aws_s3_bucket.logs.arn
}

output "logs_bucket_domain_name" {
  description = "Domain name of the logs S3 bucket"
  value       = aws_s3_bucket.logs.bucket_domain_name
}

################################################################################
# Backups Bucket
################################################################################

output "backups_bucket_name" {
  description = "Name of the backups S3 bucket"
  value       = aws_s3_bucket.backups.id
}

output "backups_bucket_arn" {
  description = "ARN of the backups S3 bucket"
  value       = aws_s3_bucket.backups.arn
}

output "backups_bucket_domain_name" {
  description = "Domain name of the backups S3 bucket"
  value       = aws_s3_bucket.backups.bucket_domain_name
}