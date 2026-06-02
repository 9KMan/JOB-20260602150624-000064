################################################################################
# ECS Module - Fargate Container Infrastructure
################################################################################

################################################################################
# ECS Cluster
################################################################################

resource "aws_ecs_cluster" "main" {
  name = "${var.environment}-${var.product_name}-cluster"

  # Setting to enable container insights for monitoring
  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-ecs-cluster"
      Type = "ecs-cluster"
    }
  )
}

################################################################################
# ECS Cluster Capacity Providers - Fargate and Fargate Spot
################################################################################

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }

  default_capacity_provider_strategy {
    base              = 0
    weight            = 50
    capacity_provider = "FARGATE_SPOT"
  }
}

################################################################################
# Security Group for ECS Tasks
################################################################################

resource "aws_security_group" "ecs_tasks" {
  name        = "${var.environment}-${var.product_name}-ecs-tasks-sg"
  description = "Security group for ECS tasks"
  vpc_id      = var.vpc_id

  # Allow traffic from the ALB security group
  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
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
      Name = "${var.environment}-${var.product_name}-ecs-tasks-sg"
      Type = "security-group"
    }
  )
}

################################################################################
# IAM Role for ECS Task Execution
################################################################################

resource "aws_iam_role" "task_execution" {
  name = "${var.environment}-${var.product_name}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-ecs-task-execution-role"
      Type = "iam-role"
    }
  )
}

resource "aws_iam_role_policy" "task_execution" {
  name = "${var.environment}-${var.product_name}-ecs-task-execution-policy"

  role = aws_iam_role.task_execution.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "SecretsManagerAccess"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = var.secretsmanager_secret_arn
      },
      {
        Sid = "KMSDecryptAccess"
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = var.kms_key_arn
      },
      {
        Sid = "CloudWatchLogsAccess"
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Sid = "ECRImagePull"
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }
    ]
  })
}

################################################################################
# IAM Role for ECS Task
################################################################################

resource "aws_iam_role" "task" {
  name = "${var.environment}-${var.product_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-ecs-task-role"
      Type = "iam-role"
    }
  )
}

resource "aws_iam_role_policy" "task" {
  name = "${var.environment}-${var.product_name}-ecs-task-policy"

  role = aws_iam_role.task.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "S3ReadAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${var.assets_bucket_arn}/*"
        ]
      },
      {
        Sid = "S3ListAccess"
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = var.assets_bucket_arn
      },
      {
        Sid = "SecretsManagerRead"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = var.secretsmanager_secret_arn
      },
      {
        Sid = "KMSEncryptDecrypt"
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = var.kms_key_arn
      },
      {
        Sid = "CloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:GetLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Sid = "SQSReceiveMessages"
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = "*"
      }
    ]
  })
}

################################################################################
# CloudWatch Log Group for ECS Tasks
################################################################################

resource "aws_cloudwatch_log_group" "ecs" {
  name              = var.cloudwatch_log_group_name
  retention_in_days  = var.log_retention_days
  kms_key_id         = var.kms_key_arn

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-ecs-logs"
      Type = "log-group"
    }
  )
}

################################################################################
# ECS Task Definition
################################################################################

resource "aws_ecs_task_definition" "main" {
  family                   = "${var.environment}-${var.product_name}-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.task_execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([
    {
      name      = var.container_name
      image     = var.container_image
      essential = true

      portMappings = [
        {
          containerPort = var.container_port
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "PRODUCT_NAME"
          value = var.product_name
        },
        {
          name  = "LOG_LEVEL"
          value = var.log_level
        }
      ]

      secrets = [
        {
          name      = "DB_PASSWORD"
          valueFrom = "${var.secretsmanager_secret_arn}:password::"
        },
        {
          name      = "DB_USERNAME"
          valueFrom = "${var.secretsmanager_secret_arn}:username::"
        },
        {
          name      = "DB_HOST"
          valueFrom = "${var.secretsmanager_secret_arn}:host::"
        },
        {
          name      = "AUTH0_CLIENT_SECRET"
          valueFrom = "${var.secretsmanager_secret_arn}:auth0_client_secret::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.cloudwatch_log_group_name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}/api/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-task-def"
      Type = "ecs-task-definition"
    }
  )
}

################################################################################
# ECS Service
################################################################################

resource "aws_ecs_service" "main" {
  name            = "${var.environment}-${var.product_name}-api-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  # Deployment configuration
  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  # Health check grace period
  health_check_grace_period_seconds = 60

  # Network configuration
  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false  # Tasks in private subnets
  }

  # Load balancer configuration
  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = var.container_name
    container_port   = var.container_port
  }

  # Preventargate from failing if the service is deleted
  propagate_tags = "NONE"

  # Enable autoscaling if configured
  dynamic "capacity_provider_strategy" {
    for_each = var.enable_autoscaling ? [1] : []
    content {
      base              = 1
      weight            = 100
      capacity_provider = "FARGATE"
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-ecs-service"
      Type = "ecs-service"
    }
  )
}

################################################################################
# ECS Service Auto Scaling
################################################################################

resource "aws_appautoscaling_target" "ecs" {
  count = var.enable_autoscaling ? 1 : 0

  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_cpu" {
  count = var.enable_autoscaling ? 1 : 0

  name               = "${var.environment}-${var.product_name}-cpu-autoscaling"
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  target_tracking_scaling_policy_configuration {
    target_value = 70
    disable_scale_in = false
  }
}

resource "aws_appautoscaling_policy" "ecs_memory" {
  count = var.enable_autoscaling ? 1 : 0

  name               = "${var.environment}-${var.product_name}-memory-autoscaling"
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  target_tracking_scaling_policy_configuration {
    target_value = 80
    disable_scale_in = false
  }
}