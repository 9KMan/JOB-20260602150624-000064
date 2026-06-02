#!/bin/bash
set -euo pipefail

# Health Check Script
# Usage: ./health-check.sh [environment] [region]

ENVIRONMENT="${1:-production}"
REGION="${2:-us-east-1}"
MAX_ATTEMPTS=30
ATTEMPT_INTERVAL=10
TIMEOUT=5

echo "=========================================="
echo "Health Check Script"
echo "=========================================="
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "Max attempts: ${MAX_ATTEMPTS}"
echo "=========================================="

# Get ALB DNS name
echo "Getting ALB DNS name..."
ALB_NAME="premium-service-${ENVIRONMENT}-alb"
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names "${ALB_NAME}" \
  --region "${REGION}" \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

if [ -z "${ALB_DNS}" ]; then
  echo "ERROR: Could not find ALB: ${ALB_NAME}"
  exit 1
fi

echo "ALB DNS: ${ALB_DNS}"

# Function to check endpoint
check_endpoint() {
  local endpoint="$1"
  local service="$2"

  echo "Checking ${service} endpoint: http://${ALB_DNS}${endpoint}"

  http_code=$(curl -s -o /dev/null -w "%{http_code}" \
    --connect-timeout ${TIMEOUT} \
    --max-time ${TIMEOUT} \
    "http://${ALB_DNS}${endpoint}")

  echo "  Status: ${http_code}"
  return $([ "$http_code" = "200" ])
}

# Main health check loop
main_healthy=false
attempts=0

echo ""
echo "Starting health check loop..."

while [ $attempts -lt $MAX_ATTEMPTS ]; do
  attempts=$((attempts + 1))
  echo ""
  echo "[Attempt ${attempts}/${MAX_ATTEMPTS}] $(date -u +"%Y-%m-%d %H:%M:%S UTC")"

  # Check main health endpoint
  if check_endpoint "/health" "main"; then
    main_healthy=true

    # Check additional services
    api_healthy=false
    auth_healthy=false
    search_healthy=false

    check_endpoint "/api/health" "api" && api_healthy=true || true
    check_endpoint "/auth/health" "auth" && auth_healthy=true || true
    check_endpoint "/search/health" "search" && search_healthy=true || true

    if [ "$api_healthy" = true ] && [ "$auth_healthy" = true ]; then
      echo ""
      echo "✅ All services are healthy!"
      break
    fi
  fi

  if [ $attempts -lt $MAX_ATTEMPTS ]; then
    echo "Waiting ${ATTEMPT_INTERVAL} seconds before next attempt..."
    sleep $ATTEMPT_INTERVAL
  fi
done

if [ "${main_healthy}" = false ]; then
  echo ""
  echo "=========================================="
  echo "❌ Health check failed after ${MAX_ATTEMPTS} attempts"
  echo "=========================================="

  # Get ECS service status for debugging
  echo ""
  echo "ECS Service Status:"
  aws ecs describe-services \
    --cluster "premium-service-${ENVIRONMENT}-cluster" \
    --services "backend-service-${ENVIRONMENT}" \
    --region "${REGION}" \
    --query 'services[0].{status:status, running:runningCount, desired:desiredCount, deployments:deployments}' \
    --output table 2>/dev/null || echo "Could not get ECS status"

  exit 1
fi

# Detailed service verification
echo ""
echo "=========================================="
echo "Performing detailed service verification"
echo "=========================================="

# Check ECS tasks are running
echo ""
echo "Checking ECS tasks..."
TASK_STATUS=$(aws ecs describe-services \
  --cluster "premium-service-${ENVIRONMENT}-cluster" \
  --services "backend-service-${ENVIRONMENT}" \
  --region "${REGION}" \
  --query 'services[0].runningCount' \
  --output text)

DESIRED_COUNT=$(aws ecs describe-services \
  --cluster "premium-service-${ENVIRONMENT}-cluster" \
  --services "backend-service-${ENVIRONMENT}" \
  --region "${REGION}" \
  --query 'services[0].desiredCount' \
  --output text)

echo "ECS Tasks Running: ${TASK_STATUS}/${DESIRED_COUNT}"

if [ "${TASK_STATUS}" != "${DESIRED_COUNT}" ]; then
  echo "WARNING: Not all tasks are running"
fi

# Check database connectivity
echo ""
echo "Checking database connectivity..."
DB_HOST=$(aws rds describe-db-instances \
  --db-instance-identifier "premium-service-${ENVIRONMENT}-db" \
  --region "${REGION}" \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text 2>/dev/null || echo "unknown")

echo "Database host: ${DB_HOST}"

# Check Redis connectivity
echo ""
echo "Checking Redis connectivity..."
REDIS_HOST=$(aws elasticache describe-cache-clusters \
  --cache-cluster-id "premium-service-${ENVIRONMENT}-redis" \
  --region "${REGION}" \
  --query 'CacheClusters[0].RedisEndpoint.Address' \
  --output text 2>/dev/null || echo "unknown")

echo "Redis host: ${REDIS_HOST}"

# Check CloudWatch metrics
echo ""
echo "Checking CloudWatch alarm status..."
ALARM_STATUS=$(aws cloudwatch describe-alarms \
  --alarm-names "premium-service-${ENVIRONMENT}-high-cpu" \
  --region "${REGION}" \
  --query 'MetricAlarms[0].StateValue' \
  --output text 2>/dev/null || echo "unknown")

echo "High CPU Alarm: ${ALARM_STATUS}"

# Final health summary
echo ""
echo "=========================================="
echo "✅ Health Check Passed!"
echo "=========================================="
echo "ALB DNS: ${ALB_DNS}"
echo "ECS Tasks: ${TASK_STATUS}/${DESIRED_COUNT}"
echo "Database: ${DB_HOST}"
echo "Redis: ${REDIS_HOST}"
echo "Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo "=========================================="