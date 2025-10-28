"""
Build Orchestration System - Manages the 5-LLM build pipeline
Coordinates Q Assistant → Code Writer → Test Auditor → Verification Overseer → Release Manager
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
from llm_roles_descriptor import LLMRole, get_role_by_name


class BuildPhase(Enum):
    """Phases of a build project"""
    DISCOVERY = "discovery"  # Q Assistant: Extract requirements
    PLANNING = "planning"    # Q Assistant: Plan the build
    IMPLEMENTATION = "implementation"  # Code Writer: Build it
    TESTING = "testing"      # Test Auditor: Test it
    VERIFICATION = "verification"  # Verification Overseer: Verify it
    RELEASE = "release"      # Release Manager: Release it
    COMPLETED = "completed"  # Build complete
    FAILED = "failed"        # Build failed


@dataclass
class LLMAssignment:
    """Assignment of a specific LLM to a role"""
    role: str  # LLMRole.value
    llm_id: str  # ID of the LLM instance
    llm_name: str  # Display name
    llm_provider: str  # e.g., "openai", "anthropic", "local"
    assigned_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BuildPhaseResult:
    """Result from completion of a build phase"""
    phase: str  # BuildPhase.value
    status: str  # "success", "warning", "failed"
    completed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    llm_role: Optional[str] = None
    llm_name: Optional[str] = None
    output: Dict[str, Any] = field(default_factory=dict)  # Phase-specific output
    issues: List[str] = field(default_factory=list)  # Any issues encountered
    next_phase: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BuildProject:
    """A complete build project managed by the 5-LLM system"""
    project_id: str
    project_name: str
    description: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    current_phase: str = field(default=BuildPhase.DISCOVERY.value)
    status: str = field(default="in_progress")  # in_progress, ready_for_release, failed, completed
    
    # LLM Assignments
    llm_assignments: Dict[str, LLMAssignment] = field(default_factory=dict)
    
    # Extracted Requirements (by Q Assistant)
    requirements: Dict[str, Any] = field(default_factory=dict)
    design_specs: Dict[str, Any] = field(default_factory=dict)
    
    # Implementation Plan (by Q Assistant → Code Writer)
    implementation_plan: Dict[str, Any] = field(default_factory=dict)
    
    # Implementation Results (by Code Writer)
    implementation: Dict[str, Any] = field(default_factory=dict)
    source_code_summary: str = ""
    
    # Test Results (by Test Auditor)
    test_results: Dict[str, Any] = field(default_factory=dict)
    test_coverage: float = 0.0
    critical_issues: List[str] = field(default_factory=list)
    
    # Verification Results (by Verification Overseer)
    verification_report: Dict[str, Any] = field(default_factory=dict)
    go_no_go_decision: Optional[str] = None  # "go", "no_go", "go_with_conditions"
    
    # Release Information (by Release Manager)
    release_notes: str = ""
    documentation: Dict[str, str] = field(default_factory=dict)
    deployment_plan: Dict[str, Any] = field(default_factory=dict)
    
    # Phase History
    phase_results: List[BuildPhaseResult] = field(default_factory=list)
    
    # Timeline
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage/API response"""
        data = asdict(self)
        data['phase_results'] = [pr.to_dict() if isinstance(pr, BuildPhaseResult) else pr for pr in self.phase_results]
        data['llm_assignments'] = {k: v.to_dict() if isinstance(v, LLMAssignment) else v for k, v in self.llm_assignments.items()}
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BuildProject':
        """Create from dictionary (from storage/API)"""
        # Reconstruct complex types
        assignments = {}
        for role, assign_data in data.get('llm_assignments', {}).items():
            if isinstance(assign_data, dict):
                assignments[role] = LLMAssignment(**assign_data)
            else:
                assignments[role] = assign_data
        
        phase_results = []
        for pr_data in data.get('phase_results', []):
            if isinstance(pr_data, dict):
                phase_results.append(BuildPhaseResult(**pr_data))
            else:
                phase_results.append(pr_data)
        
        data['llm_assignments'] = assignments
        data['phase_results'] = phase_results
        
        return cls(**data)


class BuildOrchestrator:
    """
    Orchestrates the entire build process across 5 LLM roles.
    Manages project lifecycle from requirements through release.
    """
    
    def __init__(self, storage_dir: str = "./builds"):
        """Initialize the orchestrator with a storage directory"""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.projects: Dict[str, BuildProject] = {}
        self._load_projects()
    
    def _load_projects(self):
        """Load existing projects from storage"""
        for project_file in self.storage_dir.glob("*.json"):
            try:
                with open(project_file, 'r') as f:
                    data = json.load(f)
                    project = BuildProject.from_dict(data)
                    self.projects[project.project_id] = project
            except Exception as e:
                print(f"Error loading project {project_file}: {e}")
    
    def _save_project(self, project: BuildProject):
        """Save project to storage"""
        project_file = self.storage_dir / f"{project.project_id}.json"
        try:
            with open(project_file, 'w') as f:
                json.dump(project.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving project {project.project_id}: {e}")
    
    def create_project(self, project_id: str, project_name: str, description: str) -> BuildProject:
        """Create a new build project"""
        project = BuildProject(
            project_id=project_id,
            project_name=project_name,
            description=description,
            started_at=datetime.utcnow().isoformat()
        )
        self.projects[project_id] = project
        self._save_project(project)
        return project
    
    def get_project(self, project_id: str) -> Optional[BuildProject]:
        """Get a project by ID"""
        return self.projects.get(project_id)
    
    def assign_llm_to_role(self, project_id: str, role: str, llm_id: str, llm_name: str, 
                          llm_provider: str) -> bool:
        """Assign an LLM instance to a role for this project"""
        project = self.get_project(project_id)
        if not project:
            return False
        
        # Validate role
        if not get_role_by_name(role):
            return False
        
        assignment = LLMAssignment(
            role=role,
            llm_id=llm_id,
            llm_name=llm_name,
            llm_provider=llm_provider
        )
        project.llm_assignments[role] = assignment
        self._save_project(project)
        return True
    
    def get_current_phase_info(self, project_id: str) -> Optional[Dict]:
        """Get information about current phase"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        phase = project.current_phase
        phase_enum = BuildPhase[phase.upper()] if phase.upper() in BuildPhase.__members__ else None
        
        return {
            "phase": phase,
            "status": project.status,
            "next_role": self._get_phase_role(phase),
            "phase_number": self._get_phase_number(phase),
            "total_phases": 7
        }
    
    def _get_phase_role(self, phase: str) -> Optional[str]:
        """Get the LLM role responsible for this phase"""
        phase_to_role = {
            BuildPhase.DISCOVERY.value: LLMRole.Q_ASSISTANT.value,
            BuildPhase.PLANNING.value: LLMRole.Q_ASSISTANT.value,
            BuildPhase.IMPLEMENTATION.value: LLMRole.CODE_WRITER.value,
            BuildPhase.TESTING.value: LLMRole.TEST_AUDITOR.value,
            BuildPhase.VERIFICATION.value: LLMRole.VERIFICATION_OVERSEER.value,
            BuildPhase.RELEASE.value: LLMRole.RELEASE_MANAGER.value,
        }
        return phase_to_role.get(phase)
    
    def _get_phase_number(self, phase: str) -> int:
        """Get phase sequence number"""
        phases = [
            BuildPhase.DISCOVERY.value,
            BuildPhase.PLANNING.value,
            BuildPhase.IMPLEMENTATION.value,
            BuildPhase.TESTING.value,
            BuildPhase.VERIFICATION.value,
            BuildPhase.RELEASE.value,
            BuildPhase.COMPLETED.value
        ]
        return phases.index(phase) + 1 if phase in phases else 0
    
    def record_phase_result(self, project_id: str, phase_result: BuildPhaseResult) -> bool:
        """Record completion of a phase"""
        project = self.get_project(project_id)
        if not project:
            return False
        
        project.phase_results.append(phase_result)
        
        # Update current phase if specified
        if phase_result.next_phase:
            project.current_phase = phase_result.next_phase
        
        # Update overall status
        if phase_result.status == "failed":
            project.status = "failed"
            project.current_phase = BuildPhase.FAILED.value
        
        self._save_project(project)
        return True
    
    def get_project_context(self, project_id: str) -> Dict[str, Any]:
        """Get full context for a project (for sharing between LLMs)"""
        project = self.get_project(project_id)
        if not project:
            return {}
        
        return {
            "project": project.to_dict(),
            "current_phase": project.current_phase,
            "llm_assignments": {k: v.to_dict() for k, v in project.llm_assignments.items()},
            "requirements": project.requirements,
            "design_specs": project.design_specs,
            "implementation_plan": project.implementation_plan,
        }
    
    def list_projects(self) -> List[Dict]:
        """List all projects with summary info"""
        return [{
            "project_id": p.project_id,
            "project_name": p.project_name,
            "status": p.status,
            "current_phase": p.current_phase,
            "created_at": p.created_at,
            "started_at": p.started_at,
            "completed_at": p.completed_at
        } for p in self.projects.values()]


# Global orchestrator instance
orchestrator = BuildOrchestrator()
