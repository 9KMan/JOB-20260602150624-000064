################################################################################
# IAM Module Outputs
################################################################################

output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "ecs_task_execution_role_name" {
  description = "Name of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution.name
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task.arn
}

output "ecs_task_role_name" {
  description = "Name of the ECS task role"
  value       = aws_iam_role.ecs_task.name
}

output "rds_encryption_role_arn" {
  description = "ARN of the RDS encryption role"
  value       = aws_iam_role.rds_encryption.arn
}

output "rds_encryption_role_name" {
  description = "Name of the RDS encryption role"
  value       = aws_iam_role.rds_encryption.name
}

output "cloudwatch_events_role_arn" {
  description = "ARN of the CloudWatch Events role"
  value       = aws_iam_role.cloudwatch_events.arn
}

output "guardduty_role_arn" {
  description = "ARN of the GuardDuty role"
  value       = aws_iam_role.guardduty.arn
}