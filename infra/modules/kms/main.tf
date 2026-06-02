################################################################################
# KMS Module - Customer Master Keys for Encryption
################################################################################

data "aws_caller_identity" "current" {}

################################################################################
# KMS Key for General Encryption
################################################################################

resource "aws_kms_key" "main" {
  description             = "KMS key for ${var.product_name} in ${var.environment} environment"
  deletion_window_in_days = 30  # Wait 30 days before permanent deletion
  enable_key_rotation     = var.enable_key_rotation

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-kms-key"
      Type = "kms-key"
    }
  )
}

################################################################################
# KMS Key Alias
################################################################################

resource "aws_kms_alias" "main" {
  name          = "alias/${var.environment}-${var.product_name}-key"
  target_key_id = aws_kms_key.main.key_id
}

################################################################################
# Key Policy - Define who can use the key
################################################################################

data "aws_iam_policy_document" "kms_key_policy" {
  # Policy ID - Enable IAM User Permissions
  statement {
    sid = "EnableIAMUserPermissions"
    effect = "Allow"
    actions = [
      "kms:*"
    ]
    resources = ["*"]
    principals {
      type = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
  }

  # Allow key administrators to manage key policies
  statement {
    sid = "AllowKeyAdminsToManageKey"
    effect = "Allow"
    actions = [
      "kms:Create*",
      "kms:Describe*",
      "kms:Enable*",
      "kms:List*",
      "kms:Put*",
      "kms:Update*",
      "kms:Revoke*",
      "kms:Disable*",
      "kms:Get*",
      "kms:Delete*",
      "kms:ScheduleKeyDeletion",
      "kms:CancelKeyDeletion"
    ]
    resources = [aws_kms_key.main.arn]
    principals {
      type = "AWS"
      identifiers = var.key_administrators
    }
  }

  # Allow RDS to use the key for encryption
  statement {
    sid = "AllowRDSUsage"
    effect = "Allow"
    actions = [
      "kms:CreateGrant",
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_key.main.arn]
    principals {
      type = "Service"
      identifiers = ["rds.amazonaws.com"]
    }
  }

  # Allow ECS tasks and other services to use the key
  statement {
    sid = "AllowServicesUsage"
    effect = "Allow"
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_key.main.arn]
    principals {
      type = "AWS"
      identifiers = var.kms_key_users
    }
  }

  # Allow Secrets Manager to use the key
  statement {
    sid = "AllowSecretsManagerUsage"
    effect = "Allow"
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:CreateGrant"
    ]
    resources = [aws_kms_key.main.arn]
    principals {
      type = "Service"
      identifiers = ["secretsmanager.amazonaws.com"]
    }
  }

  # Allow CloudWatch Logs to use the key for encryption
  statement {
    sid = "AllowCloudWatchLogsUsage"
    effect = "Allow"
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:GenerateDataKey"
    ]
    resources = [aws_kms_key.main.arn]
    principals {
      type = "Service"
      identifiers = ["logs.amazonaws.com"]
    }
  }
}

resource "aws_kms_key_policy" "main" {
  key_id = aws_kms_key.main.key_id
  policy = data.aws_iam_policy_document.kms_key_policy.json
}

################################################################################
# S3 Bucket Key for SSE-KMS
################################################################################

resource "aws_kms_key" "s3_bucket_key" {
  description             = "KMS key for S3 bucket keys in ${var.environment}"
  deletion_window_in_days = 30
  enable_key_rotation     = var.enable_key_rotation

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-s3-kms-key"
      Type = "kms-key"
    }
  )
}

resource "aws_kms_alias" "s3_bucket_key" {
  name          = "alias/${var.environment}-${var.product_name}-s3-key"
  target_key_id = aws_kms_key.s3_bucket_key.key_id
}