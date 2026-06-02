################################################################################
# ACM Module Outputs
################################################################################

output "certificate_arn" {
  description = "ARN of the ACM certificate"
  value       = aws_acm_certificate.main.arn
}

output "certificate_domain_validation_options" {
  description = "Domain validation options for the ACM certificate"
  value       = aws_acm_certificate.main.domain_validation_options
}

output "certificate_status" {
  description = "Status of the ACM certificate"
  value       = aws_acm_certificate.main.status
}

output "wildcard_certificate_arn" {
  description = "ARN of the wildcard ACM certificate (if created)"
  value       = length(aws_acm_certificate.wildcard) > 0 ? aws_acm_certificate.wildcard[0].arn : ""
}

output "certificate_validation_route53_record_fqdns" {
  description = "FQDNs of the Route53 validation records"
  value       = [for record in aws_route53_record.validation : record.fqdn]
}