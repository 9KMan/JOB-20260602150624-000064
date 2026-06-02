#!/bin/bash
set -euo pipefail

# Terraform Wrapper Script
# Usage: ./terraform.sh [command] [environment] [region]

TERRAFORM_VERSION="${TERRAFORM_VERSION:-1.6.0}"
TERRAFORM_WORKING_DIR="${TERRAFORM_WORKING_DIR:-infra}"
TERRAFORM_STATE_BUCKET="${TERRAFORM_STATE_BUCKET:-premium-service-terraform-state}"
TERRAFORM_LOCK_TABLE="${TERRAFORM_LOCK_TABLE:-terraform-locks}"

COMMAND="${1:-plan}"
ENVIRONMENT="${2:-production}"
REGION="${3:-us-east-1}"

TF_LOG_LEVEL="${TF_LOG:-INFO}"
TF_LOG_PATH="${TF_LOG_PATH:-terraform.log}"
TF_INPUT=0
TF_AUTO_APPROVE=""

# Enable auto-approve for apply and destroy
if [ "${COMMAND}" = "apply" ] || [ "${COMMAND}" = "destroy" ]; then
  TF_AUTO_APPROVE="-auto-approve"
fi

# AWS Region export
export AWS_DEFAULT_REGION="${REGION}"

echo "=========================================="
echo "Terraform Wrapper Script"
echo "=========================================="
echo "Command: ${COMMAND}"
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "Working Dir: ${TERRAFORM_WORKING_DIR}"
echo "Log Level: ${TF_LOG_LEVEL}"
echo "=========================================="

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
  echo "Installing Terraform v${TERRAFORM_VERSION}..."
  wget -q "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" -O /tmp/terraform.zip
  unzip -q -o /tmp/terraform.zip -d /usr/local/bin/
  chmod +x /usr/local/bin/terraform
  rm /tmp/terraform.zip
fi

# Change to terraform directory
cd "${TERRAFORM_WORKING_DIR}"

# Initialize Terraform backend
echo ""
echo "Initializing Terraform backend..."

 terraform init \
  -backend=true \
  -backend-config="bucket=${TERRAFORM_STATE_BUCKET}" \
  -backend-config="key=environments/${ENVIRONMENT}/terraform.tfstate" \
  -backend-config="region=${REGION}" \
  -backend-config="dynamodb_table=${TERRAFORM_LOCK_TABLE}" \
  -backend-config="encrypt=true"

# Select workspace
echo ""
echo "Selecting workspace: ${ENVIRONMENT}"
terraform workspace select "${ENVIRONMENT}" || terraform workspace new "${ENVIRONMENT}"

# Validate Terraform files
echo ""
echo "Validating Terraform configuration..."
terraform validate || {
  echo "ERROR: Terraform validation failed"
  exit 1
}

# Format check
echo ""
echo "Checking Terraform formatting..."
terraform fmt -check -recursive -diff || {
  echo "WARNING: Terraform formatting issues found (auto-fixing)..."
  terraform fmt -recursive
}

# Determine variable file
VAR_FILE="terraform.${ENVIRONMENT}.tfvars"
if [ ! -f "${VAR_FILE}" ]; then
  VAR_FILE="terraform.tfvars"
fi

echo ""
echo "Using variable file: ${VAR_FILE}"

# Execute command
case "${COMMAND}" in
  init)
    echo "Terraform initialized successfully"
    ;;

  validate)
    echo "Terraform validated successfully"
    terraform show
    ;;

  plan)
    echo ""
    echo "Running Terraform plan..."
    terraform plan \
      -var-file="${VAR_FILE}" \
      -var="environment=${ENVIRONMENT}" \
      -var="aws_region=${REGION}" \
      -out=tfplan

    echo ""
    echo "Plan saved to: tfplan"

    # Show plan summary
    echo ""
    echo "Plan Summary:"
    terraform show -json tfplan | jq '.changes_summary'
    ;;

  plan-destroy)
    echo ""
    echo "Running Terraform plan for destruction..."
    terraform plan \
      -var-file="${VAR_FILE}" \
      -var="environment=${ENVIRONMENT}" \
      -var="aws_region=${REGION}" \
      -destroy \
      -out=tfplan

    echo ""
    echo "Destruction plan saved to: tfplan"
    ;;

  apply)
    echo ""
    echo "Applying Terraform changes..."
    terraform apply \
      -var-file="${VAR_FILE}" \
      -var="environment=${ENVIRONMENT}" \
      -var="aws_region=${REGION}" \
      ${TF_AUTO_APPROVE} \
      tfplan

    echo ""
    echo "Applying successful!"

    # Show outputs
    echo ""
    echo "Terraform Outputs:"
    terraform output
    ;;

  destroy)
    echo ""
    echo "WARNING: This will destroy all resources!"
    read -p "Are you sure you want to continue? (yes/no): " CONFIRM
    if [ "${CONFIRM}" != "yes" ]; then
      echo "Destroy cancelled"
      exit 0
    fi

    terraform plan \
      -var-file="${VAR_FILE}" \
      -var="environment=${ENVIRONMENT}" \
      -var="aws_region=${REGION}" \
      -destroy \
      -out=tfplan

    echo ""
    echo "Applying destruction plan..."
    terraform apply \
      -var-file="${VAR_FILE}" \
      -var="environment=${ENVIRONMENT}" \
      -var="aws_region=${REGION}" \
      -auto-approve \
      tfplan

    echo "Destruction complete"
    ;;

  import)
    RESOURCE_ADDRESS="${4:-}"
    RESOURCE_ID="${5:-}"
    if [ -z "${RESOURCE_ADDRESS}" ] || [ -z "${RESOURCE_ID}" ]; then
      echo "Usage: terraform.sh import <resource_address> <resource_id>"
      exit 1
    fi
    echo "Importing resource ${RESOURCE_ADDRESS} with ID ${RESOURCE_ID}..."
    terraform import \
      -var-file="${VAR_FILE}" \
      -var="environment=${ENVIRONMENT}" \
      -var="aws_region=${REGION}" \
      "${RESOURCE_ADDRESS}" \
      "${RESOURCE_ID}"
    ;;

  output)
    terraform output
    ;;

  output-json)
    terraform output -json
    ;;

  state-list)
    terraform state list
    ;;

  state-pull)
    terraform state pull > terraform-state-backup.tfstate
    echo "State pulled to: terraform-state-backup.tfstate"
    ;;

  refresh)
    echo "Refreshing Terraform state..."
    terraform refresh \
      -var-file="${VAR_FILE}" \
      -var="environment=${ENVIRONMENT}" \
      -var="aws_region=${REGION}"
    ;;

  taint)
    RESOURCE="${4:-}"
    if [ -z "${RESOURCE}" ]; then
      echo "Usage: terraform.sh taint <resource>"
      exit 1
    fi
    echo "Tainting resource: ${RESOURCE}"
    terraform taint "${RESOURCE}"
    ;;

  untaint)
    RESOURCE="${4:-}"
    if [ -z "${RESOURCE}" ]; then
      echo "Usage: terraform.sh untaint <resource>"
      exit 1
    fi
    echo "Untainting resource: ${RESOURCE}"
    terraform untaint "${RESOURCE}"
    ;;

  workspace-list)
    terraform workspace list
    ;;

  workspace-select)
    WORKSPACE="${4:-}"
    if [ -z "${WORKSPACE}" ]; then
      echo "Usage: terraform.sh workspace-select <workspace>"
      exit 1
    fi
    terraform workspace select "${WORKSPACE}"
    ;;

  version)
    terraform version
    ;;

  graph)
    terraform graph | dot -Tsvg > terraform-graph.svg
    echo "Graph generated: terraform-graph.svg"
    ;;

  *)
    echo "Unknown command: ${COMMAND}"
    echo ""
    echo "Usage: terraform.sh <command> [environment] [region]"
    echo ""
    echo "Commands:"
    echo "  init          - Initialize Terraform"
    echo "  validate      - Validate configuration"
    echo "  plan          - Create execution plan"
    echo "  plan-destroy  - Create destruction plan"
    echo "  apply         - Apply changes"
    echo "  destroy       - Destroy all resources"
    echo "  import        - Import existing resources"
    echo "  output        - Show outputs"
    echo "  output-json   - Show outputs as JSON"
    echo "  state-list    - List state resources"
    echo "  state-pull    - Pull remote state"
    echo "  refresh       - Refresh state"
    echo "  taint         - Mark resource as tainted"
    echo "  untaint       - Unmark resource as tainted"
    echo "  workspace-list - List workspaces"
    echo "  workspace-select - Switch workspace"
    echo "  version       - Show Terraform version"
    echo "  graph         - Generate dependency graph"
    exit 1
    ;;
esac

echo ""
echo "Done!"