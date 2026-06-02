# Backup Procedures
# Premium Service Directory Platform
# Version: 1.0.0

## Overview

This document outlines the backup and restore procedures for the Premium Service Directory Platform. It covers RDS databases, S3 storage, and other critical data stores.

---

## 1. RDS Backup Procedures

### 1.1 Automated Backups

```yaml
rds_backup:
  # Automated daily backups
  automated_backup:
    enabled: true
    retention_period: 35 days
    backup_window:
      start_time: "03:00"
      end_time: "04:00"
      preference_window: 1h
  
  # Copy to secondary region
  cross_region_backup:
    enabled: true
    destination_region: us-west-2
    retention_period: 35 days
    encryption: aws:rds
  
  # Point-in-time recovery
  pitr:
    enabled: true
    recovery_window: within_35_days
```

### 1.2 Manual Snapshots

```bash
#!/bin/bash
# rds-snapshot.sh

set -e

DB_INSTANCE="premium-directory-primary"
SNAPSHOT_NAME="premium-directory-$(date +%Y%m%d-%H%M)"
REGION="us-east-1"

echo "=== Creating RDS Snapshot: ${SNAPSHOT_NAME} ==="

# Create snapshot
aws rds create-db-snapshot \
  --db-instance-identifier ${DB_INSTANCE} \
  --db-snapshot-identifier ${SNAPSHOT_NAME} \
  --tags Key=Backup,Value=manual Key=CreatedBy,Value=automation \
  --region ${REGION}

# Wait for snapshot to be available
aws rds wait db-snapshot-available \
  --db-snapshot-identifier ${SNAPSHOT_NAME} \
  --region ${REGION}

# Copy to secondary region
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier arn:aws:rds:${REGION}:123456789012:snapshot:${SNAPSHOT_NAME} \
  --target-db-snapshot-identifier ${SNAPSHOT_NAME}-us-west-2 \
  --target-region us-west-2 \
  --region ${REGION}

# Tag snapshot
aws rds add-tags-to-resource \
  --resource-name arn:aws:rds:${REGION}:123456789012:snapshot:${SNAPSHOT_NAME} \
  --tags "[{\"Key\": \"Expiration\", \"Value\": \"2024-12-31\"}]" \
  --region ${REGION}

echo "=== Snapshot Complete ==="
```

### 1.3 Backup Verification

```bash
#!/bin/bash
# verify-rds-backup.sh

set -e

SNAPSHOT_ID="premium-directory-20240115"
REGION="us-east-1"

echo "=== Verifying RDS Backup ==="

# Get snapshot details
aws rds describe-db-snapshots \
  --db-snapshot-identifier ${SNAPSHOT_ID} \
  --region ${REGION}

# Verify encryption
aws rds describe-db-snapshots \
  --db-snapshot-identifier ${SNAPSHOT_ID} \
  --query 'DBSnapshots[0].Encrypted' \
  --region ${REGION}

# Restore test (creates new instance)
echo "Testing restore to new instance..."
aws rds restore-db-instance-from-snapshot \
  --db-instance-identifier premium-directory-restore-test \
  --snapshot-identifier ${SNAPSHOT_ID} \
  --db-instance-class db.t3.medium \
  --region ${REGION}

# Wait for instance
aws rds wait db-instance-available \
  --db-instance-identifier premium-directory-restore-test \
  --region ${REGION}

# Verify data integrity
psql -h premium-directory-restore-test.xxxx.us-east-1.rds.amazonaws.com \
  -U admin \
  -d premium_directory \
  -c "SELECT count(*) FROM users;"

# Clean up test instance
aws rds delete-db-instance \
  --db-instance-identifier premium-directory-restore-test \
  --skip-final-snapshot \
  --region ${REGION}

echo "=== Backup Verification Complete ==="
```

---

## 2. S3 Backup Procedures

### 2.1 S3 Configuration

```yaml
s3_backup:
  versioning: true
  mfa_delete: enabled
  
  replication:
    enabled: true
    rules:
      - id: replicate-all
        status: Enabled
        priority: 1
        filter:
          prefix: ""
        destination:
          bucket: arn:aws:s3:::premium-directory-assets-us-west-2
          storage_class: STANDARD_IA
          encryption: SSE-S3
          account: "123456789012"
        
  lifecycle_rules:
    - id: move-to-glacier-after-30
      status: Enabled
      filter:
        prefix: "uploads/"
      transitions:
        - days: 30
          storage_class: GLACIER
        - days: 365
          storage_class: DEEP_ARCHIVE
      
    - id: abort-incomplete-uploads
      status: Enabled
      abort_incomplete_multipart_upload_days: 7
```

### 2.2 S3 Backup Script

```bash
#!/bin/bash
# s3-backup.sh

set -e

SOURCE_BUCKET="premium-directory-assets"
DEST_BUCKET="premium-directory-assets-backup"
REGION="us-east-1"

echo "=== Starting S3 Backup ==="

# List objects for verification
aws s3api list-objects \
  --bucket ${SOURCE_BUCKET} \
  --query 'length(Contents)' \
  --region ${REGION}

# Sync critical directories
echo "Syncing user uploads..."
aws s3 sync s3://${SOURCE_BUCKET}/uploads/ s3://${DEST_BUCKET}/uploads/ \
  --region ${REGION} \
  --exclude "*" \
  --include "*.jpg" \
  --include "*.png" \
  --storage-class STANDARD_IA

echo "Syncing listing assets..."
aws s3 sync s3://${SOURCE_BUCKET}/listings/ s3://${DEST_BUCKET}/listings/ \
  --region ${REGION} \
  --storage-class STANDARD_IA

echo "Syncing database backups..."
aws s3 sync s3://${SOURCE_BUCKET}/db-backups/ s3://${DEST_BUCKET}/db-backups/ \
  --region ${REGION} \
  --storage-class GLACIER

# Verify replication
echo "Verifying replication..."
aws s3api list-objects \
  --bucket ${DEST_BUCKET} \
  --query 'length(Contents)' \
  --region us-west-2

echo "=== S3 Backup Complete ==="
```

### 2.3 S3 Restore Procedure

```bash
#!/bin/bash
# s3-restore.sh

set -e

SOURCE_BUCKET="premium-directory-assets-backup"
DEST_BUCKET="premium-directory-assets"
PREFIX="${1:-}"  # Optional prefix argument

if [ -z "${PREFIX}" ]; then
  echo "Usage: $0 <prefix>"
  echo "Restoring all data..."
fi

echo "=== Starting S3 Restore: ${PREFIX} ==="

# Restore from Glacier if needed
aws s3api restore-object \
  --bucket ${SOURCE_BUCKET} \
  --key "${PREFIX}" \
  --restore-request '{"Days": 7, "GlacierJobParameters": {"Tier": "Standard"}}' \
  --region us-west-2

# Copy back to production bucket
aws s3 cp s3://${SOURCE_BUCKET}/${PREFIX} s3://${DEST_BUCKET}/${PREFIX} \
  --region us-west-2 \
  --storage-class STANDARD

echo "=== S3 Restore Complete ==="
```

---

## 3. Database-Specific Backup Procedures

### 3.1 PostgreSQL Logical Backup

```bash
#!/bin/bash
# pg-dump.sh

set -e

DB_HOST="premium-directory.xxxx.us-east-1.rds.amazonaws.com"
DB_PORT="5432"
DB_NAME="premium_directory"
DB_USER="backup_user"
S3_BUCKET="premium-directory-assets"
DATE=$(date +%Y%m%d-%H%M)

echo "=== Starting PostgreSQL Backup ==="

# Create backup directory
mkdir -p /tmp/backup/${DATE}

# Run pg_dump
pg_dump -h ${DB_HOST} \
  -p ${DB_PORT} \
  -U ${DB_USER} \
  -d ${DB_NAME} \
  -Fc \
  -f /tmp/backup/${DATE}/premium_directory.dump

# Compress
tar -czf /tmp/backup/${DATE}/premium_directory.tar.gz -C /tmp/backup/${DATE} premium_directory.dump

# Upload to S3
aws s3 cp /tmp/backup/${DATE}/premium_directory.tar.gz \
  s3://${S3_BUCKET}/db-backups/${DATE}/

# Verify upload
aws s3 ls s3://${S3_BUCKET}/db-backups/${DATE}/

# Cleanup
rm -rf /tmp/backup/${DATE}

echo "=== PostgreSQL Backup Complete ==="
```

### 3.2 Incremental Backup (WAL)

```bash
#!/bin/bash
# pg-wal-archive.sh

set -e

DB_HOST="premium-directory.xxxx.us-east-1.rds.amazonaws.com"
S3_BUCKET="premium-directory-assets"
WAL_DIR="/tmp/wal_archive"
DATE=$(date +%Y%m%d)

echo "=== Starting WAL Archive ==="

mkdir -p ${WAL_DIR}/${DATE}

# WAL archiving is configured in RDS parameter group
# This script handles manual WAL archiving for additional safety

# Connect and execute pg_switch_wal (or pg_xlog_switch for older versions)
psql -h ${DB_HOST} -U postgres -d postgres << EOF
SELECT pg_switch_wal();
EOF

# Archive WAL files
for wal_file in $(ls ${WAL_DIR}); do
  aws s3 cp ${WAL_DIR}/${wal_file} s3://${S3_BUCKET}/wal-archive/${DATE}/
done

echo "=== WAL Archive Complete ==="
```

### 3.3 Point-in-Time Recovery

```bash
#!/bin/bash
# pitr-restore.sh

set -e

TARGET_TIME="2024-01-15T10:30:00+00:00"
NEW_INSTANCE="premium-directory-pitr"
DB_SUBNET_GROUP="db-subnet-group-production"
REGION="us-east-1"

echo "=== Starting Point-in-Time Recovery ==="
echo "Target time: ${TARGET_TIME}"

# Restore to new instance
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier premium-directory-primary \
  --target-db-instance-identifier ${NEW_INSTANCE} \
  --restore-time ${TARGET_TIME} \
  --db-instance-class db.t3.large \
  --db-subnet-group-name ${DB_SUBNET_GROUP} \
  --region ${REGION} \
  --no-multi-az \
  --tags Key=Restore,Value=pitr Key=RequestedTime,Value=${TARGET_TIME}

# Wait for instance to be available
echo "Waiting for instance to be available..."
aws rds wait db-instance-available \
  --db-instance-identifier ${NEW_INSTANCE} \
  --region ${REGION}

# Get endpoint
ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier ${NEW_INSTANCE} \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text \
  --region ${REGION})

echo "Restored instance endpoint: ${ENDPOINT}"

# Verify data
echo "Verifying restored data..."
psql -h ${ENDPOINT} -U admin -d premium_directory << EOF
SELECT count(*) as user_count FROM users;
SELECT count(*) as listing_count FROM listings;
SELECT count(*) as payment_count FROM payments;
SELECT max(created_at) as last_transaction FROM payments;
EOF

echo "=== PITR Recovery Complete ==="
```

---

## 4. ElastiCache Backup Procedures

### 4.1 Redis Backup

```yaml
elasticache_backup:
  automatic_backup:
    enabled: true
    retention_days: 7
    daily_backup_window:
      start_time: "03:00"
      end_time: "04:00"
  
  manual_snapshots:
    enabled: true
    retention_days: 35
```

```bash
#!/bin/bash
# elasticache-backup.sh

set -e

REPLICATION_GROUP="premium-redis"
SNAPSHOT_NAME="premium-redis-$(date +%Y%m%d-%H%M)"
REGION="us-east-1"

echo "=== Starting ElastiCache Backup ==="

# Create manual snapshot
aws elasticache create-snapshot \
  --replication-group-id ${REPLICATION_GROUP} \
  --snapshot-name ${SNAPSHOT_NAME} \
  --tags Key=Backup,Value=manual Key=CreatedBy,Value=automation \
  --region ${REGION}

# Wait for snapshot to be available
aws elasticache wait snapshot-available \
  --snapshot-name ${SNAPSHOT_NAME} \
  --region ${REGION}

# Copy to secondary region
aws elasticache copy-snapshot \
  --source-snapshot-name ${SNAPSHOT_NAME} \
  --target-snapshot-name ${SNAPSHOT_NAME}-us-west-2 \
  --target-region us-west-2 \
  --region ${REGION}

echo "=== ElastiCache Backup Complete ==="
```

### 4.2 Redis Restore

```bash
#!/bin/bash
# elasticache-restore.sh

set -e

SNAPSHOT_ID="premium-redis-20240115"
NEW_REPLICATION_GROUP="premium-redis-restored"
REGION="us-east-1"

echo "=== Starting ElastiCache Restore ==="

# Restore from snapshot to new replication group
aws elasticache restore-from-snapshot \
  --replication-group-id ${NEW_REPLICATION_GROUP} \
  --snapshot-name ${SNAPSHOT_ID} \
  --node-group-id "0001" \
  --primary-cluster-id premium-redis-restored-001 \
  --region ${REGION}

# Wait for replication group to be available
aws elasticache wait replication-group-available \
  --replication-group-id ${NEW_REPLICATION_GROUP} \
  --region ${REGION}

# Get endpoint
ENDPOINT=$(aws elasticache describe-replication-groups \
  --replication-group-id ${NEW_REPLICATION_GROUP} \
  --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Address' \
  --output text \
  --region ${REGION})

echo "Restored cluster endpoint: ${ENDPOINT}"

echo "=== ElastiCache Restore Complete ==="
```

---

## 5. Backup Verification

### 5.1 Backup Integrity Check

```bash
#!/bin/bash
# backup-integrity.sh

set -e

S3_BUCKET="premium-directory-assets"
DATE="${1:-$(date +%Y%m%d)}"

echo "=== Verifying Backup Integrity ==="

# Check S3 backup
echo "Checking S3 backup for ${DATE}..."
aws s3 ls s3://${S3_BUCKET}/db-backups/${DATE}/

# Verify file size
SIZE=$(aws s3api head-object \
  --bucket ${S3_BUCKET} \
  --key db-backups/${DATE}/premium_directory.tar.gz \
  --query 'ContentLength' \
  --output text)

if [ ${SIZE} -lt 1000 ]; then
  echo "ERROR: Backup file too small, possible corruption"
  exit 1
fi

# Verify checksum (if stored)
aws s3api get-object-attributes \
  --bucket ${S3_BUCKET} \
  --key db-backups/${DATE}/premium_directory.tar.gz \
  --object-attributes "ETag,Checksum,Sparta"

echo "=== Backup Integrity Verified ==="
```

### 5.2 Recovery Test Schedule

```yaml
recovery_tests:
  frequency:
    weekly: ["ElastiCache"]
    monthly: ["RDS snapshot restore", "S3 integrity"]
    quarterly: ["Full disaster recovery drill"]
    
  process:
    - name: "Identify backup to test"
      method: "Select most recent successful backup"
      
    - name: "Restore to isolated environment"
      method: "Create new instance, do not overwrite production"
      
    - name: "Verify data integrity"
      method: "Compare record counts, checksums"
      
    - name: "Verify application functionality"
      method: "Run synthetic transactions"
      
    - name: "Document results"
      method: "Complete recovery test report"
      
    - name: "Cleanup"
      method: "Delete test resources, update documentation"
```

### 5.3 Recovery Test Report Template

```markdown
# Backup Recovery Test Report

**Test Date**: [Date]
**Backup Date**: [Date of backup tested]
**Tester**: [Name]

## Test Results

### Backup Verification
- [ ] Backup file exists
- [ ] File size reasonable
- [ ] S3 encryption verified
- [ ] Cross-region copy successful (if applicable)

### Restore Process
- [ ] Restore initiated successfully
- [ ] Restore completed within expected time
- [ ] Instance accessible after restore

### Data Verification
| Table | Record Count | Status |
|-------|--------------|--------|
| users | [count] | [Pass/Fail] |
| listings | [count] | [Pass/Fail] |
| payments | [count] | [Pass/Fail] |

### Application Verification
- [ ] API endpoints accessible
- [ ] Authentication working
- [ ] Write operations successful

### Performance
- Restore time: [X minutes]
- Data verification time: [X minutes]

## Issues Encountered
[Description of any issues]

## Recommendations
[Any recommendations for improvement]

## Sign-off
Tester: [Name]
Date: [Date]
Approval: [Manager Name]
```

---

## 6. Backup Monitoring and Alerts

### 6.1 CloudWatch Alarms

```yaml
backup_alarms:
  rds:
    - name: RDSSnapshotAvailable
      metric: DBInstanceSnapshotCreateCompleted
      threshold: 1 per day
      action: SNS notification
      
    - name: RDSBackupRetentionLow
      metric: BinLogDiskUsage
      threshold: > 80 percent
      action: PagerDuty alert
      
    - name: RDSFailedBackup
      metric: BackupFailed
      threshold: 1
      action: immediate notification
      
  s3:
    - name: S3BackupSyncFailed
      metric: 5XXError
      threshold: 3 consecutive
      action: SNS notification
      
    - name: S3ReplicationLag
      metric: ReplicationLatency
      threshold: > 300 seconds
      action: SNS notification
      
  elasticache:
    - name: ElastiCacheBackupFailed
      metric: BackupFailed
      threshold: 1
      action: PagerDuty alert
      
    - name: ElastiCacheSnapshotLag
      metric: ReplicationLag
      threshold: > 60 seconds
      action: SNS notification
```

### 6.2 Backup Status Dashboard

```yaml
backup_monitoring:
  dashboard:
    name: "Backup Status"
    refresh: 5m
    
    panels:
      - title: "RDS Backup Status"
        type: stat
        metrics:
          - last_successful_backup_time
          - backup_retention_days
          - snapshot_count
        
      - title: "S3 Replication Status"
        type: timeseries
        metrics:
          - replication_lag_seconds
          - sync_failures
          
      - title: "ElastiCache Backup Status"
        type: stat
        metrics:
          - last_snapshot_time
          - snapshot_count
          - replication_lag
          
      - title: "Backup Success Rate"
        type: gauge
        metrics:
          - backup_success_rate_percent
          - target: 100
```

---

## 7. Retention Schedule

### 7.1 Data Retention Matrix

| Data Type | Short-term Retention | Long-term Retention | Archive | Destruction |
|-----------|---------------------|--------------------|--------|-------------|
| RDS Automated Backups | 35 days | N/A | N/A | Auto |
| RDS Manual Snapshots | 35 days | 7 years (compliance) | Glacier | Manual |
| S3 Standard | Current | 1 year | Glacier | Lifecycle |
| S3 Standard-IA | 30 days | 1 year | Deep Archive | Lifecycle |
| ElastiCache Snapshots | 7 days | 35 days | N/A | Auto |
| Database WAL | 7 days | 35 days | Glacier | Auto |
| Application Logs | 90 days | 1 year | Glacier | Lifecycle |
| Security Logs | 3 years | 7 years | Glacier | Manual |
| Audit Logs | 7 years | 7 years | Deep Archive | Manual |

### 7.2 Lifecycle Policies

```yaml
lifecycle_policies:
  # S3 Intelligent Tiering
  intelligent_tiering:
    enabled: true
    # Automatically moves objects not accessed for 90 days to cheaper tiers
    
  # Database backups
  database_backups:
    rds:
      - id: delete-after-35
        status: Enabled
        filter:
          tag: Backup=automated
        expiration:
          days: 35
          
    manual_snapshots:
      - id: retain-7years
        status: Enabled
        filter:
          tag: Compliance=true
        expiration:
          days: 2555  # ~7 years
          
  # Log retention
  logs:
    application:
      - id: glacier-after-90
        status: Enabled
        filter:
          prefix: "logs/application/"
        transitions:
          - days: 90
            storage_class: GLACIER
          - days: 365
            storage_class: DEEP_ARCHIVE
            
    security:
      - id: deep-archive-after-1y
        status: Enabled
        filter:
          prefix: "logs/security/"
        transitions:
          - days: 365
            storage_class: DEEP_ARCHIVE
```

---

## 8. Backup Restoration Contacts

| Role | Name | Contact | Responsibility |
|------|------|---------|----------------|
| Backup Lead | [Name] | [Phone] | Overall backup coordination |
| DBA | [Name] | [Phone] | RDS backup/restore |
| Storage Lead | [Name] | [Phone] | S3 backup/restore |
| Cache Lead | [Name] | [Phone] | ElastiCache backup/restore |
| AWS Support | - | [Case #] | Infrastructure issues |

---

## 9. Emergency Contacts

| Role | Name | Contact | Availability |
|------|------|---------|--------------|
| DR Team Lead | [Name] | [Phone] | 24/7 |
| AWS TAM | [Name] | [Phone] | Business hours + on-call |
| Database Architect | [Name] | [Phone] | 24/7 |
| Security Team | - | [Email] | 24/7 |

---

*Document Version: 1.0.0*
*Last Updated: 2024*
*Next Review: Monthly*
*Classification: Internal - Restricted*