################################################################################
# GuardDuty Module Outputs
################################################################################

output "detector_id" {
  description = "ID of the GuardDuty detector"
  value       = aws_guardduty_detector.main.id
}

output "detector_arn" {
  description = "ARN of the GuardDuty detector"
  value       = aws_guardduty_detector.main.arn
}

output "guardduty_logs_bucket_arn" {
  description = "ARN of the GuardDuty logs S3 bucket"
  value       = var.enable_guardduty_s3_logs ? aws_s3_bucket.guardduty_logs[0].arn : ""
}

output "event_rule_name" {
  description = "Name of the CloudWatch Event rule for GuardDuty findings"
  value       = aws_cloudwatch_event_rule.guardduty_findings.name
}

output "event_rule_arn" {
  description = "ARN of the CloudWatch Event rule for GuardDuty findings"
  value       = aws_cloudwatch_event_rule.guardduty_findings.arn
}