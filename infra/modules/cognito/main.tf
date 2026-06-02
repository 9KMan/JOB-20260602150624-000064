################################################################################
# Cognito Module - User Management and Authentication
################################################################################

resource "aws_cognito_user_pool" "main" {
  name = "${var.environment}-${var.product_name}-user-pool"

  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
  }

  password_policy {
    minimum_length    = 12
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = true
  }

  admin_create_user_config {
    allow_admin_create_user_only = false

    invite_message_template {
      email_message = "Welcome to ${var.product_name}! Your temporary password is {##PASSWORD##}."
      email_subject = "Welcome to ${var.product_name}"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_cognito_user_pool_client" "main" {
  name = "${var.environment}-${var.product_name}-client"
  user_pool_id = aws_cognito_user_pool.main.id
  generate_secret = true
  supported_identity_providers = ["COGNITO"]
  allowed_oauth_scopes = ["openid", "profile", "email"]
  callback_urls = var.callback_urls
  logout_urls = var.logout_urls
  access_token_validity = 60
  id_token_validity = 60
  refresh_token_validity = 30
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }
  prevent_user_existence_errors = "ENABLED"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = var.domain_name
  user_pool_id = aws_cognito_user_pool.main.id
}

resource "aws_cognito_identity_pool" "main" {
  identity_pool_name = "${var.environment}-${var.product_name}-identity-pool"
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id = aws_cognito_user_pool_client.main.id
    provider_name = "cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.main.id}"
    server_side_token_check = true
  }

  lifecycle {
    create_before_destroy = true
  }
}