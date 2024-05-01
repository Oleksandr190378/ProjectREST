from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user from the database based on the provided email.

    Args:
        email (str): The email address of the user to retrieve.
        db (Session): The database session.

    Returns:
        User: The user object corresponding to the provided email.
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:

    """
    Creates a new user in the database.

    Args:
        body (UserModel): The user data to be created.
        db (Session): The database session.

    Returns:
        new user: User"""
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    # Use model_dump to get a dictionary representation of the UserModel instance
    user_data = body.model_dump()
    user_data['avatar'] = avatar
    # Create a new User instance using the dictionary
    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Updates the refresh token for a given user and commits the changes to the database.

    Args:
        user (User): The user object to update.
        token (str | None): The new refresh token value. If None, the refresh token will be cleared.
        db (Session): The database session.

    Returns:
        None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Updates the confirmed status of a user with the given email in the database.

    Args:
        email (str): The email of the user to update.
        db (Session): The database session.

    Returns:
        None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Updates the avatar of a user with the given email in the database.

    Args:
        email (str): The email of the user whose avatar is being updated.
        url (str): The URL of the new avatar image.
        db (Session): The database session.

    Returns:
        User:   The  user object """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
