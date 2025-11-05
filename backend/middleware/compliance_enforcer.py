"""
Compliance Enforcement Middleware for Medical/Scientific Workspaces
CRITICAL: Enforces HIPAA, SOC2, FEDRAMP, and other regulatory requirements
"""

from fastapi import Request, HTTPException, status
from typing import Optional, List, Dict, Any
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class WorkspaceProfile(str, Enum):
    """Workspace security profiles"""
    DEFAULT = "default"
    MEDICAL = "medical"      # Requires HIPAA, SOC2, audit logging
    SCIENTIFIC = "scientific"  # Requires SOC2, FEDRAMP, data residency


class ComplianceRequirement(str, Enum):
    """Compliance certifications"""
    HIPAA = "hipaa"            # Healthcare data protection
    SOC2 = "soc2"              # Security & availability
    FEDRAMP = "fedramp"        # Federal government requirements
    GDPR = "gdpr"              # EU data protection
    DATA_RESIDENCY = "data_residency"  # Geographic data restrictions
    AUDIT_LOGGING = "audit_logging"    # Mandatory audit trails
    ENCRYPTION_AT_REST = "encryption_at_rest"
    ENCRYPTION_IN_TRANSIT = "encryption_in_transit"
    MFA_REQUIRED = "mfa_required"
    SSO_REQUIRED = "sso_required"


# Compliance requirements by workspace profile
PROFILE_REQUIREMENTS: Dict[WorkspaceProfile, List[ComplianceRequirement]] = {
    WorkspaceProfile.DEFAULT: [],
    
    WorkspaceProfile.MEDICAL: [
        ComplianceRequirement.HIPAA,
        ComplianceRequirement.SOC2,
        ComplianceRequirement.AUDIT_LOGGING,
        ComplianceRequirement.ENCRYPTION_AT_REST,
        ComplianceRequirement.ENCRYPTION_IN_TRANSIT,
        ComplianceRequirement.MFA_REQUIRED,
        ComplianceRequirement.DATA_RESIDENCY,
    ],
    
    WorkspaceProfile.SCIENTIFIC: [
        ComplianceRequirement.SOC2,
        ComplianceRequirement.FEDRAMP,
        ComplianceRequirement.AUDIT_LOGGING,
        ComplianceRequirement.ENCRYPTION_AT_REST,
        ComplianceRequirement.ENCRYPTION_IN_TRANSIT,
        ComplianceRequirement.DATA_RESIDENCY,
    ],
}


# Tier requirements for compliance features
COMPLIANCE_TIER_REQUIREMENTS: Dict[ComplianceRequirement, str] = {
    ComplianceRequirement.HIPAA: "enterprise_standard",
    ComplianceRequirement.SOC2: "enterprise_standard",
    ComplianceRequirement.FEDRAMP: "enterprise_premium",
    ComplianceRequirement.GDPR: "pro_team",
    ComplianceRequirement.DATA_RESIDENCY: "enterprise_standard",
    ComplianceRequirement.AUDIT_LOGGING: "pro_team",
    ComplianceRequirement.ENCRYPTION_AT_REST: "pro",
    ComplianceRequirement.ENCRYPTION_IN_TRANSIT: "pro",
    ComplianceRequirement.MFA_REQUIRED: "pro_team",
    ComplianceRequirement.SSO_REQUIRED: "enterprise_standard",
}


# Blocked operations for regulated workspaces
REGULATED_BLOCKED_OPERATIONS = [
    "/api/v1/export/unencrypted",
    "/api/v1/share/public",
    "/api/v1/data/download-raw",
]


class ComplianceEnforcer:
    """
    Enforces compliance requirements for regulated workspaces.
    CRITICAL: Medical/Scientific workspaces MUST have proper tier + certifications.
    """
    
    @staticmethod
    def get_workspace_profile(request: Request) -> WorkspaceProfile:
        """
        Extract workspace profile from request headers or session.
        Medical/Scientific workspaces are explicitly marked.
        """
        # Check header first (set by frontend)
        profile_header = request.headers.get("X-Workspace-Profile", "").lower()
        if profile_header in ["medical", "scientific"]:
            return WorkspaceProfile(profile_header)
        
        # Check query params (backup)
        profile_query = request.query_params.get("workspace_profile", "").lower()
        if profile_query in ["medical", "scientific"]:
            return WorkspaceProfile(profile_query)
        
        # Check session/cookie (if auth implemented)
        # TODO: Check user's workspace settings in database
        
        return WorkspaceProfile.DEFAULT
    
    @staticmethod
    def get_user_tier(request: Request) -> Optional[str]:
        """
        Get user's subscription tier from auth/session.
        TODO: Integrate with your actual auth system.
        """
        # Check header (for testing)
        tier_header = request.headers.get("X-User-Tier", "").lower()
        if tier_header:
            return tier_header
        
        # TODO: Get from authenticated user session
        # user = get_current_user(request)
        # return user.subscription_tier
        
        return None
    
    @staticmethod
    def check_tier_compliance(
        user_tier: str,
        required_compliance: List[ComplianceRequirement]
    ) -> tuple[bool, List[str]]:
        """
        Check if user's tier meets compliance requirements.
        Returns (is_compliant, list_of_missing_features)
        """
        # Tier hierarchy (lowest to highest)
        tier_rank = {
            "free": 0,
            "pro": 1,
            "pro_plus": 2,
            "pro_team": 3,
            "teams_small": 4,
            "teams_medium": 5,
            "teams_large": 6,
            "enterprise_standard": 7,
            "enterprise_premium": 8,
            "enterprise_unlimited": 9,
        }
        
        user_rank = tier_rank.get(user_tier, -1)
        missing = []
        
        for compliance in required_compliance:
            required_tier = COMPLIANCE_TIER_REQUIREMENTS.get(compliance)
            if not required_tier:
                continue
            
            required_rank = tier_rank.get(required_tier, 999)
            if user_rank < required_rank:
                missing.append(f"{compliance.value} (requires {required_tier})")
        
        return (len(missing) == 0, missing)
    
    @staticmethod
    async def enforce_compliance(request: Request) -> None:
        """
        Main enforcement function. Checks:
        1. Workspace profile (medical/scientific)
        2. Required compliance for that profile
        3. User's tier meets requirements
        4. Operation is allowed
        
        Raises HTTPException if non-compliant.
        """
        profile = ComplianceEnforcer.get_workspace_profile(request)
        
        # Default workspace: no special requirements
        if profile == WorkspaceProfile.DEFAULT:
            return
        
        # Medical/Scientific: STRICT enforcement
        required_compliance = PROFILE_REQUIREMENTS.get(profile, [])
        if not required_compliance:
            return
        
        # Get user tier
        user_tier = ComplianceEnforcer.get_user_tier(request)
        if not user_tier:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{profile.value.upper()} workspace requires authentication. "
                       f"Please log in to access regulated workspaces."
            )
        
        # Check tier compliance
        is_compliant, missing = ComplianceEnforcer.check_tier_compliance(
            user_tier, required_compliance
        )
        
        if not is_compliant:
            compliance_names = [c.value for c in required_compliance]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"COMPLIANCE VIOLATION: {profile.value.upper()} workspace requires "
                    f"{', '.join(compliance_names)}. "
                    f"Your tier ({user_tier}) is missing: {', '.join(missing)}. "
                    f"Upgrade to ENTERPRISE tier to access regulated workspaces."
                ),
                headers={
                    "X-Compliance-Required": ",".join(compliance_names),
                    "X-Missing-Features": ",".join(missing),
                    "X-Upgrade-Required": "enterprise_standard"
                }
            )
        
        # Check if operation is blocked for regulated workspaces
        path = request.url.path
        if any(blocked in path for blocked in REGULATED_BLOCKED_OPERATIONS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"SECURITY: Operation '{path}' is not allowed in "
                    f"{profile.value.upper()} workspaces. Use encrypted/audited "
                    f"alternatives only."
                )
            )
        
        # Log compliance check (REQUIRED for audit trail)
        logger.info(
            f"COMPLIANCE CHECK PASSED: profile={profile.value}, "
            f"tier={user_tier}, path={path}, "
            f"required={[c.value for c in required_compliance]}"
        )
    
    @staticmethod
    def get_compliance_status(
        profile: WorkspaceProfile,
        user_tier: Optional[str]
    ) -> Dict[str, Any]:
        """
        Get detailed compliance status for a workspace + user tier combo.
        Used by frontend to show upgrade prompts.
        """
        required = PROFILE_REQUIREMENTS.get(profile, [])
        
        if not user_tier:
            return {
                "profile": profile.value,
                "required_compliance": [c.value for c in required],
                "is_compliant": False,
                "missing": "Authentication required",
                "required_tier": "enterprise_standard"
            }
        
        is_compliant, missing = ComplianceEnforcer.check_tier_compliance(
            user_tier, required
        )
        
        return {
            "profile": profile.value,
            "user_tier": user_tier,
            "required_compliance": [c.value for c in required],
            "is_compliant": is_compliant,
            "missing": missing,
            "required_tier": "enterprise_standard" if not is_compliant else user_tier
        }


# FastAPI dependency for route protection
async def require_compliance(request: Request):
    """
    FastAPI dependency to enforce compliance on routes.
    
    Usage:
        @router.get("/medical/data", dependencies=[Depends(require_compliance)])
        async def get_medical_data():
            ...
    """
    await ComplianceEnforcer.enforce_compliance(request)


# Helper for manual checks
def is_compliant_for_medical(user_tier: str) -> bool:
    """Quick check if tier is compliant for medical workspaces"""
    required = PROFILE_REQUIREMENTS[WorkspaceProfile.MEDICAL]
    is_compliant, _ = ComplianceEnforcer.check_tier_compliance(user_tier, required)
    return is_compliant


def is_compliant_for_scientific(user_tier: str) -> bool:
    """Quick check if tier is compliant for scientific workspaces"""
    required = PROFILE_REQUIREMENTS[WorkspaceProfile.SCIENTIFIC]
    is_compliant, _ = ComplianceEnforcer.check_tier_compliance(user_tier, required)
    return is_compliant
