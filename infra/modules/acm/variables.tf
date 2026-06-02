################################################################################
# ACM Module Variables
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
# Domain Configuration
################################################################################

variable "domain_name" {
  description = "Primary domain name for the certificate"
  type        = string
}

variable "subject_alternative_names" {
  description = "List of SANs (Subject Alternative Names) for the certificate"
  type        = list(string)
  default     = []
}

variable "hosted_zone_id" {
  description = "Route53 hosted zone ID for DNS validation"
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