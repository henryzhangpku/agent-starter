---
description: Pre-merge and deploy checklist for a feature in a team codebase
---

Prepare this change to ship through the team's own process (from
ONBOARDING.md; ask me if it is unknown). Check and report each item; fix only
what is inside the change's scope, after showing me:

1. Full test suite, lint, formatter and type checks: the commands this repo uses.
2. The diff touches only what the feature needs; no debug code, no secrets.
3. Migrations or config changes: reversible, and documented in the PR.
4. Rollout: behind a feature flag or safe by default? What does a canary or
   staged rollout look like here?
5. Rollback: the exact steps to undo it.
6. Observability: logs, metrics or alerts that will show it working or failing.
7. A PR description: what and why, how it was tested, risks, rollout and
   rollback, screenshots or output if relevant, who should review (from
   CODEOWNERS or ONBOARDING.md).

Do not merge or deploy. Hand the PR text to me; the team's reviewers and
pipeline decide. $ARGUMENTS
