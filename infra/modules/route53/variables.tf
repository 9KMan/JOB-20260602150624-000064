################################################################################
# Route53 Module Variables
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
  description = "Domain name for the hosted zone"
  type        = string
}

variable "private_zone" {
  description = "Create a private hosted zone"
  type        = bool
  default     = false
}

variable "vpc_id" {
  description = "VPC ID to associate with private hosted zone"
  type        = string
  default     = ""
}

################################################################################
# ALB Configuration
################################################################################

variable "alb_dns_name" {
  description = "DNS name of the ALB"
  type        = string
  default     = ""
}

variable "alb_zone_id" {
  description = "Zone ID of the ALB"
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