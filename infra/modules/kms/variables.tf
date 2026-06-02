################################################################################
# KMS Module Variables
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
# Key Administration
################################################################################

variable "key_administrators" {
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
# Key Configuration
################################################################################

variable "enable_key_rotation" {
  description = "Enable automatic key rotation"
  type        = bool
  default     = true
}

################################################################################
# Tags
################################################################################

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}