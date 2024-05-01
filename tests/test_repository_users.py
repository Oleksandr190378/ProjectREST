import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import UserModel, UserDb, TokenModel
from src.repository import users


class TestUsersRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Create a mock database session
        self.db_session = MagicMock(spec=Session)
        # Create a mock user model
        self.user_model = UserModel(email='test@example.com', password='test_pas', username='testuser',created_at='2024-03-04')
        # Create a mock user
        self.user = User(id=1, email='test@example.com', password='hashed_pas', avatar=None, refresh_token=None, confirmed=False, username='testuser')

    async def test_get_user_by_email(self):
        # Mock the query to return the mock user
        self.db_session.query(User).filter(User.email == self.user.email).first.return_value = self.user

        # Call the function being tested
        result = await users.get_user_by_email(self.user.email, self.db_session)

        # Assert that the function returns the expected user
        self.assertEqual(result, self.user)
        # Assert that the mock methods were called with the correct arguments
        self.db_session.query(User).filter(User.email == self.user.email).first.assert_called_once()

    async def test_create_user(self):

        result = await users.create_user(self.user_model, self.db_session)

        # Assert that the function returns a User object
        self.assertIsInstance(result, User)
        # Assert that the user has the correct attributes
        self.assertEqual(result.email, self.user_model.email)
        self.assertEqual(result.username, self.user_model.username)
        # Assert that the user was added to the session and committed

    async def test_update_token(self):
        # Call the function being tested
        await users.update_token(self.user, 'new_token', self.db_session)

        # Assert that the refresh token was updated
        self.assertEqual(self.user.refresh_token, 'new_token')
        # Assert that the session was committed
        self.db_session.commit.assert_called_once()

    async def test_confirmed_email(self):
        # Mock the get_user_by_email function
        with patch.object(users, 'get_user_by_email', return_value=self.user):
            # Call the function being tested
            await users.confirmed_email(self.user.email, self.db_session)

        # Assert that the confirmed status was updated
        self.assertTrue(self.user.confirmed)
        # Assert that the session was committed
        self.db_session.commit.assert_called_once()

    async def test_update_avatar(self):
        # Mock the get_user_by_email function
        with patch.object(users, 'get_user_by_email', return_value=self.user):
            # Call the function being tested
            result = await users.update_avatar(self.user.email, 'new_avatar_url', self.db_session)

        # Assert that the function returns the updated user
        self.assertEqual(result, self.user)
        # Assert that the avatar was updated
        self.assertEqual(self.user.avatar, 'new_avatar_url')
        # Assert that the session was committed
        self.db_session.commit.assert_called_once()

# Run the tests
if __name__ == '__main__':
    unittest.main()