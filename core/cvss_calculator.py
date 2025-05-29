#!/usr/bin/env python3
"""
CVSS v3.1 Calculator for vulnerability scoring.
Implements the Common Vulnerability Scoring System version 3.1.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple, Any
import math


class AttackVector(Enum):
    """CVSS Attack Vector"""
    NETWORK = ("N", 0.85, "Network")
    ADJACENT_NETWORK = ("A", 0.62, "Adjacent Network")
    LOCAL = ("L", 0.55, "Local")
    PHYSICAL = ("P", 0.2, "Physical")


class AttackComplexity(Enum):
    """CVSS Attack Complexity"""
    LOW = ("L", 0.77, "Low")
    HIGH = ("H", 0.44, "High")


class PrivilegesRequired(Enum):
    """CVSS Privileges Required"""
    NONE = ("N", 0.85, "None")
    LOW = ("L", 0.62, "Low")
    HIGH = ("H", 0.27, "High")
    
    def get_value(self, scope_changed: bool) -> float:
        """Get value based on scope"""
        if self == PrivilegesRequired.NONE:
            return 0.85
        elif self == PrivilegesRequired.LOW:
            return 0.68 if scope_changed else 0.62
        else:  # HIGH
            return 0.50 if scope_changed else 0.27


class UserInteraction(Enum):
    """CVSS User Interaction"""
    NONE = ("N", 0.85, "None")
    REQUIRED = ("R", 0.62, "Required")


class Scope(Enum):
    """CVSS Scope"""
    UNCHANGED = ("U", "Unchanged")
    CHANGED = ("C", "Changed")


class Impact(Enum):
    """CVSS Impact (Confidentiality, Integrity, Availability)"""
    HIGH = ("H", 0.56, "High")
    LOW = ("L", 0.22, "Low")
    NONE = ("N", 0.0, "None")


class ExploitCodeMaturity(Enum):
    """CVSS Temporal - Exploit Code Maturity"""
    NOT_DEFINED = ("X", 1.0, "Not Defined")
    HIGH = ("H", 1.0, "High")
    FUNCTIONAL = ("F", 0.97, "Functional")
    PROOF_OF_CONCEPT = ("P", 0.94, "Proof-of-Concept")
    UNPROVEN = ("U", 0.91, "Unproven")


class RemediationLevel(Enum):
    """CVSS Temporal - Remediation Level"""
    NOT_DEFINED = ("X", 1.0, "Not Defined")
    UNAVAILABLE = ("U", 1.0, "Unavailable")
    WORKAROUND = ("W", 0.97, "Workaround")
    TEMPORARY_FIX = ("T", 0.96, "Temporary Fix")
    OFFICIAL_FIX = ("O", 0.95, "Official Fix")


class ReportConfidence(Enum):
    """CVSS Temporal - Report Confidence"""
    NOT_DEFINED = ("X", 1.0, "Not Defined")
    CONFIRMED = ("C", 1.0, "Confirmed")
    REASONABLE = ("R", 0.96, "Reasonable")
    UNKNOWN = ("U", 0.92, "Unknown")


@dataclass
class CVSSv3:
    """CVSS v3.1 Calculator"""
    
    # Base Score Metrics (Required)
    attack_vector: AttackVector = AttackVector.NETWORK
    attack_complexity: AttackComplexity = AttackComplexity.LOW
    privileges_required: PrivilegesRequired = PrivilegesRequired.NONE
    user_interaction: UserInteraction = UserInteraction.NONE
    scope: Scope = Scope.UNCHANGED
    confidentiality_impact: Impact = Impact.NONE
    integrity_impact: Impact = Impact.NONE
    availability_impact: Impact = Impact.NONE
    
    # Temporal Score Metrics (Optional)
    exploit_code_maturity: ExploitCodeMaturity = ExploitCodeMaturity.NOT_DEFINED
    remediation_level: RemediationLevel = RemediationLevel.NOT_DEFINED
    report_confidence: ReportConfidence = ReportConfidence.NOT_DEFINED
    
    # Environmental Score Metrics (Optional) - Not implemented for simplicity
    
    def calculate_base_score(self) -> float:
        """Calculate CVSS Base Score"""
        # Check if any impact is not None
        if (self.confidentiality_impact == Impact.NONE and 
            self.integrity_impact == Impact.NONE and 
            self.availability_impact == Impact.NONE):
            return 0.0
        
        # Calculate Impact Sub Score (ISS)
        iss = 1 - ((1 - self.confidentiality_impact.value[1]) * 
                   (1 - self.integrity_impact.value[1]) * 
                   (1 - self.availability_impact.value[1]))
        
        # Calculate Impact
        if self.scope == Scope.UNCHANGED:
            impact = 6.42 * iss
        else:  # CHANGED
            impact = 7.52 * (iss - 0.029) - 3.25 * math.pow(iss - 0.02, 15)
        
        # Calculate Exploitability
        scope_changed = self.scope == Scope.CHANGED
        exploitability = (8.22 * self.attack_vector.value[1] * 
                         self.attack_complexity.value[1] * 
                         self.privileges_required.get_value(scope_changed) * 
                         self.user_interaction.value[1])
        
        # Calculate Base Score
        if impact <= 0:
            return 0.0
        
        if self.scope == Scope.UNCHANGED:
            base_score = min((impact + exploitability), 10)
        else:  # CHANGED
            base_score = min(1.08 * (impact + exploitability), 10)
        
        # Round up to 1 decimal place
        return math.ceil(base_score * 10) / 10
    
    def calculate_temporal_score(self, base_score: Optional[float] = None) -> float:
        """Calculate CVSS Temporal Score"""
        if base_score is None:
            base_score = self.calculate_base_score()
        
        temporal_score = (base_score * 
                         self.exploit_code_maturity.value[1] * 
                         self.remediation_level.value[1] * 
                         self.report_confidence.value[1])
        
        # Round up to 1 decimal place
        return math.ceil(temporal_score * 10) / 10
    
    def get_severity_rating(self, score: float) -> str:
        """Get severity rating from CVSS score"""
        if score == 0.0:
            return "None"
        elif 0.1 <= score <= 3.9:
            return "Low"
        elif 4.0 <= score <= 6.9:
            return "Medium"
        elif 7.0 <= score <= 8.9:
            return "High"
        else:  # 9.0 - 10.0
            return "Critical"
    
    def get_vector_string(self) -> str:
        """Generate CVSS v3.1 vector string"""
        vector_parts = [
            "CVSS:3.1",
            f"AV:{self.attack_vector.value[0]}",
            f"AC:{self.attack_complexity.value[0]}",
            f"PR:{self.privileges_required.value[0]}",
            f"UI:{self.user_interaction.value[0]}",
            f"S:{self.scope.value[0]}",
            f"C:{self.confidentiality_impact.value[0]}",
            f"I:{self.integrity_impact.value[0]}",
            f"A:{self.availability_impact.value[0]}"
        ]
        
        # Add temporal metrics if not default
        if self.exploit_code_maturity != ExploitCodeMaturity.NOT_DEFINED:
            vector_parts.append(f"E:{self.exploit_code_maturity.value[0]}")
        if self.remediation_level != RemediationLevel.NOT_DEFINED:
            vector_parts.append(f"RL:{self.remediation_level.value[0]}")
        if self.report_confidence != ReportConfidence.NOT_DEFINED:
            vector_parts.append(f"RC:{self.report_confidence.value[0]}")
        
        return "/".join(vector_parts)
    
    def parse_vector_string(self, vector: str) -> bool:
        """Parse CVSS v3.1 vector string"""
        if not vector.startswith("CVSS:3.1/"):
            return False
        
        parts = vector.split("/")[1:]  # Skip CVSS:3.1
        
        metric_map = {
            "AV": {
                "N": AttackVector.NETWORK,
                "A": AttackVector.ADJACENT_NETWORK,
                "L": AttackVector.LOCAL,
                "P": AttackVector.PHYSICAL
            },
            "AC": {
                "L": AttackComplexity.LOW,
                "H": AttackComplexity.HIGH
            },
            "PR": {
                "N": PrivilegesRequired.NONE,
                "L": PrivilegesRequired.LOW,
                "H": PrivilegesRequired.HIGH
            },
            "UI": {
                "N": UserInteraction.NONE,
                "R": UserInteraction.REQUIRED
            },
            "S": {
                "U": Scope.UNCHANGED,
                "C": Scope.CHANGED
            },
            "C": {
                "N": Impact.NONE,
                "L": Impact.LOW,
                "H": Impact.HIGH
            },
            "I": {
                "N": Impact.NONE,
                "L": Impact.LOW,
                "H": Impact.HIGH
            },
            "A": {
                "N": Impact.NONE,
                "L": Impact.LOW,
                "H": Impact.HIGH
            },
            "E": {
                "X": ExploitCodeMaturity.NOT_DEFINED,
                "U": ExploitCodeMaturity.UNPROVEN,
                "P": ExploitCodeMaturity.PROOF_OF_CONCEPT,
                "F": ExploitCodeMaturity.FUNCTIONAL,
                "H": ExploitCodeMaturity.HIGH
            },
            "RL": {
                "X": RemediationLevel.NOT_DEFINED,
                "O": RemediationLevel.OFFICIAL_FIX,
                "T": RemediationLevel.TEMPORARY_FIX,
                "W": RemediationLevel.WORKAROUND,
                "U": RemediationLevel.UNAVAILABLE
            },
            "RC": {
                "X": ReportConfidence.NOT_DEFINED,
                "U": ReportConfidence.UNKNOWN,
                "R": ReportConfidence.REASONABLE,
                "C": ReportConfidence.CONFIRMED
            }
        }
        
        try:
            for part in parts:
                if ":" not in part:
                    continue
                
                metric, value = part.split(":")
                
                if metric == "AV" and value in metric_map["AV"]:
                    self.attack_vector = metric_map["AV"][value]
                elif metric == "AC" and value in metric_map["AC"]:
                    self.attack_complexity = metric_map["AC"][value]
                elif metric == "PR" and value in metric_map["PR"]:
                    self.privileges_required = metric_map["PR"][value]
                elif metric == "UI" and value in metric_map["UI"]:
                    self.user_interaction = metric_map["UI"][value]
                elif metric == "S" and value in metric_map["S"]:
                    self.scope = metric_map["S"][value]
                elif metric == "C" and value in metric_map["C"]:
                    self.confidentiality_impact = metric_map["C"][value]
                elif metric == "I" and value in metric_map["I"]:
                    self.integrity_impact = metric_map["I"][value]
                elif metric == "A" and value in metric_map["A"]:
                    self.availability_impact = metric_map["A"][value]
                elif metric == "E" and value in metric_map["E"]:
                    self.exploit_code_maturity = metric_map["E"][value]
                elif metric == "RL" and value in metric_map["RL"]:
                    self.remediation_level = metric_map["RL"][value]
                elif metric == "RC" and value in metric_map["RC"]:
                    self.report_confidence = metric_map["RC"][value]
            
            return True
            
        except Exception:
            return False
    
    def get_detailed_analysis(self) -> Dict[str, Any]:
        """Get detailed CVSS analysis"""
        base_score = self.calculate_base_score()
        temporal_score = self.calculate_temporal_score(base_score)
        
        return {
            "scores": {
                "base_score": base_score,
                "temporal_score": temporal_score,
                "base_severity": self.get_severity_rating(base_score),
                "temporal_severity": self.get_severity_rating(temporal_score)
            },
            "vector_string": self.get_vector_string(),
            "metrics": {
                "base": {
                    "attack_vector": self.attack_vector.value[2],
                    "attack_complexity": self.attack_complexity.value[2],
                    "privileges_required": self.privileges_required.value[2],
                    "user_interaction": self.user_interaction.value[2],
                    "scope": self.scope.value[1],
                    "confidentiality_impact": self.confidentiality_impact.value[2],
                    "integrity_impact": self.integrity_impact.value[2],
                    "availability_impact": self.availability_impact.value[2]
                },
                "temporal": {
                    "exploit_code_maturity": self.exploit_code_maturity.value[2],
                    "remediation_level": self.remediation_level.value[2],
                    "report_confidence": self.report_confidence.value[2]
                }
            },
            "impact_analysis": self._analyze_impact(),
            "exploitability_analysis": self._analyze_exploitability()
        }
    
    def _analyze_impact(self) -> Dict[str, str]:
        """Analyze impact characteristics"""
        analysis = {}
        
        # Confidentiality Impact
        if self.confidentiality_impact == Impact.HIGH:
            analysis["confidentiality"] = "Total loss of confidentiality, resulting in all resources being divulged"
        elif self.confidentiality_impact == Impact.LOW:
            analysis["confidentiality"] = "Some loss of confidentiality, access to some restricted information"
        else:
            analysis["confidentiality"] = "No impact to confidentiality"
        
        # Integrity Impact
        if self.integrity_impact == Impact.HIGH:
            analysis["integrity"] = "Total loss of integrity, attacker can modify any files"
        elif self.integrity_impact == Impact.LOW:
            analysis["integrity"] = "Modification of data is possible but limited"
        else:
            analysis["integrity"] = "No impact to integrity"
        
        # Availability Impact
        if self.availability_impact == Impact.HIGH:
            analysis["availability"] = "Total loss of availability, resulting in complete denial of access"
        elif self.availability_impact == Impact.LOW:
            analysis["availability"] = "Performance is reduced or interruptions in resource availability"
        else:
            analysis["availability"] = "No impact to availability"
        
        # Scope
        if self.scope == Scope.CHANGED:
            analysis["scope"] = "Vulnerable component impacts resources beyond its security scope"
        else:
            analysis["scope"] = "Vulnerable component impacts resources only within its security scope"
        
        return analysis
    
    def _analyze_exploitability(self) -> Dict[str, str]:
        """Analyze exploitability characteristics"""
        analysis = {}
        
        # Attack Vector
        if self.attack_vector == AttackVector.NETWORK:
            analysis["attack_vector"] = "Remotely exploitable from the internet"
        elif self.attack_vector == AttackVector.ADJACENT_NETWORK:
            analysis["attack_vector"] = "Exploitable from the same network segment"
        elif self.attack_vector == AttackVector.LOCAL:
            analysis["attack_vector"] = "Requires local access to the vulnerable system"
        else:
            analysis["attack_vector"] = "Requires physical access to the device"
        
        # Attack Complexity
        if self.attack_complexity == AttackComplexity.LOW:
            analysis["attack_complexity"] = "No specialized conditions required for exploitation"
        else:
            analysis["attack_complexity"] = "Successful attack requires specific conditions"
        
        # Privileges Required
        if self.privileges_required == PrivilegesRequired.NONE:
            analysis["privileges_required"] = "No privileges required to exploit"
        elif self.privileges_required == PrivilegesRequired.LOW:
            analysis["privileges_required"] = "Basic user privileges required"
        else:
            analysis["privileges_required"] = "Administrative privileges required"
        
        # User Interaction
        if self.user_interaction == UserInteraction.NONE:
            analysis["user_interaction"] = "Can be exploited without user interaction"
        else:
            analysis["user_interaction"] = "Requires user to perform some action"
        
        return analysis


def calculate_cvss_from_cve_details(vulnerability_details: Dict[str, Any]) -> CVSSv3:
    """Calculate CVSS score from vulnerability details"""
    cvss = CVSSv3()
    
    # Parse vector string if provided
    if "cvss_vector" in vulnerability_details and vulnerability_details["cvss_vector"]:
        cvss.parse_vector_string(vulnerability_details["cvss_vector"])
        return cvss
    
    # Otherwise, estimate based on vulnerability type and characteristics
    vuln_type = vulnerability_details.get("type", "").lower()
    
    # Common vulnerability patterns
    if "rce" in vuln_type or "remote code execution" in vuln_type:
        cvss.attack_vector = AttackVector.NETWORK
        cvss.attack_complexity = AttackComplexity.LOW
        cvss.privileges_required = PrivilegesRequired.NONE
        cvss.user_interaction = UserInteraction.NONE
        cvss.scope = Scope.CHANGED
        cvss.confidentiality_impact = Impact.HIGH
        cvss.integrity_impact = Impact.HIGH
        cvss.availability_impact = Impact.HIGH
        
    elif "xss" in vuln_type or "cross-site scripting" in vuln_type:
        cvss.attack_vector = AttackVector.NETWORK
        cvss.attack_complexity = AttackComplexity.LOW
        cvss.privileges_required = PrivilegesRequired.NONE
        cvss.user_interaction = UserInteraction.REQUIRED
        cvss.scope = Scope.CHANGED
        cvss.confidentiality_impact = Impact.LOW
        cvss.integrity_impact = Impact.LOW
        cvss.availability_impact = Impact.NONE
        
    elif "sql injection" in vuln_type or "sqli" in vuln_type:
        cvss.attack_vector = AttackVector.NETWORK
        cvss.attack_complexity = AttackComplexity.LOW
        cvss.privileges_required = PrivilegesRequired.NONE
        cvss.user_interaction = UserInteraction.NONE
        cvss.scope = Scope.UNCHANGED
        cvss.confidentiality_impact = Impact.HIGH
        cvss.integrity_impact = Impact.HIGH
        cvss.availability_impact = Impact.HIGH
        
    elif "privilege escalation" in vuln_type:
        cvss.attack_vector = AttackVector.LOCAL
        cvss.attack_complexity = AttackComplexity.LOW
        cvss.privileges_required = PrivilegesRequired.LOW
        cvss.user_interaction = UserInteraction.NONE
        cvss.scope = Scope.CHANGED
        cvss.confidentiality_impact = Impact.HIGH
        cvss.integrity_impact = Impact.HIGH
        cvss.availability_impact = Impact.HIGH
        
    elif "dos" in vuln_type or "denial of service" in vuln_type:
        cvss.attack_vector = AttackVector.NETWORK
        cvss.attack_complexity = AttackComplexity.LOW
        cvss.privileges_required = PrivilegesRequired.NONE
        cvss.user_interaction = UserInteraction.NONE
        cvss.scope = Scope.UNCHANGED
        cvss.confidentiality_impact = Impact.NONE
        cvss.integrity_impact = Impact.NONE
        cvss.availability_impact = Impact.HIGH
        
    elif "information disclosure" in vuln_type:
        cvss.attack_vector = AttackVector.NETWORK
        cvss.attack_complexity = AttackComplexity.LOW
        cvss.privileges_required = PrivilegesRequired.LOW
        cvss.user_interaction = UserInteraction.NONE
        cvss.scope = Scope.UNCHANGED
        cvss.confidentiality_impact = Impact.HIGH
        cvss.integrity_impact = Impact.NONE
        cvss.availability_impact = Impact.NONE
        
    else:
        # Default medium severity
        cvss.attack_vector = AttackVector.NETWORK
        cvss.attack_complexity = AttackComplexity.LOW
        cvss.privileges_required = PrivilegesRequired.LOW
        cvss.user_interaction = UserInteraction.NONE
        cvss.scope = Scope.UNCHANGED
        cvss.confidentiality_impact = Impact.LOW
        cvss.integrity_impact = Impact.LOW
        cvss.availability_impact = Impact.LOW
    
    return cvss


# Example usage
if __name__ == "__main__":
    # Test CVSS calculator
    cvss = CVSSv3(
        attack_vector=AttackVector.NETWORK,
        attack_complexity=AttackComplexity.LOW,
        privileges_required=PrivilegesRequired.NONE,
        user_interaction=UserInteraction.NONE,
        scope=Scope.CHANGED,
        confidentiality_impact=Impact.HIGH,
        integrity_impact=Impact.HIGH,
        availability_impact=Impact.HIGH
    )
    
    print(f"Base Score: {cvss.calculate_base_score()}")
    print(f"Severity: {cvss.get_severity_rating(cvss.calculate_base_score())}")
    print(f"Vector: {cvss.get_vector_string()}")
    
    # Test vector parsing
    test_vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"
    cvss2 = CVSSv3()
    cvss2.parse_vector_string(test_vector)
    print(f"\nParsed Score: {cvss2.calculate_base_score()}")
    print(f"Parsed Vector: {cvss2.get_vector_string()}")