import os
import  unittest

from views import app, db
from _config import basedir
from models import User

TEST_DB = 'test.db'

class AllTests(unittest.TestCase):

    #############################
    #### setup and tear down ####
    #############################

    # executed prior to each test

    # Flask exposes the Werkzeug test client and handles the context locals.
    # It is important to set TESTING configuration setting to True,
    # to propagate the exceptions to the test client.
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, TEST_DB)
        # http://flask.pocoo.org/docs/0.11/api/#flask.Flask.testing
        # test_client(use_cookies=True, **kwargs) Creates a test client for Flask application.
        self.app = app.test_client()
            # create a test database initialised with the setting in the parent database db
        db.create_all()

    # executed after each test
    def tearDown(self):
        # need to destroy the session otherwise the configs set in the setUp() would be
        # auto-commited
        db.session.remove()
        # delete tables in the test database
        db.drop_all()

    # each test should start with 'test'

    # try to add a new user to the database 'test.db users' (table name has been defined in models.User)
    # if comment out the tearDown function the test should raise an error on the second attempt
    # because the same user already exists on the table
    def test_user_setup(self):
        new_user = User("london", "london@wing.org", "brighton")
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()     # returns all user_id as a list,
                                                # like [<User dddyke, <User testuser1, <User testuser2]
        for t in test:
            t.name
        assert t.name == 'london'


if __name__ == '__main__':
    unittest.main()

