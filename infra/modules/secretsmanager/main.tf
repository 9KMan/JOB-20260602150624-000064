################################################################################
# Secrets Manager Module - Secure Storage for Credentials
################################################################################

################################################################################
# Database Credentials Secret
################################################################################

resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = var.db_credentials_secret_name
  description              = "Database credentials for ${var.product_name} in ${var.environment}"
  kms_key_id               = var.kms_key_id
  recovery_window_in_days  = 7  # Must wait 7 days before permanent deletion

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-db-credentials"
      Type = "secretsmanager-secret"
    }
  )
}

################################################################################
# Auth0 Credentials Secret
################################################################################

resource "aws_secretsmanager_secret" "auth0" {
  name                    = var.auth0_secret_name
  description              = "Auth0 credentials for ${var.product_name} in ${var.environment}"
  kms_key_id               = var.kms_key_id
  recovery_window_in_days  = 7

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-auth0-credentials"
      Type = "secretsmanager-secret"
    }
  )
}

################################################################################
# API Keys Secret
################################################################################

resource "aws_secretsmanager_secret" "api_keys" {
  name                    = var.api_keys_secret_name
  description              = "API keys for ${var.product_name} in ${var.environment}"
  kms_key_id               = var.kms_key_id
  recovery_window_in_days  = 7

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-api-keys"
      Type = "secretsmanager-secret"
    }
  )
}

################################################################################
# Secret Versions with Placeholder Values (Replace with actual values via CLI)
################################################################################

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id

  secret_string = jsonencode({
    username = "placeholder_username"
    password = "placeholder_password"
    host     = "placeholder_host"
    port     = 5432
    dbname   = "placeholder_dbname"
    engine   = "postgres"
  })

  # Mark as placeholder - in production, use aws_secretsmanager_secret_version with actual values
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_secretsmanager_secret_version" "auth0" {
  secret_id = aws_secretsmanager_secret.auth0.id

  secret_string = jsonencode({
    client_id     = "placeholder_client_id"
    client_secret = "placeholder_client_secret"
    domain        = "placeholder.auth0.com"
    audience      = "https://api.${var.product_name}.com"
  })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id = aws_secretsmanager_secret.api_keys.id

  secret_string = jsonencode({
    stripe_api_key     = "sk_placeholder"
    sendgrid_api_key    = "SG.placeholder"
    twilio_account_sid = "AC.placeholder"
    twilio_auth_token  = "placeholder_token"
  })

  lifecycle {
    create_before_destroy = true
  }
}

################################################################################
# Secret Rotation Configuration (Disabled by default, enable via CLI)
################################################################################

# Note: Lambda rotation functions should be configured via AWS Console or CLI
# as they require custom rotation logic based on the secret type
resource "aws_secretsmanager_secret_rotation" "db_credentials" {
  count = var.enable_secret_rotation ? 1 : 0

  secret_id = aws_secretsmanager_secret.db_credentials.id

  # Rotation every 30 days
  rotation_rules {
    automatically_after_days = 30
  }

  # Note: In production, create a custom Lambda function for rotation
  # This requires the rotation Lambda to be created separately
}

################################################################################
# Resource Policy to Restrict Access
################################################################################

data "aws_iam_policy_document" "secretsmanager_resource_policy" {
  statement {
    sid = "DenyUnencryptedAccess"
    effect = "Deny"
    actions = ["secretsmanager:GetSecretValue"]
    resources = ["*"]
    condition {
      test     = "Null"
      variable = "kms:EncryptionContext:aws:secretsmanager:secret-id"
      values = ["true"]
    }
  }
}

resource "aws_secretsmanager_secret_policy" "db_credentials" {
  secret_arn = aws_secretsmanager_secret.db_credentials.arn
  policy = data.aws_iam_policy_document.secretsmanager_resource_policy.json
}