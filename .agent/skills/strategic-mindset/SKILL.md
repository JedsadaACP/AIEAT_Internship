---
name: strategic-mindset
description: Core principles for high-level reasoning, planning, and efficient problem solving
---

# Strategic Mindset Skill

> **"Don't just write code. Solve the right problem."**

This skill embodies the high-level reasoning capabilities defined in the Antigravity Rules. Use this when planning features, debugging complex issues, or optimizing performance.

## 🧠 Core Principles

### 1. Systematic Reasoning (The "Strong Reasoner")
**Before writing a single line of code:**
1.  **Restate the Goal**: What comes out? (e.g., "User sees translation in <2s")
2.  **Identify Constraints**: What can't change? (e.g., "Must be on localhost")
3.  **Trace the Flow**: Follow data from start to finish *mentally* first.
4.  **Check Assumptions**: "Is the API actually returning JSON?"

### 2. Efficiency First (Performance Agent)
**Don't build slow software.**
- **Measure**: Where is time spent? (Network? CPU? Rendering?)
- **Optimize**:
    - **Caching**: Don't fetch twice.
    - **Concurrency**: Don't block the main thread (CRITICAL for Flet).
    - **Data Size**: Don't request fields you don't need.

### 3. User Experience (UX) Focus
**Code is for humans.**
- **Responsiveness**: UI must *never* freeze. Use Async.
- **Feedback**: Always show loading states for >200ms ops.
- **Resilience**: Handle errors gracefully (Retries, Fallbacks).
- **Clarity**: Button text should say *what it does* (not just "Submit").

### 4. Rigorous Debugging (Systematic Bug Hunter)
**Don't guess.**
1.  **Reproduce**: Can you make it fail on demand?
2.  **Isolate**: Remove variables until only the bug remains.
3.  **Fix Root Cause**: Don't patch the symptom.
    - *Symptom*: "UI freezes."
    - *Patch*: "Add `sleep(0.1)`" (WRONG)
    - *Root Cause*: "Blocking call on main thread."
    - *Fix*: "Move to off-thread async task." (RIGHT)

## 🛑 Strategic Anti-Patterns

- **"Shotgun Debugging"**: Randomly changing code hoping it works.
- **"Premature Optimization"**: optimizing a loop when the DB call takes 3s.
- **"Ignoring the user"**: Building a feature that is technically cool but unusable.
- **"Context Explosion"**: Trying to fix everything at once. Focus on one critical path.

## 🔄 Workflow for Every Task

1.  **Plan**: Write down the steps.
2.  **Verify Plan**: Does this actually solve the user's *real* problem?
3.  **Execute**: Write clean, testable code.
4.  **Verify Result**: Does the app behave as expected?

---
*Derived from Antigravity Rules: Strong Reasoner, Debugging Agent, Performance Agent.*
