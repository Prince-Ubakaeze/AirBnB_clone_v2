#!/usr/bin/python3
"""SQLAlchemy/MySQL engine implementing the same interface as FileStorage."""
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import scoped_session, sessionmaker

from models.base_model import Base


class DBStorage:
    """MySQL-backed storage of all AirBnB model instances."""

    __engine = None
    __session = None

    def __init__(self):
        url = URL.create(
            'mysql+mysqldb',
            username=os.getenv('HBNB_MYSQL_USER'),
            password=os.getenv('HBNB_MYSQL_PWD'),
            host=os.getenv('HBNB_MYSQL_HOST'),
            database=os.getenv('HBNB_MYSQL_DB'),
        )
        self.__engine = create_engine(url, pool_pre_ping=True)
        if os.getenv('HBNB_ENV') == 'test':
            self._load_models()
            Base.metadata.drop_all(self.__engine)

    @staticmethod
    def _load_models():
        """Ensure all table classes are registered with Base.metadata."""
        import models.amenity
        import models.city
        import models.place
        import models.review
        import models.state
        import models.user

    @staticmethod
    def _model_classes():
        """Fetch supported mapped classes after importing their modules."""
        from models.amenity import Amenity
        from models.city import City
        from models.place import Place
        from models.review import Review
        from models.state import State
        from models.user import User
        return (User, State, City, Amenity, Place, Review)

    def all(self, cls=None):
        """Return a dictionary keyed as ClassName.id from the session."""
        classes = self._model_classes()
        if isinstance(cls, str):
            cls = next((candidate for candidate in classes
                        if candidate.__name__ == cls), None)
            if cls is None:
                return {}
        targets = classes if cls is None else (cls,)
        objects = {}
        for model in targets:
            for obj in self.__session.query(model).all():
                objects['{}.{}'.format(type(obj).__name__, obj.id)] = obj
        return objects

    def new(self, obj):
        """Add an object to the current SQL session."""
        self.__session.add(obj)

    def save(self):
        """Commit the current SQL session."""
        self.__session.commit()

    def delete(self, obj=None):
        """Delete an object from the current SQL session, if provided."""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """Create database tables and configure thread-local sessions."""
        self._load_models()
        Base.metadata.create_all(self.__engine)
        factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        self.__session = scoped_session(factory)
