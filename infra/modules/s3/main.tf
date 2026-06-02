################################################################################
# S3 Module - Encrypted S3 Buckets with Versioning
################################################################################

################################################################################
# Assets Bucket - For user uploads and static assets
################################################################################

resource "aws_s3_bucket" "assets" {
  bucket = var.assets_bucket_name

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-assets"
      Type = "s3-bucket"
    }
  )
}

resource "aws_s3_bucket_versioning" "assets" {
  bucket = aws_s3_bucket.assets.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_id
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "assets" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id

  rule {
    id     = "storage-class-transition"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }

    noncurrent_version_expiration {
      noncurrent_days = 365
    }
  }
}

################################################################################
# Logs Bucket - For application and access logs
################################################################################

resource "aws_s3_bucket" "logs" {
  bucket = var.logs_bucket_name

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-logs"
      Type = "s3-bucket"
    }
  )
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_id
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "logs-expiration"
    status = "Enabled"

    filter {
      prefix = "ecs-logs/"
    }

    expiration {
      days = 90
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }

  rule {
    id     = "alb-logs-expiration"
    status = "Enabled"

    filter {
      prefix = "alb-logs/"
    }

    expiration {
      days = 180
    }
  }
}

################################################################################
# Backups Bucket - For database backups
################################################################################

resource "aws_s3_bucket" "backups" {
  bucket = var.backups_bucket_name

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-backups"
      Type = "s3-bucket"
    }
  )
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_id
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket = aws_s3_bucket.backups.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "backups-retention"
    status = "Enabled"

    transition {
      days          = 7
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    noncurrent_version_transition {
      noncurrent_days = 7
      storage_class   = "STANDARD_IA"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}

################################################################################
# S3 Bucket Policies
################################################################################

# Policy to enforce SSL connections
resource "aws_s3_bucket_policy" "enforce_ssl" {
  bucket = aws_s3_bucket.assets.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "EnforceSSLViaTLS"
        Effect = "Deny"
        Action = "s3:*"
        Resource = [
          aws_s3_bucket.assets.arn,
          "${aws_s3_bucket.assets.arn}/*"
        ]
        Principal = "*"
        Condition = {
          Bool = {
            "aws:SecureTransport" = false
          }
        }
      }
    ]
  })
}