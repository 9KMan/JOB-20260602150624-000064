################################################################################
# RDS Module Variables
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
  description = "VPC ID for the RDS instance"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for RDS deployment (private subnets)"
  type        = list(string)
}

variable "allowed_security_groups" {
  description = "List of security group IDs allowed to access RDS"
  type        = list(string)
  default     = []
}

################################################################################
# Database Configuration
################################################################################

variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "premium_directory"
}

variable "db_username" {
  description = "Master username for PostgreSQL"
  type        = string
  default     = "dbadmin"
}

variable "db_password" {
  description = "Master password for PostgreSQL (should be passed via tfvars or env)"
  type        = string
  sensitive   = true
  default     = ""  # Must be provided in terraform.tfvars
}

variable "db_port" {
  description = "PostgreSQL port"
  type        = number
  default     = 5432
}

variable "engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.4"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.xlarge"
}

variable "db_allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 100
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage in GB for autoscaling"
  type        = number
  default     = 500
}

variable "db_iops" {
  description = "Provisioned IOPS for storage (gp3 supports up to 16,000)"
  type        = number
  default     = 3000
}

variable "multi_az" {
  description = "Enable multi-AZ deployment"
  type        = bool
  default     = true
}

################################################################################
# Backup Configuration
################################################################################

variable "backup_retention_period" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "backup_window" {
  description = "Preferred backup window in UTC"
  type        = string
  default     = "03:00-04:00"
}

################################################################################
# Maintenance Configuration
################################################################################

variable "maintenance_window" {
  description = "Preferred maintenance window in UTC"
  type        = string
  default     = "mon:04:00-mon:05:00"
}

################################################################################
# Encryption Configuration
################################################################################

variable "kms_key_id" {
  description = "KMS key ID for encryption at rest"
  type        = string
}

variable "kms_key_users" {
  description = "IAM principals who can use the KMS key"
  type        = list(string)
  default     = []
}

################################################################################
# PGBouncer Configuration
################################################################################

variable "enable_pgbouncer" {
  description = "Enable PGBouncer connection pooling"
  type        = bool
  default     = true
}

variable "pgbouncer_pool_size" {
  description = "PGBouncer pool size per connection"
  type        = number
  default     = 20
}

################################################################################
# Deletion Protection
################################################################################

variable "deletion_protection" {
  description = "Enable deletion protection for RDS instance"
  type        = bool
  default     = true
}

################################################################################
# Snapshot Configuration
################################################################################

variable "snapshot_identifier" {
  description = "Optional snapshot identifier to restore from"
  type        = string
  default     = null
}

################################################################################
# Secrets Manager
################################################################################

variable "db_credentials_secret_name" {
  description = "Name for the database credentials secret"
  type        = string
  default     = "premium-service-directory/db/credentials"
}

################################################################################
# Tags
################################################################################

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}