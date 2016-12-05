import os
import unittest

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
        app.config['WTF_CSRF_ENABLED'] = False
        # change the test database from flasktaskr.db to test.db
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

    ##########################
    #### Helper functions ####
    ##########################

    # helper function for registering a new user
    def register(self, name, email, password, confirm):
        # send a post request to register.html with the given form parameters
        return self.app.post('/register/', data=dict(
            name=name, email=email, password=password, confirm=confirm),
                             follow_redirects=True)

    # helper function for logging in
    # check for construction details at http://flask.pocoo.org/docs/0.11/testing/
    def login(self, name, password):
        return self.app.post('/', data=dict(name=name, password=password), follow_redirects=True)

    # again check http://flask.pocoo.org/docs/0.11/testing/ for this implementation
    def logout(self):
        return self.app.get('/logout/', follow_redirects=True)

    def create_user(self, name, email, password):
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

    def create_task(self):
        return self.app.post('/add/', data=dict(
            name='Go to the bank',
            due_date='10/12/2017',
            priority='1',
            status='1'
        ),
                             follow_redirects=True
                             )


    ########################
    #### Test functions ####
    ########################

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

    def test_form_is_present_on_login_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please login to access our task list.', response.data)



    # this test fails but cannot figure out its cause (as of 02/12/2016)
    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid username or password.', response.data)

    def test_users_can_login(self):
        self.register('testuser1', 'michael@realpython.com', 'python', 'python')
        response = self.login('testuser1', 'python')
        self.assertIn(b'Welcome!', response.data)

    def test_form_is_present_on_login_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please login to access your task list', response.data)

    def test_user_registration(self):
        self.app.get('/register/', follow_redirects=True)
        response = self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.assertIn(b'Thanks for registering. Please login', response.data)

    def test_user_registration_error(self):
        # send a get request to /register/ (the path is mock in the test environment)
        # receives a response_class object
        # expect empty
        self.app.get('/register/', follow_redirects=True)
        # register a user to the test.db
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        # send a get request again and expect the entry this time
        self.app.get('/register/', follow_redirects=True)
        # register the same user again to the test.db (expect error)
        response = self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.assertIn(b'That username and/or email already exist.', response.data)

    def test_user_can_logout(self):
        self.register('testuser1', 'test1@gmail.com', '111111', '111111')
        self.login('testuser1', '111111')
        response = self.logout()
        self.assertIn(b'Goodbye!', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn(b'Goodbye', response.data)

    def test_logged_in_users_can_access_tasks_page(self):
        self.register('testuser1', 'test1@gmail.com', '111111', '111111')
        self.login('testuser1', '111111')
        response = self.app.get('tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add a new task:', response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'You need to login first.', response.data)

    def test_users_can_add_tasks(self):
        self.create_user('testuser1', 'test1@gmail.com', '111111')
        self.login('testuser1', '111111')
        self.app.get('/tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'New entry was successfully posted. Thanks.', response.data)

    def test_users_cannot_add_tasks_when_error(self):
        self.create_user('testuser1', 'test1@gmail.com', '111111')
        self.login('testuser1', '111111')
        self.app.get('/tasks/', follow_redirects=True)
        response = self.app.post('/add/', data=dict(
            name='Go to the bank',
            due_date='',
            priority='1',
            status='1'),
                                 follow_redirects=True
                                 )
        self.assertIn(b'This field is required', response.data)

    def test_users_can_complete_tasks(self):
        self.create_user('testuser1', 'test1@gmail.com', '111111')
        self.login('testuser1', '111111')
        self.app.get('/tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('/complete/1/', follow_redirects=True)
        self.assertIn(b'The task was marked as complete.', response.data)

    def test_users_can_delete_tasks(self):
        self.create_user('testuser1', 'test1@gmail.com', '111111')
        self.login('testuser1', '111111')
        self.app.get('/tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('/delete/1/', follow_redirects=True)
        self.assertIn(b'The task was deleted.', response.data)

    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        # first user creates a task
        self.create_user('testuser1', 'test1@gmail.com', '111111')
        self.login('testuser1', '111111')
        self.app.get('/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        # second user tries to complete the task created by testuser1
        self.create_user('testuser2', 'test2@gmail.com', '222222')
        self.login('testuser2', '222222')
        self.app.get('/tasks/', follow_redirects=True)
        response = self.app.get('/complete/', follow_redirects=True)
        self.assertNotIn(b'The task was marked as complete.', response.data)

    




if __name__ == '__main__':
    unittest.main()
