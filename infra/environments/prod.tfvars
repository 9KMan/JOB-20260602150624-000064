################################################################################
# Production Environment Variables for Premium Service Directory
################################################################################

# AWS Configuration
aws_region = "us-east-1"

# Environment
environment  = "prod"
product_name = "premium-service-directory"
team_name    = "platform-team"

# Tags
tags = {
  Environment = "prod"
  Product     = "premium-service-directory"
  Team        = "platform-team"
  ManagedBy   = "terraform"
  Compliance  = "soc2"
  CostCenter  = "platform-services"
  Project     = "premium-service-directory"
}

################################################################################
# VPC Configuration - Production High-Availability Setup
################################################################################

vpc_cidr = "10.0.0.0/16"

availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]

private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]

################################################################################
# KMS Configuration - Production Key Management
################################################################################

kms_key_administrators = [
  "arn:aws:iam::123456789012:role/prod-platform-admin",
  "arn:aws:iam::123456789012:user/prod-security-admin"
]

kms_key_users = [
  "arn:aws:iam::123456789012:role/prod-ecs-task-execution-role",
  "arn:aws:iam::123456789012:role/prod-rds-encryption-role",
  "arn:aws:iam::123456789012:role/prod-secrets-manager-role"
]

################################################################################
# RDS Configuration - Production PostgreSQL
################################################################################

db_name     = "premium_directory"
db_username = "psdadmin"
db_port     = 5432

# Production instance - r6g.xlarge with 100GB storage, scalable to 500GB
db_instance_class        = "db.r6g.xlarge"
db_allocated_storage     = 100
db_max_allocated_storage = 500
db_multi_az              = true

# Enhanced backup retention for production
backup_retention_period = 14
backup_window           = "02:00-03:00"
maintenance_window      = "sun:04:00-sun:05:00"

# PGBouncer connection pooling for production
enable_pgbouncer    = true
pgbouncer_pool_size = 25

################################################################################
# ECS Configuration - Production Fargate Cluster
################################################################################

# Production auto-scaling configuration
ecs_desired_count       = 3
ecs_min_capacity        = 2
ecs_max_capacity        = 15
ecs_autoscaling_enabled = true

################################################################################
# Redis/ElastiCache Configuration - Production Cluster
################################################################################

# Production Redis configuration - r6g.large nodes, 2 replicas
redis_node_type       = "cache.r6g.large"
redis_num_cache_nodes = 3
redis_engine_version  = "7.0"
redis_port            = 6379

################################################################################
# Domain Configuration
################################################################################

domain_name = "premiumservicedirectory.com"

################################################################################
# Cognito Configuration - Production User Pool
################################################################################

cognito_domain_name = "premium-service-directory-prod"

cognito_callback_urls = [
  "https://premiumservicedirectory.com/api/auth/callback",
  "https://premiumservicedirectory.com/api/auth/callback?prompt=consent"
]

cognito_logout_urls = [
  "https://premiumservicedirectory.com/api/auth/logout"
]

################################################################################
# CloudWatch Configuration - Production Monitoring
################################################################################

# Longer retention for production logs (30 days)
cloudwatch_log_retention_days = 30
alarm_email                   = "prod-platform-alerts@premiumservicedirectory.com"