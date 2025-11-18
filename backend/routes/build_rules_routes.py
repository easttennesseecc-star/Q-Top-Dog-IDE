"""
Build Rules & Manifest API Routes
REST endpoints for managing build rules and project manifests (QR code concept)
"""

from fastapi import APIRouter, HTTPException, Path as PathParam
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from pathlib import Path
from backend.services.build_rules_service import (
    get_build_rules_service,
    BuildRule,
    RuleCategory
)

router = APIRouter(prefix="/api/v1/build-rules", tags=["build-rules"])


class CreateManifestRequest(BaseModel):
    workspace_id: str
    project_name: str
    languages: List[str]
    frameworks: Optional[List[str]] = []
    dependencies: Optional[Dict[str, str]] = {}
    required_files: Optional[List[str]] = []
    ignored_patterns: Optional[List[str]] = []
    build_commands: Optional[List[str]] = []
    test_commands: Optional[List[str]] = []
    deploy_commands: Optional[List[str]] = []
    naming_conventions: Optional[Dict[str, str]] = {}
    code_style_config: Optional[Dict[str, Any]] = {}
    directory_structure: Optional[Dict[str, Any]] = {}
    custom_metadata: Optional[Dict[str, Any]] = {}


class AddRuleRequest(BaseModel):
    category: RuleCategory
    name: str
    description: str
    enforcement: str = Field(..., pattern="^(required|recommended|optional)$")
    examples: List[str] = []
    violations_action: str = Field(..., pattern="^(block|warn|log)$")


class ManifestResponse(BaseModel):
    manifest_id: str
    workspace_id: str
    project_name: str
    version: str
    qr_hash: str
    languages: List[str]
    frameworks: List[str]
    created_at: str
    updated_at: str


@router.post("/manifests", response_model=ManifestResponse, status_code=201)
async def create_manifest(request: CreateManifestRequest):
    """Create a new build manifest for a workspace"""
    service = get_build_rules_service()
    manifest = service.create_manifest(
        workspace_id=request.workspace_id,
        project_name=request.project_name,
        languages=request.languages,
        frameworks=request.frameworks,
        dependencies=request.dependencies,
        required_files=request.required_files,
        ignored_patterns=request.ignored_patterns,
        build_commands=request.build_commands,
        test_commands=request.test_commands,
        deploy_commands=request.deploy_commands,
        naming_conventions=request.naming_conventions,
        code_style_config=request.code_style_config,
        directory_structure=request.directory_structure,
        custom_metadata=request.custom_metadata
    )
    return {
        **manifest.to_dict(),
        "qr_hash": manifest.generate_qr_hash()
    }


@router.get("/manifests/{manifest_id}")
async def get_manifest(manifest_id: str = PathParam(..., description="Manifest ID")):
    """Get a specific build manifest"""
    service = get_build_rules_service()
    manifest = service.get_manifest(manifest_id)
    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return {
        **manifest.to_dict(),
        "qr_hash": manifest.generate_qr_hash()
    }


@router.get("/manifests/workspace/{workspace_id}")
async def get_workspace_manifest(workspace_id: str):
    """Get the latest manifest for a workspace"""
    service = get_build_rules_service()
    manifest = service.get_manifest_by_workspace(workspace_id)
    if not manifest:
        raise HTTPException(status_code=404, detail="No manifest found for this workspace")
    return {
        **manifest.to_dict(),
        "qr_hash": manifest.generate_qr_hash()
    }


@router.put("/manifests/{manifest_id}")
async def update_manifest(
    manifest_id: str,
    updates: Dict[str, Any]
):
    """Update an existing manifest"""
    service = get_build_rules_service()
    manifest = service.update_manifest(manifest_id, **updates)
    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return {
        **manifest.to_dict(),
        "qr_hash": manifest.generate_qr_hash()
    }


@router.post("/manifests/{manifest_id}/rules", status_code=201)
async def add_rule(
    manifest_id: str,
    rule_request: AddRuleRequest
):
    """Add a build rule to manifest"""
    service = get_build_rules_service()
    rule = BuildRule(
        category=rule_request.category,
        name=rule_request.name,
        description=rule_request.description,
        enforcement=rule_request.enforcement,
        examples=rule_request.examples,
        violations_action=rule_request.violations_action
    )
    manifest = service.add_rule(manifest_id, rule)
    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return {"message": "Rule added successfully", "rule": rule}


@router.post("/manifests/{manifest_id}/validate")
async def validate_manifest(
    manifest_id: str,
    project_path: str
):
    """Validate a project against its manifest"""
    service = get_build_rules_service()
    validation = service.validate_against_manifest(manifest_id, Path(project_path))
    return validation


@router.post("/auto-detect")
async def auto_detect_manifest(project_path: str):
    """Auto-detect project structure and generate manifest suggestions"""
    service = get_build_rules_service()
    suggestions = service.auto_detect_manifest(Path(project_path))
    return suggestions


@router.get("/manifests/{manifest_id}/qr-hash")
async def get_qr_hash(manifest_id: str):
    """Get the QR hash for a manifest (unique identifier)"""
    service = get_build_rules_service()
    manifest = service.get_manifest(manifest_id)
    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return {
        "manifest_id": manifest_id,
        "qr_hash": manifest.generate_qr_hash(),
        "project_name": manifest.project_name,
        "version": manifest.version
    }


@router.post("/clarification-questions")
async def generate_clarification_questions(project_path: str):
    """Generate clarification questions about the project"""
    service = get_build_rules_service()
    questions = service.generate_clarification_questions(Path(project_path))
    return {
        "count": len(questions),
        "questions": questions
    }
