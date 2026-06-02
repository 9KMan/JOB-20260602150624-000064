################################################################################
# CloudWatch Module - Monitoring, Dashboards, and Alarms
################################################################################

################################################################################
# CloudWatch Log Group
################################################################################

resource "aws_cloudwatch_log_group" "main" {
  name              = var.log_group_name
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_id

  tags = {
    Name = "${var.environment}-${var.product_name}-log-group"
  }
}

################################################################################
# CloudWatch Dashboard
################################################################################

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.environment}-${var.product_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          title = "ECS CPU Utilization"
          region = var.aws_region
          annotations = {
            horizontal = [
              {
                value = 70
                label = "Critical Threshold"
                color = "#FF0000"
              }
            ]
          }
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", var.ecs_cluster_name]
          ]
          period = 300
          stat = "Average"
          view = "timeSeries"
        }
      },
      {
        type = "metric"
        properties = {
          title = "ECS Memory Utilization"
          region = var.aws_region
          metrics = [
            ["AWS/ECS", "MemoryUtilization", "ClusterName", var.ecs_cluster_name]
          ]
          period = 300
          stat = "Average"
          view = "timeSeries"
        }
      },
      {
        type = "metric"
        properties = {
          title = "RDS CPU Utilization"
          region = var.aws_region
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.rds_db_instance_id]
          ]
          period = 300
          stat = "Average"
          view = "timeSeries"
        }
      },
      {
        type = "metric"
        properties = {
          title = "RDS Database Connections"
          region = var.aws_region
          metrics = [
            ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", var.rds_db_instance_id]
          ]
          period = 300
          stat = "Average"
          view = "timeSeries"
        }
      },
      {
        type = "metric"
        properties = {
          title = "ALB Target Response Time"
          region = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", var.alb_arn]
          ]
          period = 300
          stat = "Average"
          view = "timeSeries"
        }
      },
      {
        type = "metric"
        properties = {
          title = "ALB Request Count"
          region = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", var.alb_arn]
          ]
          period = 300
          stat = "Sum"
          view = "timeSeries"
        }
      }
    ]
  })
}

################################################################################
# CloudWatch Alarms - ECS
################################################################################

resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name          = "${var.environment}-${var.product_name}-ecs-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ECS CPU utilization is above 80%"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = var.ecs_cluster_name
  }

  tags = {
    Name = "${var.environment}-${var.product_name}-ecs-cpu-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "ecs_memory_high" {
  alarm_name          = "${var.environment}-${var.product_name}-ecs-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "ECS Memory utilization is above 85%"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = var.ecs_cluster_name
  }

  tags = {
    Name = "${var.environment}-${var.product_name}-ecs-memory-alarm"
  }
}

################################################################################
# CloudWatch Alarms - RDS
################################################################################

resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  alarm_name          = "${var.environment}-${var.product_name}-rds-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 75
  alarm_description   = "RDS CPU utilization is above 75%"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = var.rds_db_instance_id
  }

  tags = {
    Name = "${var.environment}-${var.product_name}-rds-cpu-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_storage_low" {
  alarm_name          = "${var.environment}-${var.product_name}-rds-storage-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 10737418240  # 10GB in bytes
  alarm_description   = "RDS storage space is below 10GB"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = var.rds_db_instance_id
  }

  tags = {
    Name = "${var.environment}-${var.product_name}-rds-storage-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_connections_high" {
  alarm_name          = "${var.environment}-${var.product_name}-rds-connections-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Maximum"
  threshold           = 400
  alarm_description   = "RDS connections are above 400"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = var.rds_db_instance_id
  }

  tags = {
    Name = "${var.environment}-${var.product_name}-rds-connections-alarm"
  }
}

################################################################################
# CloudWatch Alarms - ALB
################################################################################

resource "aws_cloudwatch_metric_alarm" "alb_target_response_high" {
  alarm_name          = "${var.environment}-${var.product_name}-alb-response-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Average"
  threshold           = 2
  alarm_description   = "ALB target response time is above 2 seconds"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = var.alb_arn
  }

  tags = {
    Name = "${var.environment}-${var.product_name}-alb-response-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_no_targets" {
  alarm_name          = "${var.environment}-${var.product_name}-alb-no-targets"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Minimum"
  threshold           = 1
  alarm_description   = "No healthy targets in ALB target group"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = var.alb_arn
    TargetGroup  = var.alb_target_group_arn
  }

  tags = {
    Name = "${var.environment}-${var.product_name}-alb-targets-alarm"
  }
}

################################################################################
# SNS Topic for Alerts
################################################################################

resource "aws_sns_topic" "alerts" {
  name = "${var.environment}-${var.product_name}-alerts"

  kms_master_key_id = var.kms_key_id

  tags = {
    Name = "${var.environment}-${var.product_name}-alerts-topic"
  }
}

resource "aws_sns_topic_subscription" "alerts_email" {
  topic_arn = aws_sns_topic.alerts.arn
  endpoint  = var.alarm_email
  protocol  = "email"
}