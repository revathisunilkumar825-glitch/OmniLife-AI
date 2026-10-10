# Git & GitHub workflow for the 4-member team

This follows the layout in the project PDF: `main` plus one branch per member
(`frontend`, `backend`, `ai`, `database`). Everyone works on their own branch
and merges into `main` through a **pull request (PR)**. Nobody pushes straight
to `main`.

```
main
├── frontend   (Member 1)
├── backend    (Member 2)
├── ai         (Member 3)
└── database   (Member 4)
```

## 1. One-time setup (Member 4 does this on Day 1)

1. On github.com click **New repository** → name `OmniLife-AI` → **Private** →
   do **not** tick "Add a README" (we already have one).
2. In VS Code open the project folder, then open the terminal (`Ctrl + ~`):

```bash
git init
git add .
git status            # CHECK: .env must NOT appear in this list
git commit -m "Initial project structure, database layer and tests"
git branch -M main
git remote add origin https://github.com/<your-username>/OmniLife-AI.git
git push -u origin main
```

3. Create the four branches and push them:

```bash
git branch frontend
git branch backend
git branch ai
git branch database
git push -u origin frontend backend ai database
```

4. GitHub → repository **Settings → Collaborators → Add people** → add the other
   three members.
5. **Protect `main`** (Settings → Branches → Add branch ruleset / rule for `main`):
   - Require a pull request before merging
   - Require status checks to pass → select **backend-tests**
   - (Optional) Require 1 approval - another member reviews your code

## 2. Everyone's first day

```bash
git clone https://github.com/<owner>/OmniLife-AI.git
cd OmniLife-AI
git switch backend            # your own branch: frontend / backend / ai / database
```

## 3. Daily routine

```bash
# morning - get the latest work of the others into your branch
git switch main
git pull
git switch database           # your branch
git merge main

# ... write code, run  python -m pytest  ...

# save your work
git add .
git commit -m "database: add search_history table"
git push

# when a feature is finished: open GitHub → "Compare & pull request"
#   base: main   ←   compare: database
# fill the template, wait for the green CI check, ask a teammate to review, merge.
```

Small commits with clear messages are better than one giant commit at midnight.
Message style: `area: what changed`, e.g. `backend: add /login endpoint`,
`ai: use MiniLM for embeddings`, `docs: explain Docker setup`.

## 4. Merge conflicts (they will happen once!)

A conflict means two people changed the same lines. When you run
`git merge main` and Git says **CONFLICT**:

1. Open the file in VS Code - it shows **Accept Current / Accept Incoming /
   Accept Both** buttons above each conflict.
2. Choose the correct version (talk to the teammate if unsure), save.
3. `git add <file>` then `git commit` to finish the merge.

To avoid conflicts: stay in your own folder (`frontend/`, `backend/`, `ai/`,
`database/`) and tell the team before editing someone else's files.

## 5. Security habits (important for a security analyst's project!)

- **Never commit** `.env`, passwords, JWT secrets, API keys or real
  Aadhaar/PAN/passport files. `.gitignore` already blocks `.env`, `uploads/`
  contents and `*.db`, but always check `git status` before `git add .`.
- If a secret *was* pushed, deleting it in a later commit is **not** enough -
  it stays in history. Treat it as leaked: generate a new one immediately.
- Only the clearly marked mock dataset in `documents/test_dataset/` is committed.

## 6. Cheat sheet

| I want to…                         | Command                              |
|------------------------------------|--------------------------------------|
| see what changed                   | `git status` / `git diff`            |
| see history                        | `git log --oneline --graph`          |
| undo changes in a file (unsaved to git) | `git restore <file>`            |
| unstage a file                     | `git restore --staged <file>`        |
| switch branch                      | `git switch <branch>`                |
| get teammates' latest `main`       | `git switch main && git pull`        |
| throw away a mistake in last commit message | `git commit --amend`        |
