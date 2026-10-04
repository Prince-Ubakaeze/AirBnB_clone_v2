#!/usr/bin/python3
"""Defines the SQLAlchemy database storage engine."""
from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models.amenity import Amenity
from models.base_model import Base
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User


classes = {
    'Amenity': Amenity,
    'City': City,
    'Place': Place,
    'Review': Review,
    'State': State,
    'User': User
}


class DBStorage:
    """Manage storage using a MySQL database."""

    __engine = None
    __session = None

    def __init__(self):
        """Create the SQLAlchemy engine."""
        user = getenv('HBNB_MYSQL_USER')
        password = getenv('HBNB_MYSQL_PWD')
        host = getenv('HBNB_MYSQL_HOST')
        database = getenv('HBNB_MYSQL_DB')

        url = 'mysql+mysqldb://{}:{}@{}/{}'.format(
            user,
            password,
            host,
            database
        )

        self.__engine = create_engine(
            url,
            pool_pre_ping=True
        )

        if getenv('HBNB_ENV') == 'test':
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """Return objects, optionally filtered by class."""
        result = {}

        if isinstance(cls, str):
            cls = classes.get(cls)

        selected = classes.values() if cls is None else [cls]

        for model in selected:
            if model not in classes.values():
                continue

            for obj in self.__session.query(model).all():
                key = '{}.{}'.format(
                    obj.__class__.__name__,
                    obj.id
                )
                result[key] = obj

        return result

    def new(self, obj):
        """Add an object to the current database session."""
        self.__session.add(obj)

    def save(self):
        """Commit changes in the current database session."""
        self.__session.commit()

    def delete(self, obj=None):
        """Delete obj from the current database session."""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """Create tables and initialize the database session."""
        Base.metadata.create_all(self.__engine)

        factory = sessionmaker(
            bind=self.__engine,
            expire_on_commit=False
        )

        self.__session = scoped_session(factory)

    def close(self):
        """Close the current scoped session."""
        if self.__session is not None:
            self.__session.remove()
