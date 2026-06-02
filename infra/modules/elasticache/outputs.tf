################################################################################
# ElastiCache Module Outputs
################################################################################

output "cluster_id" {
  description = "ID of the ElastiCache cluster"
  value       = aws_elasticache_replication_group.main.id
}

output "cluster_arn" {
  description = "ARN of the ElastiCache cluster"
  value       = aws_elasticache_replication_group.main.arn
}

output "configuration_endpoint" {
  description = "Configuration endpoint of the ElastiCache cluster"
  value       = aws_elasticache_replication_group.main.configuration_endpoint.address
}

output "port" {
  description = "Port of the ElastiCache cluster"
  value       = aws_elasticache_replication_group.main.port
}

output "security_group_id" {
  description = "Security group ID of the ElastiCache cluster"
  value       = aws_security_group.elasticache.id
}

output "redis_nodes" {
  description = "List of Redis node addresses"
  value       = aws_elasticache_replication_group.main.cache_nodes
}

output "subnet_group_name" {
  description = "Name of the ElastiCache subnet group"
  value       = aws_elasticache_subnet_group.main.name
}