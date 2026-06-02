################################################################################
# Terraform Variables for Premium Service Directory Platform
################################################################################

################################################################################
# AWS Configuration
################################################################################

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "aws_access_key" {
  description = "AWS access key for provider authentication (leave empty for instance role)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "aws_secret_key" {
  description = "AWS secret key for provider authentication (leave empty for instance role)"
  type        = string
  sensitive   = true
  default     = ""
}

################################################################################
# Environment and Product Configuration
################################################################################

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "product_name" {
  description = "Product name for resource naming"
  type        = string
  default     = "premium-service-directory"
}

variable "team_name" {
  description = "Team name for resource tagging"
  type        = string
  default     = "platform-team"
}

################################################################################
# Tags Configuration
################################################################################

variable "tags" {
  description = "Default tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "prod"
    Product     = "premium-service-directory"
    Team        = "platform-team"
    ManagedBy   = "terraform"
    Compliance  = "soc2"
  }
}

################################################################################
# VPC Configuration
################################################################################

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones for the VPC"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

################################################################################
# KMS Configuration
################################################################################

variable "kms_key_administrators" {
  description = "IAM principals who can administer the KMS keys"
  type        = list(string)
  default     = []
}

variable "kms_key_users" {
  description = "IAM principals who can use the KMS keys for encryption/decryption"
  type        = list(string)
  default     = []
}

################################################################################
# RDS Configuration
################################################################################

variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "premium_directory"
}

variable "db_username" {
  description = "Master username for PostgreSQL"
  type        = string
  default     = "dbadmin"
}

variable "db_port" {
  description = "PostgreSQL port"
  type        = number
  default     = 5432
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.xlarge"
}

variable "db_allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 100
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage in GB for autoscaling"
  type        = number
  default     = 500
}

variable "db_multi_az" {
  description = "Enable multi-AZ deployment"
  type        = bool
  default     = true
}

variable "db_backup_retention_period" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "db_backup_window" {
  description = "Preferred backup window in UTC"
  type        = string
  default     = "03:00-04:00"
}

variable "db_maintenance_window" {
  description = "Preferred maintenance window in UTC"
  type        = string
  default     = "mon:04:00-mon:05:00"
}

variable "enable_pgbouncer" {
  description = "Enable PGBouncer connection pooling"
  type        = bool
  default     = true
}

variable "pgbouncer_pool_size" {
  description = "PGBouncer pool size per connection"
  type        = number
  default     = 20
}

################################################################################
# ECS Configuration
################################################################################

variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 2
}

variable "ecs_min_capacity" {
  description = "Minimum number of ECS tasks for autoscaling"
  type        = number
  default     = 2
}

variable "ecs_max_capacity" {
  description = "Maximum number of ECS tasks for autoscaling"
  type        = number
  default     = 10
}

variable "ecs_autoscaling_enabled" {
  description = "Enable ECS autoscaling"
  type        = bool
  default     = true
}

################################################################################
# Redis/ElastiCache Configuration
################################################################################

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.r6g.large"
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes in the cluster"
  type        = number
  default     = 2
}

variable "redis_engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.0"
}

variable "redis_port" {
  description = "Redis port"
  type        = number
  default     = 6379
}

################################################################################
# Domain and DNS Configuration
################################################################################

variable "domain_name" {
  description = "Primary domain name for the application"
  type        = string
  default     = "premiumservicedirectory.com"
}

################################################################################
# Cognito Configuration
################################################################################

variable "cognito_domain_name" {
  description = "Cognito custom domain prefix"
  type        = string
  default     = "premium-service-directory-auth"
}

variable "cognito_callback_urls" {
  description = "OAuth callback URLs"
  type        = list(string)
  default = [
    "https://premiumservicedirectory.com/api/auth/callback",
    "https://premiumservicedirectory.com/api/auth/callback?prompt=consent"
  ]
}

variable "cognito_logout_urls" {
  description = "OAuth logout URLs"
  type        = list(string)
  default = [
    "https://premiumservicedirectory.com/api/auth/logout"
  ]
}

################################################################################
# CloudWatch Configuration
################################################################################

variable "cloudwatch_log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 30
}

variable "alarm_email" {
  description = "Email address for CloudWatch alarm notifications"
  type        = string
  default     = "platform-alerts@premiumservicedirectory.com"
}