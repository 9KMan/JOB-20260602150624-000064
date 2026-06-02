# Specification: AI-native engineer to execute build phase of a Premium Service Directory Platform with security-first mindset. 3-month planning completed. Bottom-up development: Terraform IaC, PostgreSQL RDS encrypted, NestJS/Python microservices, Next.js frontend, third-party integrations (Yoti, CCBill, Pipedrive). AWS Fargate, GitHub Actions, Cloudflare/WAF, Auth0 JWT, Prometheus/Grafana.

## 1. Project Overview

**Project:** AI-native engineer to execute build phase of a Premium Service Directory Platform with security-first mindset. 3-month planning completed. Bottom-up development: Terraform IaC, PostgreSQL RDS encrypted, NestJS/Python microservices, Next.js frontend, third-party integrations (Yoti, CCBill, Pipedrive). AWS Fargate, GitHub Actions, Cloudflare/WAF, Auth0 JWT, Prometheus/Grafana.
**GitHub:** https://github.com/9KMan/JOB-20260602150624-000064
**Lead:** More than 30 hrs/week
**Client:** Premium Service Directory Platform
**Tier:** LARGE
**Budget:** hourly ($25-47/hr, >30hrs/wk, >6mo, expert, complex project)
**Rate:** $25-47/hr

## 2. Technical Stack

nextjs · nestjs · nodejs · python · postgresql · aws · terraform · docker · github-actions · cloudflare · auth0 · redis · s3 · prometheus · grafana · snyk · kms · secrets-manager

## 3. Architecture

- Backend: Python (FastAPI/Flask) REST API
- Database: PostgreSQL with proper indexing
- Cloud: AWS (EC2, S3, Lambda)
- Frontend: Next.js (React framework)
- CI/CD: Automated testing and deployment

### API Design
- RESTful endpoints with JSON request/response
- Authentication via JWT (HS256) or bcrypt
- Middleware for logging, error handling, CORS
- Versioned routes (/api/v1/...)

### Data Layer
- PostgreSQL as primary datastore
- Connection pooling via PGBouncer or similar
- Migration management via Alembic or raw SQL
- Indexes on foreign keys and high-cardinality columns

### Frontend (if applicable)
- Single-page application or server-rendered pages
- Responsive UI with modern CSS/JS framework
- State management for complex client-side logic

## 4. Data Model

### Core Entities
- Define entity schema based on job requirements
- Use UUIDs for primary keys (not auto-increment)
- Add created_at / updated_at timestamps to all tables
- Soft-delete pattern where appropriate

### Relationships
- Foreign key constraints with ON DELETE CASCADE
- Many-to-many via junction tables
- Eager loading for nested relationships in API

## 5. Project Structure

```
├── api/                  # FastAPI / Express routes + schemas
├── models/               # DB models / SQLAlchemy / Prisma
├── services/             # Business logic layer
├── workers/              # Background jobs (Celery, BullMQ, etc.)
├── migrations/           # DB migrations (Alembic / Flyway)
├── tests/                # Unit + integration tests
├── Dockerfile            # Production container
├── docker-compose.yml     # Local dev environment
└── README.md             # Setup instructions
```

## 6. Out of Scope

- Mobile apps (web only unless specified)
- Third-party integrations not mentioned in requirements
- Performance optimization at scale (1M+ users)
- White-label / multi-tenant unless explicitly required

## 7. Acceptance Criteria

- [ ] Database schema created and migrations applied
- [ ] Authentication system working (login/logout/JWT)
- [ ] Frontend UI implemented and responsive
- [ ] CI/CD pipeline configured and passing
- [ ] Security hardening applied (input validation, HTTPS)
- [ ] AI/ML pipeline integrated and functional

**GitHub:** https://github.com/9KMan/JOB-20260602150624-000064
