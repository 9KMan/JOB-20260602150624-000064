# Premium Service Directory Platform — Build Phase

**Lead:** https://www.upwork.com/jobs/~022061752658903002322
**Client:** Premium Service Directory Platform
**Tier:** LARGE | **Budget:** hourly ($25-47/hr, >30hrs/wk, >6mo, expert)

---

## 🎯 Business Problem Solved

A 3-month planning phase produced comprehensive documentation (requirements, process flows, architecture diagrams, security protocols, DB schemas, API specs, mockups). The challenge: execute the build phase without re-litigating decisions, maintaining security-first posture across a complex multi-tenant SaaS on AWS.

**Pain:** Building a platform handling PII/sensitive data with third-party integrations (age verification, payments, CRM) requires airtight security at every layer — infrastructure, API, database, frontend, and third-party bridges. AI-generated code must be security-reviewed before production. DR/BCP must be tested, not just documented.

**Solution delivered:** Bottom-up build execution using AI-native engineering workflow. All code passes security review (OWASP Top 10), automated scanning (Snyk) in CI/CD, and external penetration testing. Infrastructure as Code via Terraform following AWS Well-Architected Framework. DR/BCP procedures documented and tested.

**Key differentiators:** AWS Fargate container workload with encrypted RDS, Auth0 JWT + MFA, Cloudflare/WAF/GuardDuty for defense-in-depth, third-party integrations (Yoti/CCBill/Pipedrive) with PCI DSS awareness, full observability via Prometheus/Grafana/CloudWatch.

---

## Quick Start

```bash
# Infrastructure (Terraform)
cd infra/
terraform init
terraform plan -var-file=environments/prod.tfvars
terraform apply -var-file=environments/prod.tfvars

# Backend (NestJS + Python microservices)
cd backend && npm install && npm run start:dev

# Frontend (Next.js)
cd frontend && npm install && npm run dev

# CI/CD — GitHub Actions handles:
#   1. Snyk security scan
#   2. Docker build + push to ECR
#   3. Terraform plan review
#   4. Deploy to AWS Fargate
```

## Tech Stack

`Next.js` · `Tailwind CSS` · `shadcn/ui` · `NestJS` · `Python microservices` · `PostgreSQL RDS (encrypted)` · `Redis` · `AWS Fargate` · `Terraform` · `GitHub Actions` · `Cloudflare` · `AWS WAF` · `Auth0 JWT` · `MFA` · `Prometheus` · `Grafana` · `CloudWatch` · `GuardDuty` · `AWS KMS` · `Secrets Manager` · `Snyk`

## Architecture

- **Frontend:** Next.js + Tailwind + shadcn/ui — responsive, server-rendered
- **Backend:** NestJS (Node.js) + Python microservices — encrypted API layer
- **Database:** PostgreSQL RDS with encryption at rest, Redis encrypted in transit
- **Storage:** S3 with server-side encryption + bucket policies
- **Hosting:** AWS Fargate (Docker), controlled via AWS Control Tower (Mgmt | Log Archive | Audit | Prod | Pre-Prod | Test | Dev)
- **CDN/Security:** Cloudflare + AWS WAF + CloudFront + ALB/NAT
- **Auth:** Auth0 with JWT + MFA support
- **Observability:** Prometheus/Grafana + CloudWatch + CloudTrail + GuardDuty
- **Key Management:** AWS KMS + Secrets Manager + Parameter Store + ACM
- **CI/CD:** GitHub Actions + AWS Systems Manager
- **Third-Party:** Yoti/BlueCheck/Ondato (age verification), Mautic/Pipedrive/HubSpot (CRM), CCBill/Paxum (payments)

## Project Structure

```
├── frontend/            ← Next.js + Tailwind + shadcn/ui
├── backend/
│   ├── nestjs/         ← Node.js microservices (Auth, API Gateway)
│   └── python/        ← Python microservices (data processing, integrations)
├── infra/              ← Terraform IaC (VPC, RDS, Fargate, KMS, IAM)
├── ci/                 ← GitHub Actions workflows (build, scan, deploy)
├── observability/      ← Prometheus + Grafana dashboards, alerting rules
└── docs/               ← DR/BCP procedures, security protocols, API specs
```

## Security Controls

| Layer | Control |
|---|---|
| Infrastructure | Terraform IaC, AWS Control Tower, encryption at rest |
| Network | Cloudflare WAF, AWS WAF, ALB with NAT, TLS 1.2+ |
| Auth | Auth0 JWT + MFA, KMS for keys, Secrets Manager for secrets |
| Data | PostgreSQL RDS encrypted, S3 bucket policies, parameter store |
| CI/CD | Snyk security scan, GitHub Actions approval gates |
| Monitoring | GuardDuty, CloudTrail, CloudWatch — full audit trail |