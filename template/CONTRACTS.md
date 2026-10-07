# Contracts

Every interface two tasks share, fixed before parallel work starts. Change a
contract only through the orchestrator, and re-dispatch every task that uses it.

## C1. <name>: owned by T<id>, used by T<ids>

```python
# signature, types, and error behaviour
def example(inputs: list[Item]) -> list[Result]:
    """Raises ValueError on <condition>. Never returns None."""
```

## C2. <data file>: written by T<id>, read by T<ids>

| field | type | meaning |
|---|---|---|
| | | |
