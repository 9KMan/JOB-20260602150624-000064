################################################################################
# Cognito Module Outputs
################################################################################

################################################################################
# User Pool
################################################################################

output "user_pool_id" {
  description = "ID of the Cognito user pool"
  value       = aws_cognito_user_pool.main.id
}

output "user_pool_arn" {
  description = "ARN of the Cognito user pool"
  value       = aws_cognito_user_pool.main.arn
}

output "user_pool_endpoint" {
  description = "Endpoint of the Cognito user pool"
  value       = aws_cognito_user_pool.main.endpoint
}

################################################################################
# User Pool Client
################################################################################

output "client_id" {
  description = "ID of the Cognito user pool client"
  value       = aws_cognito_user_pool_client.main.id
}

output "client_secret" {
  description = "Secret of the Cognito user pool client"
  value       = aws_cognito_user_pool_client.main.client_secret
  sensitive   = true
}

################################################################################
# Domain
################################################################################

output "domain_url" {
  description = "URL of the Cognito custom domain"
  value       = aws_cognito_user_pool_domain.main.cloud_front_domain
}

output "domain_arn" {
  description = "ARN of the Cognito domain"
  value       = aws_cognito_user_pool_domain.main.arn
}

################################################################################
# Identity Pool
################################################################################

output "identity_pool_id" {
  description = "ID of the Cognito identity pool"
  value       = aws_cognito_identity_pool.main.id
}

output "identity_pool_arn" {
  description = "ARN of the Cognito identity pool"
  value       = aws_cognito_identity_pool.main.arn
}

################################################################################
# Auth URLs
################################################################################

output "login_url" {
  description = "URL for user login"
  value       = "https://${var.domain_name}/login"
}