################################################################################
# IAM Module - Roles and Policies for ECS and Other Services
################################################################################

################################################################################
# ECS Task Execution Role
################################################################################

resource "aws_iam_role" "ecs_task_execution" {
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

resource "aws_iam_role_policy" "ecs_task_execution" {
  name = "${var.environment}-${var.product_name}-ecs-task-execution-policy"
  role = aws_iam_role.ecs_task_execution.name

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
        Sid = "KMSDecrypt"
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = var.kms_key_arn
      },
      {
        Sid = "CloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      },
      {
        Sid = "ECRPullImage"
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

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

################################################################################
# ECS Task Role
################################################################################

resource "aws_iam_role" "ecs_task" {
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

resource "aws_iam_role_policy" "ecs_task" {
  name = "${var.environment}-${var.product_name}-ecs-task-policy"
  role = aws_iam_role.ecs_task.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "S3ReadWrite"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${var.assets_bucket_arn}",
          "${var.assets_bucket_arn}/*"
        ]
      },
      {
        Sid = "S3LogsWrite"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${var.logs_bucket_arn}",
          "${var.logs_bucket_arn}/*"
        ]
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
          "logs:PutLogEvents"
        ]
        Resource = "*"
      },
      {
        Sid = "SQSFetchMessages"
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
# RDS Encryption Role
################################################################################

resource "aws_iam_role" "rds_encryption" {
  name = "${var.environment}-${var.product_name}-rds-encryption-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "rds.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-rds-encryption-role"
      Type = "iam-role"
    }
  )
}

resource "aws_iam_role_policy" "rds_encryption" {
  name = "${var.environment}-${var.product_name}-rds-encryption-policy"
  role = aws_iam_role.rds_encryption.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "KMSEncryptDecrypt"
        Effect = "Allow"
        Action = [
          "kms:CreateGrant",
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = var.kms_key_arn
      }
    ]
  })
}

################################################################################
# CloudWatch Events Role
################################################################################

resource "aws_iam_role" "cloudwatch_events" {
  name = "${var.environment}-${var.product_name}-cloudwatch-events-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-cloudwatch-events-role"
      Type = "iam-role"
    }
  )
}

################################################################################
# GuardDuty Service Role
################################################################################

resource "aws_iam_role" "guardduty" {
  name = "${var.environment}-${var.product_name}-guardduty-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "guardduty.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-guardduty-role"
      Type = "iam-role"
    }
  )
}