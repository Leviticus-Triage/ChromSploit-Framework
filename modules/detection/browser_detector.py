#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Browser Detection Module
Automatic browser detection and version identification for intelligent exploit selection
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class BrowserType(Enum):
    """Supported browser types"""
    CHROME = "chrome"
    EDGE = "edge"
    FIREFOX = "firefox"
    BRAVE = "brave"
    VIVALDI = "vivaldi"
    OPERA = "opera"
    SAFARI = "safari"
    UNKNOWN = "unknown"


@dataclass
class BrowserInfo:
    """Browser information structure"""
    browser_type: BrowserType
    version: Optional[str] = None
    major_version: Optional[int] = None
    minor_version: Optional[int] = None
    patch_version: Optional[int] = None
    user_agent: Optional[str] = None
    platform: Optional[str] = None
    is_mobile: bool = False
    is_headless: bool = False
    confidence: float = 0.0


class BrowserDetector:
    """Automatic browser detection and analysis"""
    
    def __init__(self):
        self.compatibility_matrix = self._load_compatibility_matrix()
        self.detection_patterns = self._init_detection_patterns()
        
    def _load_compatibility_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Load browser compatibility matrix"""
        matrix_path = Path(__file__).parent.parent.parent / "data" / "browser_compatibility.json"
        
        if matrix_path.exists():
            try:
                with open(matrix_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load compatibility matrix: {e}")
        
        # Default compatibility matrix
        return {
            "CVE-2025-49741": {
                "edge": {"min": "135.0.7049.114", "max": "135.0.7049.115"},
                "chrome": {"min": None, "max": None},
                "firefox": {"min": None, "max": None}
            },
            "CVE-2020-6519": {
                "chrome": {"min": "83.0", "max": "83.0"},
                "edge": {"min": "83.0", "max": "83.0"},
                "chromium": {"min": "83.0", "max": "83.0"}
            },
            "CVE-2017-5375": {
                "firefox": {"min": "44.0.2", "max": "44.0.2"}
            },
            "CVE-2016-1960": {
                "firefox": {"min": "44.0.2", "max": "44.0.2"}
            },
            "CVE-2025-4664": {
                "chrome": {"min": None, "max": "136.0.7103.113"},
                "edge": {"min": None, "max": "136.0.7103.113"},
                "chromium": {"min": None, "max": "136.0.7103.113"}
            },
            "CVE-2025-2783": {
                "chrome": {"min": None, "max": "136.0"},
                "edge": {"min": None, "max": "136.0"}
            },
            "CVE-2025-2857": {
                "firefox": {"min": None, "max": "135.0"}
            },
            "CVE-2025-30397": {
                "edge": {"min": None, "max": "136.0"},
                "ie": {"min": None, "max": "11.0"}
            }
        }
    
    def _init_detection_patterns(self) -> Dict[BrowserType, List[Dict[str, Any]]]:
        """Initialize browser detection patterns"""
        return {
            BrowserType.CHROME: [
                {"pattern": r"Chrome/(\d+)\.(\d+)\.(\d+)\.(\d+)", "group": "full"},
                {"pattern": r"Chrome/(\d+)\.(\d+)\.(\d+)", "group": "major_minor_patch"},
                {"pattern": r"Chrome/(\d+)", "group": "major"}
            ],
            BrowserType.EDGE: [
                {"pattern": r"Edg(?:e|A)/(\d+)\.(\d+)\.(\d+)\.(\d+)", "group": "full"},
                {"pattern": r"Edg(?:e|A)/(\d+)\.(\d+)\.(\d+)", "group": "major_minor_patch"},
                {"pattern": r"Edg(?:e|A)/(\d+)", "group": "major"}
            ],
            BrowserType.FIREFOX: [
                {"pattern": r"Firefox/(\d+)\.(\d+)\.(\d+)", "group": "major_minor_patch"},
                {"pattern": r"Firefox/(\d+)\.(\d+)", "group": "major_minor"},
                {"pattern": r"Firefox/(\d+)", "group": "major"}
            ],
            BrowserType.BRAVE: [
                {"pattern": r"Brave/(\d+)\.(\d+)\.(\d+)", "group": "major_minor_patch"},
                {"pattern": r"Chrome/(\d+)\.(\d+)", "group": "chrome_based"}
            ],
            BrowserType.VIVALDI: [
                {"pattern": r"Vivaldi/(\d+)\.(\d+)\.(\d+)", "group": "major_minor_patch"},
                {"pattern": r"Chrome/(\d+)\.(\d+)", "group": "chrome_based"}
            ],
            BrowserType.OPERA: [
                {"pattern": r"OPR/(\d+)\.(\d+)\.(\d+)", "group": "major_minor_patch"},
                {"pattern": r"Chrome/(\d+)\.(\d+)", "group": "chrome_based"}
            ],
            BrowserType.SAFARI: [
                {"pattern": r"Version/(\d+)\.(\d+)\.(\d+)", "group": "major_minor_patch"},
                {"pattern": r"Version/(\d+)\.(\d+)", "group": "major_minor"}
            ]
        }
    
    def detect_browser(self, user_agent: str) -> BrowserInfo:
        """Detect browser from user agent string"""
        if not user_agent:
            return BrowserInfo(browser_type=BrowserType.UNKNOWN, confidence=0.0)
        
        user_agent_lower = user_agent.lower()
        
        # Check for headless browsers
        is_headless = any(indicator in user_agent_lower for indicator in [
            'headless', 'phantom', 'selenium', 'webdriver'
        ])
        
        # Check for mobile
        is_mobile = any(indicator in user_agent_lower for indicator in [
            'mobile', 'android', 'iphone', 'ipad', 'ipod'
        ])
        
        # Detect platform
        platform = self._detect_platform(user_agent)
        
        # Try to detect browser type and version
        best_match = None
        best_confidence = 0.0
        
        for browser_type, patterns in self.detection_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info["pattern"]
                match = re.search(pattern, user_agent, re.IGNORECASE)
                
                if match:
                    version_info = self._parse_version(match, pattern_info["group"])
                    confidence = self._calculate_confidence(browser_type, user_agent, match)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = BrowserInfo(
                            browser_type=browser_type,
                            version=version_info["version"],
                            major_version=version_info.get("major"),
                            minor_version=version_info.get("minor"),
                            patch_version=version_info.get("patch"),
                            user_agent=user_agent,
                            platform=platform,
                            is_mobile=is_mobile,
                            is_headless=is_headless,
                            confidence=confidence
                        )
        
        # Special handling for Edge (Chromium-based)
        if best_match and best_match.browser_type == BrowserType.EDGE:
            # Edge Chromium-based detection
            if "Edg" in user_agent and "Chrome" in user_agent:
                best_match.browser_type = BrowserType.EDGE
                best_match.confidence = min(best_match.confidence + 0.2, 1.0)
        
        # Special handling for Brave
        if "Brave" in user_agent:
            if best_match and best_match.browser_type == BrowserType.CHROME:
                best_match.browser_type = BrowserType.BRAVE
                best_match.confidence = min(best_match.confidence + 0.1, 1.0)
        
        # Special handling for Vivaldi
        if "Vivaldi" in user_agent:
            if best_match and best_match.browser_type == BrowserType.CHROME:
                best_match.browser_type = BrowserType.VIVALDI
                best_match.confidence = min(best_match.confidence + 0.1, 1.0)
        
        if not best_match:
            return BrowserInfo(
                browser_type=BrowserType.UNKNOWN,
                user_agent=user_agent,
                platform=platform,
                is_mobile=is_mobile,
                is_headless=is_headless,
                confidence=0.0
            )
        
        return best_match
    
    def _parse_version(self, match: re.Match, group_type: str) -> Dict[str, Any]:
        """Parse version from regex match"""
        groups = match.groups()
        version_info = {"version": match.group(0)}
        
        if group_type == "full" and len(groups) >= 4:
            version_info["major"] = int(groups[0])
            version_info["minor"] = int(groups[1])
            version_info["patch"] = int(groups[2])
            version_info["build"] = int(groups[3])
            version_info["version"] = f"{groups[0]}.{groups[1]}.{groups[2]}.{groups[3]}"
        elif group_type == "major_minor_patch" and len(groups) >= 3:
            version_info["major"] = int(groups[0])
            version_info["minor"] = int(groups[1])
            version_info["patch"] = int(groups[2])
            version_info["version"] = f"{groups[0]}.{groups[1]}.{groups[2]}"
        elif group_type == "major_minor" and len(groups) >= 2:
            version_info["major"] = int(groups[0])
            version_info["minor"] = int(groups[1])
            version_info["version"] = f"{groups[0]}.{groups[1]}"
        elif group_type == "major" and len(groups) >= 1:
            version_info["major"] = int(groups[0])
            version_info["version"] = f"{groups[0]}"
        elif group_type in ["chrome_based"] and len(groups) >= 2:
            version_info["major"] = int(groups[0])
            version_info["minor"] = int(groups[1])
            version_info["version"] = f"{groups[0]}.{groups[1]}"
        
        return version_info
    
    def _calculate_confidence(self, browser_type: BrowserType, user_agent: str, match: re.Match) -> float:
        """Calculate detection confidence"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on specific indicators
        if browser_type == BrowserType.CHROME and "Chrome" in user_agent:
            confidence += 0.3
        elif browser_type == BrowserType.EDGE and "Edg" in user_agent:
            confidence += 0.3
        elif browser_type == BrowserType.FIREFOX and "Firefox" in user_agent:
            confidence += 0.3
        
        # Full version match increases confidence
        if len(match.groups()) >= 3:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _detect_platform(self, user_agent: str) -> Optional[str]:
        """Detect operating system platform"""
        ua_lower = user_agent.lower()
        
        if "windows nt 10" in ua_lower:
            return "Windows 10"
        elif "windows nt 6.3" in ua_lower:
            return "Windows 8.1"
        elif "windows nt 6.2" in ua_lower:
            return "Windows 8"
        elif "windows" in ua_lower:
            return "Windows"
        elif "mac os x" in ua_lower or "macintosh" in ua_lower:
            return "macOS"
        elif "linux" in ua_lower:
            return "Linux"
        elif "android" in ua_lower:
            return "Android"
        elif "iphone" in ua_lower or "ipad" in ua_lower:
            return "iOS"
        
        return None
    
    def is_vulnerable(self, browser_info: BrowserInfo, cve_id: str) -> Tuple[bool, float, str]:
        """Check if browser is vulnerable to a specific CVE"""
        if cve_id not in self.compatibility_matrix:
            return False, 0.0, "CVE not in compatibility matrix"
        
        cve_info = self.compatibility_matrix[cve_id]
        browser_name = browser_info.browser_type.value
        
        # Check direct browser match
        if browser_name not in cve_info:
            # Check for Chromium-based browsers
            if browser_name in ["edge", "brave", "vivaldi", "opera"] and "chrome" in cve_info:
                browser_name = "chrome"
            elif browser_name in ["edge", "brave", "vivaldi", "opera"] and "chromium" in cve_info:
                browser_name = "chromium"
            else:
                return False, 0.0, f"Browser {browser_name} not supported for {cve_id}"
        
        version_info = cve_info[browser_name]
        min_version = version_info.get("min")
        max_version = version_info.get("max")
        
        if not browser_info.version:
            return False, 0.5, "Version unknown, cannot determine vulnerability"
        
        # Version comparison
        if min_version and not self._version_compare(browser_info.version, min_version, ">="):
            return False, 0.0, f"Version {browser_info.version} below minimum {min_version}"
        
        if max_version and not self._version_compare(browser_info.version, max_version, "<="):
            return False, 0.0, f"Version {browser_info.version} above maximum {max_version}"
        
        # Calculate confidence
        confidence = browser_info.confidence
        if min_version and max_version:
            confidence = min(confidence + 0.2, 1.0)
        
        return True, confidence, f"Vulnerable: {browser_info.version} is within range"
    
    def _version_compare(self, version1: str, version2: str, operator: str) -> bool:
        """Compare two version strings"""
        def version_tuple(v: str) -> Tuple[int, ...]:
            parts = v.split('.')
            return tuple(int(p) for p in parts if p.isdigit())
        
        v1 = version_tuple(version1)
        v2 = version_tuple(version2)
        
        if operator == ">=":
            return v1 >= v2
        elif operator == "<=":
            return v1 <= v2
        elif operator == "==":
            return v1 == v2
        elif operator == ">":
            return v1 > v2
        elif operator == "<":
            return v1 < v2
        
        return False
    
    def recommend_exploit(self, browser_info: BrowserInfo) -> List[Tuple[str, float, str]]:
        """Recommend exploits based on browser information"""
        recommendations = []
        
        for cve_id in self.compatibility_matrix.keys():
            is_vuln, confidence, reason = self.is_vulnerable(browser_info, cve_id)
            
            if is_vuln:
                recommendations.append((cve_id, confidence, reason))
        
        # Sort by confidence (highest first)
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations
    
    def get_compatible_exploits(self, browser_info: BrowserInfo) -> List[str]:
        """Get list of compatible exploit CVE IDs"""
        compatible = []
        
        for cve_id in self.compatibility_matrix.keys():
            is_vuln, _, _ = self.is_vulnerable(browser_info, cve_id)
            if is_vuln:
                compatible.append(cve_id)
        
        return compatible


def get_browser_detector() -> BrowserDetector:
    """Get browser detector instance"""
    return BrowserDetector()
