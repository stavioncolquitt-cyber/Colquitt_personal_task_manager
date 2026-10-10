# Personal Task & Project Manager

**Week 7 Programming Assignment — Base Level**
Course: Programming Fundamentals
Author: Stavion Colquitt

A command-line task manager backed by a SQLite database. Tasks persist
across sessions in a `.db` file rather than living in memory or a CSV,
and every SQL statement containing a variable uses parameterized
queries.

## Files

| File | Description |
|---|---|
| `Colquitt_personal_task_manager.py` | The program |
| `tasks.db` | SQLite database produced by a clean run |

`tasks.db` is a binary SQLite file, so GitHub will not preview it. It
contains five task records: six were inserted, one was deleted, and two
had their status changed. To inspect it, open it with
[DB Browser for SQLite](https://sqlitebrowser.org/) or query it
directly:

```python
import sqlite3
conn = sqlite3.connect("tasks.db")
for row in conn.execute("SELECT * FROM tasks"):
    print(row)
conn.close()
```

## Running it

```
python Colquitt_personal_task_manager.py
```

No installation needed — `sqlite3` ships with Python. If `tasks.db`
does not exist, it is created automatically on the first run.

Delete `tasks.db` beforehand to start from an empty database. Leave it
in place and the next run appends six more tasks with IDs continuing
from where the last run stopped, which demonstrates `AUTOINCREMENT`.

## Schema

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    description TEXT,
    priority    TEXT    DEFAULT 'Medium',
    status      TEXT    DEFAULT 'Pending',
    due_date    TEXT,
    project_id  INTEGER
)
```

`project_id` is reserved for the Intermediate level and is `NULL` on
every row here. Due dates are stored as `YYYY-MM-DD` text.

## Functions

| Function | Purpose |
|---|---|
| `create_connection(db_file)` | Opens or creates the database, returns the connection or `None` |
| `setup_database(conn)` | Creates the `tasks` table if it does not exist |
| `add_task(conn, title, description, priority, due_date)` | Inserts a task, returns the new row id |
| `get_all_tasks(conn)` | Returns all tasks ordered by priority then due date |
| `get_tasks_by_status(conn, status)` | Returns tasks matching a status |
| `update_task_status(conn, task_id, new_status)` | Updates a status, returns whether a row changed |
| `delete_task(conn, task_id)` | Deletes a task, returns whether a row was removed |
| `display_tasks(tasks)` | Prints an aligned table, or a message if empty |

## Notes

**Parameterized queries.** Every SQL statement with a variable uses `?`
placeholders with the values passed as a separate tuple, which prevents
SQL injection. No f-strings or string concatenation appear inside any
SQL string.

**Status variety.** `add_task()` has no status parameter, so every row
inserts as `Pending` by default. Two tasks are updated immediately
after insertion so the collection has the mix of statuses the
assignment calls for, and so the Pending filter returns a genuine
subset rather than everything.

**Sort order.** `ORDER BY priority` sorts the text values
alphabetically, producing High, Low, Medium rather than ordering by
importance. This matches what the assignment specifies.

## Testing

Verified scenarios are recorded in the comment block at the top of the
source file: first run with no database present, second run showing ID
continuation and persistence, status updates on valid and invalid IDs,
deletion on valid and invalid IDs, the empty-list display message, and
title truncation at 25 characters for display while the full title is
retained in the database.
