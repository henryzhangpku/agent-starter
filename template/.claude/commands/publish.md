---
description: Prepare a finished build to be open-sourced - README, licence, demo page, checks - without publishing anything
---

Prepare this repository for a public release. Do the work, then stop and show
me; I publish.

1. **Checks first, report each:**
   - secrets: grep for keys, tokens, `.env` contents, credentials in code,
     logs, fixtures and git history (`git log -p` for anything key-shaped)
   - names: any company, client, interviewer or internal name that should not
     be public (ask me for the list if unsure)
   - data: every dataset is synthetic or licensed for release; say which
   - commit messages: no attribution lines I didn't write
2. **README.md** with, in this order: a one-paragraph pitch (what it does and
   for whom), **what it shows, measured** (the real numbers from the last run,
   with what they are compared against), how it works (a small diagram), three
   design decisions from DECISIONS.md, how to run it (copy-paste commands),
   tests, honest limitations, licence.
3. **LICENSE** (MIT unless I say otherwise), `.gitignore` sane.
4. **Optional demo** in `docs/` (static, no build step) if the project has
   something visual: the headline numbers and one interactive view. Add a
   favicon and Open Graph tags so the link previews well.
5. **A 150-word post draft** for LinkedIn: hook in the first two lines,
   three arrows on what it does, one honest limitation, a real question at
   the end, no links in the body (they go in a comment).

Do not create the remote repository, push, or post. $ARGUMENTS
