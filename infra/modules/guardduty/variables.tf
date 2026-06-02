################################################################################
# GuardDuty Module Variables
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
# GuardDuty Configuration
################################################################################

variable "enable_guardduty_s3_logs" {
  description = "Enable S3 logs archiving for GuardDuty"
  type        = bool
  default     = true
}

variable "enable_threat_detection" {
  description = "Enable threat detection with custom IPSets"
  type        = bool
  default     = false
}

variable "member_account_ids" {
  description = "List of member account IDs for GuardDuty (in AWS Organizations)"
  type        = list(string)
  default     = []
}

variable "member_emails" {
  description = "List of emails for member accounts (same order as member_account_ids)"
  type        = list(string)
  default     = []
}

variable "findings_lambda_arn" {
  description = "ARN of the Lambda function to process GuardDuty findings"
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