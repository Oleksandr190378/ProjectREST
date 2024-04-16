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
    result = db.execute(select(models.Contact).where(and_(models.Contact.id == contact_id,
                                                          models.Contact.user_id == user.id)))
    return result.scalars().first()


async def get_contact_by_email(db: Session, email: str, user: User):
    result = db.execute(select(models.Contact).where(and_(models.Contact.email == email,
                                                          models.Contact.user_id == user.id)))
    return result.scalars().first()


async def get_contact_by_phone(db: Session, phone_number: str, user: User):
    result = db.execute(select(models.Contact).where(and_(models.Contact.phone_number == phone_number,
                                                          models.Contact.user_id == user.id)))
    return result.scalars().first()


async def get_contacts(db: Session, user: User, skip: int = 0, limit: int = 100):
    result = db.execute(select(models.Contact).where(models.Contact.user_id == user.id).offset(skip).limit(limit))
    return result.scalars().all()


async def create_contact(db: Session, user: User, contact: schemas.ContactCreate):
    db_contact = models.Contact(**contact.model_dump(exclude_unset=True), user=user)
    #db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def update_contact(db: Session, db_contact: models.Contact, contact: schemas.ContactUpdate):
    contact_data = contact.dict(exclude_unset=True)
    for key, value in contact_data.items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def delete_contact(db: Session, contact_id: int):
    db_contact = await get_contact(db, contact_id)
    db.delete(db_contact)
    db.commit()
    return db_contact


async def search_contacts(db: Session, first_name: str = None, last_name: str = None,
                          email: str = None):
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
