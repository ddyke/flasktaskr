from functools import wraps
from flask import flash, redirect, jsonify, session, url_for, Blueprint, make_response

from project import db
from project.models import Task

### config ###
# set blueprint to the 'api' directory. Also registered at project/__init__.py
api_blueprint = Blueprint('api', __name__)

### helper functions ###

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('users.login'))
    return wrap

def open_tasks():
    return db.session.query(Task).\
        filter_by(status='1').order_by(Task.due_date.asc())

def closed_tasks():
    return db.session.query(Task).\
        filter_by(status='0').order_by(Task.due_date.asc())

### routes ###

@api_blueprint.route('/api/v1/tasks/')
def api_tasks():
    # in flasktaskr.db/tasks table, returns the first 10 rows as a list
    results = db.session.query(Task).limit(10).offset(0).all()  #all() returns the results as a list
    json_results = []
    # append each row as dictionary data into json_results
    for result in results:
        data = {
            'task_id': result.task_id,
            'task name': result.name,
            'due date': str(result.due_date),
            'priority': result.priority,
            'posted date': str(result.posted_date),
            'status': result.status,
            'user id': result.user_id
        }
        json_results.append(data)
    # json renderer
    # flask.json.jsonify(*args, **kwargs)
    # turns the JSON output into a Response object with the application/json mimetype.
    # http://flask.pocoo.org/docs/0.11/api/#module-flask.json
    return jsonify(items=json_results)

@api_blueprint.route('/api/v1/tasks/<int:task_id>')
def task(task_id):
    result = db.session.query(Task).filter_by(task_id=task_id).first()
    if result:
        result = {
            'task_id': result.task_id,
            'task name': result.name,
            'due date': str(result.due_date),
            'priority': result.priority,
            'posted date': str(result.posted_date),
            'status': result.status,
            'user id': result.user_id
        }
        code = 200
    else:
        result = {"error": 'Element does not exist!'}
        code = 404
    # http://flask.pocoo.org/docs/0.11/api/#flask.make_response
    return make_response(jsonify(items=result), code)

