################################################################################
# Route53 Module Outputs
################################################################################

output "hosted_zone_id" {
  description = "ID of the Route53 hosted zone"
  value       = aws_route53_zone.main.zone_id
}

output "zone_name" {
  description = "Name of the Route53 hosted zone"
  value       = aws_route53_zone.main.name
}

output "name_server_records" {
  description = "NS records for the hosted zone"
  value       = aws_route53_zone.main.name_servers
}

output "alb_record_name" {
  description = "A record name for the ALB"
  value       = aws_route53_record.alb.name
}

output "api_record_name" {
  description = "A record name for the API"
  value       = aws_route53_record.api.name
}