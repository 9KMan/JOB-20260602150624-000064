#!/bin/bash
set -euo pipefail

# Slack Notification Script
# Usage: ./slack-notify.sh [status] [message] [details]

SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-${SLACK_WEBHOOK_URL}}"
CHANNEL="${SLACK_CHANNEL:-#deployments}"
USERNAME="${SLACK_USERNAME:-GitHub Actions}"
ICON_SUCCESS="${SLACK_ICON_SUCCESS:-:white_check_mark:}"
ICON_FAILURE="${SLACK_ICON_FAILURE:-:x:"
ICON_WARNING="${SLACK_ICON_WARNING:-:warning:"
ICON_INFO="${SLACK_ICON_INFO:-:information_source:}"
ICON_DEPLOY="${SLACK_ICON_DEPLOY:-:rocket:}"
ICON_BACKUP="${SLACK_ICON_BACKUP:-:floppy_disk:}"
ICON_SECURITY="${SLACK_ICON_SECURITY:-:shield:}"
ICON_BUILD="${SLACK_ICON_BUILD:-:construction:}"

# Default values
STATUS="${1:-info}"
MESSAGE="${2:-}"
DETAILS="${3:-}"
TIMESTAMP="$(date -u +"%Y-%m-%d %H:%M:%S UTC")"
GITHUB_REPOSITORY="${GITHUB_REPOSITORY:-unknown}"
GITHUB_WORKFLOW="${GITHUB_WORKFLOW:-unknown}"
GITHUB_RUN_ID="${GITHUB_RUN_ID:-unknown}"
GITHUB_SHA="${GITHUB_SHA:-unknown}"
GITHUB_ACTOR="${GITHUB_ACTOR:-unknown}"
GITHUB_SERVER_URL="${GITHUB_SERVER_URL:-https://github.com}"

# Colors for attachments
COLOR_SUCCESS="#36a64f"
COLOR_FAILURE="#ff0000"
COLOR_WARNING="#ffcc00"
COLOR_INFO="#439fe0"

# Determine icon and color based on status
case "${STATUS}" in
  success)
    ICON="${ICON_SUCCESS}"
    COLOR="${COLOR_SUCCESS}"
    STATUS_TEXT="Success"
    ;;
  failure)
    ICON="${ICON_FAILURE}"
    COLOR="${COLOR_FAILURE}"
    STATUS_TEXT="Failed"
    ;;
  warning)
    ICON="${ICON_WARNING}"
    COLOR="${COLOR_WARNING}"
    STATUS_TEXT="Warning"
    ;;
  info)
    ICON="${ICON_INFO}"
    COLOR="${COLOR_INFO}"
    STATUS_TEXT="Info"
    ;;
  deploy)
    ICON="${ICON_DEPLOY}"
    COLOR="${COLOR_SUCCESS}"
    STATUS_TEXT="Deployed"
    ;;
  backup)
    ICON="${ICON_BACKUP}"
    COLOR="${COLOR_INFO}"
    STATUS_TEXT="Backup Complete"
    ;;
  security)
    ICON="${ICON_SECURITY}"
    COLOR="${COLOR_WARNING}"
    STATUS_TEXT="Security Scan"
    ;;
  build)
    ICON="${ICON_BUILD}"
    COLOR="${COLOR_INFO}"
    STATUS_TEXT="Build"
    ;;
  *)
    ICON="${ICON_INFO}"
    COLOR="${COLOR_INFO}"
    STATUS_TEXT="${STATUS}"
    ;;
esac

# Build Slack message
build_message() {
  local message="$1"
  local details="$2"

  cat << EOF
{
  "channel": "${CHANNEL}",
  "username": "${USERNAME}",
  "icon_emoji": "${ICON}",
  "attachments": [
    {
      "color": "${COLOR}",
      "blocks": [
        {
          "type": "header",
          "text": {
            "type": "plain_text",
            "text": "${STATUS_TEXT}: ${message}",
            "emoji": true
          }
        },
        {
          "type": "section",
          "fields": [
            {
              "type": "mrkdwn",
              "text": "*Repository:*\n<${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}|${GITHUB_REPOSITORY}>"
            },
            {
              "type": "mrkdwn",
              "text": "*Workflow:*\n${GITHUB_WORKFLOW}"
            },
            {
              "type": "mrkdwn",
              "text": "*Actor:*\n${GITHUB_ACTOR}"
            },
            {
              "type": "mrkdwn",
              "text": "*Commit:*\n\`${GITHUB_SHA:0:7}\`"
            }
          ]
        },
        {
          "type": "context",
          "elements": [
            {
              "type": "mrkdwn",
              "text": "<${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}|View Logs> | ${TIMESTAMP}"
            }
          ]
        }
      ]
    }
  ]
}
EOF
}

# Build message with details
build_message_with_details() {
  local message="$1"
  local details="$2"

  cat << EOF
{
  "channel": "${CHANNEL}",
  "username": "${USERNAME}",
  "icon_emoji": "${ICON}",
  "attachments": [
    {
      "color": "${COLOR}",
      "blocks": [
        {
          "type": "header",
          "text": {
            "type": "plain_text",
            "text": "${STATUS_TEXT}: ${message}",
            "emoji": true
          }
        },
        {
          "type": "section",
          "fields": [
            {
              "type": "mrkdwn",
              "text": "*Repository:*\n<${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}|${GITHUB_REPOSITORY}>"
            },
            {
              "type": "mrkdwn",
              "text": "*Workflow:*\n${GITHUB_WORKFLOW}"
            },
            {
              "type": "mrkdwn",
              "text": "*Actor:*\n${GITHUB_ACTOR}"
            },
            {
              "type": "mrkdwn",
              "text": "*Commit:*\n\`${GITHUB_SHA:0:7}\`"
            }
          ]
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "${details}"
          }
        },
        {
          "type": "context",
          "elements": [
            {
              "type": "mrkdwn",
              "text": "<${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}|View Logs> | ${TIMESTAMP}"
            }
          ]
        }
      ]
    }
  ]
}
EOF
}

# Send notification
send_notification() {
  local payload="$1"

  if [ -z "${SLACK_WEBHOOK_URL}" ]; then
    echo "ERROR: SLACK_WEBHOOK_URL is not set"
    echo "Payload would be:"
    echo "${payload}"
    return 1
  fi

  response=$(curl -s -w "\n%{http_code}" -X POST \
    -H 'Content-Type: application/json' \
    -d "${payload}" \
    "${SLACK_WEBHOOK_URL}")

  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | head -n-1)

  if [ "$http_code" = "200" ]; then
    echo "Slack notification sent successfully"
    return 0
  else
    echo "ERROR: Failed to send Slack notification (HTTP ${http_code})"
    echo "Response: ${body}"
    return 1
  fi
}

# Main execution
main() {
  if [ -z "${MESSAGE}" ]; then
    echo "Usage: slack-notify.sh <status> <message> [details]"
    echo ""
    echo "Status options: success, failure, warning, info, deploy, backup, security, build"
    echo "Examples:"
    echo "  ./slack-notify.sh success \"Deployment succeeded\""
    echo "  ./slack-notify.sh failure \"Build failed\" \"Check build logs\""
    echo "  SLACK_WEBHOOK_URL=https://hooks.slack.com/... ./slack-notify.sh deploy \"Frontend deployed to prod\""
    exit 1
  fi

  local payload
  if [ -n "${DETAILS}" ]; then
    payload=$(build_message_with_details "${MESSAGE}" "${DETAILS}")
  else
    payload=$(build_message "${MESSAGE}")
  fi

  send_notification "${payload}"
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  main "$@"
fi