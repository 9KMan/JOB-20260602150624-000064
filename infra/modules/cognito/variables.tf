################################################################################
# Cognito Module Variables
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
# Domain Configuration
################################################################################

variable "domain_name" {
  description = "Cognito custom domain prefix"
  type        = string
}

variable "certificate_arn" {
  description = "ACM certificate ARN for custom domain"
  type        = string
  default     = ""
}

################################################################################
# OAuth Configuration
################################################################################

variable "callback_urls" {
  description = "OAuth callback URLs"
  type        = list(string)
  default     = []
}

variable "logout_urls" {
  description = "OAuth logout URLs"
  type        = list(string)
  default     = []
}

################################################################################
# Encryption
################################################################################

variable "kms_key_id" {
  description = "KMS key ID for encryption"
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