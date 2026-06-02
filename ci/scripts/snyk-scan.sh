#!/bin/bash
set -euo pipefail

# Snyk Security Scan Script
# Usage: ./snyk-scan.sh [project] [severity] [fail-on]

SNYK_TOKEN="${SNYK_TOKEN:-${SNYK_API_TOKEN:-}}"
SNYK_ORG="${SNYK_ORG:-}"
SNYK_PROJECT="${SNYK_PROJECT:-premium-service}"
SNYK_SEVERITY_THRESHOLD="${SNYK_SEVERITY_THRESHOLD:-high}"
SNYK_FAIL_ON="${SNYK_FAIL_ON:-all}"
SNYK_RESULTS_FORMAT="${SNYK_RESULTS_FORMAT:-json}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Snyk Security Scan"
echo "=========================================="
echo "Project: ${SNYK_PROJECT}"
echo "Organization: ${SNYK_ORG:-default}"
echo "Severity: ${SNYK_SEVERITY_THRESHOLD}"
echo "Fail on: ${SNYK_FAIL_ON}"
echo "=========================================="

# Check if Snyk CLI is installed
if ! command -v snyk &> /dev/null; then
  echo "Installing Snyk CLI..."
  npm install -g snyk
fi

# Set Snyk authentication
if [ -n "${SNYK_TOKEN}" ]; then
  snyk auth "${SNYK_TOKEN}"
else
  echo "ERROR: SNYK_TOKEN is not set"
  exit 1
fi

# Set organization if provided
SNYK_ORG_ARGS=""
if [ -n "${SNYK_ORG}" ]; then
  SNYK_ORG_ARGS="--org=${SNYK_ORG}"
fi

# Determine scan type based on project
detect_scan_type() {
  local project_path="$1"

  if [ -f "${project_path}/package.json" ]; then
    echo "npm"
  elif [ -f "${project_path}/requirements.txt" ] || [ -f "${project_path}/Pipfile" ]; then
    echo "pip"
  elif [ -f "${project_path}/go.mod" ]; then
    echo "go"
  elif [ -f "${project_path}/pom.xml" ]; then
    echo "maven"
  elif [ -f "${project_path}/build.gradle" ]; then
    echo "gradle"
  elif [ -f "${project_path}/Dockerfile" ]; then
    echo "docker"
  else
    echo "auto"
  fi
}

# Run Snyk test
run_snyk_test() {
  local target="$1"
  local scan_type="$2"

  echo ""
  echo "Running Snyk test on: ${target}"
  echo "Scan type: ${scan_type}"
  echo ""

  local args=(
    "test"
    "${target}"
    --severity-threshold="${SNYK_SEVERITY_THRESHOLD}"
    --fail-on="${SNYK_FAIL_ON}"
    --output-format="${SNYK_RESULTS_FORMAT}"
    --json-file-output=snyk-results.json
    ${SNYK_ORG_ARGS}
  )

  # Add scan type specific options
  case "${scan_type}" in
    npm)
      args+=(--package-manager=npm)
      ;;
    pip)
      args+=(--package-manager=pip)
      ;;
    go)
      args+=(--package-manager=go)
      ;;
    maven)
      args+=(--package-manager=maven)
      ;;
    gradle)
      args+=(--package-manager=gradle)
      ;;
  esac

  # Run the scan
  if snyk "${args[@]}"; then
    echo ""
    echo -e "${GREEN}✅ Snyk test passed - no vulnerabilities found${NC}"
    return 0
  else
    echo ""
    echo -e "${RED}❌ Snyk test found vulnerabilities${NC}"
    return 1
  fi
}

# Run Snyk monitor
run_snyk_monitor() {
  local target="$1"
  local scan_type="$2"

  echo ""
  echo "Running Snyk monitor on: ${target}"

  local args=(
    "monitor"
    "${target}"
    ${SNYK_ORG_ARGS}
  )

  case "${scan_type}" in
    npm)
      args+=(--package-manager=npm)
      ;;
    pip)
      args+=(--package-manager=pip)
      ;;
  esac

  if snyk "${args[@]}"; then
    echo ""
    echo -e "${GREEN}✅ Snyk monitor completed${NC}"
  else
    echo ""
    echo -e "${YELLOW}⚠️ Snyk monitor encountered issues${NC}"
  fi
}

# Generate HTML report
generate_report() {
  if [ -f "snyk-results.json" ]; then
    echo ""
    echo "Generating HTML report..."
    cat snyk-results.json | jq '. | if type == "array" then . else [.] end | .[] | select(.vulnerabilities != null) | .vulnerabilities[] | {id: .id, severity: .severity, title: .title, package: .packageName, fix: .fixedIn}' > vulnerabilities-summary.txt 2>/dev/null || true

    cat << 'EOF' > snyk-report.html
<!DOCTYPE html>
<html>
<head>
  <title>Snyk Security Scan Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1 { color: #333; }
    .summary { background: #f0f0f0; padding: 15px; border-radius: 5px; }
    .critical { color: #d32f2f; font-weight: bold; }
    .high { color: #f57c00; font-weight: bold; }
    .medium { color: #fbc02d; }
    .low { color: #4caf50; }
    table { border-collapse: collapse; width: 100%; margin-top: 20px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #4caf50; color: white; }
    tr:nth-child(even) { background-color: #f2f2f2; }
  </style>
</head>
<body>
  <h1>🔒 Snyk Security Scan Report</h1>
  <div class="summary">
    <p><strong>Scan Date:</strong> $(date -u +"%Y-%m-%d %H:%M:%S UTC")</p>
    <p><strong>Project:</strong> ${SNYK_PROJECT}</p>
  </div>
  <h2>Vulnerability Summary</h2>
  <div id="summary"></div>
</body>
</html>
EOF
    echo "Report generated: snyk-report.html"
  fi
}

# Main execution
main() {
  local targets=("$@")
  local exit_code=0

  if [ ${#targets[@]} -eq 0 ]; then
    # Default targets
    targets=("." "frontend" "backend")
  fi

  for target in "${targets[@]}"; do
    if [ -d "${target}" ] || [ -f "${target}/package.json" ] || [ -f "${target}/requirements.txt" ]; then
      scan_type=$(detect_scan_type "${target}")

      if run_snyk_test "${target}" "${scan_type}"; then
        run_snyk_monitor "${target}" "${scan_type}" || true
      else
        exit_code=1
      fi
    else
      echo "Skipping ${target} - not a valid project directory"
    fi
  done

  # Generate reports
  generate_report

  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ All Snyk scans passed${NC}"
  else
    echo -e "${RED}❌ Snyk scans found vulnerabilities${NC}"
  fi
  echo "=========================================="

  exit $exit_code
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  main "$@"
fi