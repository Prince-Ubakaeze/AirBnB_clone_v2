#!/usr/bin/python3
"""Defines the BaseModel class."""
import uuid
from datetime import datetime, timedelta
from os import getenv

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class BaseModel:
    """Base class for all HBNB models."""

    if getenv('HBNB_TYPE_STORAGE') == 'db':
        id = Column(String(60), primary_key=True, nullable=False)
        created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
        updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        """Initialize a new model."""
        if kwargs:
            for key, value in kwargs.items():
                if key == '__class__':
                    continue

                if key in ('created_at', 'updated_at'):
                    if isinstance(value, str):
                        value = datetime.strptime(
                            value, '%Y-%m-%dT%H:%M:%S.%f'
                        )

                setattr(self, key, value)

            if 'id' not in kwargs:
                self.id = str(uuid.uuid4())

            if 'created_at' not in kwargs:
                self.created_at = datetime.now()

            if 'updated_at' not in kwargs:
                self.updated_at = datetime.now()
        else:
            from models import storage

            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = datetime.now()

            if self.updated_at == self.created_at:
                self.updated_at = (
                    self.created_at + timedelta(microseconds=1)
                )

            storage.new(self)

    def __str__(self):
        """Return string representation of the instance."""
        cls = self.__class__.__name__
        return '[{}] ({}) {}'.format(cls, self.id, self.__dict__)

    def save(self):
        """Update updated_at and save the instance."""
        from models import storage

        self.updated_at = datetime.now()
        storage.save()

    def to_dict(self):
        """Return dictionary representation of the instance."""
        dictionary = dict(self.__dict__)
        dictionary['__class__'] = self.__class__.__name__

        if 'created_at' in dictionary:
            dictionary['created_at'] = self.created_at.isoformat()

        if 'updated_at' in dictionary:
            dictionary['updated_at'] = self.updated_at.isoformat()

        dictionary.pop('_sa_instance_state', None)
        return dictionary
