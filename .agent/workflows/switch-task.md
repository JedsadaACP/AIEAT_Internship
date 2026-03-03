---
description: Switch between tasks or start a new one
---

# Switch Task Workflow

Use this when you want to change what you're working on.

## Steps

1. **Read Current Context**
   - Read `SESSION_HANDOFF.md` for current priorities
   - Note any active issues or blockers

2. **Ask What To Work On**
   Present the user with current options from SESSION_HANDOFF.md and ask which task they want to focus on.

3. **Load Relevant Skills**
   Based on the chosen task:
   - Bug fixing → `.agent/skills/systematic-debugging/SKILL.md`
   - UI changes → `.agent/skills/flet-ui-patterns/SKILL.md`
   - Database work → `.agent/skills/database-patterns/SKILL.md`
   - Fine-tuning → Read `AIEAT_QLoRA_Training.ipynb`

4. **Start Working**
   Begin the chosen task with full context loaded.
