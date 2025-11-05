# 🎯 QUICK REFERENCE CARD (Print & Stick to Monitor)

**Top Dog 90-Day Sprint** | **Weeks 1-2: IntelliSense + Refactoring** | **Nov 3-7, 2025**

---

## THIS WEEK'S GOAL

🎯 **Ship IntelliSense v0.1 + Refactoring v0.1 by Friday**

- User types code → sees smart completions in ≤100ms ✅
- User selects → code is inserted correctly ✅
- User wants to refactor → extract/rename/move works ✅

---

## YOUR ROLE

### BACKEND ENGINEER
**Tasks**: Parser, Language Servers, Refactoring Engine  
**Files**: 
```
backend/services/intellisense/parser.py
backend/services/intellisense_service.py
backend/services/typescript_language_server.py
backend/services/python_language_server.py
backend/services/refactoring/extract_function.py
backend/services/refactoring/rename_symbol.py
backend/services/refactoring/move_to_file.py
backend/api/v1/intellisense.py
```
**Lines**: ~1,500  
**Timeline**: Mon-Fri (complete by 5 PM Fri)

### FRONTEND ENGINEER
**Tasks**: IntelliSense UI, Refactoring UI  
**Files**:
```
frontend/src/components/IntelliSenseUI.tsx
frontend/src/services/completion-engine.ts
frontend/src/components/CommandPalette.tsx
frontend/src/components/DiffViewer.tsx
frontend/src/services/refactoring-client.ts
```
**Lines**: ~700  
**Timeline**: Mon-Fri (complete by 5 PM Fri)

### INTEGRATION ENGINEER
**Tasks**: Testing, Benchmarking, Deployment  
**Files**:
```
tests/unit/test_parser.py
tests/unit/test_intellisense.py
tests/e2e/test_intellisense_flow.py
tests/performance/benchmark_*.py
.github/workflows/test.yml
```
**Goal**: All tests passing, benchmarks captured  
**Timeline**: Mon-Fri (green by 5 PM Fri)

---

## DAILY STANDUP (3:30 PM)

**15 minutes. Everyone answers:**
1. "What did I complete yesterday?"
2. "What am I doing today?"
3. "Do I have blockers?"

**If blocker**: Escalate immediately (don't wait for standup)

---

## SUCCESS CRITERIA (Must All Be ✅)

### Technical
- ✅ Completions appear in ≤100ms
- ✅ Completions 90%+ accurate
- ✅ Refactoring works (extract, rename, move)
- ✅ All tests passing (0 failures)
- ✅ Performance baseline captured

### Code Quality
- ✅ Code reviewed by peer
- ✅ No console errors
- ✅ Acceptance criteria met
- ✅ PR merged to main

---

## KEY NUMBERS

| Metric | Target |
|--------|--------|
| IntelliSense response time | ≤100ms |
| Parser speed | <50ms |
| Accuracy | 90%+ |
| Test coverage | 80%+ |
| Lines of code | 2,450 |
| Tasks completed | 13/13 |
| Bugs in production | 0 |

---

## DEPENDENCIES (Who Needs to Finish First)

```
Monday:  Everyone starts (no dependencies)
Tuesday: Backend → Frontend gets data (need API)
         Frontend → Integration gets components
Wednesday: Frontend → Integration gets UI
Thursday: Backend → Integration gets all APIs
Friday 5 PM: MERGE & SHIP
```

---

## IF YOU GET STUCK

**Q: IntelliSense too slow?**
A: Check if parsing in Web Worker (should be). Benchmark with `time.time()`. Profile with DevTools.

**Q: Can't get Language Server working?**
A: Test in isolation first. Use `curl` to call backend. Verify response format.

**Q: Tests failing?**
A: Check logs in GitHub Actions. Run locally. Match CI environment.

**Q: Don't know what to code?**
A: Re-read WEEK_1_IMPLEMENTATION_CHECKLIST.md for your task. Pseudocode is there.

**Q: Need help NOW?**
A: Slack #intellisense-questions. Tech lead will respond in <30 min.

---

## THIS WEEK'S MILESTONES

| Day | Milestone | Owner |
|-----|-----------|-------|
| **Mon** | All tasks started | Everyone |
| **Tue** | Parser working | Backend |
| **Tue** | IntelliSense API responding | Backend |
| **Wed** | Frontend UI appears | Frontend |
| **Wed** | Refactoring logic working | Backend |
| **Thu** | Refactoring UI working | Frontend |
| **Thu** | All tests passing | Integration |
| **Fri 3 PM** | Demo to team | Everyone |
| **Fri 5 PM** | Merge to main | Everyone |

---

## RESOURCES

- **Task Details**: `WEEK_1_IMPLEMENTATION_CHECKLIST.md`
- **Why This Matters**: `Q-IDE_REAL_GAP_ANALYSIS_VS_COMPETITORS.md`
- **Strategic Context**: `START_HERE_YOUR_90_DAY_PLAN.md`
- **Slack**: #Top Dog-sprint-week-1
- **GitHub**: See issues linked to Epic "IntelliSense + Refactoring MVP"

---

## TOOLS YOU'LL USE

```
Backend:
├─ Python 3.10+
├─ FastAPI (already running)
├─ tree-sitter (AST parsing)
├─ pytest (testing)
└─ curl/Postman (API testing)

Frontend:
├─ React 18 + TypeScript
├─ Monaco Editor (already in place)
├─ Web Workers (new)
├─ Jest (testing)
└─ Chrome DevTools (performance)

DevOps:
├─ GitHub Actions (CI/CD)
├─ Docker (local testing)
├─ Grafana (metrics)
└─ Postman (collection testing)
```

---

## DAILY CHECKLIST

### MORNING (Before Code)
- [ ] Pull latest code (`git pull`)
- [ ] Create task branch (`git checkout -b feature/task-1-X`)
- [ ] Read today's checklist item
- [ ] Verify build runs (`npm start` or `uvicorn main:app`)

### DURING CODE
- [ ] Write code (60-90% of the day)
- [ ] Run tests often (`pytest`, `npm test`)
- [ ] Commit every hour (`git commit -m "Progress on task X"`)
- [ ] Ask for help if stuck >30 min

### AFTERNOON (Before Standup)
- [ ] Run full test suite
- [ ] Verify no console errors
- [ ] Update GitHub issue with status
- [ ] Prepare standup notes

### STANDUP (3:30 PM)
- [ ] Tell team what you did + what you're doing next
- [ ] If blocker, escalate now

---

## CODE QUALITY CHECKLIST (Before PR)

- [ ] Code compiles/runs without errors
- [ ] Tests passing locally (`pytest` / `npm test`)
- [ ] Performance acceptable (benchmark if needed)
- [ ] Code reviewed by 1 peer
- [ ] No console errors or warnings
- [ ] Git commit message is clear
- [ ] PR title matches issue title
- [ ] PR linked to GitHub issue
- [ ] Documentation updated (if needed)
- [ ] Ready to merge!

---

## FRIDAY REVIEW (5 PM)

**Demo to the team:**
- Backend: "Here's the API response" (Postman/curl demo)
- Frontend: "Here's the UI working" (live in browser)
- Integration: "Here are the metrics" (performance baseline)

**Then**: Merge to main, celebrate, start Week 2

---

## REMINDERS

🚀 **You're not alone.** Tech lead is available. Ask for help.  
⏰ **Time is precious.** Every day counts. Focus.  
✅ **Done is better than perfect.** Ship it Friday.  
💪 **You can do this.** You have the plan. You have the skills. Execute.

---

**FINAL REMINDER**

Next Friday, Nov 7, users will use Top Dog's new IntelliSense and Refactoring.

Make them say: **"Wow, this is actually good."**

---

**Print this. Stick to monitor. Reference daily.** 📌

🚀 **Let's ship it.** 🚀

---

Version 1.0 | October 29, 2025 | One Week to Change Everything
