#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Safety & Authorization Manager
Comprehensive safety checks and authorization system
"""

import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety levels"""
    SAFE = "safe"  # Simulation mode only
    RESTRICTED = "restricted"  # Limited targets
    STANDARD = "standard"  # Normal operation
    UNRESTRICTED = "unrestricted"  # No restrictions (dangerous)


@dataclass
class Authorization:
    """Authorization record"""
    exploit_id: str
    user: str
    authorized_at: float
    expires_at: Optional[float] = None
    target_restrictions: Optional[List[str]] = None
    auth_code: Optional[str] = None


@dataclass
class SafetyCheckResult:
    """Result of safety check"""
    allowed: bool
    reason: str
    safety_level: SafetyLevel
    warnings: List[str] = None


class SafetyManager:
    """Enhanced safety and authorization manager"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path(__file__).parent.parent.parent / "config" / "safety.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.authorizations: Dict[str, Authorization] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self.sandbox_mode = True  # Default to safe
        self.safety_level = SafetyLevel.SAFE
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load safety configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.sandbox_mode = config.get("sandbox_mode", True)
                    self.safety_level = SafetyLevel(config.get("safety_level", "safe"))
            except Exception as e:
                logger.warning(f"Could not load safety config: {e}")
    
    def _save_config(self):
        """Save safety configuration"""
        try:
            config = {
                "sandbox_mode": self.sandbox_mode,
                "safety_level": self.safety_level.value,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save safety config: {e}")
    
    def set_sandbox_mode(self, enabled: bool):
        """Enable/disable sandbox mode"""
        self.sandbox_mode = enabled
        self._save_config()
        self._audit_log("sandbox_mode_changed", {"enabled": enabled})
    
    def set_safety_level(self, level: SafetyLevel):
        """Set safety level"""
        self.safety_level = level
        self._save_config()
        self._audit_log("safety_level_changed", {"level": level.value})
    
    def check_authorization(self, exploit_id: str, user: str = "default") -> bool:
        """Check if user is authorized for exploit"""
        auth_key = f"{exploit_id}:{user}"
        
        if auth_key not in self.authorizations:
            return False
        
        auth = self.authorizations[auth_key]
        
        # Check expiration
        if auth.expires_at and datetime.now(timezone.utc).timestamp() > auth.expires_at:
            del self.authorizations[auth_key]
            return False
        
        return True
    
    def authorize(self, exploit_id: str, user: str = "default", 
                 expires_in: Optional[int] = None,
                 target_restrictions: Optional[List[str]] = None,
                 auth_code: Optional[str] = None) -> str:
        """Authorize exploit execution"""
        auth_key = f"{exploit_id}:{user}"
        
        expires_at = None
        if expires_in:
            expires_at = datetime.now(timezone.utc).timestamp() + expires_in
        
        auth = Authorization(
            exploit_id=exploit_id,
            user=user,
            authorized_at=datetime.now(timezone.utc).timestamp(),
            expires_at=expires_at,
            target_restrictions=target_restrictions,
            auth_code=auth_code
        )
        
        self.authorizations[auth_key] = auth
        self._audit_log("authorization_granted", {
            "exploit_id": exploit_id,
            "user": user,
            "expires_at": expires_at
        })
        
        return auth_key
    
    def revoke_authorization(self, exploit_id: str, user: str = "default"):
        """Revoke authorization"""
        auth_key = f"{exploit_id}:{user}"
        
        if auth_key in self.authorizations:
            del self.authorizations[auth_key]
            self._audit_log("authorization_revoked", {
                "exploit_id": exploit_id,
                "user": user
            })
    
    def validate_target(self, target: str) -> SafetyCheckResult:
        """Validate target is safe to attack"""
        warnings = []
        
        # Check for localhost/local network
        if any(indicator in target.lower() for indicator in ["localhost", "127.0.0.1", "0.0.0.0"]):
            if self.safety_level == SafetyLevel.SAFE:
                return SafetyCheckResult(
                    allowed=False,
                    reason="Localhost targets not allowed in SAFE mode",
                    safety_level=self.safety_level,
                    warnings=warnings
                )
            warnings.append("Targeting localhost - ensure you have permission")
        
        # Check for common production domains
        production_indicators = ["production", "prod", "live", "www"]
        if any(indicator in target.lower() for indicator in production_indicators):
            warnings.append("Target appears to be production environment")
        
        # Check safety level
        if self.safety_level == SafetyLevel.SAFE:
            return SafetyCheckResult(
                allowed=False,
                reason="SAFE mode enabled - only simulation allowed",
                safety_level=self.safety_level,
                warnings=warnings
            )
        
        if self.safety_level == SafetyLevel.RESTRICTED:
            # Additional checks for restricted mode
            if not self._is_authorized_target(target):
                return SafetyCheckResult(
                    allowed=False,
                    reason="Target not in authorized list for RESTRICTED mode",
                    safety_level=self.safety_level,
                    warnings=warnings
                )
        
        return SafetyCheckResult(
            allowed=True,
            reason="Target validation passed",
            safety_level=self.safety_level,
            warnings=warnings
        )
    
    def _is_authorized_target(self, target: str) -> bool:
        """Check if target is in authorized list"""
        # In a real implementation, this would check against a whitelist
        # For now, we'll allow if not explicitly blocked
        return True
    
    def check_exploit_safety(self, exploit_id: str, target: str, 
                            user: str = "default") -> SafetyCheckResult:
        """Comprehensive safety check before exploit execution"""
        warnings = []
        
        # Check sandbox mode
        if self.sandbox_mode:
            return SafetyCheckResult(
                allowed=True,
                reason="Sandbox mode enabled - execution will be simulated",
                safety_level=SafetyLevel.SAFE,
                warnings=["Sandbox mode: No real exploitation will occur"]
            )
        
        # Check authorization
        if not self.check_authorization(exploit_id, user):
            return SafetyCheckResult(
                allowed=False,
                reason=f"User {user} not authorized for {exploit_id}",
                safety_level=self.safety_level,
                warnings=warnings
            )
        
        # Validate target
        target_validation = self.validate_target(target)
        if not target_validation.allowed:
            return target_validation
        
        warnings.extend(target_validation.warnings or [])
        
        # Check safety level
        if self.safety_level == SafetyLevel.SAFE:
            return SafetyCheckResult(
                allowed=False,
                reason="SAFE mode enabled",
                safety_level=self.safety_level,
                warnings=warnings
            )
        
        return SafetyCheckResult(
            allowed=True,
            reason="All safety checks passed",
            safety_level=self.safety_level,
            warnings=warnings
        )
    
    def _audit_log(self, action: str, details: Dict[str, Any]):
        """Log action to audit log"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "details": details
        }
        
        self.audit_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
        
        # Save to file
        self._save_audit_log()
    
    def _save_audit_log(self):
        """Save audit log to file"""
        audit_file = Path(__file__).parent.parent.parent / "data" / "audit_log.json"
        audit_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(audit_file, 'w') as f:
                json.dump(self.audit_log, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save audit log: {e}")
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        return self.audit_log[-limit:]
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety status"""
        return {
            "sandbox_mode": self.sandbox_mode,
            "safety_level": self.safety_level.value,
            "active_authorizations": len(self.authorizations),
            "audit_log_entries": len(self.audit_log)
        }


# Singleton instance
_safety_manager = None

def get_safety_manager() -> SafetyManager:
    """Get global safety manager instance"""
    global _safety_manager
    if _safety_manager is None:
        _safety_manager = SafetyManager()
    return _safety_manager
