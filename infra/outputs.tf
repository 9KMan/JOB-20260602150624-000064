################################################################################
# Terraform Outputs for Premium Service Directory Platform
################################################################################

################################################################################
# VPC Outputs
################################################################################

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.vpc.private_subnet_ids
}

output "availability_zones" {
  description = "List of availability zones"
  value       = module.vpc.availability_zones
}

################################################################################
# KMS Outputs
################################################################################

output "kms_key_id" {
  description = "ID of the KMS key used for encryption"
  value       = module.kms.key_id
}

output "kms_key_arn" {
  description = "ARN of the KMS key used for encryption"
  value       = module.kms.key_arn
}

output "kms_key_alias" {
  description = "Alias of the KMS key"
  value       = module.kms.key_alias
}

################################################################################
# Secrets Manager Outputs
################################################################################

output "db_credentials_secret_arn" {
  description = "ARN of the database credentials secret"
  value       = module.secretsmanager.db_credentials_secret_arn
}

output "auth0_secret_arn" {
  description = "ARN of the Auth0 credentials secret"
  value       = module.secretsmanager.auth0_secret_arn
}

output "api_keys_secret_arn" {
  description = "ARN of the API keys secret"
  value       = module.secretsmanager.api_keys_secret_arn
}

################################################################################
# RDS Outputs
################################################################################

output "rds_endpoint" {
  description = "Endpoint of the RDS PostgreSQL instance"
  value       = module.rds.db_endpoint
}

output "rds_port" {
  description = "Port of the RDS PostgreSQL instance"
  value       = module.rds.db_port
}

output "rds_db_name" {
  description = "Name of the database"
  value       = module.rds.db_name
}

output "rds_security_group_id" {
  description = "Security group ID of the RDS instance"
  value       = module.rds.security_group_id
}

output "pgbouncer_endpoint" {
  description = "Endpoint of the PGBouncer connection pooler"
  value       = module.rds.pgbouncer_endpoint
}

output "pgbouncer_port" {
  description = "Port of the PGBouncer connection pooler"
  value       = module.rds.pgbouncer_port
}

################################################################################
# ECS Outputs
################################################################################

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs.ecs_cluster_name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = module.ecs.ecs_cluster_arn
}

output "ecs_task_definition_arn" {
  description = "ARN of the ECS task definition"
  value       = module.ecs.task_definition_arn
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = module.ecs.service_name
}

output "ecs_security_group_id" {
  description = "Security group ID of the ECS tasks"
  value       = module.ecs.security_group_id
}

output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = module.ecs.task_execution_role_arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = module.ecs.task_role_arn
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = module.ecs.cloudwatch_log_group_name
}

################################################################################
# ALB Outputs
################################################################################

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = module.alb.alb_zone_id
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = module.alb.alb_arn
}

output "alb_target_group_arn" {
  description = "ARN of the ALB target group"
  value       = module.alb.target_group_arn
}

output "https_listener_arn" {
  description = "ARN of the HTTPS listener"
  value       = module.alb.https_listener_arn
}

output "alb_security_group_id" {
  description = "Security group ID of the ALB"
  value       = module.alb.security_group_id
}

################################################################################
# ACM Outputs
################################################################################

output "acm_certificate_arn" {
  description = "ARN of the ACM certificate"
  value       = module.acm.certificate_arn
}

output "acm_certificate_domain_validation_options" {
  description = "Domain validation options for the ACM certificate"
  value       = module.acm.certificate_domain_validation_options
}

################################################################################
# S3 Outputs
################################################################################

output "assets_bucket_name" {
  description = "Name of the assets S3 bucket"
  value       = module.s3.assets_bucket_name
}

output "assets_bucket_arn" {
  description = "ARN of the assets S3 bucket"
  value       = module.s3.assets_bucket_arn
}

output "logs_bucket_name" {
  description = "Name of the logs S3 bucket"
  value       = module.s3.logs_bucket_name
}

output "logs_bucket_arn" {
  description = "ARN of the logs S3 bucket"
  value       = module.s3.logs_bucket_arn
}

output "backups_bucket_name" {
  description = "Name of the backups S3 bucket"
  value       = module.s3.backups_bucket_name
}

output "backups_bucket_arn" {
  description = "ARN of the backups S3 bucket"
  value       = module.s3.backups_bucket_arn
}

################################################################################
# ElastiCache Outputs
################################################################################

output "redis_cluster_id" {
  description = "ID of the ElastiCache cluster"
  value       = module.elasticache.cluster_id
}

output "redis_configuration_endpoint" {
  description = "Configuration endpoint of the ElastiCache cluster"
  value       = module.elasticache.configuration_endpoint
}

output "redis_port" {
  description = "Port of the ElastiCache cluster"
  value       = module.elasticache.port
}

output "redis_security_group_id" {
  description = "Security group ID of the ElastiCache cluster"
  value       = module.elasticache.security_group_id
}

################################################################################
# Cognito Outputs
################################################################################

output "cognito_user_pool_id" {
  description = "ID of the Cognito user pool"
  value       = module.cognito.user_pool_id
}

output "cognito_user_pool_arn" {
  description = "ARN of the Cognito user pool"
  value       = module.cognito.user_pool_arn
}

output "cognito_client_id" {
  description = "ID of the Cognito user pool client"
  value       = module.cognito.client_id
}

output "cognito_client_secret" {
  description = "Secret of the Cognito user pool client"
  value       = module.cognito.client_secret
  sensitive   = true
}

output "cognito_domain_url" {
  description = "URL of the Cognito custom domain"
  value       = module.cognito.domain_url
}

################################################################################
# Route53 Outputs
################################################################################

output "route53_hosted_zone_id" {
  description = "ID of the Route53 hosted zone"
  value       = module.route53.hosted_zone_id
}

output "route53_zone_name" {
  description = "Name of the Route53 hosted zone"
  value       = module.route53.zone_name
}

################################################################################
# IAM Outputs
################################################################################

output "ecs_task_execution_role_name" {
  description = "Name of the ECS task execution role"
  value       = module.iam.ecs_task_execution_role_name
}

output "ecs_task_role_name" {
  description = "Name of the ECS task role"
  value       = module.iam.ecs_task_role_name
}

################################################################################
# CloudWatch Outputs
################################################################################

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = module.cloudwatch.log_group_name
}

output "cloudwatch_dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value       = module.cloudwatch.dashboard_url
}

################################################################################
# GuardDuty Outputs
################################################################################

output "guardduty_detector_id" {
  description = "ID of the GuardDuty detector"
  value       = module.guardduty.detector_id
}

################################################################################
# Platform URLs
################################################################################

output "platform_url" {
  description = "URL of the platform"
  value       = "https://${var.domain_name}"
}

output "api_url" {
  description = "URL of the API"
  value       = "https://api.${var.domain_name}"
}

output "cognito_login_url" {
  description = "URL for Cognito user login"
  value       = "https://${module.cognito.domain_url}/login"
}

output "cognito_signup_url" {
  description = "URL for Cognito user signup"
  value       = "https://${module.cognito.domain_url}/signup"
}