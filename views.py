"""
1. Users sign in and out from the landing page.
2. New users register on a separate registration page.
3. Once signed in, users add new tasks; each task consists of a name, due date, priority, status, and a unique,
   auto-incremented ID.
4. Users view all uncompleted tasks from the same screen.
5. Users also delete tasks and mark tasks as completed; if a user deletes a task, it will also be deleted from
   the database.
"""
"""
html:
landing page
registration page
main page

main.py

registration
login
logout
call sql from browser
delete tasks
change status



"""

import sqlite3
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for, g
from forms import AddTaskForm

# config

app = Flask(__name__)
app.config.from_object('_config')   # dictionary
# for printing app.config
#for key, values in app.config.items():
#    print(key, values)

# helper functions

# connect to sql database
def connect_db():
    return sqlite3.connect(app.config['DATABASE_PATH'])

# check if logged in
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash("You need to login first.")
            return redirect(url_for('login'))
    return wrap

# route handlers

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("Goodbye!")
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or \
            request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            flash("Welcome!")
            return redirect(url_for('tasks'))
    return render_template('/login.html')

#　operate database
@app.route('/tasks/')
@login_required
def tasks():
    g.db = connect_db()
    # retrieve open task items as a list of dictionaries
    cur = g.db.execute('select name, due_date, priority, task_id from tasks where status=1')

    open_tasks = [
        dict(name=row[0], due_date=row[1], priority=row[2], task_id=row[3]) for row in cur.fetchall()
    ]
    # retrieve closed tasks
    cur = g.db.execute('select name, due_date, priority, task_id from tasks where status=0')
    closed_tasks = [
        dict(name=row[0], due_date=row[1], priority=row[2], task_id=row[3]) for row in cur.fetchall()
    ]
    #close database
    g.db.close()
    # render_template(form, *context)
    # AddTaskForm not created yet (as of 26 Nov 2016)
    # returns open_tasks (list of dict), closed_tasks (list of dict) to /task.html page
    return render_template('task.html',
                           form=AddTaskForm(request.form),
                           open_tasks=open_tasks,
                           closed_tasks=closed_tasks
                           )

# Add new tasks
@app.route('/add/', methods=['POST'])   # what's this path????
@login_required
def new_task():
    g.db = connect_db()
    # receive POST requests (name, due_date, priority)
    name = request.form['name']
    date = request.form['due_date']
    priority = request.form['priority']

    # check if all fields are filled
    if not name or not date or not priority:
        flash("All fields are required. Please try again.")
        return redirect(url_for('tasks'))
    else:
        # write into 'tasks' db
        # request.form['name'] maybe replaced by name? (and two others?)
        # add 1 as the status indicating the task is open
        g.db.execute("insert into tasks (name, due_date, priority, status) \
        values(?, ?, ?, 1)", [request.form['name'], request.form['due_date'], request.form['priority']
                              ]
                     )
        # commit db, close db and redirect to the task.html
        g.db.commit()
        g.db.close()
        flash("New entry was successfully posted. Thanks.")
        return redirect(url_for('tasks'))

# mark as complete
@app.route('/complete/<int:task_id>/')  # define the path, to be assigned in the 'Mark as Complete' link in task.html
@login_required
def complete(task_id):
    # connect to db, set the status of the task_id to 0, commit and close
    g.db = connect_db()
    g.db.execute('update tasks set status = 0 where task_id='+str(task_id))
    g.db.commit()
    g.db.close()
    flash('The task was marked as complete.')
    return redirect(url_for('tasks'))

# delete tasks
@app.route('/delete/<int:task_id>/')    # what's this path????
@login_required
def delete_entry(task_id):
    # connect to db, delete task_id from db, commit and close
    g.db = connect_db()
    g.db.execute('delete from tasks where task_id='+str(task_id))
    g.db.commit()
    g.db.close()
    flash('The task was deleted.')
    return redirect(url_for('tasks'))
