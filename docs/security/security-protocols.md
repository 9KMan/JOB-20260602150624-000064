# Security Protocols
# Premium Service Directory Platform
# Version: 1.0.0

## Overview

This document outlines the security protocols implemented across the Premium Service Directory Platform. These protocols are designed to protect against OWASP Top 10 vulnerabilities and ensure compliance with industry security standards.

---

## 1. OWASP Top 10 Mitigations

### A1:2017 - Injection

**Risk**: SQL injection, NoSQL injection, OS command injection

**Mitigations Implemented**:

```yaml
# Input sanitization middleware
input_validation:
  enabled: true
  rules:
    - field: "*"
      type: string
      max_length: 10000
      pattern: "^[\\w\\s@.-]*$"
      strip_html: true
    
    - field: "email"
      type: email
      max_length: 255
      normalize_case: lowercase
    
    - field: "phone"
      type: phone
      format: E164
    
    - field: "search_query"
      type: string
      max_length: 500
      strip_sql_keywords: true
      strip_null_bytes: true

# SQL injection prevention
database:
  query_builder: parameterized
  ORM: Prisma (with parameterization)
  raw_queries: forbidden_unless_reviewed
  
# Command injection prevention  
shell_commands:
  forbidden: true
  allowed_shell: none
  execution_timeout_ms: 100
```

**Implementation Details**:
- All user input is sanitized before processing
- Parameterized queries are enforced at the ORM level
- Raw SQL queries require mandatory security review
- OS commands are completely forbidden
- Search queries have SQL keyword stripping

### A2:2017 - Broken Authentication

**Risk**: Authentication bypass, credential stuffing, session hijacking

**Mitigations Implemented**:

```yaml
authentication:
  provider: Auth0
  MFA:
    required: true_for_premium
    TOTP: true
    backup_codes: true
  
  password_policy:
    min_length: 12
    require_uppercase: true
    require_lowercase: true
    require_numbers: true
    require_special: true
    prevent_reuse: last_10
    breach_detection: k-Anonymity
  
  session:
    jwt_expiry: 1h
    refresh_token_expiry: 30d
    absolute_expiry: 30d
    secure_cookie: true
    http_only: true
    same_site: strict
    csrf_protection: double_submit_cookie
  
  rate_limiting:
    login_attempts:
      max: 5
      window: 300s
      lockout_duration: 900s
    
    otp_requests:
      max: 3
      window: 60s
```

**Implementation Details**:
- Auth0 handles authentication with MFA support
- JWT tokens with short expiry and secure storage
- Rate limiting on authentication endpoints
- Account lockout after failed attempts
- Session invalidation on password change

### A3:2017 - Sensitive Data Exposure

**Risk**: Data breaches, data in transit, data at rest

**Mitigations Implemented**:

```yaml
data_protection:
  encryption:
    in_transit:
      - TLS 1.3 minimum
      - Perfect forward secrecy
      - Strong cipher suites: ECDHE-RSA-AES256-GCM-SHA384
      - Certificate pinning: enabled
    
    at_rest:
      - AES-256-GCM for sensitive fields
      - RDS encryption: aws:rds
      - S3 encryption: AES-256 (SSE-S3)
      - DynamoDB encryption: AWS-managed
  
  sensitive_fields:
    encrypted_fields:
      - password
      - ssn
      - credit_card_number
      - bank_account_details
      - api_keys
    
    hashed_fields:
      - password (bcrypt, cost_factor: 12)
      - verification_token
  
  key_management:
    provider: AWS KMS
    key_rotation: 365d
    mfa_for_deletion: true
    automatic_rotation: enabled
```

**Implementation Details**:
- TLS 1.3 enforced on all endpoints
- Database-level encryption for sensitive data
- Field-level encryption for PII
- Secure key management via AWS KMS
- Regular key rotation schedule

### A4:2017 - XML External Entities (XXE)

**Risk**: XML parsing vulnerabilities, SSRF

**Mitigations Implemented**:

```yaml
xml_processing:
  forbidden: true
  alternative: JSON
  
api:
  no_xml_content_type: true
  request_validation:
    content_type: ["application/json"]
    reject_unknown: true
```

**Implementation Details**:
- XML parsing completely disabled
- JSON is the only accepted format
- Content-Type validation enforced

### A5:2017 - Broken Access Control

**Risk**: Unauthorized access, privilege escalation, data leaks

**Mitigations Implemented**:

```yaml
access_control:
  framework: RBAC with ABAC
  
  roles:
    admin:
      permissions: ["*"]
    provider:
      permissions:
        - "listings:read"
        - "listings:write:own"
        - "listings:delete:own"
        - "messages:read:own"
        - "messages:write:own"
    user:
      permissions:
        - "listings:read"
        - "messages:read:own"
        - "profile:read:own"
        - "profile:write:own"
    
  resource_ownership:
    listings:
      owner_field: "provider_id"
      write_permission: "owner_only"
    
    messages:
      owner_field: "sender_id"
      read_permission: "participants_only"
  
  row_level_security:
    enabled: true
    audit_logging: true
  
  api_authorization:
    middleware: JWT + Permission Check
    ownership_validation: required
```

**Implementation Details**:
- RBAC with ABAC for fine-grained control
- Resource ownership validation on every request
- Row-level security enforced at database level
- Comprehensive audit logging

### A6:2017 - Security Misconfiguration

**Risk**: Default credentials, unpatched systems, verbose errors

**Mitigations Implemented**:

```yaml
security_headers:
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Content-Security-Policy: |
    default-src 'self';
    script-src 'self';
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    font-src 'self';
    connect-src 'self';
    frame-ancestors 'none';
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  
error_handling:
  production:
    generic_message: "An error occurred. Please try again."
    log_full_error: true
    stack_trace: never
    debug_mode: false
  
  development:
    detailed_errors: true
    stack_trace: locally_only
    
server_configuration:
  remove_server_header: true
  protocol_version: TLS 1.3 only
  ciphers: ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256
  hsts_preload: true
```

**Implementation Details**:
- Comprehensive security headers
- Production error sanitization
- Secure TLS configuration only
- No server identification headers

### A7:2017 - Cross-Site Scripting (XSS)

**Risk**: Session hijacking, defacement, malicious scripts

**Mitigations Implemented**:

```yaml
xss_protection:
  output_encoding:
    HTML_context:
      method: entity_encoding
      encode_basic_special_chars: true
    
    JavaScript_context:
      method: hex_encoding
      encode_unicode: true
    
    URL_context:
      method: url_encoding
      encode_reserved: true
    
    CSS_context:
      method: css_escape
    
    JSON_context:
      method: json_string_escape
  
  input_validation:
    strip_tags: true
    strip_attributes:
      - onclick
      - onerror
      - onload
      - onmouseover
      - style
    strip_protocols:
      - javascript:
      - vbscript:
      - data:
  
  csp:
    default_src: "'none'"
    script_src: "'self'"
    object_src: "'none'"
    style_src: "'self' 'unsafe-inline'"
    img_src: "'self' data: https:"
    font_src: "'self'"
    connect_src: "'self'"
    frame_src: "'none'"
    worker_src: "'self'"
```

**Implementation Details**:
- Context-aware output encoding
- CSP header enforcement
- Input sanitization for dangerous attributes
- No inline scripts or styles

### A8:2017 - Insecure Deserialization

**Risk**: Remote code execution, object injection

**Mitigations Implemented**:

```yaml
serialization:
  forbidden_formats:
    - pickle
    - marshal
    - ruby_marshal
    - java_serial
  
  allowed_formats:
    - JSON (with strict parsing)
    - XML (if required, with XXE prevention)
  
  deserialization_protection:
    type_checking: true
    schema_validation: true
    memory_limits: 10MB
    depth_limits: 50
```

**Implementation Details**:
- Dangerous serialization formats forbidden
- Strict type checking on deserialization
- Memory and depth limits enforced

### A9:2017 - Using Components with Known Vulnerabilities

**Risk**: Exploitation of known CVEs

**Mitigations Implemented**:

```yaml
dependency_management:
  scanner: Dependabot + Snyk
  
  update_policy:
    critical_cves: auto_patch_within_24h
    high_cves: patch_within_7d
    medium_cves: patch_within_30d
    low_cves: patch_within_90d
  
  auditing:
    frequency: weekly
    automated_PR: enabled_for_critical
    lockfile_validation: sha512
  
  docker:
    base_images: distroless
    scanning: aqua_trivy
    no_latest_tag: true
```

**Implementation Details**:
- Automated dependency scanning
- Regular security updates
- Minimal base images
- Docker vulnerability scanning

### A10:2017 - Insufficient Logging & Monitoring

**Risk**: Breach undetected, slow response to attacks

**Mitigations Implemented**:

```yaml
logging:
  level: info
  format: JSON
  
  events_to_log:
    - authentication_success
    - authentication_failure
    - authorization_failure
    - data_access
    - data_modification
    - admin_actions
    - configuration_changes
    - suspicious_activity
  
  sensitive_data:
    redact:
      - password
      - credit_card
      - ssn
      - api_key
      - token
  
  retention:
    access_logs: 1y
    security_logs: 3y
    audit_logs: 7y
  
monitoring:
  SIEM: CloudWatch + Splunk
  
  alerting:
    breach_attempts: immediate
    multiple_failures: 5m_window
    privilege_escalation: immediate
    data_exfiltration: immediate
    
  dashboards:
    security_metrics: true
    threat_intelligence: true
    anomaly_detection: ML_based
```

**Implementation Details**:
- Comprehensive security event logging
- Real-time alerting for security incidents
- Long-term retention for compliance
- SIEM integration for threat detection

---

## 2. Input Validation

### General Input Validation Rules

```yaml
input_validation:
  # String inputs
  strings:
    max_length: 10000
    min_length: 1
    trim_whitespace: true
    normalize_unicode: NFC
    strip_control_characters: true
  
  # Numeric inputs
  numbers:
    min: -2147483648
    max: 2147483647
    integer_only: false
    precision: 2
  
  # Email validation
  email:
    RFC_5322_strict: true
    max_length: 254
    DNS_validation: true
    disposable_email_block: true
  
  # Phone validation  
  phone:
    formats: ["E164", "International"]
    country_codes: allowed_list
    validation: libphonenumber
  
  # URL validation
  url:
    protocols: ["https"]
    allow_internal: false
    DNS_rebinding_protection: true
    max_length: 2048
  
  # File uploads
  files:
    max_size_mb: 10
    allowed_types: ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    name_sanitization: true
    content_scan: true
    virus_scan: true
```

### Field-Specific Validation

```typescript
// User registration validation
const userRegistrationSchema = {
  email: {
    type: 'string',
    format: 'email',
    maxLength: 255,
    toLowercase: true,
    trim: true,
    rules: ['no_disposable_emails', 'dns_check']
  },
  password: {
    type: 'string',
    minLength: 12,
    maxLength: 128,
    rules: [
      'uppercase_required',
      'lowercase_required', 
      'number_required',
      'special_char_required',
      'no_common_passwords',
      'not_in_breach_database'
    ]
  },
  phone: {
    type: 'string',
    format: 'phone',
    countryCode: 'US',
    optional: true
  },
  firstName: {
    type: 'string',
    minLength: 1,
    maxLength: 100,
    pattern: /^[a-zA-Z\s'-]+$/,
    stripHtml: true
  },
  lastName: {
    type: 'string',
    minLength: 1,
    maxLength: 100,
    pattern: /^[a-zA-Z\s'-]+$/,
    stripHtml: true
  }
};

// Listing validation
const listingSchema = {
  title: {
    type: 'string',
    minLength: 5,
    maxLength: 200,
    stripHtml: true,
    stripScripts: true
  },
  description: {
    type: 'string',
    minLength: 20,
    maxLength: 10000,
    stripHtml: true,
    stripScripts: true
  },
  category: {
    type: 'enum',
    values: ['healthcare', 'legal', 'home_services', 'automotive', 'other'],
    required: true
  },
  price: {
    type: 'number',
    min: 0,
    max: 1000000,
    precision: 2
  },
  location: {
    type: 'object',
    schema: {
      address: { type: 'string', maxLength: 500 },
      city: { type: 'string', maxLength: 100 },
      state: { type: 'string', pattern: /^[A-Z]{2}$/ },
      zipCode: { type: 'string', pattern: /^\d{5}(-\d{4})?$/ }
    }
  }
};
```

---

## 3. HTTPS/TLS Enforcement

### TLS Configuration

```yaml
tls_config:
  version: TLS 1.3_only
  # TLS 1.2 allowed only for compatibility
  compatibility_mode: TLS_1.2_minimum
  
  cipher_suites:
    - TLS_AES_256_GCM_SHA384
    - TLS_AES_128_GCM_SHA256
    - TLS_CHACHA20_POLY1305_SHA256
  
  # Perfect Forward Secrecy
  key_exchange: ECDHE
  certificate: ECC_384_bit or RSA_4096_bit
  
  # Certificate management
  certificates:
    provider: AWS ACM
    auto_renewal: true
    renewal_before_expiry: 30d
    
    # HSTS
    hsts:
      enabled: true
      max_age: 31536000
      include_subdomains: true
      preload: true
    
    # Certificate pinning (for mobile apps)
    pinning:
      enabled: true
      backup_pins: true
```

### Application-Level HTTPS Enforcement

```yaml
https_enforcement:
  # Redirect HTTP to HTTPS
  redirect_http: true
  redirect_code: 301
  
  # Secure cookies
  cookies:
    secure: true
    http_only: true
    same_site: strict
    prefix: __Host-
  
  # API endpoints
  api:
    require_https: true
    allowed_methods: ["GET", "POST", "PUT", "DELETE", "PATCH"]
    cors:
      allowed_origins: production_origins_only
      allowed_methods: ["GET", "POST", "PUT", "DELETE", "PATCH"]
      allow_credentials: true
      max_age: 86400
```

### Client-Side TLS Validation

```yaml
client_validation:
  certificate_authorities:
    - system_default
    - custom_ca_for_internal_services
  
  # For internal services
  mutual_tls:
    enabled: true
    client_certificate_required: true
    allowed_client_cns: ["backend.internal", "frontend.internal"]
```

---

## 4. Web Application Firewall (WAF) Rules

### AWS WAF Configuration

```yaml
waf:
  name: premium-service-directory-waf
  scope: regional
  
  rules:
    # SQL Injection Protection
    - name: SQL_Injection_Block
      action: block
      priority: 1
      conditions:
        - type: SQL_INJECTION
          sensitivity: high
          match_pattern:
            request_component: query_string
            operator: contains
            value: "' OR '1'='1"
    
    # XSS Protection
    - name: XSS_Block
      action: block
      priority: 2
      conditions:
        - type: XSS
          sensitivity: high
          match_pattern:
            request_component: body
            operator: contains_pattern
            value: "<script>"
    
    # Rate Limiting
    - name: Rate_Limit_100_per_minute
      action: block
      priority: 3
      conditions:
        - type: RATE_BASED
          limit: 100
          window: 60
          aggregate_key_type: IP
    
    # Geo Blocking (if required)
    - name: Geo_Block
      action: block
      priority: 4
      conditions:
        - type: GEO_MATCH
          country_codes:
            - BY
            - RU
            - KP
          # Exception for trusted IPs
          exception: trusted_ip_list
    
    # Common Vulnerabilities
    - name: Size_Restriction_Headers
      action: block
      priority: 5
      conditions:
        - type: SIZE_CONSTRAINT
          comparison: greater_than
          size: 8192
          request_component: header
          header_name: User-Agent
    
    # AWS Managed Rules
    - name: AWS_Managed_Rules
      action: block
      priority: 10
      ruleset: AWSManagedRulesCommonRuleSet
      sensitivity: high
    
    - name: AWS_Managed_Rules_IP_Set
      action: block
      priority: 11
      ruleset: AWSManagedRulesAmazonIpReputationList
    
    - name: AWS_Managed_Rules_Anonymous
      action: challenge
      priority: 12
      ruleset: AWSManagedRulesAnonymousApiList
  
  logging:
    enabled: true
    log_group: /aws/waf/premium-service-directory
    redacted_fields:
      - password
      - credit_card
```

### Custom WAF Rules

```yaml
custom_rules:
  # Positive Security Model (Allowlisting)
  - name: API_Allowlist
    action: allow
    priority: 100
    conditions:
      - type: regex_match
        request_component: uri
        patterns:
          - "^/api/v[0-9]+/.*"
          - "^/health$"
          - "^/metrics$"
  
  # Header Validation
  - name: Required_Headers
    action: block
    priority: 101
    conditions:
      - type: missing
        header_name: User-Agent
      - type: missing
        header_name: Accept
  
  # Method Enforcement
  - name: HTTP_Method_Enforcement
    action: block
    priority: 102
    conditions:
      - type: NOT
        conditions:
          - type: regex_match
            request_component: method
            patterns:
              - "^GET$"
              - "^POST$"
              - "^PUT$"
              - "^DELETE$"
              - "^PATCH$"
              - "^OPTIONS$"
  
  # Query Parameter Limits
  - name: Query_Parameter_Limit
    action: block
    priority: 103
    conditions:
      - type: size_constraint
        request_component: query_string
        comparison: greater_than
        size: 4096
```

---

## 5. Rate Limiting

### Rate Limiting Configuration

```yaml
rate_limiting:
  enabled: true
  strategy: sliding_window
  
  # Per-IP limits
  by_ip:
    window: 60s
    limits:
      default: 100
      authenticated: 500
      premium: 1000
    
    # Endpoints with specific limits
    endpoints:
      "/api/auth/login":
        window: 300s
        limit: 5
        lockout: 900s
      
      "/api/auth/register":
        window: 3600s
        limit: 3
        lockout: 3600s
      
      "/api/search":
        window: 60s
        limit: 60
      
      "/api/listings":
        window: 60s
        limit: 100
      
      "/api/messages":
        window: 60s
        limit: 30
      
      "/api/payments":
        window: 60s
        limit: 10
  
  # Per-User limits (authenticated)
  by_user:
    window: 60s
    limits:
      default: 200
      premium: 500
  
  # Per-API Key limits
  by_api_key:
    window: 60s
    limits:
      standard: 1000
      premium: 10000
  
  # Burst handling
  burst:
    enabled: true
    burst_multiplier: 2
    burst_duration: 5
  
  # Response when rate limited
  response:
    status_code: 429
    headers:
      X-RateLimit-Limit: true
      X-RateLimit-Remaining: true
      X-RateLimit-Reset: true
      Retry-After: true
    body: |
      {
        "error": "rate_limit_exceeded",
        "message": "Too many requests. Please try again later.",
        "retry_after": {retry_after_seconds}
      }
```

### Distributed Rate Limiting (Redis)

```yaml
redis_rate_limiting:
  enabled: true
  cluster_mode: true
  
  lua_script: |
    local key = KEYS[1]
    local limit = tonumber(ARGV[1])
    local window = tonumber(ARGV[2])
    local current = redis.call('GET', key)
    
    if current and tonumber(current) >= limit then
      return {0, tonumber(current), window - (redis.call('TTL', key) % window)}
    end
    
    local count = redis.call('INCR', key)
    if count == 1 then
      redis.call('EXPIRE', key, window)
    end
    
    return {1, count, window - (redis.call('TTL', key) % window)}
```

---

## 6. Content Security Policy (CSP) Headers

### CSP Configuration

```yaml
csp:
  enabled: true
  report_only: false
  
  directives:
    # Default-src: Fallback for other directives
    default_src:
      - "'none'"
    
    # Scripts: Only from same origin
    script_src:
      - "'self'"
      - "https://cdn.example.com"  # If using external libs
    
    # Styles: Self + inline (for CSS-in-JS)
    style_src:
      - "'self'"
      - "'unsafe-inline'"
      - "https://fonts.googleapis.com"
    
    # Images: Self + data URIs + CDN
    img_src:
      - "'self'"
      - "data:"
      - "https://images.example.com"
    
    # Fonts
    font_src:
      - "'self'"
      - "https://fonts.gstatic.com"
    
    # Connections (AJAX, WebSockets)
    connect_src:
      - "'self'"
      - "https://api.example.com"
      - "wss://ws.example.com"
    
    # Media (if applicable)
    media_src:
      - "'self'"
    
    # Objects (PDF viewers, etc.)
    object_src:
      - "'none'"
    
    # Frames
    frame_src:
      - "'none'"
    
    # Workers
    worker_src:
      - "'self'"
    
    # Child frames (iframes)
    child_src:
      - "'none'"
    
    # Form submissions
    form_action:
      - "'self'"
    
    # Frame ancestors (clickjacking protection)
    frame_ancestors:
      - "'none'"
    
    # Base URI
    base_uri:
      - "'self'"
    
    # Plugin types
    plugin_types:
      - "application/pdf"
    
    # Upgrade insecure requests
    upgrade_insecure_requests: true
    
    # Report URI
    report_uri: /csp-report
    report_to: csp-endpoint
  
  # Nonce for inline scripts
  nonce:
    enabled: true
    length: 32
  
  # Violation reporting
  reporting:
    endpoint: https://csp-report.example.com/report
    report_sample: true
    collect_reports: true
```

### Implementation

```typescript
// Express middleware for CSP
app.use((req, res, next) => {
  const nonce = crypto.randomBytes(16).toString('base64');
  res.locals.nonce = nonce;
  
  res.setHeader('Content-Security-Policy', [
    "default-src 'none'",
    `script-src 'self' 'nonce-${nonce}'`,
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "img-src 'self' data: https://images.example.com",
    "font-src 'self' https://fonts.gstatic.com",
    "connect-src 'self' https://api.example.com wss://ws.example.com",
    "frame-ancestors 'none'",
    "form-action 'self'",
    "base-uri 'self'",
    "upgrade-insecure-requests"
  ].join('; '));
  
  next();
});

// Report endpoint
app.post('/csp-report', express.json(), (req, res) => {
  const report = req.body;
  // Log to security system
  securityLogger.logCSPViolation(report);
  res.status(204).end();
});
```

---

## 7. Security Monitoring and Incident Response

### Security Monitoring

```yaml
security_monitoring:
  SIEM: Splunk + CloudWatch
  
  log_sources:
    - WAF_logs
    - API_gateway_logs
    - Application_security_logs
    - Auth0_logs
    - VPC_flow_logs
    - CloudTrail_logs
  
  alerts:
    - name: SQL_Injection_Attempt
      severity: high
      action: immediate_notification
      
    - name: XSS_Attempt
      severity: high
      action: immediate_notification
      
    - name: Brute_Force_Attack
      severity: critical
      action: immediate_notification + auto_block
      
    - name: Data_Exfiltration
      severity: critical
      action: immediate_notification + incident_response
      
    - name: Privilege_Escalation
      severity: critical
      action: immediate_notification + incident_response
      
    - name: Unusual_Data_Access
      severity: medium
      action: security_team_review
```

### Incident Response

```yaml
incident_response:
  severity_levels:
    P1_critical:
      response_time: 15m
      notification: all_security + CTO
      
    P2_high:
      response_time: 1h
      notification: security_team + VP_engineering
      
    P3_medium:
      response_time: 4h
      notification: security_oncall
      
    P4_low:
      response_time: 24h
      notification: security_team
  
  runbooks:
    SQL_Injection: https://runbooks.example.com/sql-injection
    XSS: https://runbooks.example.com/xss
    Data_Breach: https://runbooks.example.com/data-breach
    Account_Takeover: https://runbooks.example.com/account-takeover
```

---

## 8. Regular Security Reviews

```yaml
security_reviews:
  frequency:
    code_review: per_PR
    penetration_test: annually
    security_audit: quarterly
    dependency_audit: weekly
    configuration_review: monthly
  
  checklist:
    - OWASP_Top_10_compliance
    - Secure_authentication_check
    - Data_encryption_check
    - Input_validation_check
    - Output_encoding_check
    - Access_control_check
    - Logging_monitoring_check
    - security_headers_check
    - dependency_vulnerabilities_check
    - secrets_management_check
```

---

## 9. Compliance

```yaml
compliance:
  standards:
    - SOC2_Type2
    - GDPR
    - CCPA
    - PCI_DSS_Level_2
  
  data_retention:
    logs: 3y
    user_data: 7y_after_deletion
    payment_data: 7y (PCI requirement)
    audit_logs: 7y
  
  data_subject_rights:
    access: 30d
    deletion: 30d
    portability: 30d
    rectification: 7d
```

---

*Document Version: 1.0.0*
*Last Updated: 2024*
*Classification: Internal - Security Sensitive*