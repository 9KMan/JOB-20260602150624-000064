################################################################################
# RDS Module Outputs
################################################################################

################################################################################
# RDS Instance Information
################################################################################

output "db_instance_id" {
  description = "ID of the RDS instance"
  value       = aws_db_instance.main.id
}

output "db_instance_arn" {
  description = "ARN of the RDS instance"
  value       = aws_db_instance.main.arn
}

output "db_endpoint" {
  description = "Endpoint of the RDS PostgreSQL instance"
  value       = aws_db_instance.main.endpoint
}

output "db_port" {
  description = "Port of the RDS PostgreSQL instance"
  value       = aws_db_instance.main.port
}

output "db_name" {
  description = "Name of the database"
  value       = aws_db_instance.main.db_name
}

output "db_instance_class" {
  description = "Instance class of the RDS instance"
  value       = aws_db_instance.main.instance_class
}

################################################################################
# Security Group
################################################################################

output "security_group_id" {
  description = "Security group ID of the RDS instance"
  value       = aws_security_group.rds.id
}

################################################################################
# PGBouncer Information
################################################################################

output "pgbouncer_enabled" {
  description = "Whether PGBouncer is enabled"
  value       = var.enable_pgbouncer
}

output "pgbouncer_endpoint" {
  description = "Endpoint of the PGBouncer connection pooler"
  value       = var.enable_pgbouncer ? aws_lb.pgbouncer.dns_name : ""
}

output "pgbouncer_port" {
  description = "Port of the PGBouncer connection pooler"
  value       = var.enable_pgbouncer ? 5432 : 0
}

output "pgbouncer_target_group_arn" {
  description = "ARN of the PGBouncer target group"
  value       = var.enable_pgbouncer ? aws_lb_target_group.pgbouncer.arn : ""
}

################################################################################
# Secrets Manager
################################################################################

output "db_credentials_secret_id" {
  description = "ID of the database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.id
}

output "db_credentials_secret_arn" {
  description = "ARN of the database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

################################################################################
# Connection Information
################################################################################

output "connection_string" {
  description = "PostgreSQL connection string"
  value       = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.endpoint}:${aws_db_instance.main.port}/${var.db_name}"
  sensitive   = true
}

################################################################################
# Backup Information
################################################################################

output "latest_restorable_time" {
  description = "Latest restorable time of the database"
  value       = aws_db_instance.main.latest_restorable_time
}

output "backup_retention_period" {
  description = "Backup retention period in days"
  value       = aws_db_instance.main.backup_retention_period
}

################################################################################
# Multi-AZ Information
################################################################################

output "multi_az" {
  description = "Whether Multi-AZ is enabled"
  value       = aws_db_instance.main.multi_az
}

output "secondary_availability_zone" {
  description = "Secondary availability zone for Multi-AZ"
  value       = aws_db_instance.main.secondary_availability_zone
}

################################################################################
# Monitoring
################################################################################

output "monitoring_role_arn" {
  description = "ARN of the RDS monitoring role"
  value       = aws_iam_role.rds_monitoring.arn
}

################################################################################
# Storage Information
################################################################################

output "allocated_storage" {
  description = "Allocated storage in GB"
  value       = aws_db_instance.main.allocated_storage
}

output "storage_encrypted" {
  description = "Whether storage is encrypted"
  value       = aws_db_instance.main.storage_encrypted
}

output "kms_key_id" {
  description = "KMS key ID used for storage encryption"
  value       = aws_db_instance.main.kms_key_id
}