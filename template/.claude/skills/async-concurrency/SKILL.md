---
name: async-concurrency
description: Use whenever work runs concurrently or in real time - asyncio, tasks with dependencies, parallel tool calls, streaming, cancellation or barge-in, timeouts, queues, worker pools, rate limits - or the team asks "make it handle X at once". Covers the patterns, the failure modes to name out loud, and how to test them.
---

# Async and concurrency (Python asyncio)

Real-time agents are concurrent: a turn fetches identity, the loan and a
quote at once; a borrower interrupts mid-sentence; a downstream call hangs.
The room may ask for this inside any build. Use these patterns and say the
failure mode before writing the fix.

## Dependencies between jobs (a DAG)
Create one task per job **before any job body runs**; each job awaits its
parents' tasks, then runs. The await graph is the topological order; a task
can be awaited many times, so a diamond runs the shared parent once.
```python
async def run_all(jobs):            # jobs: {id: (deps, coro_fn)}
    tasks = {}
    async def run(j):
        deps, fn = jobs[j]
        await asyncio.gather(*(tasks[d] for d in deps))
        return await fn()
    for j in jobs:
        tasks[j] = asyncio.create_task(run(j))
    return dict(zip(tasks, await asyncio.gather(*tasks.values())))
```
Name and handle, in this order:
1. **Cycles** deadlock silently (gather never returns). Detect them before
   starting (Kahn's algorithm, report the cycle) - never rely on a timeout.
2. **A failing job**: fail fast (cancel the rest, then await them, catching
   `CancelledError`) when jobs share state; otherwise collect every failure
   (`return_exceptions=True` or `TaskGroup` + `ExceptionGroup`).
3. **Limit concurrency** with an `asyncio.Semaphore` taken around the job
   body only, never while waiting for parents (that deadlocks).
4. **Timeouts** per job with `asyncio.timeout()` (3.11+) or `wait_for`;
   **retries** only for operations that are safe to repeat (reads,
   idempotent writes with a key); never retry a payment blindly.

## Real time, cancellation and barge-in
- Structure a turn as stages connected by `asyncio.Queue`s or a
  `TaskGroup`; cancel the whole turn's group when the user interrupts.
- Anything with an external effect (taking a payment, sending a message)
  is **atomic from the agent's view**: do it under
  `asyncio.shield()` or behind a commit point, and record the outcome, so
  cancellation never leaves it half done.
- Never block the loop: no `time.sleep`, no sync HTTP or DB calls in
  coroutines; use `asyncio.to_thread()` for unavoidable blocking work.
- Stream first tokens early; measure time to first output separately from
  total time.

## Tests
- `pytest` with `asyncio.run()` inside the test (no plugin needed) or
  `pytest-asyncio` if it is already there.
- Use fake jobs with `asyncio.sleep()` and record start and end order;
  assert independent jobs overlap (total time close to the longest path,
  not the sum), dependents start after parents, a cycle raises, a failure
  cancels or is collected as designed, the semaphore caps concurrency.
- For cancellation: cancel mid-turn and assert no effect is half applied.

## Show it
In ARCHITECTURE: the stages and where cancellation and timeouts sit (a
top-down diagram), p50/p95 per stage and end to end against the budget,
and the one-line rule for side effects ("money is never half done").
