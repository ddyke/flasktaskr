import os

DEBUG = False
# grab the folder where this script lives
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'flasktaskr.db'
# USERNAME = 'admin'
# PASSWORD = 'admin'
WTF_CSRF_ENABLED = True
SECRET_KEY = 'himitsu'

# define the full path of the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# set SQLAlchemy uri (not required for the sqlite3 version)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

