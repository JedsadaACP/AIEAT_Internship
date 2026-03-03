---
name: verification-checklist
description: Verification steps before marking work complete
---

# Verification Checklist Skill

## Before Marking Any Task Complete

### 1. Syntax Verification
```bash
# Always run after editing Python files
python -m py_compile <modified_file.py>
```

### 2. Import Check
```python
# Verify all imports work
python -c "from app.ui.pages.dashboard import DashboardPage"
```

### 3. Quick App Test
```bash
# Launch and verify UI renders
python run_ui.py
```

## After UI Changes

- [ ] Launch the app and verify visually
- [ ] Test the changed functionality
- [ ] Check console for errors/warnings
- [ ] Test edge cases (empty data, long text)

## After Database Changes

- [ ] Backup database before schema changes
- [ ] Run migration script if applicable
- [ ] Verify data integrity after migration
- [ ] Test CRUD operations

## After API/Backend Changes

- [ ] Test with valid inputs
- [ ] Test with invalid inputs
- [ ] Check error handling
- [ ] Verify response format

## After Bug Fixes

- [ ] Reproduce original bug - confirm it's fixed
- [ ] Test related functionality for regression
- [ ] Update `SESSION_HANDOFF.md` status
- [ ] Document the fix (what, why, how)

## Code Review Checklist

- [ ] No hardcoded values (use constants/config)
- [ ] Error handling present
- [ ] Logging for debugging
- [ ] Comments for non-obvious code
- [ ] No TODO comments left unresolved

## Final Steps

1. Update task status in conversation
2. Update `SESSION_HANDOFF.md` if issue is resolved
3. Notify user via `notify_user` tool
