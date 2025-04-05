# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please send an email to security@afrobeats.no. All security vulnerabilities will be promptly addressed.

## API Keys and Credentials

- Never commit API keys or credentials to version control
- Always use environment variables or a `.env` file (which is added to `.gitignore`)
- The project uses `python-dotenv` to load environment variables from a `.env` file
- For production, consider using a secrets manager rather than environment variables

## Security Best Practices Implemented

1. **Environment Variables**
   - All API keys and sensitive credentials are stored in environment variables
   - The `.env` file is added to `.gitignore` to prevent accidental commits
   - Key rotation policies are defined for production environments

2. **Input Validation**
   - User inputs are validated and sanitized before processing
   - Query length limits are enforced to prevent DoS attacks
   - All inputs use Pydantic models for validation and sanitization
   - Strong type checking is implemented throughout the application

3. **Error Handling**
   - Generic error messages are shown to users to avoid exposing sensitive information
   - Detailed errors are logged for debugging but not displayed to end users
   - Custom error handlers prevent stack traces from being exposed
   - Graceful degradation when services are unavailable

4. **Dependency Management**
   - Dependencies use pinned versions to prevent security regressions
   - Regular security scanning with the `safety` tool
   - Automated vulnerability scanning in CI/CD pipeline
   - Third-party library reviews for security implications

5. **API Rate Limiting**
   - Graceful handling of rate limit errors from AI service providers
   - Automatic fallback between different providers when rate limits are hit
   - Server-side rate limiting to prevent abuse
   - Token bucket algorithm for rate limiting implementation

6. **Authentication & Authorization**
   - API key validation for server endpoints
   - Role-based access control for admin features
   - Token expiration and rotation policies
   - CSRF protection for web forms

7. **Data Protection**
   - Sensitive data is never stored in logs
   - Cache entries are encrypted when containing sensitive information
   - Data minimization principles are applied
   - Regular purging of unnecessary data

8. **Network Security**
   - CORS configuration restricts origins to trusted domains
   - Content Security Policy headers are implemented
   - Security headers (X-XSS-Protection, X-Content-Type-Options, etc.)
   - HTTPS enforcement in production

## Recommendations for Production Deployment

1. **API Key Management**
   - Use a secrets manager like AWS Secrets Manager or HashiCorp Vault
   - Implement key rotation policies
   - Use least privilege principle for service accounts
   - Regular audit of access and permissions

2. **Network Security**
   - Deploy behind a firewall or WAF
   - Implement proper CORS policies
   - Use a CDN for frontend assets
   - Configure proper TLS settings (TLS 1.2+, strong ciphers)
   - Set up DDoS protection

3. **Monitoring & Logging**
   - Implement logging for security-relevant events
   - Set up alerting for failed authentication attempts or API quota issues
   - Configure real-time monitoring for suspicious activities
   - Implement centralized log management
   - Set up automatic alerts for anomalous behavior

4. **Regular Updates**
   - Regularly update dependencies with `pip install --upgrade` and run security scans
   - Subscribe to security notifications for key dependencies
   - Establish a regular patching schedule
   - Conduct periodic security reviews

5. **Backup & Recovery**
   - Regular database backups
   - Disaster recovery planning
   - Data retention policies
   - Regular backup testing

6. **Compliance**
   - GDPR compliance for user data
   - Cookie policies and consent management
   - Privacy policy implementation
   - Regular compliance audits

## Security Testing

1. **Automated Testing**
   - Static application security testing (SAST)
   - Dynamic application security testing (DAST)
   - Dependency vulnerability scanning
   - CI/CD pipeline integration

2. **Manual Testing**
   - Regular code reviews focusing on security
   - Periodic penetration testing
   - Security architecture reviews
   - Threat modeling sessions