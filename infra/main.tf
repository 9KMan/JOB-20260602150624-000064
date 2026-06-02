################################################################################
# Terraform Version and Provider Requirements
################################################################################

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.30"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  # Backend configuration - S3 with DynamoDB for state locking
  backend "s3" {
    bucket         = "premium-service-directory-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

################################################################################
# AWS Provider Configuration
################################################################################

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = var.tags
  }

  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

################################################################################
# Data Sources
################################################################################

data "aws_caller_identity" "current" {}

data "aws_partition" "current" {}

data "aws_region" "current" {}

################################################################################
# KMS Module - Encryption Keys
################################################################################

module "kms" {
  source = "./modules/kms"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # Key administrators - IAM roles that can manage key policies
  key_administrators = var.kms_key_administrators

  # Key users - services that will use the keys for encryption/decryption
  kms_key_users = concat(
    var.kms_key_users,
    [module.ecs.task_execution_role_arn] # ECS tasks need access to KMS for Secrets Manager
  )

  # Enable key rotation
  enable_key_rotation = true

  tags = var.tags
}

################################################################################
# Secrets Manager Module - Secure Storage for Credentials
################################################################################

module "secretsmanager" {
  source = "./modules/secretsmanager"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # Use the KMS key for encryption
  kms_key_id = module.kms.key_id

  # Secret names for various credentials
  db_credentials_secret_name = "premium-service-directory/db/credentials"
  auth0_secret_name = "premium-service-directory/auth0"
  api_keys_secret_name = "premium-service-directory/api/keys"

  tags = var.tags
}

################################################################################
# VPC Module - Network Infrastructure
################################################################################

module "vpc" {
  source = "./modules/vpc"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # VPC CIDR block
  vpc_cidr = var.vpc_cidr

  # Availability zones for multi-AZ deployment
  availability_zones = var.availability_zones

  # Public subnets - for ALB, NAT Gateways
  public_subnet_cidrs = var.public_subnet_cidrs

  # Private subnets - for ECS tasks, RDS, ElastiCache, Redis
  private_subnet_cidrs = var.private_subnet_cidrs

  # Single_nat_gateway = false for HA (one NAT GW per AZ)
  single_nat_gateway = false

  # Enable DNS hostnames and support
  enable_dns_hostnames = true
  enable_dns_support = true

  tags = var.tags
}

################################################################################
# RDS Module - PostgreSQL Database with Encryption
################################################################################

module "rds" {
  source = "./modules/rds"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # VPC and subnet configuration
  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids

  # Database configuration
  db_name = var.db_name
  db_username = var.db_username
  db_port = var.db_port

  # Instance class and scaling
  db_instance_class = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
  db_max_allocated_storage = var.db_max_allocated_storage
  multi_az = var.db_multi_az

  # Backup retention
  backup_retention_period = var.db_backup_retention_period
  backup_window = var.db_backup_window

  # Maintenance window
  maintenance_window = var.db_maintenance_window

  # Encryption with KMS
  kms_key_id = module.kms.key_id

  # Security
  allowed_security_groups = [module.ecs.security_group_id]

  # Secrets Manager integration
  secretsmanager_secret_id = module.secretsmanager.secret_id

  # PGBouncer configuration
  enable_pgbouncer = var.enable_pgbouncer
  pgbouncer_pool_size = var.pgbouncer_pool_size

  tags = var.tags
}

################################################################################
# S3 Module - Encrypted Storage
################################################################################

module "s3" {
  source = "./modules/s3"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # Use KMS for encryption
  kms_key_id = module.kms.key_id

  # Bucket names with environment prefix
  assets_bucket_name = "premium-service-directory-${var.environment}-assets"
  logs_bucket_name = "premium-service-directory-${var.environment}-logs"
  backups_bucket_name = "premium-service-directory-${var.environment}-backups"

  tags = var.tags
}

################################################################################
# ALB Module - Application Load Balancer with HTTPS
################################################################################

module "alb" {
  source = "./modules/alb"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # VPC and subnet configuration
  vpc_id = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids

  # Security groups
  allowed_security_groups = [module.ecs.security_group_id]

  # ACM certificate ARN
  certificate_arn = module.acm.certificate_arn

  # Health check configuration
  health_check_path = "/api/health"
  health_check_port = "traffic-port"
  health_check_protocol = "HTTP"
  healthy_threshold = 2
  unhealthy_threshold = 3
  timeout = 5
  interval = 30

  # Target group configuration
  target_port = 8080
  target_protocol = "HTTP"

  tags = var.tags
}

################################################################################
# ACM Module - SSL/TLS Certificates
################################################################################

module "acm" {
  source = "./modules/acm"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # Domain configuration
  domain_name = var.domain_name
  subject_alternative_names = ["*.${var.domain_name}"]

  # Route53 hosted zone for DNS validation
  hosted_zone_id = module.route53.hosted_zone_id

  tags = var.tags
}

################################################################################
# IAM Module - Roles and Policies
################################################################################

module "iam" {
  source = "./modules/iam"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # KMS key ARN for policies
  kms_key_arn = module.kms.key_arn

  # Secrets Manager ARN for policies
  secretsmanager_secret_arn = module.secretsmanager.secret_arn

  # S3 bucket ARNs
  assets_bucket_arn = module.s3.assets_bucket_arn
  logs_bucket_arn = module.s3.logs_bucket_arn

  tags = var.tags
}

################################################################################
# ECS Module - Container Infrastructure on Fargate
################################################################################

module "ecs" {
  source = "./modules/ecs"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # VPC and subnet configuration
  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids

  # Security groups
  allowed_security_groups = [module.alb.security_group_id]

  # IAM roles
  task_execution_role_arn = module.iam.ecs_task_execution_role_arn
  task_role_arn = module.iam.ecs_task_role_arn

  # KMS key ARN for task execution
  kms_key_arn = module.kms.key_arn

  # CloudWatch log group
  cloudwatch_log_group_name = "/ecs/premium-service-directory/${var.environment}"

  # Container configuration
  container_name = "premium-service-directory-api"
  container_port = 8080

  # Auto-scaling configuration
  enable_autoscaling = var.ecs_autoscaling_enabled
  desired_count = var.ecs_desired_count
  min_capacity = var.ecs_min_capacity
  max_capacity = var.ecs_max_capacity

  tags = var.tags
}

################################################################################
# ElastiCache Module - Redis Cluster
################################################################################

module "elasticache" {
  source = "./modules/elasticache"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # VPC and subnet configuration
  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids

  # Security groups - ECS should be able to access Redis
  allowed_security_groups = [module.ecs.security_group_id]

  # Redis configuration
  node_type = var.redis_node_type
  num_cache_nodes = var.redis_num_cache_nodes
  engine_version = var.redis_engine_version
  port = var.redis_port

  # Encryption
  kms_key_id = module.kms.key_id

  tags = var.tags
}

################################################################################
# Cognito Module - User Management
################################################################################

module "cognito" {
  source = "./modules/cognito"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # Domain configuration
  domain_name = var.cognito_domain_name

  # Callback URLs
  callback_urls = var.cognito_callback_urls
  logout_urls = var.cognito_logout_urls

  # Use KMS for encryption
  kms_key_id = module.kms.key_id

  tags = var.tags
}

################################################################################
# Route53 Module - DNS Configuration
################################################################################

module "route53" {
  source = "./modules/route53"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # Domain configuration
  domain_name = var.domain_name

  tags = var.tags
}

################################################################################
# CloudWatch Module - Monitoring and Alerting
################################################################################

module "cloudwatch" {
  source = "./modules/cloudwatch"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # Log groups
  log_group_name = "/ecs/premium-service-directory/${var.environment}"
  log_retention_days = var.cloudwatch_log_retention_days

  # Alarm configuration
  alarm_email = var.alarm_email

  # RDS module outputs for alarms
  rds_db_instance_id = module.rds.db_instance_id

  # ALB module outputs for alarms
  alb_target_group_arn = module.alb.target_group_arn
  alb_alb_arn = module.alb.alb_arn

  # ECS cluster name for service alerts
  ecs_cluster_name = module.ecs.ecs_cluster_name

  tags = var.tags
}

################################################################################
# GuardDuty Module - Security Threat Detection
################################################################################

module "guardduty" {
  source = "./modules/guardduty"

  environment = var.environment
  product_name = var.product_name
  team_name = var.team_name

  # Enable GuardDuty with findings exported to S3
  s3_bucket_arn = module.s3.logs_bucket_arn

  tags = var.tags
}