"""
ChromSploit Framework - Collaboration Module
Enables team collaboration features for bug bounty and pentesting teams
"""

import os
import json
import uuid
import sqlite3
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path
import hashlib
import threading
import logging

logger = logging.getLogger(__name__)


@dataclass
class TeamMember:
    """Represents a team member"""
    id: str
    username: str
    email: str
    role: str  # admin, pentester, viewer
    created_at: datetime
    last_active: datetime
    permissions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_active'] = self.last_active.isoformat()
        return data


@dataclass
class SharedFinding:
    """Represents a shared security finding"""
    id: str
    title: str
    description: str
    severity: str  # critical, high, medium, low, info
    cve_id: Optional[str]
    evidence_ids: List[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    status: str  # open, in_progress, resolved, false_positive
    assigned_to: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    comments: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class Project:
    """Represents a collaborative project"""
    id: str
    name: str
    description: str
    target: str
    scope: List[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    team_members: List[str]
    status: str  # active, completed, archived
    bounty_program: Optional[str] = None
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class TaskAssignment:
    """Represents a task assignment"""
    id: str
    project_id: str
    title: str
    description: str
    assigned_to: str
    assigned_by: str
    created_at: datetime
    due_date: Optional[datetime]
    status: str  # pending, in_progress, completed, blocked
    priority: str  # high, medium, low
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.due_date:
            data['due_date'] = self.due_date.isoformat()
        return data


class CollaborationManager:
    """Manages team collaboration features"""
    
    def __init__(self, db_path: str = "collaboration.db"):
        self.db_path = db_path
        self.connection = None
        self.lock = threading.Lock()
        self._init_database()
        
    def _init_database(self):
        """Initialize collaboration database"""
        with sqlite3.connect(self.db_path) as conn:
            # Team members table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS team_members (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_active TEXT NOT NULL,
                    permissions TEXT NOT NULL
                )
            """)
            
            # Projects table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    target TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    team_members TEXT NOT NULL,
                    status TEXT NOT NULL,
                    bounty_program TEXT,
                    FOREIGN KEY (created_by) REFERENCES team_members(id)
                )
            """)
            
            # Findings table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS findings (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT NOT NULL,
                    cve_id TEXT,
                    evidence_ids TEXT,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    assigned_to TEXT,
                    tags TEXT,
                    comments TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    FOREIGN KEY (created_by) REFERENCES team_members(id),
                    FOREIGN KEY (assigned_to) REFERENCES team_members(id)
                )
            """)
            
            # Task assignments table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_assignments (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    assigned_to TEXT NOT NULL,
                    assigned_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    due_date TEXT,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    FOREIGN KEY (assigned_to) REFERENCES team_members(id),
                    FOREIGN KEY (assigned_by) REFERENCES team_members(id)
                )
            """)
            
            # Activity log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    details TEXT,
                    FOREIGN KEY (user_id) REFERENCES team_members(id)
                )
            """)
            
            conn.commit()
    
    def add_team_member(self, username: str, email: str, role: str = "pentester") -> TeamMember:
        """Add a new team member"""
        member = TeamMember(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            role=role,
            created_at=datetime.now(),
            last_active=datetime.now(),
            permissions=self._get_default_permissions(role)
        )
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO team_members (id, username, email, role, created_at, last_active, permissions)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    member.id,
                    member.username,
                    member.email,
                    member.role,
                    member.created_at.isoformat(),
                    member.last_active.isoformat(),
                    json.dumps(member.permissions)
                ))
                conn.commit()
                
        self._log_activity(member.id, "user_created", "team_member", member.id)
        return member
    
    def create_project(self, name: str, description: str, target: str, 
                      scope: List[str], created_by: str, 
                      bounty_program: Optional[str] = None) -> Project:
        """Create a new project"""
        project = Project(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            target=target,
            scope=scope,
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            team_members=[created_by],
            status="active",
            bounty_program=bounty_program
        )
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO projects (id, name, description, target, scope, created_by, 
                                        created_at, updated_at, team_members, status, bounty_program)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project.id,
                    project.name,
                    project.description,
                    project.target,
                    json.dumps(project.scope),
                    project.created_by,
                    project.created_at.isoformat(),
                    project.updated_at.isoformat(),
                    json.dumps(project.team_members),
                    project.status,
                    project.bounty_program
                ))
                conn.commit()
                
        self._log_activity(created_by, "project_created", "project", project.id, 
                          {"name": name, "target": target})
        return project
    
    def add_finding(self, project_id: str, title: str, description: str,
                   severity: str, created_by: str, cve_id: Optional[str] = None,
                   evidence_ids: List[str] = None) -> SharedFinding:
        """Add a new security finding"""
        finding = SharedFinding(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            severity=severity,
            cve_id=cve_id,
            evidence_ids=evidence_ids or [],
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="open"
        )
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO findings (id, project_id, title, description, severity, cve_id,
                                        evidence_ids, created_by, created_at, updated_at, status,
                                        assigned_to, tags, comments)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    finding.id,
                    project_id,
                    finding.title,
                    finding.description,
                    finding.severity,
                    finding.cve_id,
                    json.dumps(finding.evidence_ids),
                    finding.created_by,
                    finding.created_at.isoformat(),
                    finding.updated_at.isoformat(),
                    finding.status,
                    finding.assigned_to,
                    json.dumps(finding.tags),
                    json.dumps(finding.comments)
                ))
                conn.commit()
                
        self._log_activity(created_by, "finding_created", "finding", finding.id,
                          {"title": title, "severity": severity, "project_id": project_id})
        return finding
    
    def assign_task(self, project_id: str, title: str, description: str,
                   assigned_to: str, assigned_by: str, priority: str = "medium",
                   due_date: Optional[datetime] = None) -> TaskAssignment:
        """Assign a task to a team member"""
        task = TaskAssignment(
            id=str(uuid.uuid4()),
            project_id=project_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            assigned_by=assigned_by,
            created_at=datetime.now(),
            due_date=due_date,
            status="pending",
            priority=priority
        )
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO task_assignments (id, project_id, title, description, assigned_to,
                                                assigned_by, created_at, due_date, status, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task.id,
                    task.project_id,
                    task.title,
                    task.description,
                    task.assigned_to,
                    task.assigned_by,
                    task.created_at.isoformat(),
                    task.due_date.isoformat() if task.due_date else None,
                    task.status,
                    task.priority
                ))
                conn.commit()
                
        self._log_activity(assigned_by, "task_assigned", "task", task.id,
                          {"title": title, "assigned_to": assigned_to})
        return task
    
    def add_comment_to_finding(self, finding_id: str, user_id: str, comment: str):
        """Add a comment to a finding"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                # Get current comments
                cursor = conn.execute(
                    "SELECT comments FROM findings WHERE id = ?",
                    (finding_id,)
                )
                row = cursor.fetchone()
                if row:
                    comments = json.loads(row[0])
                    new_comment = {
                        "id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "comment": comment,
                        "timestamp": datetime.now().isoformat()
                    }
                    comments.append(new_comment)
                    
                    conn.execute(
                        "UPDATE findings SET comments = ?, updated_at = ? WHERE id = ?",
                        (json.dumps(comments), datetime.now().isoformat(), finding_id)
                    )
                    conn.commit()
                    
                    self._log_activity(user_id, "comment_added", "finding", finding_id)
    
    def update_task_status(self, task_id: str, user_id: str, status: str):
        """Update task status"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE task_assignments SET status = ? WHERE id = ?",
                    (status, task_id)
                )
                conn.commit()
                
        self._log_activity(user_id, "task_status_updated", "task", task_id, {"status": status})
    
    def get_project_findings(self, project_id: str) -> List[SharedFinding]:
        """Get all findings for a project"""
        findings = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, title, description, severity, cve_id, evidence_ids,
                       created_by, created_at, updated_at, status, assigned_to,
                       tags, comments
                FROM findings
                WHERE project_id = ?
                ORDER BY created_at DESC
            """, (project_id,))
            
            for row in cursor:
                finding = SharedFinding(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    severity=row[3],
                    cve_id=row[4],
                    evidence_ids=json.loads(row[5]),
                    created_by=row[6],
                    created_at=datetime.fromisoformat(row[7]),
                    updated_at=datetime.fromisoformat(row[8]),
                    status=row[9],
                    assigned_to=row[10],
                    tags=json.loads(row[11]),
                    comments=json.loads(row[12])
                )
                findings.append(finding)
                
        return findings
    
    def get_user_tasks(self, user_id: str) -> List[TaskAssignment]:
        """Get all tasks assigned to a user"""
        tasks = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, project_id, title, description, assigned_to,
                       assigned_by, created_at, due_date, status, priority
                FROM task_assignments
                WHERE assigned_to = ?
                ORDER BY priority DESC, created_at DESC
            """, (user_id,))
            
            for row in cursor:
                task = TaskAssignment(
                    id=row[0],
                    project_id=row[1],
                    title=row[2],
                    description=row[3],
                    assigned_to=row[4],
                    assigned_by=row[5],
                    created_at=datetime.fromisoformat(row[6]),
                    due_date=datetime.fromisoformat(row[7]) if row[7] else None,
                    status=row[8],
                    priority=row[9]
                )
                tasks.append(task)
                
        return tasks
    
    def get_activity_log(self, limit: int = 50) -> List[Dict]:
        """Get recent activity log"""
        activities = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT al.timestamp, al.user_id, tm.username, al.action, 
                       al.resource_type, al.resource_id, al.details
                FROM activity_log al
                JOIN team_members tm ON al.user_id = tm.id
                ORDER BY al.id DESC
                LIMIT ?
            """, (limit,))
            
            for row in cursor:
                activity = {
                    "timestamp": row[0],
                    "user_id": row[1],
                    "username": row[2],
                    "action": row[3],
                    "resource_type": row[4],
                    "resource_id": row[5],
                    "details": json.loads(row[6]) if row[6] else None
                }
                activities.append(activity)
                
        return activities
    
    def export_project_report(self, project_id: str) -> Dict:
        """Export comprehensive project report"""
        with sqlite3.connect(self.db_path) as conn:
            # Get project details
            cursor = conn.execute(
                "SELECT * FROM projects WHERE id = ?",
                (project_id,)
            )
            project_row = cursor.fetchone()
            
            if not project_row:
                return {}
                
            # Get findings
            findings = self.get_project_findings(project_id)
            
            # Get tasks
            cursor = conn.execute(
                "SELECT * FROM task_assignments WHERE project_id = ?",
                (project_id,)
            )
            tasks = cursor.fetchall()
            
            # Build report
            report = {
                "project": {
                    "id": project_row[0],
                    "name": project_row[1],
                    "description": project_row[2],
                    "target": project_row[3],
                    "scope": json.loads(project_row[4]),
                    "status": project_row[9],
                    "bounty_program": project_row[10]
                },
                "findings": [f.to_dict() for f in findings],
                "statistics": {
                    "total_findings": len(findings),
                    "critical": len([f for f in findings if f.severity == "critical"]),
                    "high": len([f for f in findings if f.severity == "high"]),
                    "medium": len([f for f in findings if f.severity == "medium"]),
                    "low": len([f for f in findings if f.severity == "low"]),
                    "info": len([f for f in findings if f.severity == "info"]),
                    "total_tasks": len(tasks),
                    "completed_tasks": len([t for t in tasks if t[8] == "completed"])
                },
                "exported_at": datetime.now().isoformat()
            }
            
        return report
    
    def _get_default_permissions(self, role: str) -> List[str]:
        """Get default permissions for a role"""
        permissions_map = {
            "admin": ["*"],
            "pentester": ["create_finding", "update_finding", "create_task", 
                         "update_task", "view_all", "comment"],
            "viewer": ["view_all", "comment"]
        }
        return permissions_map.get(role, ["view_all"])
    
    def _log_activity(self, user_id: str, action: str, resource_type: str,
                     resource_id: str, details: Optional[Dict] = None):
        """Log user activity"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO activity_log (timestamp, user_id, action, resource_type, resource_id, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                user_id,
                action,
                resource_type,
                resource_id,
                json.dumps(details) if details else None
            ))
            conn.commit()