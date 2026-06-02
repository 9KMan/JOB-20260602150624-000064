################################################################################
# ECS Module Outputs
################################################################################

################################################################################
# ECS Cluster
################################################################################

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

################################################################################
# Task Definition
################################################################################

output "task_definition_arn" {
  description = "ARN of the ECS task definition"
  value       = aws_ecs_task_definition.main.arn
}

output "task_definition_family" {
  description = "Family of the ECS task definition"
  value       = aws_ecs_task_definition.main.family
}

################################################################################
# ECS Service
################################################################################

output "service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.main.name
}

output "service_arn" {
  description = "ARN of the ECS service"
  value       = aws_ecs_service.main.id
}

################################################################################
# Security Groups
################################################################################

output "security_group_id" {
  description = "Security group ID of the ECS tasks"
  value       = aws_security_group.ecs_tasks.id
}

################################################################################
# IAM Roles
################################################################################

output "task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.task_execution.arn
}

output "task_execution_role_name" {
  description = "Name of the ECS task execution role"
  value       = aws_iam_role.task_execution.name
}

output "task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.task.arn
}

output "task_role_name" {
  description = "Name of the ECS task role"
  value       = aws_iam_role.task.name
}

################################################################################
# CloudWatch
################################################################################

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.ecs.name
}

output "cloudwatch_log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.ecs.arn
}

################################################################################
# Auto Scaling
################################################################################

output "autoscaling_target_arn" {
  description = "ARN of the autoscaling target"
  value       = var.enable_autoscaling ? aws_appautoscaling_target.ecs[0].arn : ""
}

output "autoscaling_policy_cpu_arn" {
  description = "ARN of the CPU autoscaling policy"
  value       = var.enable_autoscaling ? aws_appautoscaling_policy.ecs_cpu[0].arn : ""
}

output "autoscaling_policy_memory_arn" {
  description = "ARN of the memory autoscaling policy"
  value       = var.enable_autoscaling ? aws_appautoscaling_policy.ecs_memory[0].arn : ""
}