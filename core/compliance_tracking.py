"""
ChromSploit Framework - Compliance and Legal Tracking Module
Ensures compliance with legal requirements and bug bounty program rules
"""

import os
import json
import sqlite3
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class ComplianceRule:
    """Represents a compliance rule or requirement"""
    id: str
    category: str  # legal, bounty_program, ethical, regulatory
    title: str
    description: str
    requirements: List[str]
    consequences: str
    severity: str  # critical, high, medium, low
    active: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Authorization:
    """Represents testing authorization"""
    id: str
    project_id: str
    target: str
    scope: List[str]
    authorized_by: str
    authorization_type: str  # written_consent, bug_bounty, responsible_disclosure
    start_date: datetime
    end_date: Optional[datetime]
    document_path: Optional[str]
    restrictions: List[str] = field(default_factory=list)
    approved: bool = False
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['start_date'] = self.start_date.isoformat()
        if self.end_date:
            data['end_date'] = self.end_date.isoformat()
        return data


@dataclass
class ComplianceCheck:
    """Represents a compliance check result"""
    id: str
    check_type: str
    target: str
    performed_at: datetime
    performed_by: str
    status: str  # passed, failed, warning
    findings: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['performed_at'] = self.performed_at.isoformat()
        return data


@dataclass
class LegalNotice:
    """Legal notice or disclaimer"""
    id: str
    type: str  # disclaimer, warning, terms
    title: str
    content: str
    requires_acknowledgment: bool
    created_at: datetime
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


class ComplianceTracker:
    """Tracks compliance and legal requirements"""
    
    def __init__(self, db_path: str = "compliance.db"):
        self.db_path = db_path
        self._init_database()
        self._load_default_rules()
        
    def _init_database(self):
        """Initialize compliance database"""
        with sqlite3.connect(self.db_path) as conn:
            # Compliance rules table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS compliance_rules (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    requirements TEXT NOT NULL,
                    consequences TEXT,
                    severity TEXT NOT NULL,
                    active BOOLEAN DEFAULT 1
                )
            """)
            
            # Authorizations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS authorizations (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    target TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    authorized_by TEXT NOT NULL,
                    authorization_type TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    document_path TEXT,
                    restrictions TEXT,
                    approved BOOLEAN DEFAULT 0
                )
            """)
            
            # Compliance checks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS compliance_checks (
                    id TEXT PRIMARY KEY,
                    check_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    performed_at TEXT NOT NULL,
                    performed_by TEXT NOT NULL,
                    status TEXT NOT NULL,
                    findings TEXT,
                    recommendations TEXT
                )
            """)
            
            # Legal notices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS legal_notices (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    requires_acknowledgment BOOLEAN DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Acknowledgments table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS acknowledgments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    notice_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    acknowledged_at TEXT NOT NULL,
                    ip_address TEXT,
                    FOREIGN KEY (notice_id) REFERENCES legal_notices(id)
                )
            """)
            
            conn.commit()
    
    def _load_default_rules(self):
        """Load default compliance rules"""
        default_rules = [
            ComplianceRule(
                id="rule_001",
                category="legal",
                title="Authorization Required",
                description="Written authorization is required before testing any target",
                requirements=[
                    "Obtain written consent from target owner",
                    "Verify scope and restrictions",
                    "Document authorization details"
                ],
                consequences="Legal prosecution, criminal charges",
                severity="critical"
            ),
            ComplianceRule(
                id="rule_002",
                category="bounty_program",
                title="Stay Within Scope",
                description="Testing must remain within defined scope of bug bounty program",
                requirements=[
                    "Review program scope carefully",
                    "Do not test out-of-scope assets",
                    "Report accidental out-of-scope findings responsibly"
                ],
                consequences="Disqualification from program, legal action",
                severity="high"
            ),
            ComplianceRule(
                id="rule_003",
                category="ethical",
                title="No Destructive Testing",
                description="Do not perform actions that could damage or disrupt services",
                requirements=[
                    "Avoid automated scanning that could cause DoS",
                    "Do not delete or modify data",
                    "Stop testing if you notice service degradation"
                ],
                consequences="Criminal charges, civil liability",
                severity="critical"
            ),
            ComplianceRule(
                id="rule_004",
                category="ethical",
                title="Data Privacy",
                description="Respect privacy of any data encountered during testing",
                requirements=[
                    "Do not access or exfiltrate personal data",
                    "Report data exposure without accessing contents",
                    "Delete any accidentally obtained data"
                ],
                consequences="Privacy law violations, criminal charges",
                severity="critical"
            ),
            ComplianceRule(
                id="rule_005",
                category="regulatory",
                title="GDPR Compliance",
                description="Comply with GDPR when handling EU citizen data",
                requirements=[
                    "Do not process personal data without legal basis",
                    "Report data breaches within 72 hours",
                    "Respect data subject rights"
                ],
                consequences="Fines up to 4% of annual revenue or €20M",
                severity="high"
            ),
            ComplianceRule(
                id="rule_006",
                category="bounty_program",
                title="Responsible Disclosure",
                description="Follow responsible disclosure guidelines",
                requirements=[
                    "Report findings only through official channels",
                    "Do not publicly disclose without permission",
                    "Allow reasonable time for fixes"
                ],
                consequences="Loss of bounty, legal action",
                severity="high"
            )
        ]
        
        # Insert default rules if not exists
        with sqlite3.connect(self.db_path) as conn:
            for rule in default_rules:
                conn.execute("""
                    INSERT OR IGNORE INTO compliance_rules 
                    (id, category, title, description, requirements, consequences, severity, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rule.id,
                    rule.category,
                    rule.title,
                    rule.description,
                    json.dumps(rule.requirements),
                    rule.consequences,
                    rule.severity,
                    rule.active
                ))
            conn.commit()
    
    def check_authorization(self, target: str, scope: List[str]) -> Tuple[bool, List[str]]:
        """Check if testing is authorized for target"""
        issues = []
        
        with sqlite3.connect(self.db_path) as conn:
            # Check for valid authorization
            cursor = conn.execute("""
                SELECT * FROM authorizations
                WHERE target = ? AND approved = 1
                AND (end_date IS NULL OR datetime(end_date) > datetime('now'))
            """, (target,))
            
            auth = cursor.fetchone()
            
            if not auth:
                issues.append("No valid authorization found for target")
                return False, issues
                
            # Check scope
            auth_scope = json.loads(auth[3])  # scope column
            for item in scope:
                if not any(self._matches_scope(item, allowed) for allowed in auth_scope):
                    issues.append(f"Scope item '{item}' not authorized")
                    
            # Check restrictions
            if auth[9]:  # restrictions column
                restrictions = json.loads(auth[9])
                issues.extend([f"Restriction: {r}" for r in restrictions])
                
        return len(issues) == 0, issues
    
    def add_authorization(self, project_id: str, target: str, scope: List[str],
                         authorized_by: str, auth_type: str,
                         start_date: datetime, end_date: Optional[datetime] = None,
                         document_path: Optional[str] = None,
                         restrictions: List[str] = None) -> Authorization:
        """Add new testing authorization"""
        import uuid
        
        auth = Authorization(
            id=str(uuid.uuid4()),
            project_id=project_id,
            target=target,
            scope=scope,
            authorized_by=authorized_by,
            authorization_type=auth_type,
            start_date=start_date,
            end_date=end_date,
            document_path=document_path,
            restrictions=restrictions or [],
            approved=False
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO authorizations
                (id, project_id, target, scope, authorized_by, authorization_type,
                 start_date, end_date, document_path, restrictions, approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                auth.id,
                auth.project_id,
                auth.target,
                json.dumps(auth.scope),
                auth.authorized_by,
                auth.authorization_type,
                auth.start_date.isoformat(),
                auth.end_date.isoformat() if auth.end_date else None,
                auth.document_path,
                json.dumps(auth.restrictions),
                auth.approved
            ))
            conn.commit()
            
        return auth
    
    def perform_compliance_check(self, check_type: str, target: str,
                               performed_by: str) -> ComplianceCheck:
        """Perform compliance check"""
        import uuid
        
        findings = []
        recommendations = []
        status = "passed"
        
        if check_type == "pre_test":
            # Check authorization
            auth_ok, auth_issues = self.check_authorization(target, [target])
            if not auth_ok:
                status = "failed"
                findings.extend(auth_issues)
                recommendations.append("Obtain proper authorization before testing")
                
            # Check active rules
            rules = self.get_active_rules()
            for rule in rules:
                if rule.severity == "critical":
                    findings.append(f"Critical rule: {rule.title}")
                    recommendations.extend(rule.requirements)
                    
        elif check_type == "data_handling":
            # Check for data privacy compliance
            findings.append("Ensure no personal data is accessed or stored")
            recommendations.append("Use data minimization principles")
            recommendations.append("Delete any test data after completion")
            
        elif check_type == "disclosure":
            # Check disclosure requirements
            findings.append("Verify responsible disclosure process is followed")
            recommendations.append("Use only authorized communication channels")
            recommendations.append("Do not publicly disclose without permission")
            
        check = ComplianceCheck(
            id=str(uuid.uuid4()),
            check_type=check_type,
            target=target,
            performed_at=datetime.now(),
            performed_by=performed_by,
            status=status,
            findings=findings,
            recommendations=recommendations
        )
        
        # Save check
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO compliance_checks
                (id, check_type, target, performed_at, performed_by, status, findings, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                check.id,
                check.check_type,
                check.target,
                check.performed_at.isoformat(),
                check.performed_by,
                check.status,
                json.dumps(check.findings),
                json.dumps(check.recommendations)
            ))
            conn.commit()
            
        return check
    
    def get_active_rules(self, category: Optional[str] = None) -> List[ComplianceRule]:
        """Get active compliance rules"""
        rules = []
        
        with sqlite3.connect(self.db_path) as conn:
            if category:
                cursor = conn.execute(
                    "SELECT * FROM compliance_rules WHERE active = 1 AND category = ?",
                    (category,)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM compliance_rules WHERE active = 1"
                )
                
            for row in cursor:
                rule = ComplianceRule(
                    id=row[0],
                    category=row[1],
                    title=row[2],
                    description=row[3],
                    requirements=json.loads(row[4]),
                    consequences=row[5],
                    severity=row[6],
                    active=bool(row[7])
                )
                rules.append(rule)
                
        return rules
    
    def add_legal_notice(self, notice_type: str, title: str, content: str,
                        requires_acknowledgment: bool = True) -> LegalNotice:
        """Add legal notice"""
        import uuid
        
        notice = LegalNotice(
            id=str(uuid.uuid4()),
            type=notice_type,
            title=title,
            content=content,
            requires_acknowledgment=requires_acknowledgment,
            created_at=datetime.now()
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO legal_notices
                (id, type, title, content, requires_acknowledgment, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                notice.id,
                notice.type,
                notice.title,
                notice.content,
                notice.requires_acknowledgment,
                notice.created_at.isoformat()
            ))
            conn.commit()
            
        return notice
    
    def acknowledge_notice(self, notice_id: str, user_id: str,
                          ip_address: Optional[str] = None):
        """Record user acknowledgment of legal notice"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO acknowledgments
                (notice_id, user_id, acknowledged_at, ip_address)
                VALUES (?, ?, ?, ?)
            """, (
                notice_id,
                user_id,
                datetime.now().isoformat(),
                ip_address
            ))
            conn.commit()
    
    def get_unacknowledged_notices(self, user_id: str) -> List[LegalNotice]:
        """Get legal notices that user hasn't acknowledged"""
        notices = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT ln.* FROM legal_notices ln
                WHERE ln.requires_acknowledgment = 1
                AND ln.id NOT IN (
                    SELECT notice_id FROM acknowledgments
                    WHERE user_id = ?
                )
            """, (user_id,))
            
            for row in cursor:
                notice = LegalNotice(
                    id=row[0],
                    type=row[1],
                    title=row[2],
                    content=row[3],
                    requires_acknowledgment=bool(row[4]),
                    created_at=datetime.fromisoformat(row[5])
                )
                notices.append(notice)
                
        return notices
    
    def generate_compliance_report(self, project_id: str) -> Dict[str, Any]:
        """Generate compliance report for project"""
        report = {
            "project_id": project_id,
            "generated_at": datetime.now().isoformat(),
            "authorizations": [],
            "compliance_checks": [],
            "active_rules": [],
            "risk_assessment": {}
        }
        
        with sqlite3.connect(self.db_path) as conn:
            # Get authorizations
            cursor = conn.execute(
                "SELECT * FROM authorizations WHERE project_id = ?",
                (project_id,)
            )
            for row in cursor:
                report["authorizations"].append({
                    "target": row[2],
                    "type": row[5],
                    "approved": bool(row[10]),
                    "expires": row[7]
                })
                
            # Get compliance checks
            cursor = conn.execute(
                "SELECT * FROM compliance_checks ORDER BY performed_at DESC LIMIT 10"
            )
            for row in cursor:
                report["compliance_checks"].append({
                    "type": row[1],
                    "target": row[2],
                    "performed_at": row[3],
                    "status": row[5]
                })
                
        # Add active rules summary
        rules = self.get_active_rules()
        critical_rules = [r for r in rules if r.severity == "critical"]
        high_rules = [r for r in rules if r.severity == "high"]
        
        report["active_rules"] = {
            "total": len(rules),
            "critical": len(critical_rules),
            "high": len(high_rules)
        }
        
        # Risk assessment
        report["risk_assessment"] = {
            "compliance_level": "high" if len(critical_rules) == 0 else "critical",
            "recommendations": [
                "Ensure all critical compliance rules are followed",
                "Maintain valid authorization for all targets",
                "Follow responsible disclosure guidelines"
            ]
        }
        
        return report
    
    def _matches_scope(self, item: str, allowed: str) -> bool:
        """Check if item matches allowed scope pattern"""
        # Simple pattern matching (can be enhanced)
        if allowed.startswith("*."):
            # Wildcard subdomain
            domain = allowed[2:]
            return item.endswith(domain)
        return item == allowed
    
    def get_legal_disclaimer(self) -> str:
        """Get standard legal disclaimer"""
        return """
IMPORTANT LEGAL NOTICE:

This tool is provided for authorized security testing and educational purposes only.
By using this tool, you acknowledge and agree to the following:

1. AUTHORIZATION REQUIRED: You must have explicit written authorization before 
   testing any systems, networks, or applications that you do not own.

2. COMPLIANCE: You must comply with all applicable laws, regulations, and 
   bug bounty program rules in your jurisdiction.

3. NO MALICIOUS USE: This tool must not be used for any malicious, illegal, 
   or unauthorized purposes.

4. LIABILITY: The developers of this tool are not responsible for any misuse 
   or damage caused by the use of this tool.

5. DATA PRIVACY: You must respect the privacy of any data encountered during 
   testing and follow data protection regulations.

By continuing, you confirm that you understand and will comply with these terms.
"""