---
name: java
description: Use whenever the work is in Java - a Solution.java for a timed or HackerRank-style problem, a Maven or Gradle project, or Java concurrency (ConcurrentHashMap, atomics, volatile, executors, CompletableFuture). Covers how tests run here, the file and main-class rules, and the concurrency patterns and bugs to name out loud.
---

# Java

## How tests run in this kit
- **Build file present** (`pom.xml`, `build.gradle`, `build.gradle.kts`): the
  PostToolUse hook runs `mvn -q test` / `gradle test -q` (the `mvnw` / `gradlew`
  wrapper when there is one). JUnit lives there.
- **No build file** (one or a few `.java` files): the hook compiles every
  `.java` file with `javac` into `.claude/build/java` (ignored by git), then runs
  each class named `*Test` or `Test*` with `java -ea`. A test class is a plain
  `main` that throws (or `assert`s, enabled by `-ea`) on failure:

```java
class SolutionTest {
    static void check(boolean ok, String what) { if (!ok) throw new AssertionError(what); }
    public static void main(String[] args) {
        check(new Solution().twoSum(new int[]{2, 7, 11}, 9)[1] == 1, "basic");
        System.out.println("all passed");
    }
}
```
- No test class yet: a clean compile passes, a compile error fails the edit.
- `"test_command"` in `.claude/guard.json` overrides all of this.

## Timed / HackerRank-style rules
- The file is `Solution.java`; only `public class Solution` may be public in
  it (other classes package-private, or `static` nested). No `package` line.
- `main` lives in `Solution` and reads stdin only if the problem says so; tests
  call methods directly, never through stdin.
- Say complexity out loud; prefer `ArrayDeque` over `Stack`/`LinkedList`,
  `HashMap.getOrDefault`/`merge`, `PriorityQueue` with a comparator.

## Concurrency: patterns, and the bug to name before the fix
| Need | Use | Bug it prevents |
|---|---|---|
| get-or-create, read-modify-write on a map | `map.compute` / `computeIfAbsent` / `merge` | check-then-act: two threads both see null and both create |
| conditional remove (evict if idle) | `computeIfPresent(k, (k, v) -> stale ? null : v)` | evict-vs-touch race |
| hot counter | `LongAdder` (striped); `AtomicLong` for a value you also read often | lost update on `x++` |
| a field one thread writes, another reads | `volatile` (or only touch it inside `compute*`) | stale read: no happens-before |
| swap a whole config | immutable object + `volatile` / `AtomicReference` pointer swap | readers see a half-built object |
| fan-out with a deadline | `CompletableFuture.supplyAsync(..).completeOnTimeout(fallback, ms, MILLISECONDS)`, `allOf` | one slow call blocks the request |
| pools | `Executors.newFixedThreadPool(cores)` for CPU; virtual threads (Java 21) for blocking I/O | unbounded threads |
| two locks | always the same global order, or `tryLock(timeout)` | deadlock |

A thread-safe map makes each call atomic, not a sequence of calls. Compare
`System.nanoTime()` readings only by subtracting: `now - t0 > timeout`.

Test concurrency with many threads hammering one key, a `CountDownLatch` to
start them together, and an assert on the final count; run it a few times.
