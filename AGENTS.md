# AGENTS.md

Instructions for coding agents working in this repository.

Present is a Django attendance **presence log** (not an official class register). Product rules live in `Present — Product Requirements Document & Implementation Specification.md`. Follow that spec. Do not reintroduce lecturer roster import or “verified attendance” claims.

---

## Git workflow

- Default integration branch: `develop`
- Production branch: `main`
- Work on a branch. Do not commit or push straight to `main`.
- Open a pull request into `develop` for significant features. Promote to `main` only via PR.
- Do not merge a PR unless the user asks.
- Do not commit unless the user explicitly asks.
- Do not `git push --force` to `main` or `develop`.
- Do not skip hooks (`--no-verify`) unless the user asks.
- Do not amend commits you did not create in this conversation, and never amend a commit that has been pushed unless the user asks.
- Do not change git config.

---

## Branch protection

Configure once in GitHub: **Settings → Branches** (ruleset or classic branch protection) for `main`:

- Require a pull request before merging — no direct pushes, including from the repo owner.
- Require status checks to pass before merging: both the `test` matrix jobs and the `lint` job from `.github/workflows/test.yml` (add that workflow when CI lands; do not merge to `main` without those checks once they exist).
- Require branches to be up to date before merging.
- Do **not** require signed commits or a minimum number of approvals for now (solo project). Revisit if collaborators join.

Apply the same PR-only rule to `develop` if it is used as a long-lived integration branch.

---

## Release tags

Configure once in GitHub: **Settings → Rules → Tags**.

Protect `v*` tags so only trusted actors can create them. A stolen `v*` tag is a supply-chain incident if deploy or release automation trusts tags. Prefer SHA-pinned Actions in `.github/workflows` (not floating `@v4` tags for third-party actions) when those workflows exist.

Do not create or push `v*` tags unless the user asks.

---

## Branch naming

```text
feature/<short-kebab-description>
fix/<short-kebab-description>
chore/<short-kebab-description>
test/<short-kebab-description>
docs/<short-kebab-description>
```

Rules:

- Lowercase kebab-case only.
- One concern per branch.
- Name the outcome, not the ticket tool (`feature/geolocation-radius`, not `feature/update`).
- Keep the slug short (roughly 3–6 words).

Examples:

```text
feature/domain-gated-auth
feature/course-management
feature/attendance-session
feature/projector-display
feature/scan-time-auth
feature/geolocation-validation
feature/manual-present
fix/duplicate-check-in
fix/session-expiry-race
test/attendance-concurrency
docs/prd-gps-privacy
chore/production-settings
```

Do not use:

```text
feature/Nana
feature/new
feature/final
fix/stuff
update
```

---

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>: <imperative summary>
```

Types:

| Type     | Use for                                      |
|----------|----------------------------------------------|
| `feat`   | New user-facing behaviour                    |
| `fix`    | Bug fix                                      |
| `test`   | Tests only                                   |
| `docs`   | Documentation only                           |
| `refactor` | Behaviour-preserving code change           |
| `chore`  | Tooling, deps, config, deploy scaffolding    |
| `style`  | Formatting only                              |
| `perf`   | Performance                                  |

Rules:

- Imperative, lowercase summary after the type (`add`, `prevent`, `reject` — not `added` / `Adds`).
- Subject line ≤ 72 characters. No trailing period.
- Explain **why** in the body when the change is not obvious.
- One logical change per commit. Do not bundle unrelated work.
- One implementation phase (PRD Section 34) may span multiple commits. Commit at logical checkpoints within a phase, not only once at the end.
- Never commit with failing tests. If a phase is left incomplete at the end of a session, commit **working, tested** partial progress and leave a note in the commit body about what is unfinished. Do not commit broken intermediate states.
- Reference the product language: check-in, session, pin, radius, stub, merge — not “enrolment roster.”

Good:

```text
feat: add custom user and domain-gated registration
feat: implement attendance sessions and qr display
feat: reject check-ins outside the session radius
feat: merge manual stub rows on student registration
fix: prevent duplicate attendance for one student
fix: hide student names on the projector display page
test: add concurrent check-in uniqueness tests
docs: document scan-time auth resume on the qr url

feat: add attendance session model and start endpoint

Phase 3 in progress. QR display page and extend/end are not
wired yet. Tests for start + one-active-session pass.
```

Bad:

```text
update
changes
stuff
final
final2
Fixed bug
Added files
feat: Updated the attendance thing.
```

---

## Pull requests

- Branch from latest `develop`.
- Title uses the same conventional-commit style as the primary change (`feat: add geolocation radius validation`).
- Body:

```markdown
## Summary
- Why this exists (1–3 bullets)

## Test plan
- [ ] Concrete checks a reviewer can run
```

- PRs should be reviewable: one feature or one fix, not a whole phase unless the user asks to ship a phase as a single PR.
- Do not include `.env`, secrets, dumps, or generated noise.

---

## Do not commit

```text
.env
.env.*
!.env.example
__pycache__/
*.pyc
db.sqlite3
media/ uploads/
.venv/ venv/
staticfiles/
```

Secrets (`SECRET_KEY`, database URLs, email passwords, API keys) never belong in git. Use environment variables as in the PRD.

---

## Agent git habits

1. `git status`, `git diff`, and `git log` before committing, when the user asks for a commit.
2. Stage only files that belong to the change. Do not `git add .` if that would pick up secrets or unrelated files.
3. Match existing commit style in `git log` if it already follows this file; if not, follow this file going forward.
4. After a commit, show `git status` and stop. Do not push unless the user asks.
5. Run the relevant tests before committing. If they fail, fix them; do not commit red.
