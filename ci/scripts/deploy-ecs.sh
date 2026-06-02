#!/bin/bash
set -euo pipefail

# ECS Deployment Script
# Usage: ./deploy-ecs.sh [environment] [region]

ENVIRONMENT="${1:-production}"
REGION="${2:-us-east-1}"
ECR_REPOSITORY="premium-service-directory"
ECS_CLUSTER="premium-service-${ENVIRONMENT}-cluster"
ECS_SERVICE="backend-service-${ENVIRONMENT}"
ECS_TASK_FAMILY="premium-service-backend-${ENVIRONMENT}"
AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
IMAGE_TAG="${CIRCLE_SHA1:-$(git rev-parse --short HEAD)}"
IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}"

echo "=========================================="
echo "ECS Deployment Script"
echo "=========================================="
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "Cluster: ${ECS_CLUSTER}"
echo "Service: ${ECS_SERVICE}"
echo "Image: ${IMAGE_URI}"
echo "=========================================="

# AWS Region export
export AWS_DEFAULT_REGION="${REGION}"

# Login to ECR
echo "Logging into Amazon ECR..."
aws ecr get-login-password --region "${REGION}" | \
  docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

# Build Docker image
echo "Building Docker image..."
docker build -t "${ECR_REPOSITORY}:${IMAGE_TAG}" \
  --build-arg NODE_ENV=production \
  --build-arg NPM_TOKEN="${NPM_TOKEN:-}" \
  -f backend/Dockerfile backend/

# Tag image for ECR
echo "Tagging image for ECR push..."
docker tag "${ECR_REPOSITORY}:${IMAGE_TAG}" "${IMAGE_URI}"

# Push to ECR
echo "Pushing image to ECR..."
docker push "${IMAGE_URI}"

echo "Image pushed successfully: ${IMAGE_URI}"

# Get current task definition
echo "Getting current task definition..."
TASK_DEFINITION=$(aws ecs describe-task-definition \
  --task-definition "${ECS_TASK_FAMILY}" \
  --region "${REGION}" \
  --query 'taskDefinition' \
  --output json)

# Create new task definition
echo "Creating new task definition..."
NEW_TASK_DEF=$(echo "${TASK_DEFINITION}" | \
  jq "\
    .containerDefinitions[0].image = \"${IMAGE_URI}\" | \
    .family = \"${ECS_TASK_FAMILY}\" | \
    del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy)")

echo "${NEW_TASK_DEF}" > new-task-definition.json

# Register new task definition
echo "Registering new task definition..."
NEW_TASK_ARN=$(aws ecs register-task-definition \
  --region "${REGION}" \
  --cli-input-json file://new-task-definition.json \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text)

echo "New task definition registered: ${NEW_TASK_ARN}"

# Update ECS service
echo "Updating ECS service..."
aws ecs update-service \
  --cluster "${ECS_CLUSTER}" \
  --service "${ECS_SERVICE}" \
  --task-definition "${ECS_TASK_FAMILY}" \
  --region "${REGION}" \
  --force-new-deployment

echo "Deployment initiated. Waiting for service stability..."

# Wait for deployment to complete
DEPLOYMENT_TIMEOUT=600
DEPLOYMENT_START=$(date +%s)

while true; do
  SERVICE_INFO=$(aws ecs describe-services \
    --cluster "${ECS_CLUSTER}" \
    --services "${ECS_SERVICE}" \
    --region "${REGION}" \
    --query 'services[0]')

  RUNNING_COUNT=$(echo "${SERVICE_INFO}" | jq '.runningCount')
  DESIRED_COUNT=$(echo "${SERVICE_INFO}" | jq '.desiredCount')
  PRIMARYDeployment=$(echo "${SERVICE_INFO}" | jq '.deployments[0]')
  DEPLOYMENT_STATUS=$(echo "${PRIMARYDeployment}" | jq -r '.status')
  DEPLOYMENT_RUNNING=$(echo "${PRIMARYDeployment}" | jq -r '.runningCount')
  DEPLOYMENT_DESIRED=$(echo "${PRIMARYDeployment}" | jq -r '.desiredCount')

  echo "[$(date +%H:%M:%S)] Running: ${DEPLOYMENT_RUNNING}/${DEPLOYMENT_DESIRED} (status: ${DEPLOYMENT_STATUS})"

  if [ "${DEPLOYMENT_RUNNING}" = "${DEPLOYMENT_DESIRED}" ] && [ "${DEPLOYMENT_STATUS}" = "PRIMARY" ]; then
    echo "Deployment completed successfully!"
    break
  fi

  ELAPSED=$(($(date +%s) - DEPLOYMENT_START))
  if [ ${ELAPSED} -gt ${DEPLOYMENT_TIMEOUT} ]; then
    echo "ERROR: Deployment timeout exceeded (${DEPLOYMENT_TIMEOUT}s)"
    exit 1
  fi

  sleep 15
done

# Verify deployment
echo "Verifying deployment..."
sleep 30  # Allow services to stabilize

DESIRED_COUNT=$(aws ecs describe-services \
  --cluster "${ECS_CLUSTER}" \
  --services "${ECS_SERVICE}" \
  --region "${REGION}" \
  --query 'services[0].desiredCount' \
  --output text)

RUNNING_COUNT=$(aws ecs describe-services \
  --cluster "${ECS_CLUSTER}" \
  --services "${ECS_SERVICE}" \
  --region "${REGION}" \
  --query 'services[0].runningCount' \
  --output text)

if [ "${RUNNING_COUNT}" = "${DESIRED_COUNT}" ]; then
  echo "=========================================="
  echo "✅ ECS Deployment Successful!"
  echo "=========================================="
  echo "Service: ${ECS_SERVICE}"
  echo "Cluster: ${ECS_CLUSTER}"
  echo "Task Definition: ${NEW_TASK_ARN}"
  echo "Image: ${IMAGE_URI}"
else
  echo "=========================================="
  echo "❌ ECS Deployment Failed!"
  echo "=========================================="
  echo "Expected: ${DESIRED_COUNT} tasks"
  echo "Running: ${RUNNING_COUNT} tasks"
  exit 1
fi

# Cleanup
rm -f new-task-definition.json

echo "Done!"