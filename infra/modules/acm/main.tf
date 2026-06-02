################################################################################
# ACM Module - SSL/TLS Certificates with DNS Validation
################################################################################

################################################################################
# ACM Certificate
################################################################################

resource "aws_acm_certificate" "main" {
  domain_name               = var.domain_name
  subject_alternative_names = var.subject_alternative_names
  validation_method         = "DNS"  # DNS validation for automatic renewal

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-acm-cert"
      Type = "acm-certificate"
    }
  )
}

################################################################################
# Route53 DNS Validation Records
################################################################################

resource "aws_route53_record" "validation" {
  count = length(aws_acm_certificate.main.domain_validation_options)

  zone_id = var.hosted_zone_id
  name    = aws_acm_certificate.main.domain_validation_options[count.index].resource_record_name
  type    = aws_acm_certificate.main.domain_validation_options[count.index].resource_record_type
  ttl     = 300

  allow_overwrite = true

  records = [aws_acm_certificate.main.domain_validation_options[count.index].resource_record_value]

  # Ensure the validation records are created before the certificate is validated
  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-validation-record"
      Type = "dns-record"
    }
  )
}

################################################################################
# Wait for Certificate Validation
################################################################################

resource "aws_acm_certificate_validation" "main" {
  certificate_arn = aws_acm_certificate.main.arn

  # Wait for DNS validation records to propagate
  depends_on = [aws_route53_record.validation]

  lifecycle {
    create_before_destroy = true
  }
}

################################################################################
# Wildcard Certificate for Subdomains (Optional Additional Certificate)
################################################################################

resource "aws_acm_certificate" "wildcard" {
  count = length(var.subject_alternative_names) > 0 ? 1 : 0

  domain_name               = "*.${var.domain_name}"
  subject_alternative_names = []
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.product_name}-wildcard-cert"
      Type = "acm-certificate"
    }
  )
}

resource "aws_route53_record" "wildcard_validation" {
  count = length(var.subject_alternative_names) > 0 ? length(aws_acm_certificate.wildcard[0].domain_validation_options) : 0

  zone_id = var.hosted_zone_id
  name    = aws_acm_certificate.wildcard[0].domain_validation_options[count.index].resource_record_name
  type    = aws_acm_certificate.wildcard[0].domain_validation_options[count.index].resource_record_type
  ttl     = 300

  allow_overwrite = true

  records = [aws_acm_certificate.wildcard[0].domain_validation_options[count.index].resource_record_value]

  lifecycle {
    create_before_destroy = true
  }
}