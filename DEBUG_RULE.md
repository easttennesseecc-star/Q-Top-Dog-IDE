# 3-Step Debugging Rule

This is the mandatory debugging protocol for all code fixes and problem-solving in this project.

## The 3 Steps

### Step 1: Take a Step Back & Assess the Wider Problem
- **Action**: Read the full context of the problem before making changes
- **Goal**: Understand the root cause, not just symptoms
- **Implementation**:
  - Read relevant file sections to understand current state
  - Check error messages and build output
  - Identify all related issues, not just the first one
  - Document what's actually broken vs. what appears broken

### Step 2: Come Up with the Best Possible Fix
- **Action**: Plan the complete solution before applying ANY changes
- **Goal**: Avoid cascading failures from incomplete or improper fixes
- **Implementation**:
  - Design the fix that addresses root cause
  - If multiple issues exist, create a comprehensive fix strategy
  - Use multi_replace_string_in_file when fixing multiple locations
  - Include 3-5 lines of context before/after changes for uniqueness
  - Never make incremental fixes that could cause new problems

### Step 3: Apply the Fix & Verify It Fixed the Problem
- **Action**: Execute the fix and immediately test
- **Goal**: Confirm the fix actually works and doesn't introduce new issues
- **Implementation**:
  - Apply all changes (using multi_replace for efficiency)
  - Run the build/test command immediately
  - Verify 0 errors in the specific area fixed
  - Test functionality related to the fix
  - Document what was fixed

## Why This Rule Exists

Previous attempts to fix App.tsx failed repeatedly because:
1. Changes were made without understanding the full scope of problems
2. Fixes were applied incrementally, causing cascading failures
3. No verification step was done between changes
4. File got corrupted with mixed old/new code

## When to Apply This Rule

**ALWAYS** - Every single code fix must follow these 3 steps, no exceptions.

## Example Application

### BAD (violates rule):
```
- See error on line 121
- Replace that line immediately
- See new error on line 200
- Replace that
- See another error
- (infinite loop of failures)
```

### GOOD (follows rule):
```
Step 1: Read entire file, identify ALL issues
        - Line 121: missing emoji in button
        - Line 122: missing emoji in button
        - Line 168: missing dynamic {i} in text
        - (3 separate issues identified)

Step 2: Create fix for all 3 issues
        - Plan 3 replacements with full context
        - Prepare multi_replace_string_in_file call

Step 3: Apply all fixes at once, then build & verify
        - npm run build → 0 errors
        - Visual check: emojis present, dynamic text works
```

## Reference This When Uncertain

If any fix is being attempted without fully following all 3 steps, **stop and refer back to this rule**.
