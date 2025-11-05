"""
Default Rules Setup
Creates a set of sensible default rules for Q-IDE projects.
"""

from backend.services.universal_rules_engine import (
    get_rules_engine,
    Rule,
    RuleType,
    RuleScope,
    RuleEnforcement
)


def create_default_rules():
    """Create and register default rules for Q-IDE projects."""
    rules_engine = get_rules_engine()
    
    default_rules = [
        # Code Style Rules
        Rule(
            id="",
            name="Use TypeScript for Frontend",
            description="All frontend code must be written in TypeScript, not JavaScript",
            rule_text="Use .ts or .tsx files. Do not create .js or .jsx files. Include proper type annotations.",
            rule_type=RuleType.CODE_STYLE,
            scope=RuleScope.GLOBAL,
            enforcement=RuleEnforcement.MANDATORY,
            priority=10,
            tags=["typescript", "frontend", "type-safety"]
        ),
        
        Rule(
            id="",
            name="Python Type Hints Required",
            description="All Python functions must have type hints",
            rule_text="Add type hints to all function parameters and return values. Use typing module for complex types.",
            rule_type=RuleType.CODE_STYLE,
            scope=RuleScope.GLOBAL,
            enforcement=RuleEnforcement.STRICT,
            priority=20,
            tags=["python", "type-hints", "backend"]
        ),
        
        Rule(
            id="",
            name="Meaningful Variable Names",
            description="Use descriptive variable names, avoid single letters except in loops",
            rule_text="Variable names should clearly describe their purpose. Avoid abbreviations unless they're well-known. Single letters (i, j, k) are acceptable only for loop counters.",
            rule_type=RuleType.CODE_STYLE,
            scope=RuleScope.GLOBAL,
            enforcement=RuleEnforcement.GUIDANCE,
            priority=50,
            tags=["readability", "naming"]
        ),
        
        # Architecture Rules
        Rule(
            id="",
            name="Separate Business Logic from UI",
            description="Keep business logic separate from UI components",
            rule_text="UI components should only handle presentation. Move business logic to services, utilities, or hooks. React components should primarily focus on rendering.",
            rule_type=RuleType.ARCHITECTURE,
            scope=RuleScope.GLOBAL,
            enforcement=RuleEnforcement.STRICT,
            priority=15,
            tags=["architecture", "separation-of-concerns"]
        ),
        
        Rule(
            id="",
            name="API Routes in Backend Only",
            description="All API calls must go through backend routes",
            rule_text="Do not make direct external API calls from frontend. Create backend endpoints to proxy requests. This ensures proper authentication, rate limiting, and error handling.",
            rule_type=RuleType.ARCHITECTURE,
            scope=RuleScope.GLOBAL,
            enforcement=RuleEnforcement.MANDATORY,
            priority=5,
            tags=["api", "security", "backend"]
        ),
        
        # Security Rules
        Rule(
            id="",
            name="No Hardcoded Credentials",
            description="Never hardcode API keys, passwords, or secrets",
            rule_text="Use environment variables or secure configuration files. Never commit credentials to git. Use .env files and add them to .gitignore.",
            rule_type=RuleType.SECURITY,
            scope=RuleScope.GLOBAL,
            enforcement=RuleEnforcement.MANDATORY,
            priority=1,
            tags=["security", "credentials", "critical"]
        ),
        
        Rule(
            id="",
            name="Validate User Input",
            description="Always validate and sanitize user input",
            rule_text="Use Pydantic models for API validation. Sanitize HTML content. Validate file uploads. Never trust user input.",
            rule_type=RuleType.SECURITY,
            scope=RuleScope.GLOBAL,
            enforcement=RuleEnforcement.MANDATORY,
            priority=2,
            tags=["security", "validation", "input"]
        ),
        
        # Testing Rules
        Rule(
            id="",
            name="Write Tests for New Features",
            description="All new features must include tests",
            rule_text="Write unit tests for new functions/methods. Include integration tests for API endpoints. Aim for >80% code coverage.",
            rule_type=RuleType.TESTING,
            scope=RuleScope.GLOBAL,
            enforcement=RuleEnforcement.STRICT,
            priority=30,
            tags=["testing", "quality"]
        ),
        
        # Documentation Rules
        Rule(
            id="",
            name="Document Complex Functions",
            description="Add docstrings to complex functions",
            rule_text="Functions with complex logic, multiple parameters, or non-obvious behavior must have docstrings explaining purpose, parameters, return values, and examples.",
            rule_type=RuleType.DOCUMENTATION,
            scope=RuleScope.GLOBAL,
            enforcement=RuleEnforcement.GUIDANCE,
            priority=40,
            tags=["documentation", "readability"]
        ),
        
        # Performance Rules
        Rule(
            id="",
            name="Avoid N+1 Queries",
            description="Prevent N+1 database queries",
            rule_text="Use eager loading or batch queries instead of making separate queries in loops. Optimize database access patterns.",
            rule_type=RuleType.PERFORMANCE,
            scope=RuleScope.GLOBAL,
            enforcement=RuleEnforcement.STRICT,
            priority=25,
            tags=["performance", "database"]
        ),
        
        # Q-IDE Specific Rules
        Rule(
            id="",
            name="No Cross-Project Data Leakage",
            description="Ensure complete isolation between projects",
            rule_text="Each project must have isolated: database schema, API keys, configuration, user data. Never share data between projects without explicit user consent. Validate project_id on all operations.",
            rule_type=RuleType.SECURITY,
            scope=RuleScope.GLOBAL,
            enforcement=RuleEnforcement.MANDATORY,
            priority=1,
            tags=["q-ide", "isolation", "security", "critical"],
            metadata={
                "q_ide_specific": True,
                "affects": ["database", "api", "storage"]
            }
        ),
        
        Rule(
            id="",
            name="Remember Build Context",
            description="Persist build context and user preferences",
            rule_text="Save project configuration, user rules, build settings to database. Load context at start of each session. Never require users to re-explain the same rules.",
            rule_type=RuleType.ARCHITECTURE,
            scope=RuleScope.GLOBAL,
            enforcement=RuleEnforcement.MANDATORY,
            priority=3,
            tags=["q-ide", "context", "ux"],
            metadata={
                "q_ide_specific": True,
                "implements": "context_memory"
            }
        ),
        
        Rule(
            id="",
            name="Pre-Build Approval Required",
            description="Present plan before executing builds",
            rule_text="Before any build: 1) Analyze requirements, 2) Generate detailed plan with affected files, 3) Present to user, 4) Wait for approval, 5) Execute only after approval. Never make changes without user consent.",
            rule_type=RuleType.BUILD,
            scope=RuleScope.GLOBAL,
            enforcement=RuleEnforcement.MANDATORY,
            priority=2,
            tags=["q-ide", "workflow", "approval"],
            metadata={
                "q_ide_specific": True,
                "implements": "approval_workflow"
            }
        ),
    ]
    
    # Add all default rules
    for rule in default_rules:
        try:
            rules_engine.add_rule(rule)
            print(f"✓ Created rule: {rule.name}")
        except Exception as e:
            print(f"✗ Failed to create rule '{rule.name}': {e}")
    
    print(f"\n✓ Created {len(default_rules)} default rules")


if __name__ == "__main__":
    create_default_rules()
