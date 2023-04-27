"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from flask_bcrypt import generate_password_hash

from models import db, User, Message, Follows

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

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test model for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """ does repr work as expected? """

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # repr should return user string
        self.assertEqual(repr(u), f"<User #{u.id}: testuser, test@test.com>")

    def test_is_following(self):
        """ Does is_following successfully detect when user1 is following user2? """

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        follower = Follows(user_being_followed_id = u2.id, user_following_id = u1.id)
        db.session.add(follower)
        db.session.commit()

        self.assertEqual(u1.following[0].id, u2.id)

    def test_is_not_following(self):
        """ Does is_following successfully detect when user1 is not following user2? """

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertFalse(u1.following)


    def test_is_followed_by(self):
        """ Does is_followed_by successfully detect when user2 is followed by user1? """

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        follower = Follows(user_being_followed_id = u2.id, user_following_id = u1.id)
        db.session.add(follower)
        db.session.commit()

        self.assertEqual(u2.followers[0].id, u1.id)


    def test_is_not_followed_by(self):
        """ Does is_followed_by successfully detect when user2 is not followed by user1? """

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertFalse(u2.followers)

    def test_user_signup(self):
        """ Does User.signup successfully create a new user given valid credentials? """

        user = User.signup("test1@test.com", "testuser1", "HASHED_PASSWORD1", "www.fakeimage.com")

        self.assertIsInstance(user, User)

    def test_user_signup_fail(self):
        """ Does User.signup fail to create a new user when validations fail (e.g. uniqueness,non-nullable fields? """

        with self.assertRaises(ValueError) as cm:
            user = User.signup("test1@test.com", "testuser1", "", "www.fakeimage.com")

        self.assertEqual(str(cm.exception), "Password must be non-empty.")

    def test_user_authenticate(self):
        """ Does user.authenticate successfully return a user when given valid username and password? """

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password=generate_password_hash("HASHED_PASSWORD1").decode('utf-8')
        )
        db.session.add(u1)
        db.session.commit()

        user = User.authenticate("testuser1", "HASHED_PASSWORD1")
        
        self.assertIsInstance(user, User)

    def test_user_authenticate_username_fail(self):
        """ Does user.authenticate fail to return a user when given invalid username """

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password=generate_password_hash("HASHED_PASSWORD1").decode('utf-8')
        )
        db.session.add(u1)
        db.session.commit()

        user = User.authenticate("testuser23", "HASHED_PASSWORD1")
        
        self.assertFalse(user)

    def test_user_authenticate_password_fail(self):
        """ Does user.authenticate fail to return a user when given invalid password """

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password=generate_password_hash("HASHED_PASSWORD1").decode('utf-8')
        )
        db.session.add(u1)
        db.session.commit()

        user = User.authenticate("testuser1", "HASHED_PASSWORD123")
        
        self.assertFalse(user)

