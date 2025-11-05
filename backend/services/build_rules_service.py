"""
Build Rules Metadata Service
Attach build rules/metadata to each build like a QR code or manifest.
System reads this to understand project structure, conventions, and rules.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class RuleCategory(str, Enum):
    FILE_STRUCTURE = "file_structure"
    NAMING_CONVENTION = "naming_convention"
    CODE_STYLE = "code_style"
    BUILD_PROCESS = "build_process"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    SECURITY = "security"
    DOCUMENTATION = "documentation"


@dataclass
class BuildRule:
    """Individual build rule"""
    category: RuleCategory
    name: str
    description: str
    enforcement: str  # "required", "recommended", "optional"
    examples: List[str]
    violations_action: str  # "block", "warn", "log"


@dataclass
class BuildManifest:
    """Build manifest - the 'QR code' for the project"""
    manifest_id: str
    workspace_id: str
    project_name: str
    version: str
    created_at: str
    updated_at: str
    
    # Project metadata
    languages: List[str]
    frameworks: List[str]
    dependencies: Dict[str, str]
    
    # Build rules
    rules: List[Dict[str, Any]]
    
    # File structure expectations
    directory_structure: Dict[str, Any]
    required_files: List[str]
    ignored_patterns: List[str]
    
    # Build configuration
    build_commands: List[str]
    test_commands: List[str]
    deploy_commands: List[str]
    
    # Conventions
    naming_conventions: Dict[str, str]
    code_style_config: Dict[str, Any]
    
    # Custom metadata
    custom_metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def generate_qr_hash(self) -> str:
        """Generate a unique hash for this manifest (like a QR code)"""
        manifest_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(manifest_str.encode()).hexdigest()[:16]


class BuildRulesService:
    """Service for managing build rules and manifests"""
    
    def __init__(self, storage_dir: str = "./data/build_manifests"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "manifests_index.json"
        self._ensure_index()
    
    def _ensure_index(self):
        """Ensure index file exists"""
        if not self.index_file.exists():
            self._save_index({})
    
    def _load_index(self) -> Dict:
        """Load manifest index"""
        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_index(self, index: Dict):
        """Save manifest index"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def _get_manifest_file(self, manifest_id: str) -> Path:
        """Get path to manifest file"""
        return self.storage_dir / f"{manifest_id}.json"
    
    def create_manifest(
        self,
        workspace_id: str,
        project_name: str,
        languages: List[str],
        frameworks: List[str] = None,
        **kwargs
    ) -> BuildManifest:
        """Create a new build manifest"""
        manifest_id = f"{workspace_id}_{datetime.utcnow().timestamp()}"
        now = datetime.utcnow().isoformat()
        
        manifest = BuildManifest(
            manifest_id=manifest_id,
            workspace_id=workspace_id,
            project_name=project_name,
            version="1.0.0",
            created_at=now,
            updated_at=now,
            languages=languages,
            frameworks=frameworks or [],
            dependencies=kwargs.get('dependencies', {}),
            rules=kwargs.get('rules', []),
            directory_structure=kwargs.get('directory_structure', {}),
            required_files=kwargs.get('required_files', []),
            ignored_patterns=kwargs.get('ignored_patterns', []),
            build_commands=kwargs.get('build_commands', []),
            test_commands=kwargs.get('test_commands', []),
            deploy_commands=kwargs.get('deploy_commands', []),
            naming_conventions=kwargs.get('naming_conventions', {}),
            code_style_config=kwargs.get('code_style_config', {}),
            custom_metadata=kwargs.get('custom_metadata', {})
        )
        
        # Save manifest
        manifest_file = self._get_manifest_file(manifest_id)
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Update index
        index = self._load_index()
        index[manifest_id] = {
            "workspace_id": workspace_id,
            "project_name": project_name,
            "qr_hash": manifest.generate_qr_hash(),
            "created_at": now,
            "version": manifest.version
        }
        self._save_index(index)
        
        return manifest
    
    def get_manifest(self, manifest_id: str) -> Optional[BuildManifest]:
        """Get a build manifest"""
        manifest_file = self._get_manifest_file(manifest_id)
        if not manifest_file.exists():
            return None
        
        with open(manifest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return BuildManifest(**data)
    
    def get_manifest_by_workspace(self, workspace_id: str) -> Optional[BuildManifest]:
        """Get the latest manifest for a workspace"""
        index = self._load_index()
        
        # Find all manifests for this workspace
        workspace_manifests = [
            (mid, data) for mid, data in index.items()
            if data.get('workspace_id') == workspace_id
        ]
        
        if not workspace_manifests:
            return None
        
        # Get the most recent one
        latest = max(workspace_manifests, key=lambda x: x[1]['created_at'])
        return self.get_manifest(latest[0])
    
    def update_manifest(
        self,
        manifest_id: str,
        **kwargs
    ) -> Optional[BuildManifest]:
        """Update an existing manifest"""
        manifest = self.get_manifest(manifest_id)
        if not manifest:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(manifest, key) and value is not None:
                setattr(manifest, key, value)
        
        manifest.updated_at = datetime.utcnow().isoformat()
        
        # Save updated manifest
        manifest_file = self._get_manifest_file(manifest_id)
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Update index
        index = self._load_index()
        if manifest_id in index:
            index[manifest_id]["qr_hash"] = manifest.generate_qr_hash()
        self._save_index(index)
        
        return manifest
    
    def add_rule(
        self,
        manifest_id: str,
        rule: BuildRule
    ) -> Optional[BuildManifest]:
        """Add a build rule to manifest"""
        manifest = self.get_manifest(manifest_id)
        if not manifest:
            return None
        
        manifest.rules.append(asdict(rule))
        return self.update_manifest(manifest_id, rules=manifest.rules)
    
    def validate_against_manifest(
        self,
        manifest_id: str,
        project_path: Path
    ) -> Dict[str, Any]:
        """Validate a project against its manifest"""
        manifest = self.get_manifest(manifest_id)
        if not manifest:
            return {"error": "Manifest not found"}
        
        violations = []
        warnings = []
        
        # Check required files
        for req_file in manifest.required_files:
            file_path = project_path / req_file
            if not file_path.exists():
                violations.append({
                    "type": "missing_required_file",
                    "file": req_file,
                    "severity": "error"
                })
        
        # Check directory structure
        for expected_dir in manifest.directory_structure.keys():
            dir_path = project_path / expected_dir
            if not dir_path.exists():
                warnings.append({
                    "type": "missing_directory",
                    "directory": expected_dir,
                    "severity": "warning"
                })
        
        return {
            "manifest_id": manifest_id,
            "qr_hash": manifest.generate_qr_hash(),
            "violations": violations,
            "warnings": warnings,
            "is_valid": len(violations) == 0,
            "checked_at": datetime.utcnow().isoformat()
        }
    
    def auto_detect_manifest(self, project_path: Path) -> Dict[str, Any]:
        """Auto-detect project structure and generate manifest suggestions"""
        suggestions = {
            "languages": [],
            "frameworks": [],
            "dependencies": {},
            "directory_structure": {},
            "required_files": [],
            "build_commands": [],
            "test_commands": []
        }
        
        # Detect languages
        file_extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".cpp": "C++",
            ".c": "C"
        }
        
        for ext, lang in file_extensions.items():
            if list(project_path.glob(f"**/*{ext}")):
                suggestions["languages"].append(lang)
        
        # Detect frameworks and dependencies
        if (project_path / "package.json").exists():
            suggestions["frameworks"].append("Node.js")
            suggestions["required_files"].append("package.json")
            suggestions["build_commands"].append("npm install")
            suggestions["build_commands"].append("npm run build")
            suggestions["test_commands"].append("npm test")
        
        if (project_path / "requirements.txt").exists():
            suggestions["frameworks"].append("Python")
            suggestions["required_files"].append("requirements.txt")
            suggestions["build_commands"].append("pip install -r requirements.txt")
            suggestions["test_commands"].append("pytest")
        
        if (project_path / "Cargo.toml").exists():
            suggestions["frameworks"].append("Rust/Cargo")
            suggestions["required_files"].append("Cargo.toml")
            suggestions["build_commands"].append("cargo build")
            suggestions["test_commands"].append("cargo test")
        
        # Detect directory structure
        common_dirs = ["src", "tests", "docs", "config", "scripts", "backend", "frontend"]
        for dir_name in common_dirs:
            if (project_path / dir_name).exists():
                suggestions["directory_structure"][dir_name] = "detected"
        
        return suggestions
    
    def generate_clarification_questions(self, project_path: Path) -> List[Dict[str, Any]]:
        """
        Analyze codebase and generate clarification questions for the user.
        Helps system understand project before building.
        """
        questions = []
        
        # Detect languages and frameworks
        detected_info = self.auto_detect_manifest(project_path)
        
        # Question 1: Confirm primary language/framework
        if detected_info["languages"]:
            questions.append({
                "id": "q1_primary_lang",
                "question": f"I detected: {', '.join(detected_info['languages'])}. Which is the primary language?",
                "type": "choice",
                "options": detected_info["languages"],
                "priority": "high"
            })
        
        # Question 2: Build process
        if not detected_info["build_commands"]:
            questions.append({
                "id": "q2_build_process",
                "question": "How do you build this project? What commands should I run?",
                "type": "text",
                "priority": "high",
                "hint": "e.g., 'npm run build' or 'make' or 'cargo build'"
            })
        
        # Question 3: Testing strategy
        if not detected_info["test_commands"]:
            questions.append({
                "id": "q3_testing",
                "question": "How do you test this project? What testing framework do you use?",
                "type": "text",
                "priority": "medium",
                "hint": "e.g., 'pytest', 'jest', 'cargo test'"
            })
        
        # Question 4: Entry point
        entry_files = list(project_path.glob("**/main.*")) + list(project_path.glob("**/index.*"))
        if not entry_files:
            questions.append({
                "id": "q4_entry_point",
                "question": "What is the entry point / main file for this project?",
                "type": "text",
                "priority": "high",
                "hint": "e.g., 'src/main.py' or 'index.js'"
            })
        
        # Question 5: Deployment target
        questions.append({
            "id": "q5_deployment",
            "question": "Where will this be deployed? (local, server, cloud, container, etc.)",
            "type": "choice",
            "options": ["Local development only", "Server/VM", "Docker container", "Kubernetes", "Serverless/Lambda", "Other"],
            "priority": "medium"
        })
        
        # Question 6: Dependencies management
        has_lock_file = any([
            (project_path / "package-lock.json").exists(),
            (project_path / "yarn.lock").exists(),
            (project_path / "Cargo.lock").exists(),
            (project_path / "poetry.lock").exists()
        ])
        if not has_lock_file and detected_info["dependencies"]:
            questions.append({
                "id": "q6_dependencies",
                "question": "I don't see a lock file. Should I create one to ensure reproducible builds?",
                "type": "yes_no",
                "priority": "low"
            })
        
        # Question 7: Code style preferences
        has_linter = any([
            (project_path / ".eslintrc").exists(),
            (project_path / ".eslintrc.json").exists(),
            (project_path / "pylintrc").exists(),
            (project_path / ".flake8").exists()
        ])
        if not has_linter:
            questions.append({
                "id": "q7_code_style",
                "question": "Do you have code style preferences? (e.g., tabs vs spaces, line length, naming conventions)",
                "type": "text",
                "priority": "low",
                "hint": "Leave blank to use language defaults"
            })
        
        # Question 8: Git workflow
        if (project_path / ".git").exists():
            questions.append({
                "id": "q8_git_workflow",
                "question": "What is your git workflow? (e.g., main branch, feature branches, pull requests)",
                "type": "text",
                "priority": "low",
                "hint": "This helps me understand branching strategy"
            })
        
        return questions


# Singleton instance
_build_rules_service = None

def get_build_rules_service() -> BuildRulesService:
    """Get singleton build rules service instance"""
    global _build_rules_service
    if _build_rules_service is None:
        import os
        storage_dir = os.getenv("BUILD_MANIFESTS_DIR", "./data/build_manifests")
        _build_rules_service = BuildRulesService(storage_dir)
    return _build_rules_service
