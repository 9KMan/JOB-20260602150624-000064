################################################################################
# KMS Module Outputs
################################################################################

output "key_id" {
  description = "ID of the main KMS key"
  value       = aws_kms_key.main.key_id
}

output "key_arn" {
  description = "ARN of the main KMS key"
  value       = aws_kms_key.main.arn
}

output "key_alias" {
  description = "Alias of the main KMS key"
  value       = aws_kms_alias.main.name
}

output "s3_bucket_key_id" {
  description = "ID of the S3 bucket key KMS key"
  value       = aws_kms_key.s3_bucket_key.key_id
}

output "s3_bucket_key_arn" {
  description = "ARN of the S3 bucket key KMS key"
  value       = aws_kms_key.s3_bucket_key.arn
}