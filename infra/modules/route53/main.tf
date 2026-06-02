################################################################################
# Route53 Module - DNS Configuration
################################################################################

################################################################################
# Route53 Hosted Zone
################################################################################

resource "aws_route53_zone" "main" {
  name = var.domain_name

  # VPC association for private hosted zone (if enabled)
  dynamic "vpc" {
    for_each = var.private_zone ? [1] : []
    content {
      vpc_id = var.vpc_id
    }
  }

  tags = {
    Name = "${var.environment}-${var.product_name}-hosted-zone"
    Type = "route53-hosted-zone"
  }
}

################################################################################
# A Record for ALB
################################################################################

resource "aws_route53_record" "alb" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health  = true
  }
}

################################################################################
# A Record for API Subdomain
################################################################################

resource "aws_route53_record" "api" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.${var.domain_name}"
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health  = true
  }
}

################################################################################
# CNAME for WWW Redirect
################################################################################

resource "aws_route53_record" "www" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "www.${var.domain_name}"
  type    = "CNAME"
  ttl     = 300
  records = [var.domain_name]
}

################################################################################
# MX Records for Email
################################################################################

resource "aws_route53_record" "mx" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "MX"
  ttl     = 3600
  records = [
    "1 aspmx.l.google.com",
    "5 alt1.aspmx.l.google.com",
    "5 alt2.aspmx.l.google.com",
    "10 alt3.aspmx.l.google.com",
    "10 alt4.aspmx.l.google.com"
  ]
}

################################################################################
# TXT Record for SPF
################################################################################

resource "aws_route53_record" "spf" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "TXT"
  ttl     = 3600
  records = ["v=spf1 include:_spf.google.com ~all"]
}

################################################################################
# CAA Records for SSL
################################################################################

resource "aws_route53_record" "caa" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "CAA"
  ttl     = 3600
  records = [
    "0 issuewild letsencrypt.org",
    "0 issue letsencrypt.org",
    "0 iodef mailto:security@${var.domain_name}"
  ]
}