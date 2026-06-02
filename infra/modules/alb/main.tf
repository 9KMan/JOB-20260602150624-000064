################################################################################
# ALB Module - Application Load Balancer with HTTPS
################################################################################

################################################################################
# Security Group for ALB
################################################################################

resource "aws_security_group" "alb" {
  name        = "${var.environment}-${var.product_name}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = var.vpc_id

  # Allow HTTP and HTTPS from anywhere
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
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
      Name = "${var.environment}-${var.product_name}-alb-sg"
      Type = "security-group"
    }
  )
}

################################################################################
# Application Load Balancer
################################################################################

resource "aws_lb" "main" {
  name               = "${var.environment}-${var.product_name}-alb"
  internal           = false  # Public-facing ALB
  load_balancer_type = "application"

  # Deploy in public subnets across multiple AZs
  subnets = var.public_subnet_ids

  # Security group for the ALB
  security_groups = [aws_security_group.alb.id]

  # Enable deletion protection in production
  enable_deletion_protection = var.deletion_protection

  # Idle timeout (seconds)
  idle_timeout = 60

  # Enable HTTP/2
  enable_http2 = true

  # Drop invalid headers
  drop_invalid_header_fields = true

  # Access logs configuration
  dynamic "access_logs" {
    for_each = var.alb_access_logs_bucket != "" ? [1] : []
    content {
      bucket  = var.alb_access_logs_bucket
      enabled = true
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-alb"
      Type = "load-balancer"
    }
  )
}

################################################################################
# Target Group for ECS Tasks
################################################################################

resource "aws_lb_target_group" "main" {
  name     = "${var.environment}-${var.product_name}-tg"
  port     = var.target_port
  protocol = var.target_protocol
  vpc_id   = var.vpc_id

  # Deregistration delay - time to wait before removing a target
  deregistration_delay = 30

  # Health check configuration
  health_check {
    enabled             = true
    path                = var.health_check_path
    port                = var.health_check_port
    protocol            = var.health_check_protocol
    healthy_threshold   = var.healthy_threshold
    unhealthy_threshold = var.unhealthy_threshold
    timeout             = var.timeout
    interval            = var.interval
    matcher             = "200-299"  # HTTP status codes for healthy
  }

  # Slow start for gradual traffic increase
  slow_start = 30

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-target-group"
      Type = "target-group"
    }
  )
}

################################################################################
# HTTPS Listener with ACM Certificate
################################################################################

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"  # TLS 1.3
  certificate_arn   = var.certificate_arn

  # Default action - forward to target group
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-https-listener"
      Type = "lb-listener"
    }
  )
}

################################################################################
# HTTP Listener (Redirect to HTTPS)
################################################################################

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  # Redirect all HTTP traffic to HTTPS
  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"  # Permanent redirect
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-http-listener"
      Type = "lb-listener"
    }
  )
}

################################################################################
# WAF Web ACL for ALB
################################################################################

resource "aws_wafv2_web_acl" "alb" {
  name        = "${var.environment}-${var.product_name}-waf-acl"
  description = "WAF Web ACL for Application Load Balancer"
  scope       = "REGIONAL"  # Use REGIONAL for ALB

  # Default rule to allow all traffic (we'll add more specific rules in production)
  default_action {
    allow {}
  }

  # Rule: Block common attack patterns
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1

    override_action {
      count {}
    }

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name               = "AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # Rule: Block SQL injection attacks
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 2

    override_action {
      count {}
    }

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesSQLiRuleSet"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name               = "AWSManagedRulesSQLiRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # Rule: Block common Linux exploits
  rule {
    name     = "AWSManagedRulesLinuxRuleSet"
    priority = 3

    override_action {
      count {}
    }

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesLinuxRuleSet"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name               = "AWSManagedRulesLinuxRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # Rule: Rate limiting - block IPs exceeding 10000 requests per 5 minutes
  rule {
    name     = "RateLimitRule"
    priority = 4

    action {
      block {
        custom_response {
          response_code = 429
          response_header {
            name  = "X-Blocked-By"
            value = "WAF Rate Limit"
          }
        }
      }
    }

    statement {
      rate_based_statement {
        limit              = 10000
        evaluation_window_sec = 300
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name               = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name               = "${var.environment}-${var.product_name}-waf-metrics"
    sampled_requests_enabled   = true
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-waf-acl"
      Type = "waf-web-acl"
    }
  )
}

################################################################################
# WAF Association with ALB
################################################################################

resource "aws_wafv2_web_acl_association" "alb" {
  resource_arn = aws_lb.main.arn
  web_acl_arn  = aws_wafv2_web_acl.alb.arn
}

################################################################################
# ALB Access Logs to S3
################################################################################

resource "aws_s3_bucket" "alb_access_logs" {
  count = var.alb_access_logs_bucket != "" ? 1 : 0

  bucket = var.alb_access_logs_bucket

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-alb-access-logs"
      Type = "s3-bucket"
    }
  )
}

resource "aws_s3_bucket_policy" "alb_access_logs" {
  count = var.alb_access_logs_bucket != "" ? 1 : 0

  bucket = aws_s3_bucket.alb_access_logs[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowALBToWriteAccessLogs"
        Effect = "Allow"
        Principal = {
          Service = "delivery.logs.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "arn:aws:s3:::${var.alb_access_logs_bucket}/AWSLogs/*"
      },
      {
        Sid    = "AllowALBAccessLogsDelivery"
        Effect = "Allow"
        Principal = {
          Service = "delivery.logs.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = "arn:aws:s3:::${var.alb_access_logs_bucket}"
      }
    ]
  })
}