# sqlite3 commands list

"""
# sqlite3 version
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
"""
from views import db
from models import Task
from datetime import date

# Create all tables stored in this metadata
# db = SQLAlchemy(app), configured in db_create.py in the form of dictionary
db.create_all()

# insert data
# Task defines the format of the table 'tasks'
db.session.add(Task('Finish this tutorial', date(2016, 11, 30), 10, 1))
db.session.add(Task('Finish Real Python', date(2016, 12, 1), 10, 1))

# commit the changes
db.session.commit()