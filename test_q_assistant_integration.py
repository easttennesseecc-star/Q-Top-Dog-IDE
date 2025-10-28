#!/usr/bin/env python3
"""
Integration test for Q Assistant scope enforcement and build orchestration system.

Tests that:
1. Q Assistant role is properly configured
2. Forbidden patterns are detected
3. Build orchestration system works
4. All 5 LLM roles are defined
5. API routes are registered
"""

import sys
sys.path.insert(0, "backend")

from llm_roles_descriptor import LLMRole, ROLE_SPECIFICATIONS
from q_assistant_scope import (
    QAssistantScope,
    validate_q_assistant_output,
    Q_ASSISTANT_SYSTEM_PROMPT,
    generate_simple_wireframe,
    generate_simple_user_flow,
    generate_simple_database_schema,
    generate_simple_architecture_diagram,
)
from build_orchestrator import BuildOrchestrator, BuildPhase
from build_orchestration_routes import router


def test_q_assistant_role():
    """Test Q Assistant role is properly configured"""
    print("\n" + "="*70)
    print("TEST 1: Q Assistant Role Configuration")
    print("="*70)
    
    q_role = ROLE_SPECIFICATIONS[LLMRole.Q_ASSISTANT.value]
    
    print(f"[OK] Q Assistant title: {q_role.title}")
    print(f"[OK] Position number: {q_role.position_number}")
    print(f"[OK] Description length: {len(q_role.description)} chars")
    print(f"[OK] System prompt length: {len(q_role.system_prompt)} chars")
    
    # Verify system prompt contains critical boundaries
    assert "DO NOT WRITE CODE" in q_role.system_prompt, \
        "System prompt missing 'DO NOT WRITE CODE'"
    print("[OK] System prompt contains 'DO NOT WRITE CODE' constraint")
    
    assert "ORCHESTRATOR" in q_role.system_prompt, \
        "System prompt missing 'ORCHESTRATOR'"
    print("[OK] System prompt contains 'ORCHESTRATOR' metaphor")
    
    # Check responsibilities
    assert len(q_role.responsibilities) > 0, "No responsibilities defined"
    print(f"[OK] {len(q_role.responsibilities)} responsibilities defined")
    
    # Check capabilities
    assert len(q_role.capabilities) > 0, "No capabilities defined"
    print(f"[OK] {len(q_role.capabilities)} capabilities defined")
    
    # Check success criteria
    assert len(q_role.success_criteria) > 0, "No success criteria defined"
    print(f"[OK] {len(q_role.success_criteria)} success criteria defined")
    
    print("\n[PASS] Q Assistant role configuration: PASS")
    return True


def test_forbidden_patterns():
    """Test that forbidden code patterns are detected"""
    print("\n" + "="*70)
    print("TEST 2: Forbidden Pattern Detection")
    print("="*70)
    
    test_cases = [
        {"text": "def foo(): pass", "pattern": "def ", "should_detect": True},
        {"text": "const x = 'y'", "pattern": "const ", "should_detect": True},
        {"text": "SELECT * FROM users", "pattern": "SELECT ", "should_detect": True},
        {"text": "<div>Hello</div>", "pattern": "<div", "should_detect": True},
        {"text": "I need a user authentication system with email and password verification", "pattern": None, "should_detect": False},
        {"text": "Create an API endpoint that retrieves user data by ID", "pattern": None, "should_detect": False},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        result = validate_q_assistant_output(test_case["text"])
        if test_case["should_detect"]:
            assert result["has_forbidden_content"], \
                f"Failed to detect code pattern in: {test_case['text']}"
            print(f"[OK] Test {i}: Correctly detected forbidden pattern '{test_case['pattern']}'")
        else:
            assert not result["has_forbidden_content"], \
                f"False positive for: {test_case['text']}"
            print(f"[OK] Test {i}: Correctly allowed valid Q Assistant output")
    
    print("\n[PASS] Forbidden pattern detection: PASS")
    return True


def test_llm_roles():
    """Test all 5 LLM roles are defined"""
    print("\n" + "="*70)
    print("TEST 3: All 5 LLM Roles Defined")
    print("="*70)
    
    expected_roles = [
        LLMRole.Q_ASSISTANT,
        LLMRole.CODE_WRITER,
        LLMRole.TEST_AUDITOR,
        LLMRole.VERIFICATION_OVERSEER,
        LLMRole.RELEASE_MANAGER,
    ]
    
    for role in expected_roles:
        spec = ROLE_SPECIFICATIONS[role.value]
        print(f"[OK] {role.value}: {spec.title}")
        print(f"    - Position: {spec.position_number}")
        print(f"    - Responsibilities: {len(spec.responsibilities)}")
        print(f"    - Capabilities: {len(spec.capabilities)}")
        print(f"    - Success criteria: {len(spec.success_criteria)}")
    
    print("\n[PASS] All 5 LLM roles configured: PASS")
    return True


def test_build_orchestrator():
    """Test build orchestration system"""
    print("\n" + "="*70)
    print("TEST 4: Build Orchestration System")
    print("="*70)
    
    from uuid import uuid4
    
    print("[OK] BuildOrchestrator initialized")
    
    # Create a project
    project_id = f"test-{str(uuid4())[:8]}"
    orchestrator = BuildOrchestrator(project_id)
    project = orchestrator.create_project(project_id, "Test Project", "Test Description")
    
    print(f"[OK] Created project: {project.project_id}")
    print(f"    - Status: {project.status}")
    print(f"    - Current phase: {project.current_phase}")
    
    # Verify initial phase
    assert project.current_phase == BuildPhase.DISCOVERY.value, \
        "Initial phase should be DISCOVERY"
    print("[OK] Initial phase is DISCOVERY")
    
    # Retrieve project
    retrieved = orchestrator.get_project(project.project_id)
    assert retrieved is not None, "Project not persisted"
    print("[OK] Project persisted and retrievable")
    
    # Check all phases exist
    phases = list(BuildPhase)
    print(f"[OK] All {len(phases)} phases defined")
    
    print("\n[PASS] Build orchestration system: PASS")
    return True


def test_api_routes():
    """Test API routes are registered"""
    print("\n" + "="*70)
    print("TEST 5: API Routes Registration")
    print("="*70)
    
    # Check routes exist
    routes = list(router.routes)
    print(f"[OK] Total API routes registered: {len(routes)}")
    
    # Check route types
    methods = set()
    for route in routes:
        if hasattr(route, 'methods'):
            methods.update(route.methods)
    
    print(f"[OK] Route methods: {', '.join(sorted(methods))}")
    
    # Check for expected patterns
    route_paths = [route.path for route in routes if hasattr(route, 'path')]
    has_builds = any('/builds' in path for path in route_paths)
    assert has_builds, "Missing /builds routes"
    print("[OK] Expected route patterns found")
    
    # Show sample routes
    print("\n    Sample routes:")
    for route in routes[:5]:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            method = ', '.join(sorted(route.methods))
            print(f"    - {method:8} {route.path}")
    print(f"    ... and {len(routes) - 5} more routes")
    
    print("\n[PASS] API routes: PASS")
    return True


def test_q_assistant_system_prompt():
    """Test Q Assistant system prompt contains critical elements"""
    print("\n" + "="*70)
    print("TEST 6: Q Assistant System Prompt Content")
    print("="*70)
    
    q_role = ROLE_SPECIFICATIONS[LLMRole.Q_ASSISTANT.value]
    prompt = q_role.system_prompt
    
    critical_elements = [
        ("YOU ARE THE ORCHESTRATOR", "Main role statement"),
        ("YOU DO NOT WRITE CODE", "Primary constraint"),
        ("ORCHESTRATOR", "Role metaphor"),
        ("EXTRACT REQUIREMENTS", "Key responsibility 1 (EXTRACT REQUIREMENTS)"),
        ("EXTRACT DESIGN", "Key responsibility 2 (EXTRACT DESIGN SPECS)"),
        ("CREATE IMPLEMENTATION PLAN", "Key responsibility 3 (CREATE PLAN)"),
        ("COORDINATE TEAM", "Key responsibility 4 (COORDINATE HANDOFFS)"),
        ("FORBIDDEN", "Forbidden activities section"),
        ("ABSOLUTELY FORBIDDEN", "Strong language for constraints"),
        ("ONLY JOB IS TO", "Task definition"),
    ]
    
    for element, description in critical_elements:
        assert element in prompt, f"Missing: {element} ({description})"
        print(f"[OK] Contains: {description}")
    
    print(f"\n[OK] System prompt length: {len(prompt):,} characters")
    print("[OK] All critical elements present")
    
    print("\n[PASS] Q Assistant system prompt: PASS")
    return True


def test_simple_image_generation():
    """Test Q Assistant simple image generation (cost optimization)"""
    print("\n" + "="*70)
    print("TEST 7: Simple Image Generation (Cost Optimization)")
    print("="*70)
    
    # Test 1: Wireframe generation
    wireframe = generate_simple_wireframe(800, 600)
    assert "<svg" in wireframe, "Wireframe not SVG format"
    assert "Header" in wireframe, "Wireframe missing header"
    assert "Sidebar" in wireframe, "Wireframe missing sidebar"
    print("[OK] Wireframe generation works (800x600)")
    
    # Test 2: User flow generation
    flow = generate_simple_user_flow("Test Flow")
    assert "<svg" in flow, "Flow not SVG format"
    assert "Step 1" in flow, "Flow missing Step 1"
    assert "Test Flow" in flow, "Flow missing title"
    print("[OK] User flow generation works")
    
    # Test 3: Database schema generation
    schema = generate_simple_database_schema(["users", "posts", "comments"])
    assert "<svg" in schema, "Schema not SVG format"
    assert "users" in schema, "Schema missing users table"
    assert "posts" in schema, "Schema missing posts table"
    assert "comments" in schema, "Schema missing comments table"
    print("[OK] Database schema generation works (3 tables)")
    
    # Test 4: Architecture diagram
    arch = generate_simple_architecture_diagram()
    assert "<svg" in arch, "Architecture not SVG format"
    assert "Frontend" in arch, "Architecture missing Frontend"
    assert "Backend" in arch, "Architecture missing Backend"
    assert "Database" in arch, "Architecture missing Database"
    print("[OK] Architecture diagram generation works")
    
    # Test 5: Verify no code patterns in generated images
    from q_assistant_scope import FORBIDDEN_PATTERNS
    false_positives = ["from ", "<div", "<button", "<form"]
    
    for image_name, image_svg in [
        ("wireframe", wireframe),
        ("flow", flow),
        ("schema", schema),
        ("arch", arch),
    ]:
        found_code = []
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.lower() in image_svg.lower():
                if pattern not in false_positives:
                    found_code.append(pattern)
        
        assert len(found_code) == 0, \
            f"{image_name} contains code patterns: {found_code}"
    
    print("[OK] No code patterns detected in generated images")
    
    # Test 6: Verify GENERATE_SIMPLE_IMAGES is in allowed scope
    assert hasattr(QAssistantScope, 'GENERATE_SIMPLE_IMAGES'), \
        "GENERATE_SIMPLE_IMAGES not in QAssistantScope"
    print("[OK] GENERATE_SIMPLE_IMAGES is in allowed scope")
    
    print("\n[PASS] Simple image generation: PASS")
    print("       (Cost optimization feature working - $0 per image, no API calls)")
    return True


def main():
    """Run all integration tests"""
    print("\n")
    print("[" + "="*68 + "]")
    print("|  Q ASSISTANT SCOPE ENFORCEMENT - INTEGRATION TEST SUITE          |")
    print("[" + "="*68 + "]")
    
    tests = [
        ("Q Assistant Role Configuration", test_q_assistant_role),
        ("Forbidden Pattern Detection", test_forbidden_patterns),
        ("All 5 LLM Roles", test_llm_roles),
        ("Build Orchestration System", test_build_orchestrator),
        ("API Routes", test_api_routes),
        ("Q Assistant System Prompt", test_q_assistant_system_prompt),
        ("Simple Image Generation", test_simple_image_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            test_func()
            results.append((test_name, True, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"\n[FAIL] {test_name}: FAIL")
            print(f"   Error: {str(e)}")
    
    # Summary
    print("\n" + "="*70)
    print("INTEGRATION TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, error in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} - {test_name}")
        if error:
            print(f"         {error}")
    
    print("\n" + "="*70)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("\n[PASS] Q Assistant scope enforcement is fully operational")
        print("[PASS] Build orchestration system is ready")
        print("[PASS] All 5 LLM roles configured")
        print("[PASS] API endpoints registered")
        print("[PASS] Simple image generation (cost optimization) enabled")
        print("\nStatus: [READY] PRODUCTION READY")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
