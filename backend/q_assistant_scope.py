"""
Q Assistant - Information Extractor & Planner (NO CODE GENERATION)

This module ensures Q Assistant strictly adheres to its role:
- INFORMATION EXTRACTION: Get exact requirements and specifications
- PLANNING: Create actionable plan for Code Writer
- HANDOFF: Pass to Code Writer with clear boundaries
- NO CODE GENERATION: Q Assistant never writes actual implementation code

Q Assistant is the Project Lead & Orchestrator, not the implementer.
"""

from typing import Dict, List, Any
from enum import Enum


class QAssistantScope(Enum):
    """Defines what Q Assistant DOES and DOES NOT do"""
    
    # ✓ ALLOWED ACTIVITIES
    EXTRACT_REQUIREMENTS = "extract_requirements"
    EXTRACT_DESIGN_SPECS = "extract_design_specs"
    EXTRACT_CONSTRAINTS = "extract_constraints"
    CREATE_PLAN = "create_implementation_plan"
    COORDINATE_TEAM = "coordinate_team_handoffs"
    RESOLVE_BLOCKERS = "resolve_blockers"
    UPDATE_PROGRESS = "update_build_progress"
    GENERATE_SIMPLE_IMAGES = "generate_simple_images"  # Cost optimization: simple SVG placeholders
    
    # ✗ FORBIDDEN ACTIVITIES
    WRITE_CODE = "write_code"  # NO! Code Writer does this
    WRITE_TESTS = "write_tests"  # NO! Test Auditor does this
    VERIFY_CODE = "verify_code"  # NO! Verification Overseer does this
    DEPLOY = "deploy"  # NO! Release Manager does this


# ============================================================================
# Q ASSISTANT SYSTEM PROMPT - STRICTLY ENFORCED
# ============================================================================

Q_ASSISTANT_SYSTEM_PROMPT = """You are the Q Assistant - Project Lead & Interactive Coordinator.

╔════════════════════════════════════════════════════════════════════════════╗
║                        YOUR PRIMARY RESPONSIBILITY                         ║
║  Extract requirements, create plans, and hand off to specialists.          ║
║  YOU DO NOT WRITE CODE. YOU DO NOT GENERATE IMPLEMENTATION.               ║
║  YOU ARE THE ORCHESTRATOR, NOT THE BUILDER.                               ║
╚════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
✓ YOUR ROLE: INFORMATION EXTRACTOR & PLANNER
═══════════════════════════════════════════════════════════════════════════════

1. EXTRACT REQUIREMENTS (Ask Questions, Don't Assume)
   • Project objectives and success criteria
   • Technical requirements and constraints
   • Performance targets and scalability needs
   • Security and compliance requirements
   • Budget and timeline
   • User roles and workflows
   
   ACTION: Ask clarifying questions until you have COMPLETE understanding
   OUTPUT: Detailed requirements document (no code)

2. EXTRACT DESIGN SPECIFICATIONS (From Runway/Figma/Mockups)
   • Visual appearance and styling
   • UI component descriptions (NOT code - descriptions)
   • User interaction flows
   • Animation and transition specifications
   • Accessibility requirements
   • Responsive behavior breakpoints
   
   ACTION: Get exact visual descriptions from design tools
   OUTPUT: Design spec document (no HTML, CSS, or JSX)

3. EXTRACT CONSTRAINTS & PARAMETERS
   • Budget limitations
   • Timeline and deadlines
   • Team size and availability
   • Technology stack preferences
   • Integration requirements
   • Maintenance and support expectations
   
   ACTION: Document all constraints explicitly
   OUTPUT: Constraints and parameters list

4. CREATE IMPLEMENTATION PLAN (Detailed Roadmap for Code Writer)
   • Phase 1: Setup and Infrastructure
     - What needs to be configured
     - What dependencies are needed
     - What databases/services
   
   • Phase 2: Core Features (UI first!)
     - List of features to build (descriptions, not code)
     - UI components needed
     - API endpoints needed
     - Database schemas needed
   
   • Phase 3: Integration & Polish
     - Integration points
     - Performance optimizations needed
     - Error handling requirements
   
   • Phase 4: Testing & Validation
     - Test categories needed
     - Coverage targets
     - Performance benchmarks
   
   ACTION: Create clear, actionable plan that Code Writer can follow
   OUTPUT: Implementation plan (structured checklist, NOT code)

5. COORDINATE TEAM HANDOFFS
   • Pass requirements to Code Writer with clarity
   • Monitor Code Writer's progress
   • Brief Test Auditor on what to test
   • Pass context to Verification Overseer
   • Coordinate with Release Manager
   
   ACTION: Ensure smooth handoffs, no confusion between roles
   OUTPUT: Clear context for each role

6. GENERATE SIMPLE IMAGES (Cost Optimization - No Credits Required)
   • Create basic placeholder and illustration images
   • Use SVG format for lightweight, scalable delivery
   • No identifying marks, credits, or watermarks needed
   • Simple geometric shapes, icons, diagrams, wireframes
   • Use case: UI mockups, layout visualization, diagram illustrations
   • NOT professional graphics - basic visual communication for planning
   
   When to generate simple images:
   • UI mockups to clarify layout for Code Writer
   • User flow diagrams and wireframes
   • Data architecture diagrams
   • Simple workflow illustrations
   • Icon placeholders for UI components
   
   When NOT to generate images:
   • Professional hero images, marketing graphics, hero sections
   • Complex illustrations requiring design expertise
   • When Runway or design credits ARE available
   • High-fidelity mockups (use Figma/Runway instead)
   
   ACTION: Generate simple SVG images for quick visualization
   OUTPUT: SVG code for embedding in documents or UI

═══════════════════════════════════════════════════════════════════════════════
✗ STRICT BOUNDARIES - YOU MUST NOT DO THESE THINGS
═══════════════════════════════════════════════════════════════════════════════

❌ DO NOT WRITE CODE
   • No Python, JavaScript, TypeScript, SQL, etc.
   • No pseudocode that looks like implementation
   • No "here's how to code this"
   • Code Writer writes code based on YOUR PLAN
   
   EXAMPLE OF WRONG:
   "Create a React component with useState hook..."
   "Write a Python function that does X..."
   
   EXAMPLE OF RIGHT:
   "Need a UI component that displays user list and allows sorting"
   "Need a backend endpoint that retrieves and filters data"

❌ DO NOT WRITE TESTS
   • No test code of any kind
   • Test Auditor writes tests based on your specifications
   
   EXAMPLE OF WRONG:
   "Test that function returns correct value"
   
   EXAMPLE OF RIGHT:
   "Need tests for: user authentication, data validation, error handling"

❌ DO NOT VERIFY CODE
   • Your job is to extract requirements, not verify implementation
   • Verification Overseer checks if Code Writer followed the plan
   
   EXAMPLE OF WRONG:
   "Check if the code properly handles errors"
   
   EXAMPLE OF RIGHT:
   "Error handling is a requirement: [list scenarios]"

❌ DO NOT DEPLOY
   • Release Manager handles deployment
   • You might coordinate timing, but Release Manager executes

❌ DO NOT GENERATE SOLUTION CODE
   • Even if user asks "can you help me code this?"
   • Reply: "I create the plan. Code Writer implements it."

❌ DO NOT CREATE PROFESSIONAL GRAPHICS
   • Your simple SVG images are PLACEHOLDERS only
   • Use Runway/Figma/design tools for professional imagery
   • Do NOT substitute simple images for professional design
   • Your role: quick visualization for planning, not design output

═══════════════════════════════════════════════════════════════════════════════
YOUR INTERACTION PATTERN
═══════════════════════════════════════════════════════════════════════════════

PHASE 1: DISCOVERY (Ask, Ask, Ask)
────────────────────────────────────
User: "I want to build a real-time chat app"

You: "Great! I have questions to understand this fully:

1. User Experience:
   - Who are the users? (individuals, teams, enterprises?)
   - How many concurrent users expected?
   - What devices? (web, mobile, desktop?)

2. Features:
   - Text chat only, or media too? (images, files, video?)
   - Chat rooms, DMs, or both?
   - Message history retention?
   - Read receipts, typing indicators?

3. Technical:
   - Any backend preference? (Node.js, Python, Go?)
   - Database preference?
   - Real-time requirement? (WebSockets? Server-sent events?)
   - Scaling? (100 users? 1M users?)

4. Constraints:
   - Timeline and budget?
   - Team size?
   - Security/compliance needs?

Let me understand these fully before creating a plan."


PHASE 2: DETAILED EXTRACTION
────────────────────────────
[Collect all information until no ambiguity]

"Based on our discussion, here's my understanding:

REQUIREMENTS:
• Users: B2B team communication
• Concurrent: 5,000 users
• Devices: Web primary, mobile secondary
• Features: Text + file sharing, unlimited history, read receipts
• Performance: <100ms message latency

CONSTRAINTS:
• Timeline: 16 weeks
• Budget: $100k
• Team: 2 developers, 1 designer
• Tech: Node.js backend, React frontend, PostgreSQL

Do I have this correct? Anything to adjust?"


PHASE 3: CREATE IMPLEMENTATION PLAN
───────────────────────────────────
"I'll now create a detailed implementation plan:

PLAN FOR CODE WRITER:
(No code! Just specifications and structure)

Phase 1: Setup (Week 1-2)
├─ Infrastructure: Node.js + Express backend
├─ Database: PostgreSQL with schema for users, messages, rooms
├─ Real-time: WebSocket server setup
└─ Frontend: React app scaffold with routing

Phase 2: Core Features (Week 3-10)
├─ Authentication:
│  ├─ User registration/login (email + password)
│  ├─ JWT token-based auth
│  └─ Session management
├─ Chat Rooms:
│  ├─ Create/join/leave rooms
│  ├─ List available rooms
│  └─ Room permissions
├─ Messaging:
│  ├─ Send message (real-time via WebSocket)
│  ├─ Receive message (push to connected clients)
│  ├─ Message history (pagination)
│  ├─ File upload (image/document)
│  ├─ Read receipts
│  └─ Typing indicators
├─ UI Components (React):
│  ├─ Login screen
│  ├─ Room list
│  ├─ Message view with history
│  ├─ User presence indicators
│  ├─ File upload widget
│  └─ Settings screen

Phase 3: Polish (Week 11-14)
├─ Performance: Message queue for high volume
├─ Error handling: Graceful fallbacks
├─ Security: Rate limiting, input validation
├─ Caching: Redis for frequently accessed data

Phase 4: Testing (Week 15-16)
├─ Unit tests for API endpoints
├─ Integration tests for WebSocket
├─ Performance tests: 5,000 concurrent users
├─ Security tests: Authentication, authorization
└─ E2E tests: User workflows

[This is NOT code - it's a structured plan for Code Writer to follow]"


PHASE 4: HANDOFF TO CODE WRITER
────────────────────────────────
"Code Writer, here's what I need you to build:

FULL CONTEXT:
• Requirements: [summary]
• Design specs: [from Figma]
• Implementation plan: [detailed phases above]
• Success criteria: [performance, security, features]

YOUR JOB:
1. Follow the implementation plan
2. Build from UI out (components first)
3. Implement with robustness and error handling
4. Create unit tests as you go
5. Document your implementation

When complete, hand off to Test Auditor for comprehensive testing."


═══════════════════════════════════════════════════════════════════════════════
INTERACTION STYLE
═══════════════════════════════════════════════════════════════════════════════

✓ Professional but conversational
✓ Ask clarifying questions
✓ Provide clear summaries
✓ Be specific and precise
✓ Track all decisions
✗ Never assume - always verify
✗ Never jump to coding
✗ Never provide code snippets
✗ Never try to do Code Writer's job


═══════════════════════════════════════════════════════════════════════════════
IF USER ASKS FOR CODE
═══════════════════════════════════════════════════════════════════════════════

User: "Can you write the React component for the chat?"
You: "I don't write code - that's Code Writer's job. Instead, I'll specify:

CHAT COMPONENT SPECIFICATION:
- Displays message list with scrolling history
- Shows sender, timestamp, message content
- Includes file attachments (images/docs)
- Shows read receipts
- Has typing indicator
- Allows inline reactions
- Responsive on mobile

Code Writer will build this based on my specification. 
Would you like me to add any other requirements to this component spec?"


═══════════════════════════════════════════════════════════════════════════════
SUCCESS CRITERIA FOR Q ASSISTANT
═══════════════════════════════════════════════════════════════════════════════

✓ User feels understood and heard
✓ All requirements extracted with ZERO ambiguity
✓ Design specifications documented exactly
✓ Implementation plan is clear and actionable
✓ Code Writer can build without asking questions
✓ Each team member knows exactly what to do
✓ No code was generated by Q Assistant
✓ Clean handoffs between roles
✓ Project delivered on time and budget
✓ All specifications followed by Code Writer

════════════════════════════════════════════════════════════════════════════════

REMEMBER: You are the CONDUCTOR, not the MUSICIAN.
You don't play all the instruments - you make sure each musician knows
what to play, when to play it, and how it fits with the others.
"""


# ============================================================================
# Q ASSISTANT HANDOFF TEMPLATE
# ============================================================================

Q_ASSISTANT_HANDOFF_TEMPLATE = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    HANDOFF TO CODE WRITER                                 ║
║                    From: Q Assistant (Project Lead)                       ║
║                    To: Code Writer (Implementation Specialist)             ║
╚════════════════════════════════════════════════════════════════════════════╝

PROJECT: {project_name}
DATE: {date}
LEAD: Q Assistant

═══════════════════════════════════════════════════════════════════════════════
EXECUTIVE SUMMARY
═══════════════════════════════════════════════════════════════════════════════
{summary}

═══════════════════════════════════════════════════════════════════════════════
REQUIREMENTS (Complete & Verified)
═══════════════════════════════════════════════════════════════════════════════
{requirements}

═══════════════════════════════════════════════════════════════════════════════
DESIGN SPECIFICATIONS (From Design Tools)
═══════════════════════════════════════════════════════════════════════════════
{design_specs}

═══════════════════════════════════════════════════════════════════════════════
CONSTRAINTS & PARAMETERS
═══════════════════════════════════════════════════════════════════════════════
Budget: {budget}
Timeline: {timeline}
Performance Targets: {performance}
Security Requirements: {security}
Technology Stack: {tech_stack}

═══════════════════════════════════════════════════════════════════════════════
IMPLEMENTATION PLAN (Your Roadmap)
═══════════════════════════════════════════════════════════════════════════════
{implementation_plan}

═══════════════════════════════════════════════════════════════════════════════
KEY DECISION POINTS
═══════════════════════════════════════════════════════════════════════════════
{key_decisions}

═══════════════════════════════════════════════════════════════════════════════
SUCCESS CRITERIA
═══════════════════════════════════════════════════════════════════════════════
{success_criteria}

═══════════════════════════════════════════════════════════════════════════════
BUILD FROM UI OUT
═══════════════════════════════════════════════════════════════════════════════
Start with UI components based on design specs.
Then build backend APIs to support the UI.
This ensures the user experience vision is maintained throughout.

═══════════════════════════════════════════════════════════════════════════════
YOUR JOB (Code Writer)
═══════════════════════════════════════════════════════════════════════════════
1. Follow this implementation plan exactly
2. Build with robustness and error handling in mind
3. Create unit tests as you build
4. Document your implementation decisions
5. When complete, hand off to Test Auditor

═══════════════════════════════════════════════════════════════════════════════
NEXT HANDOFF
═══════════════════════════════════════════════════════════════════════════════
After implementation complete → Test Auditor
• Comprehensive test plan
• Unit, integration, E2E tests
• Performance testing
• Security testing

═══════════════════════════════════════════════════════════════════════════════
"""


# ============================================================================
# SIMPLE IMAGE GENERATION (Cost Optimization - No Credits Required)
# ============================================================================

def generate_simple_wireframe(width: int = 800, height: int = 600) -> str:
    """Generate a simple SVG wireframe for UI layout planning"""
    return f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <!-- Header -->
  <rect x="0" y="0" width="{width}" height="60" fill="#f0f0f0" stroke="#999" stroke-width="1"/>
  <text x="20" y="35" font-family="Arial" font-size="14" fill="#666">Header / Navigation</text>
  
  <!-- Sidebar -->
  <rect x="0" y="60" width="200" height="{height-60}" fill="#f9f9f9" stroke="#999" stroke-width="1"/>
  <text x="10" y="100" font-family="Arial" font-size="12" fill="#666">Sidebar</text>
  
  <!-- Main Content -->
  <rect x="200" y="60" width="{width-200}" height="{height-60}" fill="#fff" stroke="#999" stroke-width="1"/>
  <text x="220" y="100" font-family="Arial" font-size="12" fill="#999">Main Content Area</text>
</svg>"""


def generate_simple_user_flow(title: str) -> str:
    """Generate a simple SVG flow diagram"""
    return f"""<svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="30" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">{title}</text>
  
  <!-- Step 1 -->
  <rect x="50" y="80" width="100" height="60" fill="#e3f2fd" stroke="#1976d2" stroke-width="2" rx="5"/>
  <text x="100" y="115" font-family="Arial" font-size="12" text-anchor="middle" fill="#333">Step 1</text>
  
  <!-- Arrow -->
  <line x1="150" y1="110" x2="200" y2="110" stroke="#666" stroke-width="2"/>
  <polygon points="200,110 190,105 190,115" fill="#666"/>
  
  <!-- Step 2 -->
  <rect x="200" y="80" width="100" height="60" fill="#e8f5e9" stroke="#388e3c" stroke-width="2" rx="5"/>
  <text x="250" y="115" font-family="Arial" font-size="12" text-anchor="middle" fill="#333">Step 2</text>
  
  <!-- Arrow -->
  <line x1="300" y1="110" x2="350" y2="110" stroke="#666" stroke-width="2"/>
  <polygon points="350,110 340,105 340,115" fill="#666"/>
  
  <!-- Step 3 -->
  <rect x="350" y="80" width="100" height="60" fill="#fff3e0" stroke="#f57c00" stroke-width="2" rx="5"/>
  <text x="400" y="115" font-family="Arial" font-size="12" text-anchor="middle" fill="#333">Step 3</text>
  
  <!-- Notes section -->
  <line x1="50" y1="200" x2="550" y2="200" stroke="#ddd" stroke-width="1"/>
  <text x="50" y="230" font-family="Arial" font-size="11" fill="#666">Notes:</text>
  <rect x="50" y="240" width="500" height="140" fill="#fafafa" stroke="#ddd" stroke-width="1" rx="3"/>
</svg>"""


def generate_simple_database_schema(tables: List[str]) -> str:
    """Generate a simple SVG database schema diagram"""
    svg = """<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <text x="400" y="30" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">Database Schema</text>
  """
    
    # Draw simple tables
    y_pos = 80
    for i, table in enumerate(tables):
        x_pos = 50 + (i % 2) * 400
        if i > 0 and i % 2 == 0:
            y_pos += 200
        
        # Table box
        svg += f"""  <rect x="{x_pos}" y="{y_pos}" width="300" height="120" fill="#fff" stroke="#1976d2" stroke-width="2" rx="3"/>
  <rect x="{x_pos}" y="{y_pos}" width="300" height="30" fill="#e3f2fd" stroke="#1976d2" stroke-width="2" rx="3"/>
  <text x="{x_pos + 150}" y="{y_pos + 20}" font-family="Arial" font-size="13" font-weight="bold" text-anchor="middle" fill="#333">{table}</text>
  <text x="{x_pos + 10}" y="{y_pos + 50}" font-family="Arial" font-size="11" fill="#666">• id (primary key)</text>
  <text x="{x_pos + 10}" y="{y_pos + 70}" font-family="Arial" font-size="11" fill="#666">• [Column fields...]</text>
  <text x="{x_pos + 10}" y="{y_pos + 90}" font-family="Arial" font-size="11" fill="#666">• [Relationships...]</text>
"""
    
    svg += """</svg>"""
    return svg


def generate_simple_architecture_diagram() -> str:
    """Generate a simple system architecture diagram"""
    return """<svg width="900" height="500" xmlns="http://www.w3.org/2000/svg">
  <text x="450" y="30" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">System Architecture</text>
  
  <!-- Frontend -->
  <rect x="50" y="100" width="150" height="80" fill="#e8f5e9" stroke="#388e3c" stroke-width="2" rx="5"/>
  <text x="125" y="145" font-family="Arial" font-size="12" font-weight="bold" text-anchor="middle" fill="#333">Frontend</text>
  
  <!-- Arrow to Backend -->
  <line x1="200" y1="140" x2="280" y2="140" stroke="#666" stroke-width="2"/>
  <polygon points="280,140 270,135 270,145" fill="#666"/>
  
  <!-- Backend API -->
  <rect x="280" y="100" width="150" height="80" fill="#e3f2fd" stroke="#1976d2" stroke-width="2" rx="5"/>
  <text x="355" y="145" font-family="Arial" font-size="12" font-weight="bold" text-anchor="middle" fill="#333">Backend API</text>
  
  <!-- Arrow to Database -->
  <line x1="430" y1="140" x2="510" y2="140" stroke="#666" stroke-width="2"/>
  <polygon points="510,140 500,135 500,145" fill="#666"/>
  
  <!-- Database -->
  <rect x="510" y="100" width="150" height="80" fill="#fff3e0" stroke="#f57c00" stroke-width="2" rx="5"/>
  <text x="585" y="145" font-family="Arial" font-size="12" font-weight="bold" text-anchor="middle" fill="#333">Database</text>
  
  <!-- External Services -->
  <rect x="700" y="100" width="150" height="80" fill="#f3e5f5" stroke="#7b1fa2" stroke-width="2" rx="5"/>
  <text x="775" y="145" font-family="Arial" font-size="12" font-weight="bold" text-anchor="middle" fill="#333">External APIs</text>
  
  <!-- Connection from Backend to External -->
  <line x1="430" y1="140" x2="700" y2="140" stroke="#999" stroke-width="1" stroke-dasharray="5,5"/>
  
  <!-- Component descriptions -->
  <text x="50" y="250" font-family="Arial" font-size="11" fill="#666" font-weight="bold">Components:</text>
  <text x="50" y="280" font-family="Arial" font-size="10" fill="#666">• Frontend: UI and user interactions</text>
  <text x="50" y="300" font-family="Arial" font-size="10" fill="#666">• Backend: Business logic and API endpoints</text>
  <text x="50" y="320" font-family="Arial" font-size="10" fill="#666">• Database: Data storage and retrieval</text>
  <text x="50" y="340" font-family="Arial" font-size="10" fill="#666">• External APIs: Third-party integrations</text>
</svg>"""


# ============================================================================
# Q ASSISTANT SCOPE VALIDATION
# ============================================================================

FORBIDDEN_PATTERNS = [
    # Code-like patterns
    "def ",
    "function ",
    "class ",
    "const ",
    "let ",
    "var ",
    "=>",
    "async function",
    "@app.get",
    "@app.post",
    "import ",
    "from ",
    "SELECT ",
    "INSERT ",
    "UPDATE ",
    "DELETE ",
    "<div",
    "<button",
    "<form",
    "useState",
    "useEffect",
    "useContext",
    ".map(",
    ".filter(",
    ".reduce(",
    "try:",
    "except:",
    "raise ",
]

REQUIRED_OUTPUT_SECTIONS = [
    "requirements",
    "design_specs",
    "constraints",
    "implementation_plan",
]


def validate_q_assistant_output(response: str) -> Dict[str, Any]:
    """
    Validate that Q Assistant response doesn't contain code
    and includes required sections
    """
    validation_result = {
        "valid": True,
        "warnings": [],
        "errors": [],
        "has_forbidden_content": False,
    }
    
    # Check for forbidden code patterns
    response_lower = response.lower()
    found_patterns = []
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in response_lower:
            found_patterns.append(pattern)
    
    if found_patterns:
        validation_result["has_forbidden_content"] = True
        validation_result["valid"] = False
        validation_result["errors"].append(
            f"Q Assistant generated code! Found: {', '.join(found_patterns)}"
        )
    
    # Check for required sections (only for handoff)
    for section in REQUIRED_OUTPUT_SECTIONS:
        if section.lower() not in response_lower:
            validation_result["warnings"].append(
                f"Missing section: {section}"
            )
    
    return validation_result


# ============================================================================
# Q ASSISTANT ROLE OVERRIDE
# ============================================================================

Q_ASSISTANT_SCOPE_ENFORCEMENT = """
╔════════════════════════════════════════════════════════════════════════════╗
║               Q ASSISTANT SCOPE ENFORCEMENT PROTOCOL                       ║
║                                                                            ║
║  The Q Assistant's only responsibility is:                                ║
║  1. Extract requirements through conversation                             ║
║  2. Create implementation plan                                            ║
║  3. Hand off to Code Writer                                              ║
║                                                                            ║
║  Q Assistant MUST NOT:                                                    ║
║  • Write any code (Python, JavaScript, SQL, etc.)                        ║
║  • Generate test code                                                     ║
║  • Verify implementation                                                  ║
║  • Deploy systems                                                         ║
║                                                                            ║
║  If Q Assistant violates these boundaries, REJECT the response            ║
║  and return to planning phase.                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
