################################################################################
# CloudWatch Module Variables
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
# Log Configuration
################################################################################

variable "log_group_name" {
  description = "Name of the CloudWatch log group"
  type        = string
  default     = "/ecs/premium-service-directory/prod"
}

variable "log_retention_days" {
  description = "Log retention period in days"
  type        = number
  default     = 30
}

variable "kms_key_id" {
  description = "KMS key ID for log encryption"
  type        = string
  default     = ""
}

################################################################################
# Alarm Configuration
################################################################################

variable "alarm_email" {
  description = "Email address for CloudWatch alarm notifications"
  type        = string
}

################################################################################
# ECS Configuration
################################################################################

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
  default     = ""
}

################################################################################
# RDS Configuration
################################################################################

variable "rds_db_instance_id" {
  description = "RDS DB instance identifier"
  type        = string
  default     = ""
}

################################################################################
# ALB Configuration
################################################################################

variable "alb_arn" {
  description = "ARN of the ALB"
  type        = string
  default     = ""
}

variable "alb_target_group_arn" {
  description = "ARN of the ALB target group"
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