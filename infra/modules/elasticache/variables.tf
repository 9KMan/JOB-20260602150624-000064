################################################################################
# ElastiCache Module Variables
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
# Network Configuration
################################################################################

variable "vpc_id" {
  description = "VPC ID for the ElastiCache cluster"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for ElastiCache deployment"
  type        = list(string)
}

variable "allowed_security_groups" {
  description = "List of security group IDs allowed to access ElastiCache"
  type        = list(string)
  default     = []
}

################################################################################
# Redis Configuration
################################################################################

variable "node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.r6g.large"
}

variable "num_cache_nodes" {
  description = "Number of cache nodes in the cluster"
  type        = number
  default     = 2
}

variable "engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.0"
}

variable "port" {
  description = "Redis port"
  type        = number
  default     = 6379
}

################################################################################
# Backup Configuration
################################################################################

variable "snapshot_retention_limit" {
  description = "Number of days to retain snapshots"
  type        = number
  default     = 7
}

variable "snapshot_window" {
  description = "Preferred snapshot window in UTC"
  type        = string
  default     = "03:00-05:00"
}

variable "maintenance_window" {
  description = "Preferred maintenance window in UTC"
  type        = string
  default     = "mon:05:00-mon:07:00"
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