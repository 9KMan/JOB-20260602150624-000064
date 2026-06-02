################################################################################
# CloudWatch Module Outputs
################################################################################

output "log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.main.name
}

output "log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.main.arn
}

output "dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

output "dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "alerts_sns_topic_arn" {
  description = "ARN of the alerts SNS topic"
  value       = aws_sns_topic.alerts.arn
}

output "alarms" {
  description = "Map of alarm names and ARNs"
  value = {
    ecs_cpu_high       = aws_cloudwatch_metric_alarm.ecs_cpu_high.arn
    ecs_memory_high    = aws_cloudwatch_metric_alarm.ecs_memory_high.arn
    rds_cpu_high       = aws_cloudwatch_metric_alarm.rds_cpu_high.arn
    rds_storage_low    = aws_cloudwatch_metric_alarm.rds_storage_low.arn
    rds_connections_high = aws_cloudwatch_metric_alarm.rds_connections_high.arn
    alb_response_high  = aws_cloudwatch_metric_alarm.alb_target_response_high.arn
    alb_no_targets     = aws_cloudwatch_metric_alarm.alb_no_targets.arn
  }
}