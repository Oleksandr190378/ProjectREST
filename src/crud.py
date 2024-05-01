from sqlalchemy import or_, and_
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from src import schemas
from src.database import models
from src.database.models import User
from datetime import date
from sqlalchemy import func


class ResponseValidationError(Exception):
    pass


async def get_contact(db: Session, contact_id: int,  user: User):
    """
    Retrieves a contact from the database based on the provided contact ID and user.

    Args:
        db (Session): The database session.
        contact_id (int): The ID of the contact to retrieve.
        user (User): The user associated with the contact.

    Returns:
        Contact: The contact object corresponding to the provided contact ID and user, or None if not found.
    """
    result = db.execute(select(models.Contact).where(and_(models.Contact.id == contact_id,
                                                          models.Contact.user_id == user.id)))
    return result.scalars().first()


async def get_contact_by_email(db: Session, email: str, user: User):
    """
    Retrieves a contact from the database based on the provided email and user.

    Args:
        db (Session): The database session.
        email (str): The email of the contact to retrieve.
        user (User): The user associated with the contact.

    Returns:
        Contact: The contact object corresponding to the provided email and user, or None if not found.
    """
    result = db.execute(select(models.Contact).where(and_(models.Contact.email == email,
                                                          models.Contact.user_id == user.id)))
    return result.scalars().first()


async def get_contact_by_phone(db: Session, phone_number: str, user: User):
    result = db.execute(select(models.Contact).where(and_(models.Contact.phone_number == phone_number,
                                                          models.Contact.user_id == user.id)))
    return result.scalars().first()


async def get_contacts(db: Session, user: User, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of contacts from the database for a specific user.

    Args:
        db (Session): The database session.
        user (User): The user for whom to retrieve the contacts.
        skip (int, optional): The number of contacts to skip. Defaults to 0.
        limit (int, optional): The maximum number of contacts to retrieve. Defaults to 100.

    Returns:
        List[Contact]: A list of contacts for the specified user.
    """
    result = db.execute(select(models.Contact).where(models.Contact.user_id == user.id).offset(skip).limit(limit))
    return result.scalars().all()


async def create_contact(db: Session, user: User, contact: schemas.ContactCreate):
    """
    Creates a new contact in the database.

    Args:
        db (Session): The database session.
        user (User): The user associated with the contact.
        contact (schemas.ContactCreate): The contact data to be created.

    Returns:
        models.Contact: The created contact object.

    Raises:
        None.

    Description:
        This function creates a new contact in the database. It takes in a database session, a user object, and a contact data object. It creates a new contact object using the contact data and associates it with the user. It then adds the contact object to the database, commits the changes, and refreshes the contact object to ensure it has the latest data. Finally, it returns the created contact object.
    """
    db_contact = models.Contact(**contact.model_dump(exclude_unset=True), user=user)
    #db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def update_contact(db: Session, db_contact: models.Contact, contact: schemas.ContactUpdate):
    """
    Update a contact in the database.

    Args:
        db (Session): The database session.
        db_contact (models.Contact): The contact object to be updated.
        contact (schemas.ContactUpdate): The updated contact data.

    Returns:
        models.Contact: The updated contact object.

    Description:
        This function updates a contact in the database. It takes in a database session, a contact object to be updated, and updated contact data. It iterates over the key-value pairs in the updated contact data and sets the corresponding attributes of the contact object. It then commits the changes to the database and refreshes the contact object to ensure it has the latest data. Finally, it returns the updated contact object.

    """
    contact_data = contact.model_dump(exclude_unset=True)
    #contact_data = contact.dict(exclude_unset=True)
    for key, value in contact_data.items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def delete_contact(db: Session, contact_id: int, user: User):
    """
    Deletes a contact from the database.

    Args:
        db (Session): The database session.
        contact_id (int): The ID of the contact to delete.

    Returns:
        Contact: The deleted contact object.

    Description:
        This function deletes a contact from the database based on the provided contact ID. It takes in a database session and the ID of the contact to delete. It retrieves the contact object from the database using the `get_contact` function, deletes it from the session, commits the changes to the database, and returns the deleted contact object.
    """
    db_contact = await get_contact(db, contact_id, user)
    db.delete(db_contact)
    db.commit()
    return db_contact


async def search_contacts(db: Session, first_name: str = None, last_name: str = None,
                          email: str = None):
    """
    A function that searches for contacts based on the provided first name, last name, and email.

    Args:
        db (Session): The database session.
        first_name (str, optional): The first name of the contact to search for. Defaults to None.
        last_name (str, optional): The last name of the contact to search for. Defaults to None.
        email (str, optional): The email of the contact to search for. Defaults to None.

    Returns:
        List[Contact]: A list of contacts that match the search criteria.
    """
    query = select(models.Contact)
    conditions = []
    if first_name:
        conditions.append(models.Contact.first_name == first_name)
    if last_name:
        conditions.append(models.Contact.last_name == last_name)
    if email:
        conditions.append(models.Contact.email == email)
    # Якщо жодна умова не була додана, то піднімаємо помилку ResponseValidationError
    if not conditions:
        raise ResponseValidationError("Please provide at least one search condition.")
    # Якщо хочемо знайти контакти, які відповідають хоча б одній з умов, використовуємо or_
    query = query.where(or_(*conditions))
    result = db.execute(query)
    return result.scalars().all()


async def get_contacts_by_birthday_range(db: Session, start_date: date, end_date: date,
                                         user: User):
    """
    Retrieves contacts from the database based on their birthday range.

    Args:
        db (Session): The database session object.
        start_date (date): The start date of the birthday range.
        end_date (date): The end date of the birthday range.
        user (User): The user object.

    Returns:
        List[Contact]: A list of Contact objects that match the birthday range.
    """
    query = select(models.Contact).where(
        and_(
            func.extract('month', models.Contact.birthday) >= start_date.month,
            func.extract('day', models.Contact.birthday) >= start_date.day,
            func.extract('month', models.Contact.birthday) <= end_date.month,
            func.extract('day', models.Contact.birthday) <= end_date.day,
        )
    )
    if end_date.year > start_date.year:
        # Вибираємо контакти, де місяць та день народження відповідають проміжку часу до кінця року
        first_part_query = select(models.Contact).where(
            and_(
                func.extract('month', models.Contact.birthday) >= start_date.month,
                func.extract('day', models.Contact.birthday) >= start_date.day,
            )
        )
        # Вибираємо контакти, де місяць та день народження відповідають проміжку часу з початку року до кінця проміжку
        second_part_query = select(models.Contact).where(
            and_(
                func.extract('month', models.Contact.birthday) <= end_date.month,
                func.extract('day', models.Contact.birthday) <= end_date.day,
            )
        )
        # Об'єднуємо обидва запити
        query = first_part_query.union(second_part_query)
    else:
        # Вибираємо контакти, де місяць та день народження відповідають проміжку часу наступного тижня
        query = select(models.Contact).where(
            and_(
                func.extract('month', models.Contact.birthday) >= start_date.month,
                func.extract('day', models.Contact.birthday) >= start_date.day,
                func.extract('month', models.Contact.birthday) <= end_date.month,
                func.extract('day', models.Contact.birthday) <= end_date.day,
            )
        )
    result = db.execute(query)
    return result.scalars().all()
