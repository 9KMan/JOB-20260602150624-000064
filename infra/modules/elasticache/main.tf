################################################################################
# ElastiCache Module - Redis Cluster with Encryption
################################################################################

resource "aws_security_group" "elasticache" {
  name        = "${var.environment}-${var.product_name}-elasticache-sg"
  description = "Security group for ElastiCache Redis cluster"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = var.port
    to_port         = var.port
    protocol        = "tcp"
    security_groups = var.allowed_security_groups
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.environment}-${var.product_name}-elasticache-subnet-group"
  subnet_ids = var.subnet_ids
}

resource "aws_elasticache_parameter_group" "main" {
  name        = "${var.environment}-${var.product_name}-redis-params"
  family      = "redis7"
  description = "Redis parameter group for ${var.environment} environment"

  parameter {
    name  = "tls_enabled"
    value = "yes"
  }

  parameter {
    name  = "transit_encryption_mode"
    value = "required"
  }
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.environment}-${var.product_name}-redis"
  engine                     = "redis"
  engine_version             = var.engine_version
  parameter_group_name       = aws_elasticache_parameter_group.main.name
  node_type                  = var.node_type
  num_cache_clusters         = var.num_cache_nodes
  port                      = var.port
  subnet_group_name         = aws_elasticache_subnet_group.main.name
  security_group_ids        = [aws_security_group.elasticache.id]
  at_rest_encryption_enabled = true
  kms_key_id                = var.kms_key_id
  transit_encryption_enabled = true
  snapshot_retention_limit   = var.snapshot_retention_limit
  snapshot_window           = var.snapshot_window
  automatic_failover_enabled = true
  maintenance_window        = var.maintenance_window
}

resource "aws_cloudwatch_log_group" "redis" {
  name              = "/aws/elasticache/${var.environment}-${var.product_name}-redis"
  retention_in_days = 30
}