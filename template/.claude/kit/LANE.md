# Lane brief: <lane name>

For a second agent session in its own worktree:
`git worktree add ../build-<lane> -b <lane>`, then `cd ../build-<lane> && claude`,
then paste this as the first message.

- **Goal:** <one sentence>
- **You own only:** `<folder>/`. Do not edit anything outside it.
- **Input contract:** <file and fields you consume; it will not change>
- **Done when:** <tests in `<folder>/tests` pass; what it shows>
- **Constraints:** standard library + pytest; no new dependencies without asking.
- **First:** show me your plan, then wait.
