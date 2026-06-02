################################################################################
# S3 Module Variables
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
# Bucket Configuration
################################################################################

variable "assets_bucket_name" {
  description = "Name of the assets S3 bucket"
  type        = string
}

variable "logs_bucket_name" {
  description = "Name of the logs S3 bucket"
  type        = string
}

variable "backups_bucket_name" {
  description = "Name of the backups S3 bucket"
  type        = string
}

################################################################################
# Encryption Configuration
################################################################################

variable "kms_key_id" {
  description = "KMS key ID for encryption"
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