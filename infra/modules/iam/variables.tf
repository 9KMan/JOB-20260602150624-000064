################################################################################
# IAM Module Variables
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

################################################################################
# KMS Configuration
################################################################################

variable "kms_key_arn" {
  description = "KMS key ARN for policies"
  type        = string
}

################################################################################
# Secrets Manager Configuration
################################################################################

variable "secretsmanager_secret_arn" {
  description = "Secrets Manager secret ARN for policies"
  type        = string
}

################################################################################
# S3 Configuration
################################################################################

variable "assets_bucket_arn" {
  description = "ARN of the assets S3 bucket"
  type        = string
}

variable "logs_bucket_arn" {
  description = "ARN of the logs S3 bucket"
  type        = string
}

################################################################################
# Tags
################################################################################

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}