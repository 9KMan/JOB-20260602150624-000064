################################################################################
# ECS Module Variables
################################################################################

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "product_name" {
  description = "Product name for resource naming"
  type        = string
}

variable "team_name" {
  description = "Team name for resource tagging"
  type        = string
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

################################################################################
# Network Configuration
################################################################################

variable "vpc_id" {
  description = "VPC ID for the ECS cluster"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for ECS tasks (private subnets)"
  type        = list(string)
}

variable "allowed_security_groups" {
  description = "List of security group IDs allowed to access ECS tasks"
  type        = list(string)
  default     = []
}

################################################################################
# Container Configuration
################################################################################

variable "container_name" {
  description = "Name of the container"
  type        = string
  default     = "premium-service-directory-api"
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8080
}

variable "container_image" {
  description = "Container image URL"
  type        = string
  default     = "nginx:latest"  # Placeholder - should be provided via tfvars
}

variable "task_cpu" {
  description = "CPU units for the task (1024 = 1 vCPU)"
  type        = number
  default     = 1024
}

variable "task_memory" {
  description = "Memory in MB for the task"
  type        = number
  default     = 2048
}

################################################################################
# Auto Scaling Configuration
################################################################################

variable "desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 2
}

variable "min_capacity" {
  description = "Minimum number of ECS tasks for autoscaling"
  type        = number
  default     = 2
}

variable "max_capacity" {
  description = "Maximum number of ECS tasks for autoscaling"
  type        = number
  default     = 10
}

variable "enable_autoscaling" {
  description = "Enable ECS autoscaling"
  type        = bool
  default     = true
}

################################################################################
# Load Balancer Configuration
################################################################################

variable "target_group_arn" {
  description = "ARN of the target group for the ECS service"
  type        = string
  default     = ""
}

################################################################################
# IAM Roles
################################################################################

variable "task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  type        = string
  default     = ""
}

variable "task_role_arn" {
  description = "ARN of the ECS task role"
  type        = string
  default     = ""
}

################################################################################
# CloudWatch Configuration
################################################################################

variable "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  type        = string
  default     = "/ecs/premium-service-directory/prod"
}

variable "log_retention_days" {
  description = "Log retention period in days"
  type        = number
  default     = 30
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "info"
}

################################################################################
# KMS Configuration
################################################################################

variable "kms_key_arn" {
  description = "KMS key ARN for encryption"
  type        = string
}

variable "secretsmanager_secret_arn" {
  description = "Secrets Manager secret ARN for credentials"
  type        = string
}

################################################################################
# S3 Configuration
################################################################################

variable "assets_bucket_arn" {
  description = "ARN of the assets S3 bucket"
  type        = string
  default     = ""
}

################################################################################
# Tags
################################################################################

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}