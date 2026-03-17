# MAR 14 - MULTI-LLM SESSION HANDOFF 

**To: Co-Supervisor (5.3 Codex)**
**To: Worker (MINI M2.5)**
**From: Supervisor 1**

Welcome to the **Mar 14 Polish Sprint** for AIEAT v1.0.0. 

AIEAT is a local-first news intelligence dashboard built on Python, Flet UI, SQLite, and the Ollama AI engine (Typhoon 2.5). We are preparing to publish the v1.0.0 open-source release on March 18.

Here is the exact state of the project and the strict rules you must follow.

---

## 🛑 STRICT RULES (from `AGENTS.md`)
1. **Python 3.10+** with type hints required.
2. **Flet UI threading:** Use `page.run_task()` for async background work. **NEVER** use raw `threading.Thread` + `page.update()`.
3. **Never** use `api/generate` for Typhoon -> use `api/chat`.
4. **Never** assume `published_at` exists -> Use `COALESCE()` in SQL.
5. **No Laziness:** Find root causes. No temporary fixes.
6. **Zero Context Switching:** Don't ask the user for hand-holding. If fixing a bug, point at the logs, find it, and fix it.
7. **Verification:** Do not mark tasks complete without proving it works. Run `python -m py_compile <file.py>` on EVERY file you edit.

---

## 🧑‍💼 CO-SUPERVISOR (5.3 CODEX) BRIEFING
**Your Role:** We are peers. We DO NOT write code. 
- You must review the Worker LLM's changes against the strict rules above.
- Specifically guard against `threading.Thread` regressions and ensure the Flet UI does not freeze during heavy AI scoring tasks.
- Do not let the Worker touch files outside of the defined scope below.

---

## 🛠 WORKER (MINI M2.5) BRIEFING
**Your Role:** You are the execution engine.
- You will write the code. 
- You must write a summary of your changes before editing.
- After editing, you must compile your `.py` files to check for syntax errors before reporting back to the Supervisors.

### TODAY'S TARGET: The Mar 14 "Polish Sprint" Checklist
You must execute the following tasks. They are also located in `tasks/todo.md`. 
Wait for explicit permission from the user or supervisors before starting.

**PHASE 1: Debug Code Purge & Root Cleanup**
- [ ] Remove 5 debug prints from `app/ui/components/sources_dialog.py`
- [ ] Remove 4 batch debug prints from `app/services/backend_api.py` 
- [ ] Convert 6 prints to `logger` events across `dashboard.py`, `config.py`, `main.py`, and `prompt_builder.py`.
- [ ] Remove "Logs" nav button from `app/ui/components/sidebar.py`.
- [ ] Run `python -m py_compile` on all edited files.
- [ ] Delete all throwaway root files (`check_*.py`, `test_*.py`, local `.txt` outputs).

**PHASE 2: Threading & UI Polish**
- [ ] **CRITICAL:** In `app/ui/main.py`, replace `threading.Thread(target=self.api.preload_model)` with Flet's async `page.run_task()`.
- [ ] Add a non-blocking snackbar warning on app startup if the Ollama engine is offline.

**PHASE 3: GitHub & Release Prep**
- [ ] Add `LICENSE` file (MIT).
- [ ] Update `README.md` to version 1.0.0.
- [ ] Clean up build folders (`dist/`, `build/`).

---

**Supervisors**, please acknowledge these parameters.
**Worker**, please stand by for the user's command to begin Phase 1.
