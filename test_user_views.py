"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from flask_bcrypt import generate_password_hash

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app, CURR_USER_KEY

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
        self.assertNotIn(b'logout', response.data)

    def test_signup(self):
        """ ensures signup route returns signup page as get and signs up new user as post """

        response = self.client.get('/signup')
        self.assertIn(b'signup', response.data)

        with self.client:
            form_data = {
                'username': 'test_user',
                'password': 'test_password',
                'email': 'test_user@test.com',
                'image_url': ''
            }
        response = self.client.post('/signup', data=form_data, follow_redirects=True)
        self.assertIn(b'logout', response.data)

    def test_login(self):
        """ ensures login shows login form or returns the logged in page if logged in already"""

        response = self.client.get('/login')
        self.assertIn(b'login', response.data)

        with self.client:
            form_data = {
                'username': 'testuser',
                'password': 'testuser'
            }

        response = self.client.post('/login', data=form_data, follow_redirects=True)
        self.assertIn(b'logout', response.data)

    def test_logout(self):
        """ ensures logout route returns valid status code and logs user out """

        response = self.client.get('/logout', follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data)

    def test_users(self):
        """ ensure users route returns valid status code and current user in database """  

        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'@testuser', response.data)

    def test_users_id(self):
        """ ensures users/user_id route returns valid status code and correct user """

        response = self.client.get(f'/users/{self.testuser.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'@testuser', response.data)

    def test_users_id_following(self):
        """ ensures users/user_id/following route returns valid status and people user is following,
            if not logged in or not user then returns unauthorized """

        followingTest = Follows(user_being_followed_id=884, user_following_id=778)
        db.session.add(followingTest)
        db.session.commit()
        
        response = self.client.get(f'/users/{self.u1.id}/following', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'unauthorized', response.data)  

        with self.client as c: 
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f'/users/{self.u1_id}/following', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@efg', resp.data)

    def test_users_id_followers(self):
        """ ensures users/user_id/followers route returns valid status and followers,
            if not logged in or not user then returns unauthorized """

        followersTest = Follows(user_being_followed_id=884, user_following_id=778)
        db.session.add(followersTest)
        db.session.commit()
        
        response = self.client.get(f'/users/{self.u2.id}/followers', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'unauthorized', response.data)  

        with self.client as c: 
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id

            resp = c.get(f'/users/{self.u2_id}/followers')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@abc', resp.data)

    def test_add_follow(self):
        """ ensures users/follow/user_id route returns valid status and follows,
            if not logged in or not user then returns unauthorized """
        
        response = self.client.post(f'/users/follow/{self.u2.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'unauthorized', response.data)  

        with self.client as c: 
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f'/users/follow/{self.u2_id}', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@efg', resp.data)

    def test_stop_following(self):
        """ ensures users/follow/user_id route returns valid status and stops following,
            if not logged in or not user then returns unauthorized """
        
        followersTest = Follows(user_being_followed_id=884, user_following_id=778)
        db.session.add(followersTest)
        db.session.commit()

        response = self.client.post(f'/users/stop-following/{self.u2.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'unauthorized', response.data)  

        with self.client as c: 
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f'/users/stop-following/{self.u2_id}', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(b'@efg', resp.data)

    def test_profile(self):
        """ ensures profile route returns profile page as get and updates profile as a post, 
            if not logged in should return with unathorized """

        response = self.client.get('/users/profile', follow_redirects=True)
        self.assertIn(b'unauthorized', response.data)
        response = self.client.post('/users/profile', follow_redirects=True)
        self.assertIn(b'unauthorized', response.data)

        with self.client as c: 
            c.form_data = {
                    'username': 'testuser',
                    'email': 'test@test.com',
                    'image_url': '',
                    'header_image_url': '',
                    'bio': 'testbio',
                    'password': 'testuser',

                }
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 8989
                
            resp = c.post(f'/users/profile', data=c.form_data, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'testbio', resp.data)

    def test_delete(self):
        """ ensures deletes user if authorized, returns unauthorized if not logged in """

        response = self.client.post('/users/delete', follow_redirects=True)
        self.assertIn(b'unauthorized', response.data)

        with self.client as c: 
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 8989
                
            resp = c.post(f'/users/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'signup', resp.data)

            users = User.query.all()
            user_ids = [user.id for user in users]
            self.assertNotIn(8989, user_ids)

    