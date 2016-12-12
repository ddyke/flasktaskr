import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import User

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
        app.config['DEBUG'] = False
        # change the test database from flasktaskr.db to test.db
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, TEST_DB)
        # http://flask.pocoo.org/docs/0.11/api/#flask.Flask.testing
        # test_client(use_cookies=True, **kwargs) Creates a test client for Flask application.
        self.app = app.test_client()
            # create a test database initialised with the setting in the parent database db
        db.create_all()
        self.assertEquals(app.debug, False)

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
        new_user = User(
            name=name,
            email=email,
            password=bcrypt.generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()





    ########################
    #### Test functions ####
    ########################

    # each test should start with 'test'
    # try to add a new user to the database 'test.db users' (table name has been defined in models.User)
    # if comment out the tearDown function the test should raise an error on the second attempt
    # because the same user already exists on the table
    def test_users_can_register(self):
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
        self.assertIn(b'Please login to access your task list.', response.data)

    # this test fails but cannot figure out its cause (as of 02/12/2016)
    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid username or password.', response.data)

    def test_users_can_login(self):
        self.register('testuser1', 'michael@realpython.com', 'python', 'python')
        response = self.login('testuser1', 'python')
        self.assertIn(b'Welcome!', response.data)

    def test_invalid_form_data(self):
        self.register('testuser1', 'test1@gmail.com', '111111', '111111')
        response = self.login('alert("alert box!");', 'foo')
        self.assertIn(b'Invalid username or password', response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please register to access the task list.', response.data)

    def test_user_registration(self):
        self.app.get('/register/', follow_redirects=True)
        response = self.register('Michael', 'michael@realpython.com', 'python', 'python')
        print(response.data)
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

    def test_default_user_role(self):
        db.session.add(
            User("Johnny",
                 "john@doe.com",
                 "johnny"
            )
        )

        db.session.commit()
        users = db.session.query(User).all()
        print(users)
        for user in users:
            self.assertEquals(user.role, 'user')

    def test_task_template_displays_logged_in_user_name(self):
        self.register('testuser1', 'test1@gmail.com', '111111', '111111')
        self.login('testuser1', '111111')
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'testuser1', response.data)

    def test_user_redirected_to_login_after_successful_registration(self):
        response = self.register('testuser1', 'test1@gmail.com', '111111', '111111')
        self.assertIn(b'Please login to access your task list.', response.data)

    #def test_duplicate_user_registeration_throws_error(self):
    #    self.register('takutaku', 'taku@takkun.com', 'ohmondieu', 'ohmondieu')
    #    response = self.register('takutaku', 'taku@takkun.com', 'ohmondieu', 'ohmondieu')
    #    self.assertIn(b'That username and/or email already exist.', response.data)


    #def test_user_login_field_errors(self):

    #def test_string_representation_of_the_user_object(self):


if __name__ == '__main__':
    unittest.main()
