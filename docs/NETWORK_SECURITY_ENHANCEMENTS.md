# Network Security Enhancements

## Overview

This document describes the comprehensive network security enhancements implemented in ChromSploit Framework v2.0. These improvements provide robust protection against common security vulnerabilities and implement industry best practices for secure network operations.

## Implemented Features

### 1. Rate Limiting for Network Requests

**Location**: `core/utils.py` - `RateLimiter` class

**Features**:
- Token bucket algorithm implementation
- Configurable request limits and time windows
- Thread-safe operation with mutex locks
- Decorator support for easy function protection
- Wait time calculation for clients

**Usage Example**:
```python
from core.utils import NetworkSecurityManager

security_manager = NetworkSecurityManager()

@security_manager.rate_limit(name='api_calls', max_requests=10, time_window=60)
def api_call():
    return "API response"
```

### 2. Request Throttling with Exponential Backoff

**Location**: `core/utils.py` - `ExponentialBackoff` class

**Features**:
- Configurable base delay and maximum delay
- Exponential multiplier with jitter support
- Automatic retry mechanism
- Reset functionality for successful operations

**Usage Example**:
```python
@security_manager.retry_with_backoff(max_retries=3, base_delay=1.0)
def unreliable_network_call():
    # Network operation that may fail
    pass
```

### 3. Enhanced Path Validation

**Location**: `core/path_utils.py` - Enhanced `PathUtils` class

**Security Features**:
- Path traversal attack detection (`../`, `..\\`, URL-encoded variants)
- Null byte injection prevention
- Unicode bypass detection
- Absolute path validation within base directory
- Dangerous file extension blocking
- Reserved filename detection (Windows CON, PRN, etc.)

**New Methods**:
- `is_safe_path()` - Comprehensive path security validation
- `sanitize_filename()` - Safe filename generation
- `validate_file_path()` - Full path validation with base directory checks
- `get_secure_temp_path()` - Secure temporary file creation
- `is_within_base_directory()` - Directory traversal prevention
- `secure_file_copy()` - Safe file operations

### 4. Secure HTTP Headers

**Location**: `core/utils.py` - `NetworkSecurityManager` class

**Default Security Headers**:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

### 5. Connection Timeouts

**Features**:
- Configurable connection, read, and total timeouts
- Automatic timeout application to all requests
- Sensible defaults (10s connect, 30s read, 60s total)

### 6. SSL Certificate Validation

**Security Features**:
- Enforced TLS 1.2+ minimum version
- Strong cipher suite configuration
- Hostname verification enabled
- Certificate chain validation
- Custom SSL adapter with secure defaults

**Cipher Suite**: `ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS`

### 7. Additional Security Features

#### CSRF Protection
- Token generation with HMAC-SHA256
- Time-based token expiration
- Secure token validation

#### SSRF Prevention
- Internal IP address detection and blocking
- URL validation with scheme restrictions
- Hostname resolution checks

#### Secure Request Session
- Pre-configured security headers
- SSL/TLS enforcement
- Automatic timeout handling
- Connection pooling with security options

## NetworkSecurityManager API

### Core Methods

```python
# Create secure HTTP session
session = security_manager.create_secure_session(verify_ssl=True)

# Make secure request with all protections
response = security_manager.secure_request('GET', 'https://api.example.com')

# Generate/validate CSRF tokens
token = security_manager.generate_csrf_token(secret_key)
is_valid = security_manager.validate_csrf_token(token, secret_key)

# Configure timeouts
security_manager.set_timeouts(connect=15, read=45, total=90)

# Get/update security headers
headers = security_manager.get_security_headers()
security_manager.update_security_headers({'X-Custom-Header': 'value'})
```

### Decorators

```python
# Rate limiting
@security_manager.rate_limit(name='endpoint', max_requests=100, time_window=3600)
def protected_function():
    pass

# Retry with backoff
@security_manager.retry_with_backoff(max_retries=5, base_delay=2.0)
def network_operation():
    pass
```

## Enhanced PathUtils API

### Security Methods

```python
# Path validation
is_safe = PathUtils.is_safe_path('/path/to/file')
is_valid = PathUtils.validate_file_path('/path/to/file', base_dir='/allowed/base')
is_within = PathUtils.is_within_base_directory('/path/to/check')

# Filename sanitization
clean_name = PathUtils.sanitize_filename('dangerous<file>name.txt')

# Secure operations
temp_path = PathUtils.get_secure_temp_path('prefix_', '.tmp')
success = PathUtils.secure_file_copy(src, dst, preserve_permissions=False)
PathUtils.create_secure_directory('/path/to/dir', mode=0o700)

# File type validation
is_allowed = PathUtils.is_allowed_file_type('document.pdf')
allowed_types = PathUtils.get_allowed_file_extensions()
```

## Security Event Logging

All security events are logged with appropriate severity levels:
- Rate limit violations
- Path traversal attempts
- SSL verification failures
- CSRF token validation failures
- Internal IP access attempts

Example log entries:
```
SECURITY EVENT [RATE_LIMIT]: Rate limit exceeded for api_endpoint
SECURITY EVENT [PATH_TRAVERSAL]: Blocked unsafe path: ../../../etc/passwd
SECURITY EVENT [SSL_ERROR]: SSL verification failed for self-signed certificate
SECURITY EVENT [SSRF_PREVENTION]: Blocked request to internal IP: 127.0.0.1
```

## Testing

### Automated Tests

Run the comprehensive security test suite:

```bash
python -m pytest tests/test_network_security.py -v
```

Test coverage includes:
- Rate limiting functionality
- Exponential backoff behavior
- URL validation and SSRF prevention
- Path traversal detection
- Filename sanitization
- File type validation
- CSRF token security
- SSL configuration

### Interactive Demo

Experience all security features with the interactive demo:

```bash
python demos/network_security_demo.py
```

The demo showcases:
- Real-time rate limiting
- Exponential backoff simulation
- Path security validation
- Secure HTTP requests
- Security header configuration

## Security Considerations

### Default Security Posture
- SSL verification enabled by default
- Strict path validation enforced
- Rate limiting applied to all network operations
- Security headers automatically included

### Customization
- All security settings are configurable
- Rate limits can be adjusted per endpoint
- Security headers can be customized
- Path validation can be relaxed for specific use cases

### Performance Impact
- Minimal overhead for most operations
- Rate limiting uses efficient token bucket algorithm
- Path validation uses optimized regex patterns
- SSL configuration reuses connection pools

## Dependencies

The following packages are required for the security enhancements:
- `requests>=2.31.0` - HTTP client library
- `urllib3>=2.0.0` - HTTP library with SSL support
- Standard library modules: `ssl`, `socket`, `hmac`, `hashlib`, `threading`

## Integration

### Existing Code Migration

To integrate security features into existing ChromSploit modules:

1. Import the security manager:
```python
from core.utils import NetworkSecurityManager
```

2. Create an instance with logging:
```python
security_manager = NetworkSecurityManager(logger=your_logger)
```

3. Replace direct requests with secure requests:
```python
# Before
response = requests.get(url)

# After
response = security_manager.secure_request('GET', url)
```

4. Add path validation:
```python
# Before
file_path = user_input

# After
if not PathUtils.is_safe_path(user_input):
    raise ValueError("Unsafe path detected")
file_path = user_input
```

### New Module Development

For new modules, use the security features from the start:
- Always use `NetworkSecurityManager` for HTTP requests
- Validate all file paths with `PathUtils`
- Apply rate limiting to public APIs
- Include security headers in web interfaces

## Future Enhancements

Planned security improvements:
- Web Application Firewall (WAF) integration
- Advanced threat detection
- API key management
- Certificate pinning
- Request signing and verification
- Advanced logging and monitoring
- Security metrics and alerting

## Conclusion

These network security enhancements significantly improve the security posture of the ChromSploit Framework while maintaining ease of use and performance. The modular design allows for easy integration into existing code and provides a solid foundation for future security improvements.

For questions or security concerns, please review the code in `core/utils.py` and `core/path_utils.py`, or run the test suite to understand the expected behavior.