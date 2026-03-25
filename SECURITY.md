# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Martian Bank, please report it responsibly:

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Email security concerns to the maintainers
3. Include detailed steps to reproduce the vulnerability
4. Allow reasonable time for the issue to be resolved before disclosure

## Security Measures

### Authentication & Authorization
- JWT-based authentication with httpOnly cookies
- TOTP-based Two-Factor Authentication (2FA)
- Password hashing with bcrypt (10 salt rounds)
- Protected routes with middleware validation
- Session management with secure cookie settings

### Input Validation & Sanitization
- Server-side validation on all endpoints using express-validator (Node.js) and custom validators (Python)
- Email format validation
- Password strength enforcement (min 8 chars, 1 uppercase, 1 number)
- NoSQL injection prevention through input sanitization
- Amount and account number format validation

### Rate Limiting
- Login endpoint: 5 requests per minute
- Registration endpoint: 20 requests per minute
- General API: 100 requests per minute
- Financial endpoints: Configurable limits

### Transport Security
- CORS configured with explicit allowed origins
- Security headers via NGINX:
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff
  - X-XSS-Protection: 1; mode=block
  - Content-Security-Policy: default-src 'self'
  - Strict-Transport-Security: max-age=31536000; includeSubDomains
  - Referrer-Policy: strict-origin-when-cross-origin
- CSRF protection on state-changing operations

### Data Protection
- AES-256 encryption for sensitive data at rest (govt IDs)
- Masked display of sensitive data (show only last 4 digits)
- Environment variable-based secret management
- No hardcoded credentials in codebase
- Debug mode disabled by default in production

### Audit & Monitoring
- Immutable audit log for all financial operations
- AML transaction monitoring with configurable rules
- Login attempt tracking (success/failure)

### GDPR Compliance
- Data export endpoint for data portability
- Data erasure endpoint (right to be forgotten)
- Financial records retained per regulatory requirements
- Personal data anonymization on erasure

## Environment Variables for Security

All security-sensitive configuration is managed through environment variables:

| Variable | Purpose |
|----------|---------|
| `JWT_SECRET` | JWT token signing |
| `ENCRYPTION_KEY` | Data encryption at rest |
| `MONGO_USERNAME` | Database authentication |
| `MONGO_PASSWORD` | Database authentication |
| `CORS_ORIGINS` | CORS allowed origins |
| `FLASK_DEBUG` | Debug mode control |

## Known Limitations

- MongoDB transactions require replica set configuration
- 2FA backup codes not yet implemented
- Rate limiting is per-service (not distributed)
- Encryption key rotation not yet automated
