# ⚠️ GitHub Branch Reminder — SPZAGENTS/xmls

## CRITICAL: Always use `main`, NOT `master`!

**Date discovered:** 2026-03-09
**Issue:** All international XML files gave 404 errors

## The Problem
The repository `SPZAGENTS/xmls` uses `main` as its default branch.
When files were pushed to `master`, they were not accessible via the raw.githubusercontent.com URLs.

## Check Before Pushing
```bash
cd xml
git branch -vv

# Should show:
# * main                xxxxx [origin/main] ...
#   master              xxxxx ...
#   remotes/origin/HEAD -> origin/main   <-- THIS IS THE KEY!
```

## Correct Workflow
```bash
cd xml

# ALWAYS start with main
git checkout main
git pull origin main

# Make changes...
git add *.xml
git commit -m "..."

# Push to main, NOT master!
git push origin main
```

## Repository URL Pattern
✅ Correct: `https://raw.githubusercontent.com/SPZAGENTS/xmls/main/bbc_uk.xml`
❌ Wrong:   `https://raw.githubusercontent.com/SPZAGENTS/xmls/master/bbc_uk.xml`

## Active Branches
- `main` — ✅ DEFAULT — all XML updates go here
- `master` — old branch, no longer used
- `ground-zero-xmls` — other feature branch

Last updated: 2026-03-09 by Shpitzi 🦔
