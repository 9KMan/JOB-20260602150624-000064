################################################################################
# Secrets Manager Module Outputs
################################################################################

################################################################################
# Database Credentials
################################################################################

output "db_credentials_secret_id" {
  description = "ID of the database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.id
}

output "db_credentials_secret_arn" {
  description = "ARN of the database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "db_credentials_secret_name" {
  description = "Name of the database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.name
}

################################################################################
# Auth0 Credentials
################################################################################

output "auth0_secret_id" {
  description = "ID of the Auth0 credentials secret"
  value       = aws_secretsmanager_secret.auth0.id
}

output "auth0_secret_arn" {
  description = "ARN of the Auth0 credentials secret"
  value       = aws_secretsmanager_secret.auth0.arn
}

output "auth0_secret_name" {
  description = "Name of the Auth0 credentials secret"
  value       = aws_secretsmanager_secret.auth0.name
}

################################################################################
# API Keys
################################################################################

output "api_keys_secret_id" {
  description = "ID of the API keys secret"
  value       = aws_secretsmanager_secret.api_keys.id
}

output "api_keys_secret_arn" {
  description = "ARN of the API keys secret"
  value       = aws_secretsmanager_secret.api_keys.arn
}

output "api_keys_secret_name" {
  description = "Name of the API keys secret"
  value       = aws_secretsmanager_secret.api_keys.name
}

################################################################################
# Combined Secret ARN
################################################################################

output "secret_arn" {
  description = "ARN of the secrets manager secret (db_credentials as primary)"
  value       = aws_secretsmanager_secret.db_credentials.arn
}