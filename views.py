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


from functools import wraps
from forms import AddTaskForm, RegisterForm, LoginForm
from flask import Flask, flash, redirect, render_template, request, session, url_for, g
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import datetime

# config

app = Flask(__name__)
app.config.from_object('_config')   # dictionary
# the dictionary includes "WTF_CSRF_ENABLED = True" and thus CSRF token is enabled. this needs to be reflected
# in the html templates by writing {{ form.csrf_token }}

# for printing app.config
# for key, values in app.config.items():
#     print(key, values)
db = SQLAlchemy(app)

# Import Task, User class from models.py, need this line placed after db=SQLAlchemy to avoid
# circular referencing
from models import Task, User

# helper functions

"""
# connect to sql database
# code for the sqlite3 version, not used in the SQLAlchemy version
def connect_db():
    return sqlite3.connect(app.config['DATABASE_PATH'])
"""



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

# helper function to return open tasks
def open_tasks():
    return db.session.query(Task).filter_by(status='1').order_by(Task.due_date.asc())

# helper function to return closed tasks
def closed_tasks():
    return db.session.query(Task).filter_by(status='0').order_by(Task.due_date.asc())

# route handlers

@app.route('/logout/')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None )
    flash("Goodbye!")
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def login():
    """
    # code for the sqlite3 version
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
    """

    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(name=request.form['name']).first()
            if user is not None and user.password == request.form['password']:
                session['logged_in'] = True
                session['user_id'] = user.id
                flash('Welcome!')
                return redirect(url_for('tasks'))
            else:
                error = 'Invalid username or password.'
        else:
            error = 'Both fields are required.'
    return render_template('login.html',
                           form=form,
                           error=error
                           )

# registration handler
@app.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    # form is an inheritance of RegisterForm class that is a child of flask_wrf.Form module
    # flask_wrf > RegisterForm > form > validate_on_submit (check CSRF token, {{ form.csrf_token }} )
    form = RegisterForm(request.form)

    if request.method == 'POST':
        # validate the input
        if form.validate_on_submit():
            #add new user data to the "user" table
            new_user = User(
                form.name.data,
                form.email.data,
                form.password.data,
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                # redirect to the login page
                flash('Thanks for registering. Please login.')
                return redirect(url_for('login'))
            except IntegrityError:
                error = "That username and/or email already exist."
                return render_template('register.html',
                                       form=form,
                                       error=error
                                       )
    return render_template('register.html',
                           form=form,
                           error=error
                           )

#　operate database
@app.route('/tasks/')
@login_required
def tasks():
    """
    # code for the sqlite3 version
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
    # returns open_tasks (list of dict), closed_tasks (list of dict) to /tasks.html page
    return render_template('tasks.html',
                           form=AddTaskForm(request.form),
                           open_tasks=open_tasks,
                           closed_tasks=closed_tasks
                           )
    """

    return render_template('tasks.html',
                           form=AddTaskForm(request.form),
                           open_tasks=open_tasks(),
                           closed_tasks=closed_tasks()
                           )

# Add new tasks
@app.route('/add/', methods=['GET', 'POST'])   # what's this path????
@login_required
def new_task():
    """
    # codes for the sqlite3 version
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
        # commit db, close db and redirect to the tasks.html
        g.db.commit()
        g.db.close()
        flash("New entry was successfully posted. Thanks.")
        return redirect(url_for('tasks'))
    """
    error = None
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_task = Task(
                form.name.data,
                form.due_date.data,
                form.priority.data,
                datetime.datetime.utcnow(),
                '1',
                session['user_id']
            )
            db.session.add(new_task)
            db.session.commit()
            flash('New entry was successfully posted. Thanks.')
            return redirect(url_for('tasks'))
    # return form values if request.method is NOT 'POST' or form.validate_on_submit() is False
    return render_template('tasks.html',
                           form=form,
                           error=error,
                           open_tasks=open_tasks(),
                           closed_tasks=closed_tasks()
                           )



# mark as complete
@app.route('/complete/<int:task_id>/')  # define the path, to be assigned in the 'Mark as Complete' link in tasks.html
@login_required
def complete(task_id):
    """
    # connect to db, set the status of the task_id to 0, commit and close
    # the code for the sqlite3 version
    g.db = connect_db()
    g.db.execute('update tasks set status = 0 where task_id='+str(task_id))
    g.db.commit()
    g.db.close()
    flash('The task was marked as complete.')
    return redirect(url_for('tasks'))
    """
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).update({"status": "0"})
    db.session.commit()
    flash('The task was marked as complete.')
    return redirect(url_for('tasks'))

# delete tasks
@app.route('/delete/<int:task_id>/')    # what's this path????
@login_required
def delete_entry(task_id):
    """
    # code for the sqlite3 version
    # connect to db, delete task_id from db, commit and close
    g.db = connect_db()
    g.db.execute('delete from tasks where task_id='+str(task_id))
    g.db.commit()
    g.db.close()
    flash('The task was deleted.')
    return redirect(url_for('tasks'))
    """
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).delete()
    db.session.commit()
    flash('The task was deleted.')
    return redirect(url_for('tasks'))

# not sure where this function is used
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the {} field - {}"
                  .format(getattr(form, field).label.text, error), 'error')

