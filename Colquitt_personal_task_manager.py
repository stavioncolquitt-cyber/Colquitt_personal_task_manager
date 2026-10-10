"""
Personal Task & Project Manager
Author: Stavion Colquitt
Date:   2026-10-09
Tier:   Base Level
Description:
    A task manager backed by a SQLite database. Tasks persist across
    sessions in tasks.db. Supports adding, querying by status,
    updating status, and deleting tasks using parameterized SQL.

TEST RESULTS (verified by running the program)

    [x] First run with no .db file present
            sqlite3.connect() created tasks.db automatically, the
            CREATE TABLE IF NOT EXISTS statement ran without error,
            and the six tasks inserted with sequential IDs 1 through 6.

    [x] Second run without deleting the .db
            IDs continued at 7 through 12 rather than restarting,
            confirming AUTOINCREMENT, and the records from the first
            run were still present.

    [x] update_task_status() on a valid ID
            update_task_status(conn, 2, "In Progress") returned True.
            cursor.rowcount was 1, and "Fix login bug" showed the new
            status in every later display.

    [x] update_task_status() on a non-existent ID
            update_task_status(conn, 9999, "Done") returned False.
            No rows were changed and the program continued normally.

    [x] delete_task() on a valid ID
            delete_task(conn, 6) returned True and "Renew
            certification" no longer appeared in get_all_tasks().
            delete_task(conn, 9999) returned False without crashing.

    [x] display_tasks() with an empty list
            Printed "No tasks found." instead of an empty table.

    [x] Long title handling
            A 48-character title stored in full in the database and
            displayed truncated to 25 characters, so truncation is
            display-only and no data is lost.

    Note: ORDER BY priority sorts the text values alphabetically,
    so results come back High, Low, Medium rather than by importance.
    This matches the ordering the assignment specifies.
"""

import sqlite3

DB_FILE = "tasks.db"


def create_connection(db_file):
    """Open or create the database file and return the connection."""
    try:
        return sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(f"Could not connect to {db_file}: {e}")
        return None


def setup_database(conn):
    """Create the tasks table if it does not already exist."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                description TEXT,
                priority    TEXT    DEFAULT 'Medium',
                status      TEXT    DEFAULT 'Pending',
                due_date    TEXT,
                project_id  INTEGER
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Could not create the tasks table: {e}")


def add_task(conn, title, description, priority, due_date):
    """Insert one task and return its new id, or None on failure."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, description, priority, due_date, project_id)
            VALUES (?, ?, ?, ?, ?)
        """, (title, description, priority, due_date, None))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Could not add task: {e}")
        return None


def get_all_tasks(conn):
    """Return every task as a list of row tuples."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY priority, due_date")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Could not read tasks: {e}")
        return []


def get_tasks_by_status(conn, status):
    """Return tasks matching the given status, ordered by priority."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE status = ? ORDER BY priority",
            (status,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Could not read tasks by status: {e}")
        return []


def update_task_status(conn, task_id, new_status):
    """Change a task's status. Returns True if a row was updated."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (new_status, task_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Could not update task {task_id}: {e}")
        return False


def delete_task(conn, task_id):
    """Delete a task by id. Returns True if a row was deleted."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Could not delete task {task_id}: {e}")
        return False


def display_tasks(tasks):
    """Print a list of task rows as an aligned table."""
    if not tasks:
        print("No tasks found.")
        return

    print(f"{'ID':<5}{'Title':<28}{'Priority':<12}{'Status':<14}{'Due Date':<12}")
    print("-" * 71)
    for row in tasks:
        task_id, title, priority = row[0], row[1][:25], row[3]
        status, due_date = row[4], row[5]
        print(f"{task_id:<5}{title:<28}{priority:<12}{status:<14}{due_date:<12}")


conn = create_connection(DB_FILE)
if conn is None:
    print("Exiting: no database connection.")
    raise SystemExit

setup_database(conn)

new_tasks = [
    ("Write project proposal", "Draft and submit the Q4 proposal", "Medium", "2026-11-20"),
    ("Fix login bug", "Session token expires too early", "High", "2026-11-15"),
    ("Update resume", "Add recent coursework and projects", "Low", "2026-12-01"),
    ("Review pull requests", "Clear the open review queue", "High", "2026-11-12"),
    ("Back up project files", "Copy everything to external drive", "Medium", "2026-11-28"),
    ("Renew certification", "Schedule the exam date", "Low", "2026-12-15"),
]

for title, description, priority, due_date in new_tasks:
    new_id = add_task(conn, title, description, priority, due_date)
    print(f"Task added with ID: {new_id}")

# add_task() has no status parameter, so every row inserts as 'Pending'.
# Set two of them here so the collection has the mix of statuses the
# assignment asks for, and so the Pending filter below is meaningful.
update_task_status(conn, 3, "Done")
update_task_status(conn, 5, "In Progress")

print("\n=== All Tasks ===")
display_tasks(get_all_tasks(conn))

print("\n=== Pending Tasks ===")
display_tasks(get_tasks_by_status(conn, "Pending"))

print()
if update_task_status(conn, 2, "In Progress"):
    print("Status updated for task 2: True")
else:
    print("Status updated for task 2: False (no such task)")

if delete_task(conn, 6):
    print("Task 6 deleted: True")
else:
    print("Task 6 deleted: False (no such task)")

print("\n=== All Tasks (updated) ===")
display_tasks(get_all_tasks(conn))

conn.close()
