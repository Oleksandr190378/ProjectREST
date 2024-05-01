import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import select, or_, and_, func
from sqlalchemy.orm import Session
from src.database.models import User, Contact
from src import schemas
from datetime import date
from src.crud import (
    get_contact, create_contact, update_contact, delete_contact,
    get_contacts,
    search_contacts, get_contacts_by_birthday_range
)


class TestCRUD(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Create a mock database session
        self.db_session = MagicMock(spec=Session)
        # Create a mock user
        self.user = User(id=1, username='testuser')
        # Create a mock contact
        self.contact = Contact(id=1, user_id=self.user.id, first_name='John', last_name='Doe', email='john.doe@example.com')

    async def test_get_contact(self):
        # Mock the query to return the mock contact
        self.db_session.execute.return_value.scalars.return_value.first.return_value = self.contact

        # Call the function being tested
        result = await get_contact(self.db_session, self.contact.id, self.user)
        print(result, self.contact)
        # Assert that the function returns the expected contact
        self.assertEqual(result, self.contact)

    async def test_create_contact(self):

        # Create a mock contact create schema
        contact_create = schemas.ContactCreate(first_name='John', last_name='Doe',
                                               email='john.doe@example.com', phone_number='1234567890',birthday='2000-04-02')

        # Call the function being tested
        result = await create_contact(self.db_session, self.user, contact_create)

        # Assert that the function returns the expected contact
        self.assertEqual(result.first_name, contact_create.first_name)
        self.assertEqual(result.last_name, contact_create.last_name)
        self.assertEqual(result.email, contact_create.email)

    async def test_update_contact(self):

        # Create a mock contact update schema
        contact_update = schemas.ContactUpdate(first_name='Jack', last_name='Black',
                                               email='jack.black@example.com', phone_number='6634567890',
                                               birthday='2005-04-02', completed=True)

        # Call the function being tested
        result = await update_contact(self.db_session, self.contact, contact_update)

        # Assert that the function returns the expected contact
        self.assertEqual(result.first_name, contact_update.first_name)

    async def test_delete_contact(self):
        self.db_session.execute.return_value.scalars.return_value.first.return_value = self.contact

        # Call the function being tested
        result = await delete_contact(self.db_session, self.contact.id, self.user)

        # Assert that the function returns the expected contact
        self.assertEqual(result, self.contact)

    async def test_get_contacts(self):
        # Create a list of mock contacts
        mock_contacts = [Contact(), Contact(), Contact()]

        # Mock the query and all methods
        self.db_session.execute.return_value.scalars.return_value.all.return_value = mock_contacts

        # Call the function being tested
        result = await get_contacts(db=self.db_session, user=self.user, skip=0, limit=100)
        print(result, mock_contacts)
        # Assert that the function returns the expected list of contacts
        self.assertEqual(result, mock_contacts)

    async def test_search_contacts(self):
        # Create a list of mock contacts
        mock_contacts = [Contact(), Contact(), Contact()]

        # Mock the query and all methods
        self.db_session.execute.return_value.scalars.return_value.all.return_value = mock_contacts

        # Call the function being tested with search criteria
        result = await search_contacts(db=self.db_session, first_name="John", last_name="Doe",
                                       email="john.doe@example.com")

        # Assert that the function returns the expected list of contacts
        self.assertEqual(result, mock_contacts)

        # Assert that the execute method was called with the correct query
        self.db_session.execute.assert_called_once()
        query = self.db_session.execute.call_args[0][0]
        self.assertEqual(str(query), str(select(Contact).where(or_(
            Contact.first_name == "John",
            Contact.last_name == "Doe",
            Contact.email == "john.doe@example.com"
        ))))

    async def test_get_contacts_by_birthday_range(self):
        # Create a list of mock contacts
        mock_contacts = [Contact(), Contact(), Contact()]

        # Mock the query and all methods
        self.db_session.execute.return_value.scalars.return_value.all.return_value = mock_contacts

        # Define the birthday range
        start_date = date(2022, 1, 1)
        end_date = date(2022, 12, 31)

        # Call the function being tested with the birthday range
        result = await get_contacts_by_birthday_range(db=self.db_session, start_date=start_date, end_date=end_date,
                                                      user=self.user)

        # Assert that the function returns the expected list of contacts
        self.assertEqual(result, mock_contacts)

        # Assert that the execute method was called with the correct query
        self.db_session.execute.assert_called_once()
        # Since the query is constructed dynamically based on the birthday range, we cannot assert the exact query string
        # Instead, we can check that the query is of the correct type
        query = self.db_session.execute.call_args[0][0]
        expected_query_str = str(select(Contact).where(
            and_(
                func.extract('month', Contact.birthday) >= start_date.month,
                func.extract('day', Contact.birthday) >= start_date.day,
                func.extract('month', Contact.birthday) <= end_date.month,
                func.extract('day', Contact.birthday) <= end_date.day,
            )
        ))
        self.assertEqual(str(query), expected_query_str)

    # Add more async test methods for other CRUD functions...

if __name__ == '__main__':
    unittest.main()