# sqlite3 commands list

import sqlite3
from _config import DATABASE_PATH
import pdb

pdb.set_trace()
with sqlite3.connect(DATABASE_PATH) as conn:
    # get a cursor
    c = conn.cursor()

    # create the table
    c.execute("DROP TABLE if exists tasks")
    c.execute("CREATE TABLE tasks(task_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, \
    due_date TEXT NOT NULL, priority INTEGER NOT NULL, status INTEGER NOT NULL)")

    # insert data to the table
    # status=1 means 'open'
    c.execute("INSERT INTO tasks (name, due_date, priority, status)" \
              "VALUES('Finish this tutorial', '25/11/2016', 10, 1)")

    c.execute("INSERT INTO tasks (name, due_date, priority, status)" \
              "VALUES('Finish Real Python Course 2', '25/11/2016', 10, 1)")

