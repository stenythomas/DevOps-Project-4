# Security Assessment and Known Exceptions

## Project
Student Complaint Box — DevSecOps Pipeline

## Security Improvements

- Django CSRF and session cookie HttpOnly protection.
- Content Security Policy enforcement.
- Cross-Origin Resource Policy configured as same-origin.
- Cross-Origin Opener Policy configured as same-origin.
- Permissions Policy restrictions.
- MIME-type sniffing protection.
- Clickjacking protection.
- Sensitive HTML response cache protection.
- Locally hosted Poppins fonts.
- Updated Bootstrap and jQuery libraries.
- Minified third-party JavaScript distributions.
- Gunicorn and Nginx deployment.
- Automated Bandit, pip-audit and OWASP ZAP scanning.

## Known Security Exceptions

### CSP unsafe-eval

Retained temporarily because the Kommunicate chatbot requires dynamic JavaScript evaluation.

Risk: Reduced protection against script injection.

Future remediation: Replace or update the chatbot integration to support a stricter CSP.

### Cross-Origin Embedder Policy

COEP enforcement is deferred because it may interfere with third-party chatbot resources.

The application currently has no demonstrated requirement for cross-origin isolation.

### Non-Storable Content

HTML responses intentionally use no-store cache protection to reduce exposure of sensitive information.

### Informational ZAP Findings

Modern Web Application, Authentication Request Identified and Session Management Response Identified require review but do not independently establish exploitable vulnerabilities.

### HTTPS Configuration

The current deployment uses local HTTP. HSTS, HTTPS redirection and Secure cookie flags must be configured before public production deployment.

## Security Validation

All remediation changes must be verified through the Jenkins CI pipeline and a fresh OWASP ZAP scan. Known exceptions must be reviewed before production release.
