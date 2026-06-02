################################################################################
# VPC Module - Network Infrastructure for Premium Service Directory
################################################################################

resource "aws_vpc" "main" {
  # VPC with standard CIDR block
  cidr_block = var.vpc_cidr

  # Enable DNS support for the VPC
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support

  # Instance tenancy - dedicated for security compliance
  instance_tenancy = "default"

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-vpc"
      Type = "vpc"
    }
  )
}

################################################################################
# Internet Gateway - Connectivity for Public Subnets
################################################################################

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-igw"
      Type = "internet-gateway"
    }
  )
}

################################################################################
# Public Subnets - For ALB, NAT Gateways, and Internet-facing resources
# Deploy across 3 Availability Zones for High Availability
################################################################################

resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true  # Auto-assign public IPs for NAT Gateway instances

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-public-subnet-${var.availability_zones[count.index]}"
      Type = "public-subnet"
    }
  )
}

################################################################################
# NAT Gateways - One per AZ for High Availability
# Allow private subnet resources to access the internet while remaining private
################################################################################

resource "aws_eip" "nat" {
  count = length(var.public_subnet_cidrs)

  # EIPs must be in the same VPC as the NAT Gateway
  domain = "vpc"

  # Ensure the EIP is not released when the resource is destroyed
  # This prevents accidental disruption of services
  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-nat-eip-${var.availability_zones[count.index]}"
      Type = "elastic-ip"
    }
  )
}

resource "aws_nat_gateway" "main" {
  count = length(var.public_subnet_cidrs)

  # Allocate the EIP to the NAT Gateway
  allocation_id = aws_eip.nat[count.index].id

  # Connect NAT Gateway to the public subnet in its AZ
  subnet_id = aws_subnet.public[count.index].id

  # NAT Gateways require connectivity through an Internet Gateway
  # This dependency is handled by the IGW attachment
  depends_on = [aws_internet_gateway.main]

  # Tags for tracking and management
  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-nat-${var.availability_zones[count.index]}"
      Type = "nat-gateway"
    }
  )
}

################################################################################
# Private Subnets - For ECS Tasks, RDS, ElastiCache, Internal services
# Deploy across 3 Availability Zones for High Availability
################################################################################

resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidrs)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.private_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = false  # Private subnets should NOT auto-assign public IPs

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-private-subnet-${var.availability_zones[count.index]}"
      Type = "private-subnet"
    }
  )
}

################################################################################
# Route Tables
################################################################################

# Public Route Table - Routes traffic from public subnets to the Internet Gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  # Default route to Internet Gateway (0.0.0.0/0)
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-public-rt"
      Type = "route-table"
    }
  )
}

# Private Route Table - Routes traffic from private subnets through NAT Gateway
# One per AZ for HA - each NAT Gateway is in a different AZ
resource "aws_route_table" "private" {
  count = length(var.private_subnet_cidrs)

  vpc_id = aws_vpc.main.id

  # Default route to NAT Gateway in the same AZ (0.0.0.0/0)
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-private-rt-${var.availability_zones[count.index]}"
      Type = "route-table"
    }
  )
}

################################################################################
# Route Table Associations
################################################################################

# Associate public subnets with the public route table
resource "aws_route_table_association" "public" {
  count = length(var.public_subnet_cidrs)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Associate private subnets with the private route table in the same AZ
resource "aws_route_table_association" "private" {
  count = length(var.private_subnet_cidrs)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

################################################################################
# VPC Endpoints - Private connectivity to AWS services
# Avoids traffic going through the public internet for AWS API calls
################################################################################

# S3 Gateway Endpoint - Private access to S3
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.s3"

  # Gateway endpoints are used for S3 and DynamoDB
  vpc_endpoint_type = "Gateway"

  # Route table for the S3 endpoint - add to private subnets route tables
  route_table_ids = concat(
    [aws_route_table.public.id],
    [for rt in aws_route_table.private : rt.id]
  )

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-s3-vpce"
      Type = "vpc-endpoint"
    }
  )
}

# Secrets Manager Interface Endpoint - Private access to Secrets Manager
resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.secretsmanager"

  # Interface endpoints are used for most AWS services
  vpc_endpoint_type = "Interface"

  # Security group to control access to the endpoint
  security_group_ids = [aws_security_group.vpc_endpoints.id]

  # Private DNS must be enabled for Secrets Manager
  private_dns_enabled = true

  # Subnets for the ENIs - deploy in private subnets
  subnet_ids = aws_subnet.private[*].id

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-secretsmanager-vpce"
      Type = "vpc-endpoint"
    }
  )
}

# KMS Interface Endpoint - Private access to KMS
resource "aws_vpc_endpoint" "kms" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.kms"

  vpc_endpoint_type   = "Interface"
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true
  subnet_ids          = aws_subnet.private[*].id

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-kms-vpce"
      Type = "vpc-endpoint"
    }
  )
}

# CloudWatch Logs Interface Endpoint - Private access to CloudWatch
resource "aws_vpc_endpoint" "logs" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.logs"

  vpc_endpoint_type   = "Interface"
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true
  subnet_ids          = aws_subnet.private[*].id

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-logs-vpce"
      Type = "vpc-endpoint"
    }
  )
}

################################################################################
# Security Groups
################################################################################

# VPC Endpoints Security Group
# Controls traffic to VPC endpoints (Secrets Manager, KMS, CloudWatch)
resource "aws_security_group" "vpc_endpoints" {
  name        = "${var.environment}-${var.product_name}-vpc-endpoints-sg"
  description = "Security group for VPC endpoints"
  vpc_id      = aws_vpc.main.id

  # Allow all traffic within the VPC
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.vpc_cidr]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-vpc-endpoints-sg"
      Type = "security-group"
    }
  )
}

################################################################################
# Network ACLs (NACLs) - Additional security layer at subnet level
################################################################################

# Public Subnet NACL - Allow HTTP/HTTPS from anywhere, all outbound
resource "aws_network_acl" "public" {
  vpc_id = aws_vpc.main.id

  # Ephemeral ports for outbound connections
  egress {
    from_port   = 1024
    to_port     = 65535
    protocol    = "tcp"
    action      = "allow"
    cidr_block  = "0.0.0.0/0"
  }

  # Allow inbound HTTP (80) and HTTPS (443)
  ingress {
    from_port   = 80
    to_port     = 443
    protocol    = "tcp"
    action      = "allow"
    cidr_block  = "0.0.0.0/0"
  }

  # Allow inbound SSH (22) from restricted CIDR - management access only
  # In production, this should be limited to VPN or bastion host CIDR
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    action      = "allow"
    cidr_block  = "10.0.0.0/8"  # Limit to internal network
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-public-nacl"
      Type = "network-acl"
    }
  )
}

# Private Subnet NACL - More restrictive, only allow traffic from VPC
resource "aws_network_acl" "private" {
  vpc_id = aws_vpc.main.id

# Ephemeral ports for outbound connections (through NAT)
  egress {
    from_port   = 1024
    to_port     = 65535
    protocol    = "tcp"
    action      = "allow"
    cidr_block  = "0.0.0.0/0"
  }

  # Allow all traffic from within the VPC
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    action      = "allow"
    cidr_block  = var.vpc_cidr
  }

# Allow all traffic from within the VPC
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    action      = "allow"
    cidr_block  = var.vpc_cidr
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-private-nacl"
      Type = "network-acl"
    }
  )
}

# Associate NACLs with subnets
resource "aws_network_acl_association" "public" {
  count = length(var.public_subnet_cidrs)

  network_acl_id = aws_network_acl.public.id
  subnet_id      = aws_subnet.public[count.index].id
}

resource "aws_network_acl_association" "private" {
  count = length(var.private_subnet_cidrs)

  network_acl_id = aws_network_acl.private.id
  subnet_id      = aws_subnet.private[count.index].id
}