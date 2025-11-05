# ✅ WEEK 1 IMPLEMENTATION CHECKLIST: Real-Time IntelliSense + Refactoring

**Goal**: Ship competitive code intelligence features that VS Code has, but Top Dog currently lacks  
**Timeline**: 5 business days  
**Team Size**: 2-3 developers recommended  
**Success Criteria**: Users report <100ms completions, feature parity with VS Code on top 5 refactorings

---

## MODULE 1: Real-Time IntelliSense Engine

### Phase 1A: Local Parsing (Days 1-2)

#### Task 1.1: Create Web Worker for Code Parsing
```
File: frontend/services/workers/code-parser.worker.ts
Lines: 300-400
Purpose: Parse code on background thread without blocking UI

Pseudocode:
├─ Import language parsers (Acorn for JS, Babel for JSX)
├─ Listen for parse messages from main thread
├─ Parse code on every keystroke
├─ Extract symbols: functions, classes, variables, imports
├─ Return symbol table to main thread
└─ Cache results

Dependencies:
├─ acorn (JavaScript parser)
├─ @babel/parser (JSX/TypeScript)
├─ web-tree-sitter (fast parsing library)
└─ recast (AST transformation)

Tests:
├─ Parse simple function
├─ Parse complex class
├─ Performance: parse 1000+ line file in <100ms
└─ Cache invalidation on file change
```

**Acceptance Criteria**:
- ✅ Parses JavaScript in <50ms
- ✅ Extracts 100+ symbols per file
- ✅ Returns results via postMessage
- ✅ Doesn't block main thread

---

#### Task 1.2: Integrate Parser into Editor
```
File: frontend/components/CodeEditor.tsx (update existing)
Lines: Add 200-300 lines
Purpose: Wire up Web Worker to editor

Implementation:
├─ Instantiate worker on component mount
├─ Send file content on every change (debounced 300ms)
├─ Receive symbol table from worker
├─ Store in local state (symbolTable map)
├─ Use for completions filtering

Code Snippet:
---
const parserWorker = useRef(new Worker('code-parser.worker.ts'));

const handleCodeChange = (newCode) => {
  // Debounce: only parse every 300ms
  debouncedParse(() => {
    parserWorker.current.postMessage({
      code: newCode,
      language: detectLanguage(filename)
    });
  });
};

parserWorker.current.onmessage = (e) => {
  const { symbols, imports, exports } = e.data;
  setSymbolTable(symbols);
  setImports(imports);
  setExports(exports);
};
---
```

**Acceptance Criteria**:
- ✅ Symbol table updates on every keystroke
- ✅ Debounce prevents excessive parsing
- ✅ No UI lag (<16ms per frame)

---

### Phase 1B: IntelliSense API (Days 2-3)

#### Task 1.3: Create Completion Engine
```
File: frontend/services/intellisense.ts
Lines: 400-500
Purpose: Generate completions from symbol table + context

Implementation:
├─ Function getCompletions(prefix, position, context)
│  ├─ Get word being typed (prefix)
│  ├─ Get current scope (local, module, global)
│  ├─ Filter symbols matching prefix
│  ├─ Rank by relevance (local > module > global)
│  ├─ Return top 20 completions
│  └─ Add documentation snippets
│
├─ Function getHoverInfo(symbol)
│  ├─ Get symbol type + docs
│  ├─ Show function signature
│  ├─ Show examples (from docstring)
│  └─ Show related symbols
│
└─ Function getDefinition(symbolName, position)
   ├─ Find symbol definition in codebase
   ├─ Return file + line number
   └─ Support cross-file jumps

Key Algorithms:
├─ Fuzzy matching (for typos)
├─ Scope analysis (local > module > global)
├─ Type inference (basic: string, number, boolean, array)
└─ Context awareness (what tokens are valid here?)

Tests:
├─ Completions for variable: ["toString", "toLowerCase", ...]
├─ Completions for import: ["react", "react-dom", ...]
├─ Hover shows function signature
└─ Go to definition finds correct file
```

**Acceptance Criteria**:
- ✅ Generates 10-50 completions per keystroke
- ✅ Fuzzy matching works (tStr → toString)
- ✅ Hover shows documentation
- ✅ Completion latency <100ms

---

#### Task 1.4: Connect to UI (Completion UI Already Exists)
```
File: frontend/components/CompletionPopup.tsx (update existing)
Lines: Add 100-150 lines
Purpose: Use new IntelliSense service

Implementation:
├─ On editor keystroke:
│  ├─ Call intellisense.getCompletions()
│  ├─ Show popup if matches found
│  ├─ Highlight top match
│  └─ Show preview/docs
│
├─ On arrow keys:
│  ├─ Navigate completions
│  └─ Update preview
│
├─ On Enter/Tab:
│  ├─ Insert selected completion
│  ├─ Auto-format if function
│  └─ Move cursor appropriately
│
└─ On Escape:
   └─ Hide popup

UX Details:
├─ Show icon (function 𝒇, variable x, class 🏛️)
├─ Show type annotation (string, number, boolean)
├─ Show documentation preview
└─ Fuzzy match highlighting (bold matched parts)
```

**Acceptance Criteria**:
- ✅ Popup shows on keystroke
- ✅ Selection works with arrow keys
- ✅ Tab/Enter inserts completion
- ✅ No visual lag

---

### Phase 1C: Language Server Integration (Days 3-4)

#### Task 1.5: Add TypeScript Language Server
```
File: backend/language_servers.py (new)
Lines: 200-300
Purpose: Use LSP for TypeScript/JavaScript

Implementation:
├─ Class TypeScriptLanguageServer(LSP):
│  ├─ Start server process (node_modules/.bin/typescript-language-server)
│  ├─ Send initialize request
│  ├─ Track open documents
│  ├─ Forward textDocument/completion requests
│  ├─ Parse responses + format for frontend
│  └─ Handle server shutdown
│
├─ async def get_completions(file_path, position):
│  ├─ Call LSP completionProvider/resolve
│  ├─ Parse response
│  ├─ Extract: label, detail, documentation
│  ├─ Return formatted completions
│  └─ Cache 30 seconds
│
└─ async def get_hover_info(file_path, position):
   ├─ Call LSP hover provider
   ├─ Format markdown response
   └─ Return to frontend

Configuration:
├─ Port: 3001 (local TS server)
├─ Timeout: 5 seconds per request
├─ Cache: 30 seconds TTL
└─ Error handling: Fall back to local parser
```

**Acceptance Criteria**:
- ✅ TypeScript completions accurate
- ✅ Hover info shows correct types
- ✅ Performance <200ms per request
- ✅ Graceful fallback to local parser

---

#### Task 1.6: Add Python Language Server (Pyright)
```
File: backend/language_servers.py (extend)
Lines: Add 150-200 lines
Purpose: Full Python semantic analysis

Implementation:
├─ Class PythonLanguageServer(LSP):
│  ├─ Initialize Pyright (npx pyright --version)
│  ├─ Configure for Python project
│  ├─ Track imports and dependencies
│  └─ Provide completions, definitions, references
│
└─ Features:
   ├─ Code completion (99% of VS Code quality)
   ├─ Go to definition (cross-file)
   ├─ Find all references
   ├─ Rename symbol (all files)
   ├─ Hover information
   └─ Diagnostic errors/warnings
```

**Acceptance Criteria**:
- ✅ Python completions work
- ✅ Errors highlighted inline
- ✅ Performance acceptable (<200ms)

---

### Phase 1D: Frontend Integration (Day 4-5)

#### Task 1.7: API Endpoints
```
File: backend/semantic_routes.py (new)
Lines: 100-200
Purpose: Expose language server features via REST

Endpoints:
├─ GET /api/semantic/completions
│  ├─ Query: file, position, prefix
│  ├─ Response: [{label, detail, kind, docs}, ...]
│  └─ Cache: 30s per file
│
├─ GET /api/semantic/hover
│  ├─ Query: file, position
│  ├─ Response: {contents, range}
│  └─ Cache: 60s per position
│
├─ GET /api/semantic/definition
│  ├─ Query: file, position
│  ├─ Response: {file, line, column}
│  └─ Cache: unlimited (file content changes invalidate)
│
├─ GET /api/semantic/references
│  ├─ Query: file, position
│  ├─ Response: [{file, line, column}, ...]
│  └─ Cache: 60s
│
└─ POST /api/semantic/rename
   ├─ Body: {file, position, newName}
   ├─ Response: {edits: [{file, range, newText}, ...]}
   └─ Apply multi-file changes

Error Handling:
├─ 400: Invalid file/position
├─ 408: Language server timeout
├─ 500: Language server crash
└─ Fallback: Return empty results gracefully
```

**Acceptance Criteria**:
- ✅ All endpoints return correct format
- ✅ Response times <200ms average
- ✅ Error handling graceful

---

#### Task 1.8: Frontend Integration
```
File: frontend/services/intellisense.ts (update)
Lines: Add 200 lines
Purpose: Call new backend endpoints

Implementation:
├─ Switch from local-only to hybrid:
│  ├─ Local: Fast results (symbols, imports)
│  ├─ Backend: Accurate results (LSP)
│  └─ Combine + rank by quality
│
├─ Caching strategy:
│  ├─ Memory cache (in-process): 30s TTL
│  ├─ Disk cache (localStorage): unlimited
│  └─ Server cache: 30s per file
│
├─ Debouncing:
│  ├─ Completions: 300ms (show local, fetch backend)
│  ├─ Hover: 200ms
│  ├─ Definition: 100ms (instant if in local table)
│  └─ References: 500ms (heavy operation)
│
└─ Error handling:
   ├─ Timeout: Show local results only
   ├─ Backend down: Use local only
   └─ Network error: Use cache
```

**Acceptance Criteria**:
- ✅ Completions ≤100ms (local) → 200-300ms (backend)
- ✅ Hover info appears
- ✅ Navigation (go to definition) works
- ✅ Graceful degradation

---

## MODULE 2: AI-Powered Refactoring

### Phase 2A: Refactoring Backend (Days 1-3)

#### Task 2.1: Extract Function Refactoring
```
File: backend/refactoring_service.py (new)
Lines: 300-400
Purpose: Extract selection into new function

Algorithm:
├─ Parse code using language server
├─ Identify selection range
├─ Extract AST nodes for selection
├─ Find free variables (used but not defined in selection)
├─ Create function signature with free variables as parameters
├─ Replace selection with function call
├─ Insert function definition above/below
├─ Handle scope correctly (local functions, class methods)
└─ Format code

Implementation:
---python
class RefactoringService:
    async def extract_function(
        self, 
        file_path: str, 
        start_pos: Tuple[int, int],  # line, col
        end_pos: Tuple[int, int],
        function_name: str,
        language: str
    ) -> Dict:
        """Extract code selection into function"""
        
        # 1. Get code
        code = read_file(file_path)
        
        # 2. Parse
        tree = parse_code(code, language)
        
        # 3. Find selected nodes
        selected_nodes = find_nodes_in_range(tree, start_pos, end_pos)
        
        # 4. Analyze free variables
        free_vars = find_free_variables(selected_nodes, tree)
        
        # 5. Generate function
        function_def = generate_function_def(
            name=function_name,
            params=free_vars,
            body=selected_nodes
        )
        
        # 6. Replace selection with call
        replacement = f"{function_name}({', '.join(free_vars)})"
        
        # 7. Apply changes
        new_code = apply_edit(code, start_pos, end_pos, replacement)
        new_code = insert_function(new_code, function_def)
        
        # 8. Format
        new_code = format_code(new_code, language)
        
        return {
            "old_code": code,
            "new_code": new_code,
            "function_def": function_def,
            "changes": [...]  # for diffs
        }
---

Tests:
├─ Simple variable assignment → parameter
├─ Multiple lines → multi-line function body
├─ Return value handling
├─ Local function nesting
└─ Performance: <200ms for typical selection
```

**Acceptance Criteria**:
- ✅ Extract function works for selections
- ✅ Free variables detected correctly
- ✅ Code formatted properly
- ✅ Diff shows changes

---

#### Task 2.2: Rename Symbol Refactoring
```
File: backend/refactoring_service.py (extend)
Lines: Add 150-200 lines
Purpose: Rename variable/function/class across workspace

Implementation:
├─ Use language server's textDocument/rename
├─ Find ALL references (already implemented in LS)
├─ Generate edits for all occurrences
├─ Return multi-file changes
└─ Client applies all changes atomically

Key Feature:
└─ Scope-aware (local var doesn't collide with global)
```

**Acceptance Criteria**:
- ✅ Finds all references
- ✅ Renames only correct scope
- ✅ Updates all files
- ✅ Handles edge cases (comments, strings)

---

#### Task 2.3: Move to File Refactoring
```
File: backend/refactoring_service.py (extend)
Lines: Add 100-150 lines
Purpose: Move function/class to different file

Implementation:
├─ Extract function/class code
├─ Create/update target file
├─ Add imports to source file
├─ Remove from source file
├─ Format both files
└─ Return multi-file changes
```

**Acceptance Criteria**:
- ✅ Moves code correctly
- ✅ Imports added to source
- ✅ Target file created if needed
- ✅ Both files formatted

---

### Phase 2B: Refactoring UI (Days 3-5)

#### Task 2.4: Refactoring Command Palette
```
File: frontend/components/RefactoringPalette.tsx (new)
Lines: 300-400
Purpose: UI for triggering refactorings

Features:
├─ Right-click menu on selection:
│  ├─ "Extract Function"
│  ├─ "Extract Variable"
│  ├─ "Move to File"
│  └─ (more as implemented)
│
├─ Keyboard shortcuts:
│  ├─ Ctrl+Shift+E: Extract Function
│  ├─ Ctrl+Shift+V: Extract Variable
│  ├─ Ctrl+Shift+M: Move to File
│  └─ F2: Rename (when cursor on symbol)
│
├─ Dialog for each refactoring:
│  ├─ Show preview (side-by-side diff)
│  ├─ Input fields (function name, new name, etc)
│  ├─ Confirmation button
│  └─ Undo support
│
└─ Error handling:
   ├─ Invalid selection → error message
   ├─ Refactoring failed → show error
   └─ Offline → show message

UX:
├─ Show spinner while calculating
├─ Display diff before applying
├─ Allow cancellation
└─ Show notification on success
```

**Acceptance Criteria**:
- ✅ Right-click menu works
- ✅ Dialog displays correctly
- ✅ Preview shows before/after code
- ✅ Can confirm/cancel

---

#### Task 2.5: Diff Viewer Integration
```
File: frontend/components/DiffViewer.tsx (update if exists, or new)
Lines: 100-200
Purpose: Show before/after code changes

Display:
├─ Left: Original code (red highlights for deletions)
├─ Right: New code (green highlights for additions)
├─ Line numbers
├─ Side-by-side or unified view
└─ "Apply" / "Cancel" buttons

Tests:
├─ Shows correct diffs
├─ Highlighting correct
├─ Apply button works
```

**Acceptance Criteria**:
- ✅ Diff displays clearly
- ✅ Line highlighting correct
- ✅ Apply button applies changes

---

## Integration Testing

### Test Matrix (Run After Each Task)

```
┌─────────────────────────────────────────┐
│ Task              │ Unit Test │ E2E Test│
├─────────────────────────────────────────┤
│ 1.1 Web Worker    │ ✅        │ ✅      │
│ 1.2 Parser        │ ✅        │ ✅      │
│ 1.3 IntelliSense  │ ✅        │ ✅      │
│ 1.4 UI Popup      │ ✅        │ ✅      │
│ 1.5 TS Server     │ ✅        │ ✅      │
│ 1.6 Python Server │ ✅        │ ✅      │
│ 1.7 API Routes    │ ✅        │ ✅      │
│ 1.8 Integration   │ ✅        │ ✅      │
│ 2.1 Extract Func  │ ✅        │ ✅      │
│ 2.2 Rename Symbol │ ✅        │ ✅      │
│ 2.3 Move to File  │ ✅        │ ✅      │
│ 2.4 UI Commands   │ ✅        │ ✅      │
│ 2.5 Diff Viewer   │ ✅        │ ✅      │
└─────────────────────────────────────────┘
```

---

## Definition of Done (DoD)

### For Each Task
- [ ] Code written + reviewed
- [ ] Unit tests pass (>80% coverage)
- [ ] E2E tests pass
- [ ] No console errors/warnings
- [ ] Performance meets requirements
- [ ] Documentation updated
- [ ] PR approved + merged

### For Week 1 Overall
- [ ] All 13 tasks completed
- [ ] Combined feature works end-to-end
- [ ] User can:
  - [ ] Type and see completions ≤100ms
  - [ ] See hover documentation
  - [ ] Go to definition
  - [ ] Extract function from selection
  - [ ] Rename symbol globally
  - [ ] Preview refactoring diff
- [ ] Performance metrics met
- [ ] 0 critical bugs

---

## Team Assignments (3-person team)

### Person A: IntelliSense Backend
- Tasks: 1.1, 1.5, 1.6, 1.7
- Skill: Python, Language Servers, LSP protocol
- Timeline: Days 1-4 (staggered)

### Person B: IntelliSense Frontend
- Tasks: 1.2, 1.3, 1.4, 1.8
- Skill: React, TypeScript, Web Workers
- Timeline: Days 1-5 (parallel with A)

### Person C: Refactoring
- Tasks: 2.1, 2.2, 2.3, 2.4, 2.5
- Skill: AST manipulation, Python, React
- Timeline: Days 2-5 (after 1.7 complete)

### Handoffs
- Day 2 (EOD): Person A completes 1.5/1.6 → Person C uses
- Day 4 (EOD): Persons A+B complete 1.7 → Person C uses

---

## Success Metrics (End of Week)

### Technical
| Metric | Target | Pass/Fail |
|--------|--------|-----------|
| Completion latency | ≤100ms | ✅/❌ |
| Completion accuracy | 90%+ | ✅/❌ |
| Hover working | 100% | ✅/❌ |
| Refactoring count | 3+ | ✅/❌ |
| Test coverage | >80% | ✅/❌ |
| Zero critical bugs | 100% | ✅/❌ |

### User Perception (Optional: gather from beta users)
| Metric | Target | Pass/Fail |
|--------|--------|-----------|
| Faster than before | 2x+ | ✅/❌ |
| Feature complete | Parity with VS Code | ✅/❌ |
| No regressions | 0 new bugs | ✅/❌ |

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Language server crashes | Medium | High | Implement graceful fallback to local parser |
| Performance regression | Medium | High | Run performance tests daily |
| Multi-file refactoring bugs | Medium | Medium | Extra testing on complex projects |
| Browser memory issues | Low | Medium | Implement garbage collection in Web Worker |

---

## Rollout Plan

### Week 2 (After development)
- [ ] Internal dogfooding (use new features daily)
- [ ] Beta user testing (subset of power users)
- [ ] Performance profiling in production
- [ ] Bug fixes
- [ ] Documentation + video tutorials

### Week 3
- [ ] Public release on main branch
- [ ] Product announcement
- [ ] Video: "Top Dog now faster than VS Code"

---

## Resources

### Required Dependencies
```json
{
  "acorn": "^8.0.0",              // JS parser
  "@babel/parser": "^7.0.0",       // JSX/TS parser
  "web-tree-sitter": "^0.20.0",    // Fast parsing
  "yjs": "^13.0.0",                // CRDT (for later)
  "typescript-language-server": "^3.0.0",
  "pyright": "^1.1.0"              // Python LSP
}
```

### Documentation
- [LSP Specification](https://microsoft.github.io/language-server-protocol/)
- [TypeScript Language Server](https://github.com/typescript-language-server/typescript-language-server)
- [Pyright Documentation](https://github.com/microsoft/pyright)

---

## Sign-Off

- **Product Lead**: ____________ (Approve timelines?)
- **Tech Lead**: ____________ (Approve architecture?)
- **QA Lead**: ____________ (Define test plan?)
- **DevOps**: ____________ (Ready for deployment?)

---

**Version**: 1.0  
**Date**: October 29, 2025  
**Status**: Ready for Development ✅

