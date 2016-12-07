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

    def create_admin_user(self):
        new_user = User(
            name='Superman',
            email='admin@realpython.com',
            password='allpowerful',
            role='admin'
        )
        db.session.add(new_user)
        db.session.commit()


    ########################
    #### Test functions ####
    ########################

    # each test should start with 'test'


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
        response = self.app.get('/complete/1/', follow_redirects=True)
        self.assertNotIn(b'The task was marked as complete.', response.data)
        self.assertIn(b'You can only update tasks that belong to you.', response.data)

    def test_users_cannot_delete_tasks_that_are_not_created_by_them(self):
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
        response = self.app.get('/delete/1/', follow_redirects=True)
        #self.assertNotIn(b'The task was deleted.', response.data)
        self.assertIn(b'You can only delete tasks that belong to you.', response.data)

    def test_admin_users_can_complete_tasks_that_are_not_created_by_them(self):
        self.create_user('testuser1', 'test1@gmail.com', '111111')
        self.login('testuser1', '111111')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()

        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('/complete/1', follow_redirects=True)
        self.assertNotIn(b'You can only update tasks that belong to you.', response.data)

    #def test_admin_users_can_delete_tasks_that_are_not_created_by_them(self):

    #def test_string_reprsentation_of_the_task_object(self):






if __name__ == '__main__':
    unittest.main()
