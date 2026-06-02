################################################################################
# ALB Module Variables
################################################################################

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "product_name" {
  description = "Product name for resource naming"
  type        = string
}

variable "team_name" {
  description = "Team name for resource tagging"
  type        = string
}

################################################################################
# Network Configuration
################################################################################

variable "vpc_id" {
  description = "VPC ID for the ALB"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for ALB deployment"
  type        = list(string)
}

variable "allowed_security_groups" {
  description = "List of security group IDs allowed to access ECS tasks from ALB"
  type        = list(string)
  default     = []
}

################################################################################
# SSL/TLS Configuration
################################################################################

variable "certificate_arn" {
  description = "ARN of the ACM certificate for HTTPS"
  type        = string
}

################################################################################
# Health Check Configuration
################################################################################

variable "health_check_path" {
  description = "Health check path"
  type        = string
  default     = "/api/health"
}

variable "health_check_port" {
  description = "Health check port"
  type        = string
  default     = "traffic-port"
}

variable "health_check_protocol" {
  description = "Health check protocol"
  type        = string
  default     = "HTTP"
}

variable "healthy_threshold" {
  description = "Number of successful health checks before considering healthy"
  type        = number
  default     = 2
}

variable "unhealthy_threshold" {
  description = "Number of failed health checks before considering unhealthy"
  type        = number
  default     = 3
}

variable "timeout" {
  description = "Health check timeout in seconds"
  type        = number
  default     = 5
}

variable "interval" {
  description = "Health check interval in seconds"
  type        = number
  default     = 30
}

################################################################################
# Target Group Configuration
################################################################################

variable "target_port" {
  description = "Target port for the target group"
  type        = number
  default     = 8080
}

variable "target_protocol" {
  description = "Target protocol for the target group"
  type        = string
  default     = "HTTP"
}

################################################################################
# Deletion Protection
################################################################################

variable "deletion_protection" {
  description = "Enable deletion protection for ALB"
  type        = bool
  default     = true
}

################################################################################
# Access Logs
################################################################################

variable "alb_access_logs_bucket" {
  description = "S3 bucket name for ALB access logs (empty to disable)"
  type        = string
  default     = ""
}

################################################################################
# Tags
################################################################################

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}