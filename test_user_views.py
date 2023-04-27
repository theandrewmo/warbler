"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from flask_bcrypt import generate_password_hash

from models import db, User, Message, Follows
from forms import UserAddForm

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewsTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()
        self.testuser = User.signup(username='testuser',
                                    email='test@test.com',
                                    password='testuser',
                                    image_url=None)
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        self.u1 = User.signup('abc', 'test1@test.com', 'password', None)
        self.u1_id = 778
        self.u1.id = self.u1_id
        self.u2 = User.signup('efg', 'test2@test.com', 'password', None)
        self.u2_id = 884
        self.u2.id = self.u2_id
        self.u3 = User.signup('hij', 'test3@test.com', 'password', None)
        self.u4 = User.signup('testing', 'test4@test.com', 'password', None)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_index(self):
        """ ensure index returns a valid status code and responds with correct data """

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'signup', response.data)
        self.assertNotIn(b'log out', response.data)

    def test_signup(self):
        """ ensures signup route returns valid status code """

        response = self.client.get('/signup')
        self.assertIn(b'signup', response.data)

        with self.client:
            form_data = {
                'username': 'test_user',
                'password': 'test_password',
                'email': 'test_user@test.com',
                'image_url': ''
            }
        response = self.client.post('/signup', data=form_data, follow_redirects=False)

