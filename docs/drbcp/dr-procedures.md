# Disaster Recovery and Business Continuity Procedures
# Premium Service Directory Platform
# Version: 1.0.0

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2024 | Platform Team | Initial release |

---

## 1. Overview

This document establishes the disaster recovery (DR) and business continuity (BC) procedures for the Premium Service Directory Platform. These procedures ensure minimal service disruption and quick recovery in case of catastrophic failures.

### 1.1 Scope

This DR/BC plan covers:
- AWS Cloud infrastructure (ECS, RDS, S3, ElastiCache, CloudFront)
- Backend API services (NestJS)
- Frontend applications (Next.js)
- Supporting services (Auth0, payment gateways)

### 1.2 DR Philosophy

We follow a **pilot light** approach for disaster recovery, maintaining pre-provisioned standby infrastructure that can be quickly activated. For critical systems, we maintain active-active multi-region deployment.

---

## 2. Recovery Objectives

### 2.1 Recovery Time Objective (RTO)

| Priority | System | RTO | Description |
|----------|--------|-----|-------------|
| P1 Critical | Core API, Authentication | 15 minutes | 99.95% availability |
| P2 High | User-facing features | 1 hour | 99.9% availability |
| P3 Medium | Administrative functions | 4 hours | 99.5% availability |
| P4 Low | Reporting, analytics | 24 hours | 99% availability |

### 2.2 Recovery Point Objective (RPO)

| Priority | System | RPO | Description |
|----------|--------|-----|-------------|
| P1 Critical | User data, listings | 1 hour | Maximum 1 hour data loss |
| P2 High | Payments, transactions | 15 minutes | Maximum 15 minutes data loss |
| P3 Medium | Session data, cache | 4 hours | Can tolerate 4-hour data loss |
| P4 Low | Analytics, reports | 24 hours | Batch-based recovery acceptable |

### 2.3 Recovery Location

- **Primary Region**: us-east-1 (Northern Virginia)
- **Secondary Region**: us-west-2 (Oregon)
- **Tertiary Backup**: AWS GovCloud (for compliance data)

---

## 3. DR Architecture

### 3.1 Infrastructure Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRIMARY REGION (us-east-1)               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    VPC (10.0.0.0/16)                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │  Public Subnet│ │ Private Subnet│ │  Private Subnet  │  │   │
│  │  │ (ALB, WAF)   │ │(ECS Services)│  │ (RDS, ElastiCache)│  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │  ECS Cluster │ │  ECS Cluster │ │      RDS        │  │   │
│  │  │  (Backend)   │ │  (Frontend)  │ │  (Primary DB)   │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │  ElastiCache│ │      S3      │ │    CloudFront   │  │   │
│  │  │   (Redis)   │ │   (Assets)   │ │   (CDN)         │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    (Async Replication)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SECONDARY REGION (us-west-2)                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    VPC (10.1.0.0/16)                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │  Public Subnet│ │ Private Subnet│ │  Private Subnet  │  │   │
│  │  │ (ALB, WAF)   │ │(ECS Services)│  │  (RDS Replica)  │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │  ECS Cluster │ │  ECS Cluster │ │      RDS        │  │   │
│  │  │  (Standby)   │ │  (Standby)   │ │  (Read Replica) │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │  ElastiCache│ │      S3      │ │    CloudFront   │  │   │
│  │  │ (Standby)   │ │(Cross-Region)│ │   (Standby)     │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Failover Strategy

```yaml
failover_strategy:
  method: pilot_light_with_automatic_failover
  
  # Pilot Light Configuration
  pilot_light:
    always_on:
      - RDS Read Replica (us-west-2)
      - S3 Cross-Region Replication
      - ElastiCache Redis Replica
      - CloudFront Distribution
    
    warm_standby:
      - ECS Services (scaled to 10% during normal)
      - ALB Target Group (registered but 0 weight)
    
    cold_standby:
      - Full ECS Cluster (ready to scale)
      - Complete VPC infrastructure
  
  # Automatic Failover Triggers
  triggers:
    - type: availability_zone_failure
      detection: AWS Health Dashboard
      action: automatic
      
    - type: region_failure
      detection: Health Check + CloudWatch
      action: automatic (with manual confirmation for data)
      
    - type: rds_failover
      detection: RDS Event + Application Error Rate
      action: automatic
      
    - type: manual
      approval: required (DR Team Lead)
```

---

## 4. Failover Procedures

### 4.1 Automatic Failover

#### Trigger: RDS Primary Failure

```
Timeline: T+0 to T+2 minutes

1. T+0:00 - RDS detects primary failure
   - RDS initiates automatic failover to read replica
   - Event published to CloudWatch Events
   
2. T+0:30 - CloudWatch alarm triggers
   - Alarm: "RDSReplicaLag" metric breach
   - Action: Invoke Lambda function
   
3. T+0:45 - Lambda executes
   - Update Route53 DNS to point to new RDS endpoint
   - Update Secrets Manager with new connection string
   - Trigger ECS service restart (if needed)
   
4. T+1:00 - Application recovery
   - ECS tasks reconnect using updated secrets
   - ElastiCache Redis automatically reconnects
   - Health checks verify recovery
   
5. T+2:00 - Monitoring
   - Enhanced monitoring enabled
   - Alert acknowledgment required
```

#### Trigger: Region Failure

```
Timeline: T+0 to T+15 minutes

1. T+0:00 - Detection
   - Multi-point health check failure
   - AWS Service Health Dashboard notification
   - Synthetic transaction failure
   
2. T+0:30 - DR Team Alert
   - PagerDuty alert to DR Team
   - War room conference call initiated
   - Initial assessment by on-call engineer
   
3. T+2:00 - Failover Decision
   - DR Team Lead authorizes failover
   - DNS failover to us-west-2 initiated
   
4. T+5:00 - Infrastructure Activation
   - ECS services scaled up in us-west-2
   - ALB weights shifted to secondary region
   - CloudFront origin failover triggered
   
5. T+10:00 - Database Promotion
   - RDS read replica promoted to primary
   - Connection string update in Secrets Manager
   - Database connectivity verified
   
6. T+15:00 - Service Verification
   - Synthetic transaction test passes
   - Real user traffic verified
   - Monitoring enhanced to secondary region
```

### 4.2 Manual Failover Procedures

#### Step 1: Pre-Failover Verification

```bash
# Verify DR infrastructure status
aws ec2 describe-vpcs --region us-west-2 --filters Name=vpc-id,Values=vpc-xxxx

# Check RDS replica status
aws rds describe-db-instances --region us-west-2 --db-instance-identifier premium-directory-replica

# Verify S3 replication status
aws s3api head-object --bucket premium-directory-assets-us-west-2 --key manifests/latest.json

# Check ElastiCache replication
aws elasticache describe-replication-groups --replication-group-id premium-redis-replica
```

#### Step 2: Initiate Failover

```bash
#!/bin/bash
# failover-initiate.sh

set -e

REGION_PRIMARY="us-east-1"
REGION_SECONDARY="us-west-2"
DNS_ZONE="premium-directory.com"

echo "=== Initiating Failover to ${REGION_SECONDARY} ==="

# 1. Update Route53 DNS
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://dns-failover.json

# 2. Promote RDS replica
aws rds promote-read-replica \
  --db-instance-identifier premium-directory-replica \
  --region ${REGION_SECONDARY}

# 3. Wait for RDS promotion to complete
aws rds wait db-instance-available \
  --db-instance-identifier premium-directory-replica \
  --region ${REGION_SECONDARY}

# 4. Update application secrets
aws secretsmanager update-secret \
  --secret-id prod/database-connection-string \
  --secret-string file://new-connection-string.json \
  --region ${REGION_SECONDARY}

# 5. Scale up ECS services
aws ecs update-service \
  --cluster backend-cluster \
  --service backend-api \
  --desired-count 10 \
  --region ${REGION_SECONDARY}

aws ecs update-service \
  --cluster frontend-cluster \
  --service frontend-app \
  --desired-count 5 \
  --region ${REGION_SECONDARY}

echo "=== Failover Complete ==="
```

#### Step 3: Post-Failover Verification

```bash
#!/bin/bash
# failover-verify.sh

set -e

echo "=== Post-Failover Verification ==="

# API Health Check
curl -f https://api.premium-directory.com/health || exit 1

# Database Connectivity
psql -h $DB_HOST -U $DB_USER -d premium_directory -c "SELECT 1" || exit 1

# Critical Functionality
curl -f https://api.premium-directory.com/api/v1/listings | jq '.data | length' || exit 1

# Payment Processing
curl -f https://api.premium-directory.com/api/v1/payments/health || exit 1

echo "=== All Checks Passed ==="
```

---

## 5. Recovery Procedures

### 5.1 Database Recovery

#### RDS Recovery Options

```yaml
recovery_options:
  point_in_time_recovery:
    enabled: true
    backup_retention: 35 days
    recovery_window: any_point_within_retention
    
  snapshot_recovery:
    enabled: true
    snapshot_copy_to_secondary: true
    automated_snapshots: daily
    
  cross_region_replication:
    enabled: true
    replica_region: us-west-2
    encryption: aws:rds
```

#### PITR Recovery Procedure

```bash
#!/bin/bash
# restore-pitr.sh

TARGET_TIME="2024-01-15T10:30:00Z"
INSTANCE_ID="premium-directory-recovery"
SUBNET_GROUP="db-subnet-group-production"

echo "=== Restoring RDS to point in time: ${TARGET_TIME} ==="

# Restore to new instance (PITR creates new instance)
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier premium-directory-primary \
  --target-db-instance-identifier ${INSTANCE_ID} \
  --restore-time ${TARGET_TIME} \
  --db-subnet-group-name ${SUBNET_GROUP} \
  --region us-east-1

# Wait for instance to be available
aws rds wait db-instance-available \
  --db-instance-identifier ${INSTANCE_ID} \
  --region us-east-1

# Update application to point to new instance
# (Implementation details in runbook)

echo "=== PITR Restore Complete ==="
```

### 5.2 ECS Recovery

```yaml
ecs_recovery:
  task_definition_rollback:
    enabled: true
    previous_version_retention: 10
    
  service_redeployment:
    minimum_healthy_percent: 50
    maximum_percent: 200
    
  auto_scaling:
    cpu_threshold: 75
    memory_threshold: 80
    scale_in_cooldown: 300s
    scale_out_cooldown: 60s
```

#### ECS Service Recovery

```bash
#!/bin/bash
# ecs-recover.sh

CLUSTER="backend-cluster"
SERVICE="backend-api"
REGION="us-east-1"

echo "=== ECS Service Recovery ==="

# Force new deployment
aws ecs update-service \
  --cluster ${CLUSTER} \
  --service ${SERVICE} \
  --force-new-deployment \
  --region ${REGION}

# Wait for service to stabilize
aws ecs wait services-stable \
  --cluster ${CLUSTER} \
  --services ${SERVICE} \
  --region ${REGION}

# Verify task count
aws ecs describe-services \
  --cluster ${CLUSTER} \
  --services ${SERVICE} \
  --region ${REGION}

echo "=== ECS Recovery Complete ==="
```

### 5.3 S3 Recovery

```yaml
s3_recovery:
  versioning: true
  mfa_delete: enabled
  cross_region_replication:
    enabled: true
    destination_region: us-west-2
    destination_storage_class: STANDARD_IA
    
  lifecycle_rules:
    - id: current-version
      prefix: ""
      status: Enabled
      actions:
        - type: Transition
          storage_classes: [GLACIER]
          days: 30
          
    - id: previous-versions
      prefix: ""
      status: Enabled
      noncurrent_versions: true
      noncurrent_days: 90
```

#### S3 Object Recovery

```bash
#!/bin/bash
# s3-recover.sh

BUCKET="premium-directory-assets"
OBJECT_KEY="uploads/listings/2024/01/image-12345.jpg"
VERSION_ID="abc123"

echo "=== S3 Object Recovery ==="

# Restore from versioning
aws s3api restore-object \
  --bucket ${BUCKET} \
  --key ${OBJECT_KEY} \
  --restore-request '{"Days": 7, "GlacierJobParameters": {"Tier": "Standard"}}'

# Or copy from replica bucket
aws s3 cp \
  s3://premium-directory-assets-us-west-2/${OBJECT_KEY} \
  s3://${BUCKET}/${OBJECT_KEY}

echo "=== S3 Recovery Complete ==="
```

### 5.4 ElastiCache Recovery

```yaml
elasticache_recovery:
  replication:
    enabled: true
    automatic_failover: true
    multi_az: true
    
  backup:
    enabled: true
    retention_days: 7
    daily_backup_hour: 03
```

#### Redis Cache Recovery

```bash
#!/bin/bash
# redis-recover.sh

REPLICATION_GROUP="premium-redis"
REGION="us-east-1"

echo "=== ElastiCache Recovery ==="

# Describe current status
aws elasticache describe-replication-groups \
  --replication-group-id ${REPLICATION_GROUP} \
  --region ${REGION}

# Create manual backup
aws elasticache create-snapshot \
  --replication-group-id ${REPLICATION_GROUP} \
  --snapshot-name pre-disaster-$(date +%Y%m%d%H%M) \
  --region ${REGION}

# Restore from snapshot (creates new cluster)
aws elasticache restore-from-snapshot \
  --replication-group-id ${REPLICATION_GROUP}-recovery \
  --snapshot-identifier manual-backup-latest \
  --region ${REGION}

echo "=== ElastiCache Recovery Complete ==="
```

---

## 6. Data Recovery Priority

### 6.1 Recovery Order

| Priority | Data Type | RTO | Procedure |
|----------|-----------|-----|-----------|
| 1 | Authentication (Auth0 backup) | 15 min | Auth0 automatic replication |
| 2 | User data (RDS) | 15 min | Multi-AZ failover |
| 3 | Listings data (RDS) | 30 min | PITR or snapshot |
| 4 | Static assets (S3) | 1 hour | Cross-region copy |
| 5 | Session cache (ElastiCache) | 2 hours | Redis backup restore |
| 6 | Search index (if separate) | 4 hours | Elasticsearch snapshot |

### 6.2 Data Verification

```bash
#!/bin/bash
# verify-data-integrity.sh

echo "=== Data Integrity Verification ==="

# Database checksums
psql -h $DB_HOST -U $DB_USER -d premium_directory -c "SELECT md5(array_agg::text) FROM users;" > /tmp/users_checksum.txt
psql -h $DB_HOST -U $DB_USER -d premium_directory -c "SELECT md5(array_agg::text) FROM listings;" > /tmp/listings_checksum.txt

# Compare with backup
# (Implementation depends on backup verification strategy)

# Count verification
psql -h $DB_HOST -U $DB_USER -d premium_directory -c "SELECT count(*) FROM users; SELECT count(*) FROM listings; SELECT count(*) FROM payments;"

echo "=== Data Integrity Verified ==="
```

---

## 7. Communication Procedures

### 7.1 Incident Communication

```yaml
communication:
  internal:
    - channel: "#dr-incidents"
      audience: Engineering, Operations, Leadership
      frequency: Every 30 minutes during active incident
      
    - channel: "#dr-status"
      audience: All hands
      frequency: Hourly updates
      
  external:
    - channel: Status Page
      url: status.premium-directory.com
      update_frequency: Every 30 minutes
      
    - channel: Customer Communication
      template: dr_customer_template.md
      send_after: 30 minutes of RTO breach
```

### 7.2 Status Page Template

```markdown
## Service Disruption - [Component Name]

**Status**: Investigating
**Started**: [Timestamp]
**Affected**: [Systems/Services]
**ETA**: [If known]

**What we're seeing**:
[Description of the issue]

**What we're doing**:
[Actions being taken]

**Next update**: [Time]
```

---

## 8. Post-Incident Procedures

### 8.1 Recovery Verification Checklist

```markdown
## Post-Recovery Verification Checklist

### Infrastructure
- [ ] All ECS services healthy
- [ ] RDS primary and replicas operational
- [ ] ElastiCache replication group healthy
- [ ] S3 buckets accessible with correct permissions
- [ ] CloudFront distributions serving content

### Application
- [ ] API health checks passing
- [ ] Authentication working
- [ ] Database connections stable
- [ ] Cache hit rates normal
- [ ] No increase in error rates

### Data
- [ ] User data integrity verified
- [ ] Transactional integrity confirmed
- [ ] No data loss detected (RPO verified)
- [ ] Backup restoration tested

### Monitoring
- [ ] All alerts resolved
- [ ] Dashboards showing normal metrics
- [ ] Logs flowing correctly
- [ ] Monitoring sensitivity restored
```

### 8.2 Post-Incident Review

```markdown
## Post-Incident Review Template

**Incident Date**: [Date]
**Duration**: [X hours Y minutes]
**Severity**: [P1/P2/P3/P4]
**Root Cause**: [Description]

### Timeline
- [HH:MM] Event 1
- [HH:MM] Event 2
- ...

### Impact
- Users Affected: [Number]
- Revenue Impact: [Amount]
- Reputation Impact: [Description]

### Response Effectiveness
- Detection Time: [Minutes]
- Response Time: [Minutes]
- Recovery Time: [Minutes vs RTO]

### Root Cause Analysis
[Detailed RCA]

### Lessons Learned
1. [Lesson 1]
2. [Lesson 2]

### Action Items
| Item | Owner | Due Date | Priority |
|------|-------|----------|----------|
| Action 1 | Name | Date | High |
| ... | ... | ... | ... |

### Recommendations
[Improvements to prevent recurrence]
```

---

## 9. DR Testing

### 9.1 Testing Schedule

```yaml
dr_testing:
  frequency:
    tabletop_exercise: quarterly
    backup_restoration_test: monthly
    partial_failover_test: quarterly
    full_failover_test: annually
    
  scenarios:
    - RDS failover (automated)
    - Region failover (manual)
    - S3 restoration
    - ECS recovery
    - Data restoration from backup
```

### 9.2 Failover Test Procedure

```bash
#!/bin/bash
# dr-failover-test.sh

set -e

REGION_PRIMARY="us-east-1"
REGION_SECONDARY="us-west-2"
TEST_USER="dr-test-user-$(date +%s)"

echo "=== Starting DR Failover Test ==="

# 1. Create test data
echo "Creating test data..."
curl -X POST https://api.premium-directory.com/api/v1/test/data \
  -d '{"email": "${TEST_USER}@test.com", "data": "DR_TEST"}'

# 2. Document current state
echo "Documenting current state..."
aws rds describe-db-instances --region ${REGION_PRIMARY} > /tmp/pre-failover-rds.json

# 3. Initiate failover
echo "Initiating failover..."
# (Use actual failover procedure)

# 4. Verify test data accessible
echo "Verifying test data..."
sleep 300  # Wait for failover
curl -f https://api.premium-directory.com/api/v1/test/data/${TEST_USER}

# 5. Verify no data loss
echo "Checking for data loss..."
# (Compare test data timestamps)

# 6. Failback
echo "Initiating failback..."
# (Reverse failover procedure)

# 7. Cleanup
echo "Cleaning up..."
curl -X DELETE https://api.premium-directory.com/api/v1/test/data/${TEST_USER}

echo "=== DR Failover Test Complete ==="
```

---

## 10. DR Infrastructure Checklist

### 10.1 Pre-Deployment Checklist

```markdown
## DR Infrastructure Verification

### Networking
- [ ] VPC configured in secondary region
- [ ] Subnets properly routed
- [ ] Security groups configured
- [ ] NAT Gateway available
- [ ] VPC Peering established (if needed)

### Compute
- [ ] ECS cluster created and sized
- [ ] Auto-scaling configured
- [ ] Task definitions registered
- [ ] Service discovery configured

### Database
- [ ] RDS replica created
- [ ] Automated backups enabled
- [ ] Point-in-time recovery tested
- [ ] Connection strings in Secrets Manager

### Storage
- [ ] S3 buckets with versioning
- [ ] Cross-region replication configured
- [ ] Lifecycle policies set
- [ ] Glacier restore tested

### Cache
- [ ] ElastiCache replication group
- [ ] Multi-AZ enabled
- [ ] Automatic failover tested
- [ ] Backup/restore verified

### DNS
- [ ] Route53 health checks configured
- [ ] Failover record sets created
- [ ] TTL values appropriate
- [ ] DNS propagation verified

### Monitoring
- [ ] CloudWatch alarms configured
- [ ] PagerDuty integration active
- [ ] Dashboards available in secondary region
- [ ] Alert routing verified
```

---

## 11. Key Contacts

| Role | Name | Contact | Escalation |
|------|------|---------|------------|
| DR Team Lead | [Name] | [Phone] | CTO |
| Database Lead | [Name] | [Phone] | DR Team Lead |
| Network Lead | [Name] | [Phone] | DR Team Lead |
| AWS Support | - | [Case #] | All |
| Auth0 Support | - | [Case #] | Auth Lead |

---

*Document Version: 1.0.0*
*Last Updated: 2024*
*Next Review: Quarterly*
*Classification: Internal - Restricted*