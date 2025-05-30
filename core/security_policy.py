#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework Security Policy
Enforces global safety mechanisms and security controls
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum

try:
    from .enhanced_logger import get_logger
    from .colors import Colors
    logger = get_logger()
except ImportError:
    logger = logging.getLogger(__name__)
    
    class Colors:
        END = ''
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        CYAN = ''
        MAGENTA = ''


class SecurityLevel(Enum):
    """Security level definitions"""
    SAFE = "safe"  # Default - simulation only
    RESTRICTED = "restricted"  # Limited real operations with safety checks
    AUTHORIZED = "authorized"  # Full operations with audit trail
    EMERGENCY = "emergency"  # Emergency shutdown mode


class OperationType(Enum):
    """Types of operations that require authorization"""
    NETWORK_SCAN = "network_scan"
    EXPLOIT_EXECUTION = "exploit_execution"
    PAYLOAD_DEPLOYMENT = "payload_deployment"
    DATA_EXFILTRATION = "data_exfiltration"
    SYSTEM_MODIFICATION = "system_modification"
    PERSISTENCE_INSTALLATION = "persistence_installation"


class SecurityPolicy:
    """Global security policy for ChromSploit Framework"""
    
    def __init__(self):
        self.config_file = Path("/tmp/.chromsploit_security_policy.json")
        self.audit_file = Path("/tmp/chromsploit_security_audit.jsonl")
        self.emergency_stop_file = Path("/tmp/.chromsploit_emergency_stop")
        
        self.current_level = SecurityLevel.SAFE
        self.authorized_operations = set()
        self.blocked_targets = set()
        self.allowed_targets = {'127.0.0.1', 'localhost', '0.0.0.0'}
        
        self._load_policy()
        self._check_emergency_stop()
    
    def _load_policy(self):
        """Load security policy from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.current_level = SecurityLevel(data.get('security_level', 'safe'))
                    self.authorized_operations = set(data.get('authorized_operations', []))
                    self.blocked_targets = set(data.get('blocked_targets', []))
                    self.allowed_targets.update(data.get('allowed_targets', []))
        except Exception as e:
            logger.error(f"Failed to load security policy: {e}")
            self._set_safe_defaults()
    
    def _save_policy(self):
        """Save security policy to file"""
        try:
            data = {
                'security_level': self.current_level.value,
                'authorized_operations': list(self.authorized_operations),
                'blocked_targets': list(self.blocked_targets),
                'allowed_targets': list(self.allowed_targets),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save security policy: {e}")
    
    def _set_safe_defaults(self):
        """Set safe default configuration"""
        self.current_level = SecurityLevel.SAFE
        self.authorized_operations.clear()
        self.blocked_targets = {
            # Block all public IPs and production domains by default
            '8.8.8.8', '8.8.4.4',  # Google DNS
            '1.1.1.1', '1.0.0.1',  # Cloudflare DNS
            'google.com', 'microsoft.com', 'amazon.com',
            'facebook.com', 'twitter.com', 'github.com'
        }
        self._save_policy()
    
    def _check_emergency_stop(self):
        """Check for emergency stop signal"""
        if self.emergency_stop_file.exists():
            self.current_level = SecurityLevel.EMERGENCY
            logger.critical(f"{Colors.RED}[EMERGENCY]{Colors.END} Emergency stop activated!")
            logger.critical("All operations are blocked until emergency stop is cleared")
    
    def activate_emergency_stop(self, reason: str = "Manual activation"):
        """Activate emergency stop"""
        self.current_level = SecurityLevel.EMERGENCY
        
        try:
            with open(self.emergency_stop_file, 'w') as f:
                json.dump({
                    'activated': datetime.now().isoformat(),
                    'reason': reason
                }, f)
            
            logger.critical(f"{Colors.RED}[EMERGENCY STOP]{Colors.END} Activated: {reason}")
            self._audit_event("EMERGENCY_STOP_ACTIVATED", {'reason': reason})
        except Exception as e:
            logger.error(f"Failed to activate emergency stop: {e}")
    
    def clear_emergency_stop(self, auth_code: str) -> bool:
        """Clear emergency stop with authorization"""
        expected_hash = hashlib.sha256(b"CHROMSPLOIT_EMERGENCY_CLEAR_2025").hexdigest()
        
        if auth_code != expected_hash[:16]:
            logger.error("Invalid authorization code for emergency stop clear")
            return False
        
        try:
            if self.emergency_stop_file.exists():
                os.remove(self.emergency_stop_file)
            
            self.current_level = SecurityLevel.SAFE
            logger.info(f"{Colors.GREEN}[SECURITY]{Colors.END} Emergency stop cleared")
            self._audit_event("EMERGENCY_STOP_CLEARED", {'cleared_by': 'authorized_user'})
            self._save_policy()
            return True
        except Exception as e:
            logger.error(f"Failed to clear emergency stop: {e}")
            return False
    
    def set_security_level(self, level: SecurityLevel, auth_code: str = None) -> bool:
        """Set security level with authorization"""
        if self.current_level == SecurityLevel.EMERGENCY:
            logger.error("Cannot change security level during emergency stop")
            return False
        
        if level in [SecurityLevel.AUTHORIZED, SecurityLevel.RESTRICTED]:
            if not auth_code:
                logger.error("Authorization code required for elevated security levels")
                return False
            
            # Verify authorization
            expected_hash = hashlib.sha256(f"CHROMSPLOIT_LEVEL_{level.value}_2025".encode()).hexdigest()
            if auth_code != expected_hash[:16]:
                logger.error("Invalid authorization code")
                self._audit_event("UNAUTHORIZED_LEVEL_CHANGE_ATTEMPT", {
                    'requested_level': level.value,
                    'current_level': self.current_level.value
                })
                return False
        
        old_level = self.current_level
        self.current_level = level
        self._save_policy()
        
        logger.info(f"{Colors.CYAN}[SECURITY]{Colors.END} Security level changed: {old_level.value} -> {level.value}")
        self._audit_event("SECURITY_LEVEL_CHANGED", {
            'old_level': old_level.value,
            'new_level': level.value
        })
        
        return True
    
    def authorize_operation(self, operation: OperationType, auth_code: str) -> bool:
        """Authorize a specific operation type"""
        if self.current_level == SecurityLevel.EMERGENCY:
            logger.error("Cannot authorize operations during emergency stop")
            return False
        
        # Verify authorization
        expected_hash = hashlib.sha256(f"CHROMSPLOIT_OP_{operation.value}_2025".encode()).hexdigest()
        if auth_code != expected_hash[:16]:
            logger.error(f"Invalid authorization code for operation: {operation.value}")
            return False
        
        self.authorized_operations.add(operation.value)
        self._save_policy()
        
        logger.warning(f"{Colors.YELLOW}[AUTHORIZED]{Colors.END} Operation authorized: {operation.value}")
        self._audit_event("OPERATION_AUTHORIZED", {'operation': operation.value})
        
        return True
    
    def check_operation_allowed(self, operation: OperationType, target: str = None) -> bool:
        """Check if an operation is allowed under current policy"""
        # Emergency stop blocks everything
        if self.current_level == SecurityLevel.EMERGENCY:
            logger.error(f"{Colors.RED}[BLOCKED]{Colors.END} Emergency stop active - all operations blocked")
            return False
        
        # Check target restrictions
        if target and not self._check_target_allowed(target):
            logger.error(f"{Colors.RED}[BLOCKED]{Colors.END} Target not allowed: {target}")
            return False
        
        # Safe mode allows only simulations
        if self.current_level == SecurityLevel.SAFE:
            return True  # Simulations are always allowed
        
        # Check if operation is authorized
        if operation.value not in self.authorized_operations:
            logger.error(f"{Colors.RED}[BLOCKED]{Colors.END} Operation not authorized: {operation.value}")
            return False
        
        return True
    
    def _check_target_allowed(self, target: str) -> bool:
        """Check if target is allowed"""
        if not target:
            return True
        
        target_lower = target.lower()
        
        # Check blocked targets
        for blocked in self.blocked_targets:
            if blocked in target_lower:
                return False
        
        # Check allowed targets
        for allowed in self.allowed_targets:
            if allowed in target_lower:
                return True
        
        # Default deny for non-local targets in safe/restricted mode
        if self.current_level in [SecurityLevel.SAFE, SecurityLevel.RESTRICTED]:
            return False
        
        return True
    
    def add_allowed_target(self, target: str, auth_code: str) -> bool:
        """Add a target to allowed list"""
        expected_hash = hashlib.sha256(f"CHROMSPLOIT_TARGET_{target}_2025".encode()).hexdigest()
        if auth_code != expected_hash[:16]:
            logger.error(f"Invalid authorization code for target: {target}")
            return False
        
        self.allowed_targets.add(target)
        self._save_policy()
        
        logger.info(f"{Colors.GREEN}[ALLOWED]{Colors.END} Target added to allowed list: {target}")
        self._audit_event("TARGET_ALLOWED", {'target': target})
        
        return True
    
    def block_target(self, target: str):
        """Block a target"""
        self.blocked_targets.add(target)
        self.allowed_targets.discard(target)
        self._save_policy()
        
        logger.warning(f"{Colors.YELLOW}[BLOCKED]{Colors.END} Target blocked: {target}")
        self._audit_event("TARGET_BLOCKED", {'target': target})
    
    def get_policy_status(self) -> Dict[str, Any]:
        """Get current policy status"""
        return {
            'security_level': self.current_level.value,
            'emergency_stop': self.current_level == SecurityLevel.EMERGENCY,
            'authorized_operations': list(self.authorized_operations),
            'allowed_targets': list(self.allowed_targets),
            'blocked_targets': list(self.blocked_targets),
            'audit_file': str(self.audit_file)
        }
    
    def _audit_event(self, event_type: str, data: Dict[str, Any] = None):
        """Log security event to audit trail"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'security_level': self.current_level.value,
            'data': data or {}
        }
        
        try:
            with open(self.audit_file, 'a') as f:
                f.write(json.dumps(audit_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def enforce_safe_mode(self):
        """Force framework into safe mode"""
        self.current_level = SecurityLevel.SAFE
        self.authorized_operations.clear()
        self._save_policy()
        
        logger.info(f"{Colors.GREEN}[SECURITY]{Colors.END} Enforced safe mode - all operations restricted to simulation")
        self._audit_event("SAFE_MODE_ENFORCED", {'enforced_by': 'security_policy'})


# Global security policy instance
_security_policy = None


def get_security_policy() -> SecurityPolicy:
    """Get global security policy instance"""
    global _security_policy
    if _security_policy is None:
        _security_policy = SecurityPolicy()
    return _security_policy


def check_operation_permitted(operation: OperationType, target: str = None) -> bool:
    """Quick check if operation is permitted"""
    policy = get_security_policy()
    return policy.check_operation_allowed(operation, target)


def enforce_security_boundary(func):
    """Decorator to enforce security boundaries on functions"""
    def wrapper(*args, **kwargs):
        policy = get_security_policy()
        
        # Check emergency stop
        if policy.current_level == SecurityLevel.EMERGENCY:
            logger.error(f"{Colors.RED}[SECURITY]{Colors.END} Operation blocked by emergency stop")
            return {
                'success': False,
                'error': 'Emergency stop activated',
                'security_level': policy.current_level.value
            }
        
        # Get operation type from function name or kwargs
        operation_type = kwargs.get('operation_type', OperationType.EXPLOIT_EXECUTION)
        target = kwargs.get('target') or kwargs.get('target_url')
        
        if not policy.check_operation_allowed(operation_type, target):
            logger.error(f"{Colors.RED}[SECURITY]{Colors.END} Operation not permitted by security policy")
            return {
                'success': False,
                'error': 'Operation not permitted by security policy',
                'required_authorization': operation_type.value,
                'security_level': policy.current_level.value
            }
        
        # Log operation attempt
        policy._audit_event("OPERATION_ATTEMPTED", {
            'function': func.__name__,
            'operation': operation_type.value,
            'target': target
        })
        
        return func(*args, **kwargs)
    
    return wrapper