from views import db
from _config import DATABASE_PATH
import sqlite3
from datetime import datetime

with sqlite3.connect(DATABASE_PATH) as conn:
    c = conn.cursor()
    # Rename the table
    #c.execute("ALTER TABLE tasks RENAME TO old_tasks")
    # recreate a new tasks table with updated schema by SQLAlchemy
    db.create_all()
    # retrieve data from the old_tasks sorted by the task_id
    c.execute("SELECT name, due_date, priority, status FROM old_tasks ORDER BY task_id ASC")
    # convert each row to a tuple
    data = [(row[0], row[1], row[2], datetime.now(), row[3], 1) for row in c.fetchall()]
    # load data to the new table
    c.executemany("INSERT INTO tasks (name, due_date, priority, posted_date, status, user_id) \
    VALUES (?, ?, ?, ?, ?, ?)", data)
    c.execute("UPDATE tasks SET status=1")
    # delete old_tasks table
    c.execute("DROP TABLE old_tasks")
