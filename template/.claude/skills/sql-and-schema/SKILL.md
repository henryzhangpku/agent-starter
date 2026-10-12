---
name: sql-and-schema
description: Use whenever the build reads or writes a database, the team hands over a .db/.sql file or a Postgres/MySQL connection, or a question involves tables, joins, schema design, indexes, migrations or query performance. Covers designing the schema, writing safe and testable queries, and showing the work.
---

# SQL and schema

The room may slip SQL into any problem ("the book is in this SQLite file",
"store the decisions", "why is this query slow"). Treat the database as
part of the product: designed, tested and explained, not an afterthought.

## Reading a database you were handed
1. Inspect before you design: list tables, columns, types, keys and row
   counts (`sqlite3 x.db ".schema"`, `SELECT count(*)`, or
   `information_schema` on Postgres). Put a short data dictionary in
   `docs/ARCHITECTURE.md`.
2. The data is read-only (it is under `data/`): open SQLite with
   `sqlite3.connect("file:...?mode=ro", uri=True)`; on Postgres use a
   read-only role or a transaction you never commit.
3. Find the messiness in SQL, then say the numbers: duplicates per key,
   NULL rates, values stored as TEXT that should be dates or money,
   orphans (a foreign key with no parent).

## Patterns to reach for
- **Latest row per key** (snapshots, re-sent documents):
  `ROW_NUMBER() OVER (PARTITION BY id ORDER BY ts DESC) = 1` in a CTE.
  Order by a parsed timestamp, never by text in mixed formats.
- **Idempotent writes**: a natural or request key with
  `INSERT ... ON CONFLICT (key) DO UPDATE` (SQLite 3.24+, Postgres), so a
  retried request never duplicates a row.
- **Money**: integer cents or `NUMERIC`; never float. In Python, `Decimal`.
- **Dates**: store ISO 8601 or a real `DATE`/`TIMESTAMPTZ`; parse mixed text
  once in the loader, in code with tests, not with string tricks in SQL.
- **Audit**: an append-only table (who, what, when, why, rule id) for any
  decision a regulator could ask about.

## Schema design (when you store something)
- One table per thing, a primary key, foreign keys declared, `NOT NULL`
  where the rule says so, `CHECK` for small enums.
- An index for the one query that matters, named in ARCHITECTURE with the
  reason; show `EXPLAIN QUERY PLAN` (SQLite) or `EXPLAIN ANALYZE` (Postgres)
  before and after if performance comes up.
- Migrations as numbered `.sql` files applied in order by a tiny runner;
  never edit a migration that has run.
- Default to SQLite from the standard library for the day; say what changes
  for Postgres (types, `ON CONFLICT` targets, connection pool, isolation).

## Safety and tests
- Parameterised queries only (`?` / `%s`), never f-strings into SQL.
- Transactions around multi-statement writes; one connection per thread
  (SQLite) or a pool (Postgres).
- Tests run against a temporary database built from the schema plus a few
  hand-written rows, including the messy cases (duplicate key, NULL, bad
  date). Assert on query results, not on SQL text.
- Every query that feeds a decision has a test with a known answer.

## Show it
In the team view and ARCHITECTURE: the tables (a small ER diagram, top-down,
short labels), the key query with its index, and one line on scale ("at 10x
rows this index keeps the morning run under N seconds; at 100x we partition
by servicer"). Be ready to explain any query line by line.
