################################################################################
# Secrets Manager Module Variables
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
# Secret Names
################################################################################

variable "db_credentials_secret_name" {
  description = "Name for the database credentials secret"
  type        = string
  default     = "premium-service-directory/db/credentials"
}

variable "auth0_secret_name" {
  description = "Name for the Auth0 credentials secret"
  type        = string
  default     = "premium-service-directory/auth0"
}

variable "api_keys_secret_name" {
  description = "Name for the API keys secret"
  type        = string
  default     = "premium-service-directory/api/keys"
}

################################################################################
# Encryption Configuration
################################################################################

variable "kms_key_id" {
  description = "KMS key ID for encryption"
  type        = string
}

################################################################################
# Rotation Configuration
################################################################################

variable "enable_secret_rotation" {
  description = "Enable automatic secret rotation"
  type        = bool
  default     = false
}

################################################################################
# Tags
################################################################################

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}