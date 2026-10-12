---
name: reliability
description: Use when the build calls other services or is asked about production - retries, idempotency, at-least-once delivery, queues, failure of a dependency, deploy and scale (Docker, Kubernetes, health checks), monitoring, or "what happens when X is down". Covers the defaults to build in and how to explain them.
---

# Reliability and operations

Kastle-style systems run inside bank environments: a dependency fails, a
message is delivered twice, a deploy happens mid-day. Build the safe
default in, test it, and write the rest down honestly.

## Defaults to build in
- **Fail closed.** If a dependency or input is missing, do the safe thing
  (no contact, hold, a human) and say why in the output. Never guess.
- **Idempotency.** Every write or side effect takes a key (request id,
  loan id + date). A repeat with the same key returns the first result.
  Test it by sending the same request twice.
- **Timeouts on every outbound call**, with a budget per hop that adds up
  to the end-to-end budget.
- **Retries** with exponential backoff and jitter, a cap, and only for
  safe operations; after the cap, fail closed and record it.
- **At-least-once** delivery is the norm for queues and webhooks: consumers
  must be idempotent; ordering is per key, not global.
- **Circuit breaker** idea, said in one line, when a dependency is slow:
  stop calling it for a while and take the fallback.

## Deploy and operate (written down, built where cheap)
- `Dockerfile`: slim Python base, non-root user, `--port` argument.
- `GET /healthz` (process up, data and rules loaded) for readiness.
- Kubernetes paragraph: stateless replicas behind a service, readiness
  probe, config from env, secrets from the secret store, where state
  lives, what scales horizontally and what does not, rollout and rollback.
- Observability: one structured log line per decision (id, outcome, rule
  ids, latency; never PII), counters for fail-closed paths, an alert on
  their rate.

## Tests
Same request twice gives one effect; a dependency that times out yields the
fail-closed result within the budget; a malformed input never raises past
the API boundary.

## Show it
A "what happens when" table in ARCHITECTURE: each dependency, its timeout,
its failure behaviour, and how we would notice.
