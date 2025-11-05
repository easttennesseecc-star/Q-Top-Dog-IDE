"""
Universal Rules Engine - Enforce User Rules Across ALL AI Models
This system ensures that user-defined rules are respected by ALL AI models:
Claude, GPT-4, Gemini, Copilot, Cursor, and any future models.

Rules are injected into system prompts and enforced at the API layer.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import hashlib
from enum import Enum


class RuleScope(Enum):
    """Where the rule applies"""
    GLOBAL = "global"  # Applies to all projects
    PROJECT = "project"  # Applies to specific project
    FILE = "file"  # Applies to specific file/folder
    BUILD = "build"  # Applies to specific build type


class RuleEnforcement(Enum):
    """How strictly the rule is enforced"""
    MANDATORY = "mandatory"  # Must be followed, blocks non-compliant responses
    STRICT = "strict"  # Must be followed, warns on violations
    GUIDANCE = "guidance"  # Should be followed, logged only
    SUGGESTION = "suggestion"  # Nice to follow, informational


class RuleType(Enum):
    """Type of rule"""
    CODE_STYLE = "code_style"  # Formatting, naming conventions
    ARCHITECTURE = "architecture"  # Design patterns, structure
    SECURITY = "security"  # Security requirements
    PERFORMANCE = "performance"  # Performance constraints
    TESTING = "testing"  # Testing requirements
    DOCUMENTATION = "documentation"  # Documentation standards
    BUILD = "build"  # Build process rules
    DEPLOYMENT = "deployment"  # Deployment rules
    CUSTOM = "custom"  # User-defined custom rules


@dataclass
class Rule:
    """A single enforceable rule"""
    id: str  # Unique identifier (hash of content)
    name: str  # Human-readable name
    description: str  # What the rule does
    rule_text: str  # The actual rule content
    rule_type: RuleType
    scope: RuleScope
    enforcement: RuleEnforcement
    applies_to: List[str] = field(default_factory=list)  # Project IDs, file patterns, etc.
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    active: bool = True
    priority: int = 100  # Lower = higher priority
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate ID if not provided"""
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID from rule content"""
        content = f"{self.name}:{self.rule_text}:{self.created_at.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rule_text": self.rule_text,
            "rule_type": self.rule_type.value,
            "scope": self.scope.value,
            "enforcement": self.enforcement.value,
            "applies_to": self.applies_to,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "active": self.active,
            "priority": self.priority,
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rule':
        """Create from dictionary"""
        return cls(
            id=data.get("id", ""),
            name=data["name"],
            description=data["description"],
            rule_text=data["rule_text"],
            rule_type=RuleType(data["rule_type"]),
            scope=RuleScope(data["scope"]),
            enforcement=RuleEnforcement(data["enforcement"]),
            applies_to=data.get("applies_to", []),
            created_by=data.get("created_by", ""),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            modified_at=datetime.fromisoformat(data.get("modified_at", datetime.now().isoformat())),
            active=data.get("active", True),
            priority=data.get("priority", 100),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class RuleViolation:
    """A detected rule violation"""
    rule_id: str
    rule_name: str
    violation_text: str
    severity: RuleEnforcement
    detected_at: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


class UniversalRulesEngine:
    """
    Universal Rules Engine that enforces rules across ALL AI models.
    
    This engine:
    1. Stores and manages rules
    2. Injects rules into model prompts
    3. Validates model responses against rules
    4. Provides rule context to all models
    """
    
    def __init__(self, rules_dir: Optional[Path] = None):
        """
        Initialize the rules engine.
        
        Args:
            rules_dir: Directory to store rules. Defaults to ~/.q-ide/rules
        """
        if rules_dir is None:
            rules_dir = Path.home() / ".q-ide" / "rules"
        
        self.rules_dir = Path(rules_dir)
        self.rules_dir.mkdir(parents=True, exist_ok=True)
        
        self.rules: Dict[str, Rule] = {}
        self.project_rules: Dict[str, List[str]] = {}  # project_id -> rule_ids
        self.load_all_rules()
    
    def load_all_rules(self) -> None:
        """Load all rules from disk"""
        # Load global rules
        global_rules_file = self.rules_dir / "global_rules.json"
        if global_rules_file.exists():
            with open(global_rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for rule_data in data.get("rules", []):
                    rule = Rule.from_dict(rule_data)
                    self.rules[rule.id] = rule
        
        # Load project-specific rules
        for project_file in self.rules_dir.glob("project_*.json"):
            with open(project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                project_id = data.get("project_id")
                for rule_data in data.get("rules", []):
                    rule = Rule.from_dict(rule_data)
                    self.rules[rule.id] = rule
                    if project_id:
                        if project_id not in self.project_rules:
                            self.project_rules[project_id] = []
                        self.project_rules[project_id].append(rule.id)
    
    def save_rules(self, project_id: Optional[str] = None) -> None:
        """Save rules to disk"""
        if project_id:
            # Save project-specific rules
            project_file = self.rules_dir / f"project_{project_id}.json"
            project_rule_ids = self.project_rules.get(project_id, [])
            project_rules = [self.rules[rid].to_dict() for rid in project_rule_ids if rid in self.rules]
            
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "project_id": project_id,
                    "rules": project_rules
                }, f, indent=2)
        else:
            # Save global rules
            global_rules_file = self.rules_dir / "global_rules.json"
            global_rules = [r.to_dict() for r in self.rules.values() if r.scope == RuleScope.GLOBAL]
            
            with open(global_rules_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "rules": global_rules
                }, f, indent=2)
    
    def add_rule(self, rule: Rule, project_id: Optional[str] = None) -> str:
        """
        Add a new rule.
        
        Args:
            rule: The rule to add
            project_id: Optional project ID if this is a project-specific rule
            
        Returns:
            The rule ID
        """
        self.rules[rule.id] = rule
        
        if project_id and rule.scope == RuleScope.PROJECT:
            if project_id not in self.project_rules:
                self.project_rules[project_id] = []
            self.project_rules[project_id].append(rule.id)
        
        self.save_rules(project_id)
        return rule.id
    
    def remove_rule(self, rule_id: str, project_id: Optional[str] = None) -> bool:
        """Remove a rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            
            if project_id and project_id in self.project_rules:
                if rule_id in self.project_rules[project_id]:
                    self.project_rules[project_id].remove(rule_id)
            
            self.save_rules(project_id)
            return True
        return False
    
    def get_applicable_rules(
        self,
        project_id: Optional[str] = None,
        file_path: Optional[str] = None,
        rule_types: Optional[List[RuleType]] = None,
        enforcement_levels: Optional[List[RuleEnforcement]] = None
    ) -> List[Rule]:
        """
        Get all rules applicable to the current context.
        
        Args:
            project_id: Current project ID
            file_path: Current file path
            rule_types: Filter by rule types
            enforcement_levels: Filter by enforcement levels
            
        Returns:
            List of applicable rules, sorted by priority
        """
        applicable_rules: List[Rule] = []
        
        for rule in self.rules.values():
            if not rule.active:
                continue
            
            # Check scope
            if rule.scope == RuleScope.GLOBAL:
                applicable_rules.append(rule)
            elif rule.scope == RuleScope.PROJECT and project_id:
                if not rule.applies_to or project_id in rule.applies_to:
                    applicable_rules.append(rule)
            elif rule.scope == RuleScope.FILE and file_path:
                # Check if file matches any patterns in applies_to
                for pattern in rule.applies_to:
                    if Path(file_path).match(pattern):
                        applicable_rules.append(rule)
                        break
        
        # Filter by rule type
        if rule_types:
            applicable_rules = [r for r in applicable_rules if r.rule_type in rule_types]
        
        # Filter by enforcement level
        if enforcement_levels:
            applicable_rules = [r for r in applicable_rules if r.enforcement in enforcement_levels]
        
        # Sort by priority (lower number = higher priority)
        applicable_rules.sort(key=lambda r: r.priority)
        
        return applicable_rules
    
    def generate_rules_prompt(
        self,
        project_id: Optional[str] = None,
        file_path: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """
        Generate a prompt section with all applicable rules.
        This will be injected into the system prompt for ALL models.
        
        Args:
            project_id: Current project ID
            file_path: Current file being worked on
            context: Additional context (e.g., "code_generation", "refactoring")
            
        Returns:
            Formatted rules text to inject into prompts
        """
        rules = self.get_applicable_rules(project_id=project_id, file_path=file_path)
        
        if not rules:
            return ""
        
        prompt_parts = [
            "# MANDATORY RULES - YOU MUST FOLLOW THESE RULES",
            "The following rules MUST be followed in all responses and code generation:",
            ""
        ]
        
        # Group rules by enforcement level
        mandatory_rules = [r for r in rules if r.enforcement == RuleEnforcement.MANDATORY]
        strict_rules = [r for r in rules if r.enforcement == RuleEnforcement.STRICT]
        guidance_rules = [r for r in rules if r.enforcement == RuleEnforcement.GUIDANCE]
        
        if mandatory_rules:
            prompt_parts.append("## MANDATORY RULES (MUST FOLLOW - VIOLATIONS WILL BE BLOCKED)")
            for i, rule in enumerate(mandatory_rules, 1):
                prompt_parts.append(f"{i}. **{rule.name}** [{rule.rule_type.value}]")
                prompt_parts.append(f"   {rule.description}")
                prompt_parts.append(f"   Rule: {rule.rule_text}")
                prompt_parts.append("")
        
        if strict_rules:
            prompt_parts.append("## STRICT RULES (MUST FOLLOW - VIOLATIONS WILL BE FLAGGED)")
            for i, rule in enumerate(strict_rules, 1):
                prompt_parts.append(f"{i}. **{rule.name}** [{rule.rule_type.value}]")
                prompt_parts.append(f"   {rule.description}")
                prompt_parts.append(f"   Rule: {rule.rule_text}")
                prompt_parts.append("")
        
        if guidance_rules:
            prompt_parts.append("## GUIDANCE RULES (SHOULD FOLLOW - BEST PRACTICES)")
            for i, rule in enumerate(guidance_rules, 1):
                prompt_parts.append(f"{i}. **{rule.name}** [{rule.rule_type.value}]")
                prompt_parts.append(f"   {rule.description}")
                prompt_parts.append(f"   Rule: {rule.rule_text}")
                prompt_parts.append("")
        
        prompt_parts.append("---")
        prompt_parts.append("YOU MUST ACKNOWLEDGE AND FOLLOW THESE RULES IN YOUR RESPONSE.")
        prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    def validate_response(
        self,
        response_text: str,
        code_generated: Optional[str] = None,
        project_id: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> tuple[bool, List[RuleViolation]]:
        """
        Validate a model's response against applicable rules.
        
        Args:
            response_text: The model's response text
            code_generated: Any code that was generated
            project_id: Current project ID
            file_path: Current file path
            
        Returns:
            (is_valid, violations) - True if valid, False if violations found
        """
        rules = self.get_applicable_rules(project_id=project_id, file_path=file_path)
        violations: List[RuleViolation] = []
        
        # Check mandatory and strict rules
        for rule in rules:
            if rule.enforcement not in [RuleEnforcement.MANDATORY, RuleEnforcement.STRICT]:
                continue
            
            # Basic validation - can be enhanced with more sophisticated checks
            violation = self._check_rule_violation(rule, response_text, code_generated)
            if violation:
                violations.append(violation)
        
        # Response is invalid if there are mandatory violations
        mandatory_violations = [v for v in violations if v.severity == RuleEnforcement.MANDATORY]
        is_valid = len(mandatory_violations) == 0
        
        return is_valid, violations
    
    def _check_rule_violation(
        self,
        rule: Rule,
        response_text: str,
        code_generated: Optional[str] = None
    ) -> Optional[RuleViolation]:
        """
        Check if a specific rule is violated.
        This is a basic implementation - can be enhanced with:
        - AST parsing for code rules
        - Regex matching for patterns
        - LLM-based validation
        - Custom validators per rule type
        """
        # This is a placeholder - real implementation would use
        # sophisticated validation based on rule type
        
        # For now, just check for keywords in rule text
        # Real implementation should be much more sophisticated
        
        return None  # No violation detected in basic check


# Global instance
_rules_engine: Optional[UniversalRulesEngine] = None


def get_rules_engine() -> UniversalRulesEngine:
    """Get the global rules engine instance"""
    global _rules_engine
    if _rules_engine is None:
        _rules_engine = UniversalRulesEngine()
    return _rules_engine
