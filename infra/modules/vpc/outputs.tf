################################################################################
# VPC Module Outputs
################################################################################

################################################################################
# VPC Information
################################################################################

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "vpc_arn" {
  description = "ARN of the VPC"
  value       = aws_vpc.main.arn
}

################################################################################
# Subnet Information
################################################################################

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = [for subnet in aws_subnet.public : subnet.id]
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = [for subnet in aws_subnet.private : subnet.id]
}

output "availability_zones" {
  description = "List of availability zones"
  value       = var.availability_zones
}

################################################################################
# Internet Gateway
################################################################################

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

################################################################################
# NAT Gateways
################################################################################

output "nat_gateway_ids" {
  description = "IDs of the NAT Gateways"
  value       = [for gw in aws_nat_gateway.main : gw.id]
}

output "nat_gateway_ips" {
  description = "Elastic IPs of the NAT Gateways"
  value       = [for eip in aws_eip.nat : eip.public_ip]
}

################################################################################
# Route Tables
################################################################################

output "public_route_table_id" {
  description = "ID of the public route table"
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "IDs of the private route tables"
  value       = [for rt in aws_route_table.private : rt.id]
}

################################################################################
# VPC Endpoints
################################################################################

output "s3_vpc_endpoint_id" {
  description = "ID of the S3 VPC endpoint"
  value       = aws_vpc_endpoint.s3.id
}

output "secretsmanager_vpc_endpoint_id" {
  description = "ID of the Secrets Manager VPC endpoint"
  value       = aws_vpc_endpoint.secretsmanager.id
}

output "kms_vpc_endpoint_id" {
  description = "ID of the KMS VPC endpoint"
  value       = aws_vpc_endpoint.kms.id
}

output "logs_vpc_endpoint_id" {
  description = "ID of the CloudWatch Logs VPC endpoint"
  value       = aws_vpc_endpoint.logs.id
}

################################################################################
# Security Groups
################################################################################

output "vpc_endpoints_security_group_id" {
  description = "ID of the VPC endpoints security group"
  value       = aws_security_group.vpc_endpoints.id
}

################################################################################
# Network ACLs
################################################################################

output "public_network_acl_id" {
  description = "ID of the public subnet NACL"
  value       = aws_network_acl.public.id
}

output "private_network_acl_id" {
  description = "ID of the private subnet NACL"
  value       = aws_network_acl.private.id
}

################################################################################
# Subnet CIDRs
################################################################################

output "public_subnet_cidrs" {
  description = "CIDR blocks of the public subnets"
  value       = var.public_subnet_cidrs
}

output "private_subnet_cidrs" {
  description = "CIDR blocks of the private subnets"
  value       = var.private_subnet_cidrs
}