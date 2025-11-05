"""
Rules Management API
Endpoints for creating, updating, and managing user-defined rules.
"""

from fastapi import APIRouter, HTTPException, Body, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from backend.services.universal_rules_engine import (
    get_rules_engine,
    Rule,
    RuleType,
    RuleScope,
    RuleEnforcement
)

router = APIRouter(prefix="/rules", tags=["Rules Management"])


class RuleCreate(BaseModel):
    """Request model for creating a rule"""
    name: str = Field(..., description="Human-readable rule name")
    description: str = Field(..., description="What the rule does")
    rule_text: str = Field(..., description="The actual rule content")
    rule_type: str = Field(..., description="Type of rule (code_style, architecture, etc.)")
    scope: str = Field(default="global", description="Where rule applies (global, project, file)")
    enforcement: str = Field(default="strict", description="How strictly enforced (mandatory, strict, guidance)")
    applies_to: List[str] = Field(default_factory=list, description="Project IDs or file patterns")
    priority: int = Field(default=100, description="Priority (lower = higher)")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class RuleUpdate(BaseModel):
    """Request model for updating a rule"""
    name: Optional[str] = None
    description: Optional[str] = None
    rule_text: Optional[str] = None
    rule_type: Optional[str] = None
    scope: Optional[str] = None
    enforcement: Optional[str] = None
    applies_to: Optional[List[str]] = None
    active: Optional[bool] = None
    priority: Optional[int] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class RuleResponse(BaseModel):
    """Response model for a rule"""
    id: str
    name: str
    description: str
    rule_text: str
    rule_type: str
    scope: str
    enforcement: str
    applies_to: List[str]
    created_by: str
    created_at: str
    modified_at: str
    active: bool
    priority: int
    tags: List[str]
    metadata: Dict[str, Any]


@router.post("/", response_model=RuleResponse)
async def create_rule(
    rule_data: RuleCreate,
    project_id: Optional[str] = Query(None, description="Project ID if this is a project rule"),
    created_by: Optional[str] = Query(None, description="User creating the rule")
):
    """
    Create a new rule.
    
    All AI models (Claude, GPT-4, Gemini, Copilot, etc.) will automatically
    respect this rule in their responses.
    """
    try:
        rules_engine = get_rules_engine()
        
        # Create rule object
        rule = Rule(
            id="",  # Will be auto-generated
            name=rule_data.name,
            description=rule_data.description,
            rule_text=rule_data.rule_text,
            rule_type=RuleType(rule_data.rule_type),
            scope=RuleScope(rule_data.scope),
            enforcement=RuleEnforcement(rule_data.enforcement),
            applies_to=rule_data.applies_to,
            created_by=created_by or "unknown",
            priority=rule_data.priority,
            tags=rule_data.tags,
            metadata=rule_data.metadata
        )
        
        # Add to engine
        rule_id = rules_engine.add_rule(rule, project_id=project_id)
        
        # Return created rule
        created_rule = rules_engine.rules[rule_id]
        return RuleResponse(**created_rule.to_dict())
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating rule: {str(e)}")


@router.get("/", response_model=List[RuleResponse])
async def list_rules(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    file_path: Optional[str] = Query(None, description="Filter by file path"),
    rule_type: Optional[str] = Query(None, description="Filter by rule type"),
    enforcement: Optional[str] = Query(None, description="Filter by enforcement level"),
    active_only: bool = Query(True, description="Only return active rules"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by")
):
    """
    List all rules, optionally filtered by various criteria.
    """
    try:
        rules_engine = get_rules_engine()
        
        # Get applicable rules
        rule_types = [RuleType(rule_type)] if rule_type else None
        enforcement_levels = [RuleEnforcement(enforcement)] if enforcement else None
        
        rules = rules_engine.get_applicable_rules(
            project_id=project_id,
            file_path=file_path,
            rule_types=rule_types,
            enforcement_levels=enforcement_levels
        )
        
        # Filter by active status
        if active_only:
            rules = [r for r in rules if r.active]
        
        # Filter by tags
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            rules = [r for r in rules if any(tag in r.tags for tag in tag_list)]
        
        return [RuleResponse(**r.to_dict()) for r in rules]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing rules: {str(e)}")


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(rule_id: str):
    """Get a specific rule by ID."""
    try:
        rules_engine = get_rules_engine()
        
        if rule_id not in rules_engine.rules:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        rule = rules_engine.rules[rule_id]
        return RuleResponse(**rule.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting rule: {str(e)}")


@router.patch("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: str,
    rule_update: RuleUpdate,
    project_id: Optional[str] = Query(None, description="Project ID if updating project rule")
):
    """Update a rule."""
    try:
        rules_engine = get_rules_engine()
        
        if rule_id not in rules_engine.rules:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        rule = rules_engine.rules[rule_id]
        
        # Update fields
        if rule_update.name is not None:
            rule.name = rule_update.name
        if rule_update.description is not None:
            rule.description = rule_update.description
        if rule_update.rule_text is not None:
            rule.rule_text = rule_update.rule_text
        if rule_update.rule_type is not None:
            rule.rule_type = RuleType(rule_update.rule_type)
        if rule_update.scope is not None:
            rule.scope = RuleScope(rule_update.scope)
        if rule_update.enforcement is not None:
            rule.enforcement = RuleEnforcement(rule_update.enforcement)
        if rule_update.applies_to is not None:
            rule.applies_to = rule_update.applies_to
        if rule_update.active is not None:
            rule.active = rule_update.active
        if rule_update.priority is not None:
            rule.priority = rule_update.priority
        if rule_update.tags is not None:
            rule.tags = rule_update.tags
        if rule_update.metadata is not None:
            rule.metadata = rule_update.metadata
        
        rule.modified_at = datetime.now()
        
        # Save changes
        rules_engine.save_rules(project_id=project_id)
        
        return RuleResponse(**rule.to_dict())
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating rule: {str(e)}")


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: str,
    project_id: Optional[str] = Query(None, description="Project ID if deleting project rule")
):
    """Delete a rule."""
    try:
        rules_engine = get_rules_engine()
        
        if rule_id not in rules_engine.rules:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        rules_engine.remove_rule(rule_id, project_id=project_id)
        
        return {"message": "Rule deleted successfully", "rule_id": rule_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting rule: {str(e)}")


@router.post("/{rule_id}/activate")
async def activate_rule(
    rule_id: str,
    project_id: Optional[str] = Query(None)
):
    """Activate a rule."""
    try:
        rules_engine = get_rules_engine()
        
        if rule_id not in rules_engine.rules:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        rule = rules_engine.rules[rule_id]
        rule.active = True
        rule.modified_at = datetime.now()
        
        rules_engine.save_rules(project_id=project_id)
        
        return {"message": "Rule activated", "rule_id": rule_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error activating rule: {str(e)}")


@router.post("/{rule_id}/deactivate")
async def deactivate_rule(
    rule_id: str,
    project_id: Optional[str] = Query(None)
):
    """Deactivate a rule without deleting it."""
    try:
        rules_engine = get_rules_engine()
        
        if rule_id not in rules_engine.rules:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        rule = rules_engine.rules[rule_id]
        rule.active = False
        rule.modified_at = datetime.now()
        
        rules_engine.save_rules(project_id=project_id)
        
        return {"message": "Rule deactivated", "rule_id": rule_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating rule: {str(e)}")


@router.get("/preview/prompt")
async def preview_rules_prompt(
    project_id: Optional[str] = Query(None),
    file_path: Optional[str] = Query(None)
):
    """
    Preview what rules prompt will be injected for given context.
    Useful for testing rules before they're used.
    """
    try:
        rules_engine = get_rules_engine()
        
        prompt = rules_engine.generate_rules_prompt(
            project_id=project_id,
            file_path=file_path
        )
        
        return {
            "prompt": prompt,
            "context": {
                "project_id": project_id,
                "file_path": file_path
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating preview: {str(e)}")


@router.get("/types")
async def get_rule_types():
    """Get all available rule types."""
    return {
        "rule_types": [rt.value for rt in RuleType],
        "descriptions": {
            "code_style": "Formatting, naming conventions, code organization",
            "architecture": "Design patterns, structure, modularity",
            "security": "Security requirements, authentication, data protection",
            "performance": "Performance constraints, optimization requirements",
            "testing": "Testing requirements, coverage, test structure",
            "documentation": "Documentation standards, comments, README",
            "build": "Build process rules, dependencies, compilation",
            "deployment": "Deployment rules, environments, CI/CD",
            "custom": "User-defined custom rules"
        }
    }


@router.get("/scopes")
async def get_rule_scopes():
    """Get all available rule scopes."""
    return {
        "scopes": [rs.value for rs in RuleScope],
        "descriptions": {
            "global": "Applies to all projects and files",
            "project": "Applies to specific project(s)",
            "file": "Applies to specific file(s) or patterns",
            "build": "Applies to specific build type"
        }
    }


@router.get("/enforcement-levels")
async def get_enforcement_levels():
    """Get all available enforcement levels."""
    return {
        "enforcement_levels": [re.value for re in RuleEnforcement],
        "descriptions": {
            "mandatory": "MUST be followed - violations will block responses",
            "strict": "MUST be followed - violations will be flagged",
            "guidance": "SHOULD be followed - logged only",
            "suggestion": "Nice to follow - informational"
        }
    }
