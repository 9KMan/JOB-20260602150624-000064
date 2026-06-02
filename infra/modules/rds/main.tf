################################################################################
# RDS Module - PostgreSQL Database with Encryption at Rest
# Multi-AZ deployment with PGBouncer for connection pooling
################################################################################

################################################################################
# Data Sources
################################################################################

data "aws_vpc" "main" {
  id = var.vpc_id
}

data "aws_subnet" "private" {
  count = length(var.subnet_ids)
  id    = var.subnet_ids[count.index]
}

################################################################################
# Security Group for RDS
################################################################################

resource "aws_security_group" "rds" {
  name        = "${var.environment}-${var.product_name}-rds-sg"
  description = "Security group for RDS PostgreSQL instance"
  vpc_id      = var.vpc_id

  # Allow PostgreSQL from ECS security group only
  ingress {
    from_port       = var.db_port
    to_port         = var.db_port
    protocol        = "tcp"
    security_groups = var.allowed_security_groups
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-rds-sg"
      Type = "security-group"
    }
  )
}

################################################################################
# RDS Subnet Group
################################################################################

resource "aws_db_subnet_group" "main" {
  name       = "${var.environment}-${var.product_name}-db-subnet-group"
  description = "Subnet group for RDS PostgreSQL instance"

  # Deploy RDS in private subnets across multiple AZs
  subnet_ids = var.subnet_ids

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-db-subnet-group"
      Type = "db-subnet-group"
    }
  )
}

################################################################################
# RDS Option Group - PostgreSQL features
################################################################################

resource "aws_db_option_group" "main" {
  name_prefix = "${var.environment}-${var.product_name}-pg"

  # PostgreSQL engine
  engine_name = "postgres"

  # PostgreSQL 15 major version
  major_engine_version = "15"

  # Option group settings
  option_group_description = "Option group for PostgreSQL ${var.engine_version}"

  # TDE (Transparent Data Encryption) is handled at the storage level with KMS
  # No additional options needed for basic encryption

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-db-option-group"
      Type = "db-option-group"
    }
  )
}

################################################################################
# RDS Parameter Group - PostgreSQL configuration
################################################################################

resource "aws_db_parameter_group" "main" {
  name_prefix = "${var.environment}-${var.product_name}-pg"

  # PostgreSQL 15
  family = "postgres15"

  # Parameter group description
  description = "Parameter group for PostgreSQL ${var.engine_version}"

  # PostgreSQL parameters for production workloads
  parameter {
    name  = "max_connections"
    value = "500"
  }

  parameter {
    name  = "shared_buffers"
    value = "256MB"
  }

  parameter {
    name  = "effective_cache_size"
    value = "768MB"
  }

  parameter {
    name  = "maintenance_work_mem"
    value = "256MB"
  }

  parameter {
    name  = "checkpoint_completion_target"
    value = "0.9"
  }

  parameter {
    name  = "wal_buffers"
    value = "16MB"
  }

  parameter {
    name  = "default_statistics_target"
    value = "100"
  }

  parameter {
    name  = "random_page_cost"
    value = "1.1"
  }

  parameter {
    name  = "effective_io_concurrency"
    value = "200"
  }

  parameter {
    name  = "work_mem"
    value = "4MB"
  }

  parameter {
    name  = "min_wal_size"
    value = "1GB"
  }

  parameter {
    name  = "max_wal_size"
    value = "4GB"
  }

  parameter {
    name  = "log_destination"
    value = "stderr"
  }

  parameter {
    name  = "logging_collector"
    value = "1"
  }

  parameter {
    name  = "log_directory"
    value = "log"
  }

  parameter {
    name  = "log_filename"
    value = "postgresql.log.%Y-%m-%d"
  }

  parameter {
    name  = "log_rotation_age"
    value = "1d"
  }

  parameter {
    name  = "log_rotation_size"
    value = "100MB"
  }

  parameter {
    name  = "log_line_prefix"
    value = "%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h "
  }

  parameter {
    name  = "log_timezone"
    value = "UTC"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-db-parameter-group"
      Type = "db-parameter-group"
    }
  )
}

################################################################################
# KMS Policy for RDS - Allow RDS to use the KMS key for encryption
################################################################################

data "aws_iam_policy_document" "rds_kms_policy" {
  statement {
    sid = "AllowRDSEncryption"

    actions = [
      "kms:CreateGrant",
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:DescribeKey",
    ]

    resources = [var.kms_key_id]

    # RDS service principal must be allowed
    principals {
      type = "Service"
      identifiers = ["rds.amazonaws.com"]
    }
  }

  statement {
    sid = "AllowKMSKeyUsage"

    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:DescribeKey",
    ]

    resources = [var.kms_key_id]

    # Allow ECS tasks to access the key for secret rotation
    principals {
      type = "AWS"
      identifiers = var.kms_key_users
    }
  }
}

resource "aws_kms_key_policy" "rds" {
  key_id = var.kms_key_id
  policy = data.aws_iam_policy_document.rds_kms_policy.json
}

################################################################################
# RDS Instance - PostgreSQL with Encryption at Rest
################################################################################

resource "aws_db_instance" "main" {
  # Instance identifier
  identifier = "${var.environment}-${var.product_name}-db"

  # Database engine and version
  engine               = "postgres"
  engine_version       = var.engine_version

  # Instance class - determines compute and memory capacity
  instance_class = var.db_instance_class

  # Storage configuration
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type         = "gp3"  # General Purpose SSD v3
  iops                 = var.db_iops
  storage_encrypted    = true   # Encryption at rest enabled

  # KMS key for storage encryption
  kms_key_id = var.kms_key_id

  # Database name and credentials
  db_name  = var.db_name
  username = var.db_username
  port     = var.db_port

  # Multi-AZ deployment for high availability
  multi_az = var.multi_az

  # PostgreSQL parameters
  parameter_group_name   = aws_db_parameter_group.main.name
  option_group_name      = aws_db_option_group.main.name
  publicly_accessible    = false  # Always private, no public access
  db_subnet_group_name   = aws_db_subnet_group.main.name

  # Security group - only allow access from ECS
  vpc_security_group_ids = [aws_security_group.rds.id]

  # Backup configuration
  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  backup_target          = "region"  # Backup to another region for disaster recovery

  # Maintenance window
  maintenance_window      = var.maintenance_window
  auto_minor_version_upgrade = true
  allow_major_version_upgrade = false  # Prevent automatic major version upgrades

  # Deletion protection for production
  deletion_protection = var.deletion_protection

  # Copy tags to snapshots for better tracking
  copy_tags_to_snapshot = true
  snapshot_identifier   = var.snapshot_identifier  # Optional: restore from snapshot

  # Performance insights for monitoring
  performance_insights_enabled        = true
  performance_insights_retention_period = 7  # 7 days for production
  performance_insights_kms_key_id    = var.kms_key_id

  # Monitoring
  monitoring_interval = 60  # Enhanced monitoring every 60 seconds
  monitoring_role_arn  = aws_iam_role.rds_monitoring.arn

  # Log exports
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  # Timezone
  timezone = "UTC"

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-db-instance"
      Type = "db-instance"
    }
  )
}

################################################################################
# RDS Monitoring Role - For enhanced monitoring
################################################################################

resource "aws_iam_role" "rds_monitoring" {
  name = "${var.environment}-${var.product_name}-rds-monitoring-role"

  # Role trusts the RDS service
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-rds-monitoring-role"
      Type = "iam-role"
    }
  )
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

################################################################################
# PGBouncer - Connection Pooler for PostgreSQL
################################################################################

resource "aws_lb" "pgbouncer" {
  name               = "${var.environment}-${var.product_name}-pgbouncer"
  internal           = true  # Internal load balancer for connection pooling
  load_balancer_type = "network"

  # Deploy in private subnets
  subnets = var.subnet_ids

  # Enable deletion protection in production
  enable_deletion_protection = var.deletion_protection

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-pgbouncer"
      Type = "load-balancer"
    }
  )
}

resource "aws_lb_target_group" "pgbouncer" {
  name     = "${var.environment}-${var.product_name}-pgbouncer-tg"
  port     = 5432
  protocol = "TCP"
  vpc_id   = var.vpc_id

  # Health check on the PostgreSQL port
  health_check {
    protocol            = "TCP"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-pgbouncer-tg"
      Type = "target-group"
    }
  )
}

resource "aws_lb_listener" "pgbouncer" {
  load_balancer_arn = aws_lb.pgbouncer.arn
  port              = 5432
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.pgbouncer.arn
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-pgbouncer-listener"
      Type = "lb-listener"
    }
  )
}

# PGBouncer security group
resource "aws_security_group" "pgbouncer" {
  name        = "${var.environment}-${var.product_name}-pgbouncer-sg"
  description = "Security group for PGBouncer connection pooler"
  vpc_id      = var.vpc_id

  # Allow PostgreSQL port from ECS security group
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = var.allowed_security_groups
  }

  # Allow the load balancer to send traffic to PGBouncer
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.pgbouncer.id]
  }

  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-pgbouncer-sg"
      Type = "security-group"
    }
  )
}

################################################################################
# Secrets Manager Integration for DB Credentials
################################################################################

resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = var.db_credentials_secret_name
  description              = "Database credentials for ${var.product_name}"
  kms_key_id              = var.kms_key_id
  recovery_window_in_days  = 7  # Must wait 7 days before permanent deletion

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-db-credentials"
      Type = "secret"
    }
  )
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id

  # Store credentials as JSON
  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password  # This should be passed as a sensitive variable
    host     = aws_db_instance.main.endpoint
    port     = aws_db_instance.main.port
    dbname   = var.db_name
    engine   = "postgres"
  })
}

################################################################################
# Readme: DB credentials are managed through Secrets Manager
# The actual password should be provided through terraform.tfvars or environment
################################################################################