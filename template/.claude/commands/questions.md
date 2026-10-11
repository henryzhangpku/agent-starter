---
description: From the prompt, who to talk to and what to ask them, when - written into TEAM.md
---

Read PROMPT.md (and ONBOARDING.md and TEAM.md if they exist). The build is a
team effort; most of the risk in the prompt is answered by people, not code.
Produce a communication plan and write it into TEAM.md under "Who owns what"
and a new section "Questions to ask". Do not change code.

1. **Who to reach out to.** From the prompt, list the roles whose knowledge
   the build depends on (use real names from TEAM.md or ONBOARDING.md if
   known, otherwise roles): e.g. the person who set the prompt (scope,
   priorities, what done means), product or customer-facing (who the user is,
   what they complain about), an engineer who owns the nearest system (seams,
   conventions, data shapes), infra or deploy owner (how it ships, where it
   runs, limits), compliance or risk (what must never happen), data or ML
   (labels, evaluation, existing metrics). Only roles this prompt needs.
2. **What to ask each, max three questions per person**, each one specific to
   this prompt and answerable in a minute. Prefer questions whose answer
   changes the design ("If a caller interrupts mid-confirmation, should the
   payment stand or roll back?") over questions that only fill in detail.
3. **When to ask**: at kickoff (scope, done, costliest mistake), before the
   contracts are fixed (data shapes, interfaces, seams), before shipping
   (deploy, rollback, monitoring), and at each check-in (one line of status
   to the person who set the prompt).
4. **What you will offer back**, one line per person: a task row they could
   own, a demo time, or a decision you want them to make.

End with the three questions to ask in the first five minutes, in order,
phrased exactly as you would say them out loud. $ARGUMENTS

If the build must plug into the team's existing system (their agent, their
pipeline, their data), the first questions are about **their real interface**,
never an invented one: what does their agent emit (an action or tool-call
schema, a message object, an event), where can a step hook in (before a
reply goes out, as a tool, after the call), what is the latency budget at
that point, what rules or engine already exist, and can we see one real
sample (a log line, a payload, a schema file). Ask for the sample by name.
