# Security Policy

## Supported Versions

Currently, the following versions of Nexus AI are receiving security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.1.x   | ✅ Yes             |
| 2.0.x   | ❌ No              |
| < 2.0   | ❌ No              |

## Reporting a Vulnerability

We take the security of Nexus AI seriously. If you discover a security vulnerability, please do NOT open a public issue. Instead, please report it via the following process:

1. **Email us**: Send a detailed report to `security@nexus-ai.com`.
2. **Describe the issue**: Include steps to reproduce, the impact of the vulnerability, and any potential fixes you suggest.
3. **Response time**: We will acknowledge your report within 48 hours and provide a regular progress update.

## Our Security Approach

Nexus AI implements several layers of security:

### 1. Authentication & Authorization
- **JWT**: Secure, signed tokens for session management.
- **Password Hashing**: Industry-standard Argon2 or BCrypt via Passlib.

### 2. Resiliency & Protection
- **Rate Limiting**: Protects against brute-force and DDoS attacks.
- **Input Sanitization**: Global protection against XSS and injection.
- **Security Headers**: Standard headers (HSTS, CSP, X-Frame-Options) enabled by default.

### 3. Data Privacy
- **Local Storage**: Your SQL and Vector data is stored on your local machine by default.
- **Encryption**: Sensitive environment variables are never logged.

### 4. Dependency Management
- We use automated tools to monitor and patch vulnerabilities in our dependencies.

Thank you for helping us keep Nexus AI secure!
