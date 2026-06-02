################################################################################
# GuardDuty Module - Security Threat Detection
################################################################################

################################################################################
# GuardDuty Detector
################################################################################

resource "aws_guardduty_detector" "main" {
  enable = true

  # Finding publishing frequency
  finding_publishing_frequency = "SIX_HOURS"

  tags = {
    Name = "${var.environment}-${var.product_name}-guardduty"
  }
}

################################################################################
# GuardDuty S3 Logs Archive (Optional - for storing findings)
################################################################################

resource "aws_s3_bucket" "guardduty_logs" {
  count = var.enable_guardduty_s3_logs ? 1 : 0

  bucket = "${var.environment}-${var.product_name}-guardduty-logs-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "${var.environment}-${var.product_name}-guardduty-logs"
  }
}

resource "aws_s3_bucket_policy" "guardduty_logs" {
  count = var.enable_guardduty_s3_logs ? 1 : 0

  bucket = aws_s3_bucket.guardduty_logs[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowGuardDutyToWriteLogs"
        Effect = "Allow"
        Principal = {
          Service = "guardduty.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.guardduty_logs[0].arn}/*"
      },
      {
        Sid    = "AllowGuardDutyToReadLogs"
        Effect = "Allow"
        Principal = {
          Service = "guardduty.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.guardduty_logs[0].arn}/*"
      },
      {
        Sid    = "AllowGuardDutyBucketAcl"
        Effect = "Allow"
        Principal = {
          Service = "guardduty.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.guardduty_logs[0].arn
      }
    ]
  })
}

data "aws_caller_identity" "current" {}

################################################################################
# GuardDuty IPSet - For internal threat detection
################################################################################

resource "aws_guardduty_ipset" "main" {
  count = var.enable_threat_detection ? 1 : 0

  detector_id = aws_guardduty_detector.main.id

  name     = "${var.environment}-${var.product_name}-ipset"
  format   = "CIDR"
  location = "https://s3.amazonaws.com/${aws_s3_bucket.guardduty_logs[0].id}/threat-intel/cidrs.txt"

  activate = true

  tags = {
    Name = "${var.environment}-${var.product_name}-guardduty-ipset"
  }
}

################################################################################
# GuardDuty Member Accounts (for AWS Organizations integration)
################################################################################

resource "aws_guardduty_member" "main" {
  count = length(var.member_account_ids)

  detector_id     = aws_guardduty_detector.main.id
  account_id      = var.member_account_ids[count.index]
  email           = var.member_emails[count.index]
  invite          = true

  lifecycle {
    create_before_destroy = true
  }
}

################################################################################
# CloudWatch Event Rule for GuardDuty Findings
################################################################################

resource "aws_cloudwatch_event_rule" "guardduty_findings" {
  name        = "${var.environment}-${var.product_name}-guardduty-findings"
  description = "Capture GuardDuty findings"

  event_pattern = jsonencode({
    "source" : ["aws.guardduty"],
    "detail-type" : ["GuardDuty Finding"]
  })

  tags = {
    Name = "${var.environment}-${var.product_name}-guardduty-findings-rule"
  }
}

resource "aws_cloudwatch_event_target" "guardduty_findings" {
  rule           = aws_cloudwatch_event_rule.guardduty_findings.name
  target_id      = "GuardDutyFindingsLambda"
  arn            = var.findings_lambda_arn
  input_transformer {
    input_template = <<EOF
{
  "findings": "<$.detail.findings>"
}
EOF
  }
}