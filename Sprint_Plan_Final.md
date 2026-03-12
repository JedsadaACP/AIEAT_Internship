# AIEAT V1.0.0 — Definitive Plan (Tonight → Open Source Publish)

**Created:** Mar 13, 2026 00:46 AM | **Hard deadline:** Mar 18

> This document is the **single source of truth** for all remaining work.
> Every Worker LLM prompt should reference this plan.

---

## Status Snapshot (What Is Already Done)

| Item | Status |
|------|--------|
| Article Profile Silos (backend + UI) | ✅ Complete |
| Progress bar thread-safe fix | ✅ Complete |
| Dashboard cache clear on profile switch | ✅ Complete |
| [build_app.spec](file:///c:/Users/pechj/Desktop/AIEAT_Internship/build_app.spec) verified | ✅ Complete |
| [installer.iss](file:///c:/Users/pechj/Desktop/AIEAT_Internship/installer.iss) with Ollama checkbox | ✅ Complete |
| [AIEAT_Setup.exe](file:///c:/Users/pechj/Desktop/AIEAT_Internship/installer_output/AIEAT_Setup.exe) built | ✅ Complete |
| [User_Manual.md](file:///C:/Users/pechj/.gemini/antigravity/brain/a5d0abd9-dc67-4a9c-a0cb-0ae4399346ad/User_Manual.md) drafted + polished | ✅ Complete |
| Presentation script + slide bullets | ✅ Complete |
| [Worker_Debug_Purge.md](file:///C:/Users/pechj/.gemini/antigravity/brain/a5d0abd9-dc67-4a9c-a0cb-0ae4399346ad/Worker_Debug_Purge.md) ready | ✅ Ready to execute |

---

## 🌙 Tonight — Mar 12→13 (Hard stop 3:00 AM)

**Rule: No code changes tonight. Presentation readiness only.**

### 1. Archive workspace (30 min)
- [ ] Create `archive/2026-03-13/`
- [ ] Move into archive: [build/](file:///c:/Users/pechj/Desktop/AIEAT_Internship/app/ui/pages/profiles.py#18-50), `dist/`, `installer_output/`, `installer_output - Copy/`, `AIEAT.exe_extracted/`, `AIEAT_Backup/`, [AIEAT_Distribution.zip](file:///c:/Users/pechj/Desktop/AIEAT_Internship/AIEAT_Distribution.zip)
- [ ] Keep in root: [installer.iss](file:///c:/Users/pechj/Desktop/AIEAT_Internship/installer.iss), [build_app.spec](file:///c:/Users/pechj/Desktop/AIEAT_Internship/build_app.spec), [README.md](file:///c:/Users/pechj/Desktop/AIEAT_Internship/README.md), [User_Manual.md](file:///C:/Users/pechj/.gemini/antigravity/brain/a5d0abd9-dc67-4a9c-a0cb-0ae4399346ad/User_Manual.md), [QuickStart_Guide.md](file:///c:/Users/pechj/Desktop/AIEAT_Internship/QuickStart_Guide.md), [Install_AI_Engine.bat](file:///c:/Users/pechj/Desktop/AIEAT_Internship/Install_AI_Engine.bat), [app/](file:///c:/Users/pechj/Desktop/AIEAT_Internship/app/ui/pages/dashboard.py#454-462), `data/`

### 2. Copy User Manual to project root (2 min)
- [ ] Copy [User_Manual.md](file:///C:/Users/pechj/.gemini/antigravity/brain/a5d0abd9-dc67-4a9c-a0cb-0ae4399346ad/User_Manual.md) from brain artifact dir → project root
- [ ] Visual sanity check: open it, confirm steps match the UI

### 3. Demo smoke run (30–40 min)
- [ ] Launch app (`python run_ui.py`)
- [ ] Switch profile (verify dashboard clears + reloads)
- [ ] Add a source in User Config → News Sources
- [ ] Set keywords, run scraper, verify progress bar animates
- [ ] Batch Score → filter "High Relevance (5+)" → open detail → Translate
- [ ] Note any UI mismatches for tomorrow's polish

### 4. Presentation prep (10 min — script already written)
- [ ] Review the talking script (already drafted)
- [ ] Prepare 3 bullets: Profile Silos, Installer + Ollama, User Manual

### 5. Buffer (10–20 min)
- [ ] Capture any smoke test notes in `tasks/todo.md`
- [ ] Optional: take a screenshot for slides

---

## 📊 Mar 13 (Thu) — Weekly Presentation

### Demo flow:
1. Profile switching → Dashboard updates
2. Scraper → progress bar animates
3. Show installer wizard with Ollama checkbox
4. Show [User_Manual.md](file:///C:/Users/pechj/.gemini/antigravity/brain/a5d0abd9-dc67-4a9c-a0cb-0ae4399346ad/User_Manual.md)

### Script:
> "This week I completed the Article Profile Silos feature, fixed the installer to include optional Ollama AI installation, and wrote a scenario-based User Manual for end users."

### After presentation:
- [ ] Log any supervisor feedback in `tasks/feedback.md`

---

## 🔧 Mar 14 (Fri) — Polish Sprint

### Morning: Debug Code Purge (Worker LLM — use [Worker_Debug_Purge.md](file:///C:/Users/pechj/.gemini/antigravity/brain/a5d0abd9-dc67-4a9c-a0cb-0ae4399346ad/Worker_Debug_Purge.md))

**File: [sources_dialog.py](file:///c:/Users/pechj/Desktop/AIEAT_Internship/app/ui/components/sources_dialog.py)** — DELETE 5 debug prints:
- [ ] Line ~212: `print("Import CSV clicked")`
- [ ] Line ~217: `print("Remove duplicates clicked")`
- [ ] Line ~222: `print("Add source clicked")`
- [ ] Line ~226: `print(f"Check source: ...")`
- [ ] Line ~230: `print(f"Remove source: ...")`

**File: [backend_api.py](file:///c:/Users/pechj/Desktop/AIEAT_Internship/app/services/backend_api.py)** — DELETE 4 batch debug prints:
- [ ] Line ~510: `print(f"\n=== BATCH PROCESS START ===")`
- [ ] Line ~511: `print(f"Action: ...")`
- [ ] Line ~512: `print(f"Target Status: ...")`
- [ ] Line ~523: `print(f"Found {total} articles...")`

**File: [dashboard.py](file:///c:/Users/pechj/Desktop/AIEAT_Internship/app/ui/pages/dashboard.py)** — CONVERT 3 prints → logger:
- [ ] Line 773: `print(f"Loop Error: {loop_e}")` → `logger.error(f"Loop Error: {loop_e}")`
- [ ] Line 777: `print(f"Batch Error: {e}")` → `logger.error(f"Batch Error: {e}")`
- [ ] Line 792: `print(f"Safe update failed...")` → `logger.debug(f"Safe update failed: {e}")`

**File: [config.py](file:///c:/Users/pechj/Desktop/AIEAT_Internship/app/ui/pages/config.py)** — CONVERT 1 print → logger:
- [ ] Line 914: `print(f"DEBUG: Save error: {e}")` → `logger.error(f"Save error: {e}")`

**File: [main.py](file:///c:/Users/pechj/Desktop/AIEAT_Internship/app/ui/main.py)** — CONVERT 1 print → logger:
- [ ] Line 156: `print(f"Style refresh error: {e}")` → `logger.warning(f"Style refresh error: {e}")`

**File: [prompt_builder.py](file:///c:/Users/pechj/Desktop/AIEAT_Internship/app/services/prompt_builder.py)** — CONVERT 1 print → logger:
- [ ] Line 187: `print(f"Parser Error: {e}")` → `logger.error(f"Parser Error: {e}")`

**File: [sidebar.py](file:///c:/Users/pechj/Desktop/AIEAT_Internship/app/ui/components/sidebar.py)** — REMOVE unfinished Log page:
- [ ] Delete the "Logs" nav button (lines ~157-160)

**Verification:** `python -m py_compile` on every edited file.

### Morning: Delete throwaway files from root
- [ ] [check_db_stats.py](file:///c:/Users/pechj/Desktop/AIEAT_Internship/check_db_stats.py)
- [ ] [check_tags.py](file:///C:/Users/pechj/Desktop/AIEAT_Internship/check_tags.py)
- [ ] [quick_test.py](file:///c:/Users/pechj/Desktop/AIEAT_Internship/quick_test.py)
- [ ] [test_models.py](file:///c:/Users/pechj/Desktop/AIEAT_Internship/test_models.py)
- [ ] [test_ollama.py](file:///c:/Users/pechj/Desktop/AIEAT_Internship/test_ollama.py)
- [ ] [nul](file:///c:/Users/pechj/Desktop/AIEAT_Internship/nul)
- [ ] [implementation_plan.md.resolved](file:///c:/Users/pechj/Desktop/AIEAT_Internship/implementation_plan.md.resolved)
- [ ] [task.md.resolved](file:///c:/Users/pechj/Desktop/AIEAT_Internship/task.md.resolved)
- [ ] [task_final_sprint.md](file:///c:/Users/pechj/Desktop/AIEAT_Internship/task_final_sprint.md)
- [ ] All `*_scb10x_*.txt` and `*_translategemma_*.txt` files
- [ ] [sources.csv](file:///c:/Users/pechj/Desktop/AIEAT_Internship/sources.csv)

### Afternoon: Fix `threading.Thread` in [main.py](file:///c:/Users/pechj/Desktop/AIEAT_Internship/app/ui/main.py)
- [ ] Line 39-41: Replace `threading.Thread(target=self.api.preload_model)` with a proper `page.run_task()` async call
- [ ] Add Ollama offline startup snackbar (non-blocking warning if Ollama is not running)

### Afternoon: GitHub Cleanup
- [ ] Fix [.gitignore](file:///c:/Users/pechj/Desktop/AIEAT_Internship/.gitignore):
  - Remove line 115 ([HANDOFF.md](file:///c:/Users/pechj/Desktop/AIEAT_Internship/HANDOFF.md) — should be public)
  - Remove duplicate [AGENTS.md](file:///c:/Users/pechj/Desktop/AIEAT_Internship/AGENTS.md) entries (lines 116, 118, 120)
  - Remove stale entries for deleted files
- [ ] Add `LICENSE` file (MIT, your full name, 2026)
- [ ] Update [README.md](file:///c:/Users/pechj/Desktop/AIEAT_Internship/README.md):
  - Add "Profiles" to features list
  - Update version to `1.0.0`
  - Add installation section pointing to GitHub Releases

### Evening: Final Rebuild
- [ ] `rmdir /s /q build dist`
- [ ] `python -m PyInstaller build_app.spec --clean`
- [ ] `"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss`
- [ ] Smoke test: install on clean path → profile switch → scrape → score → translate
- [ ] Git commit all changes
- [ ] Git push

---

## 📬 Mar 15 (Sat) — Ship to Testers

- [ ] Package: [AIEAT_Setup.exe](file:///c:/Users/pechj/Desktop/AIEAT_Internship/installer_output/AIEAT_Setup.exe) + [User_Manual.md](file:///C:/Users/pechj/.gemini/antigravity/brain/a5d0abd9-dc67-4a9c-a0cb-0ae4399346ad/User_Manual.md) + [QuickStart_Guide.md](file:///c:/Users/pechj/Desktop/AIEAT_Internship/QuickStart_Guide.md) + [Install_AI_Engine.bat](file:///c:/Users/pechj/Desktop/AIEAT_Internship/Install_AI_Engine.bat) → zip
- [ ] Upload zip to Google Drive / OneDrive
- [ ] Send link to supervisor + testers
- [ ] Create `tasks/feedback.md` to log all feedback

### Likely feedback to prep for:
| Area | Probable Issue |
|------|---------------|
| AI scoring | Scores seem random / not relevant |
| Sources | Need more default sources per profile |
| UI | Text too small / dark mode readability |
| Manual | Too technical for non-dev users |

---

## 🛠 Mar 16–17 (Sun–Mon) — Feedback Fixes

- [ ] Triage feedback: Critical (data bugs) > UX > Cosmetic
- [ ] Fix critical bugs reported by testers
- [ ] Update [User_Manual.md](file:///C:/Users/pechj/.gemini/antigravity/brain/a5d0abd9-dc67-4a9c-a0cb-0ae4399346ad/User_Manual.md) based on tester confusion points
- [ ] Update [HANDOFF.md](file:///c:/Users/pechj/Desktop/AIEAT_Internship/HANDOFF.md) with known limitations + V2 ideas
- [ ] Rebuild installer if code changed
- [ ] Re-test smoke run after fixes

---

## 🎯 Mar 18 (Tue) — Final Handout + Open Source Publish

### Final build:
- [ ] Clean rebuild: PyInstaller + InnoSetup
- [ ] Final smoke test

### GitHub Release:
- [ ] `git add -A && git commit -m "v1.0.0: AIEAT News Dashboard"`
- [ ] `git tag v1.0.0`
- [ ] `git push && git push --tags`
- [ ] Go to GitHub → Releases → Draft new release
- [ ] Select tag `v1.0.0`
- [ ] Upload [AIEAT_Setup.exe](file:///c:/Users/pechj/Desktop/AIEAT_Internship/installer_output/AIEAT_Setup.exe) as binary asset
- [ ] Write release notes:
  > **AIEAT News Dashboard v1.0.0**
  > - Multi-profile article silos (Finance, Tech, etc.)
  > - AI relevance scoring via local Typhoon 2.5
  > - Thai translation
  > - Optional Ollama + model install during setup
  > - 74+ configurable news sources

### Final deliverables checklist:
- [ ] [AIEAT_Setup.exe](file:///c:/Users/pechj/Desktop/AIEAT_Internship/installer_output/AIEAT_Setup.exe) (final build)
- [ ] [User_Manual.md](file:///C:/Users/pechj/.gemini/antigravity/brain/a5d0abd9-dc67-4a9c-a0cb-0ae4399346ad/User_Manual.md) (reviewed + polished)
- [ ] [QuickStart_Guide.md](file:///c:/Users/pechj/Desktop/AIEAT_Internship/QuickStart_Guide.md)
- [ ] [HANDOFF.md](file:///c:/Users/pechj/Desktop/AIEAT_Internship/HANDOFF.md) (architecture + known limits + V2 ideas)
- [ ] [CONTRIBUTING.md](file:///c:/Users/pechj/Desktop/AIEAT_Internship/CONTRIBUTING.md)
- [ ] [README.md](file:///c:/Users/pechj/Desktop/AIEAT_Internship/README.md) (updated)
- [ ] `LICENSE` (MIT)
- [ ] GitHub repo — public, tagged `v1.0.0`, with Release page

### Presentation talking points:
- What AIEAT does (end-to-end demo)
- Architecture (local AI, SQLite, Flet — no cloud dependency)
- Challenges (async scraping, profile silos, Windows packaging)
- Known limitations + V2 roadmap

---

## Quick Reference: Worker LLM Prompts

| When | Prompt File | What It Does |
|------|-------------|-------------|
| Mar 14 AM | [Worker_Debug_Purge.md](file:///C:/Users/pechj/.gemini/antigravity/brain/a5d0abd9-dc67-4a9c-a0cb-0ae4399346ad/Worker_Debug_Purge.md) | Strip 14 debug prints + hide Log page |
| Mar 14 PM | *(create new)* | Fix `threading.Thread` → `page.run_task()` + Ollama snackbar |
| Mar 16-17 | *(create based on feedback)* | Fix bugs reported by testers |
