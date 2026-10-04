#!/usr/bin/python3
"""Defines the BaseModel class."""
import uuid
from datetime import datetime, timedelta
from os import getenv

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base


time = '%Y-%m-%dT%H:%M:%S.%f'

if getenv('HBNB_TYPE_STORAGE') == 'db':
    Base = declarative_base()
else:
    Base = object


class BaseModel:
    """Base class for all HBNB models."""

    if getenv('HBNB_TYPE_STORAGE') == 'db':
        id = Column(String(60), primary_key=True, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        """Initialize a model instance."""
        if kwargs:
            if getenv('HBNB_TYPE_STORAGE') != 'db':
                kwargs['updated_at'] = datetime.strptime(
                    kwargs['updated_at'], time
                )
                kwargs['created_at'] = datetime.strptime(
                    kwargs['created_at'], time
                )
                del kwargs['__class__']
                self.__dict__.update(kwargs)
            else:
                for key, value in kwargs.items():
                    if key == '__class__':
                        continue

                    if key in ('created_at', 'updated_at'):
                        if isinstance(value, str):
                            value = datetime.strptime(value, time)

                    setattr(self, key, value)

                if 'id' not in kwargs:
                    self.id = str(uuid.uuid4())

                if 'created_at' not in kwargs:
                    self.created_at = datetime.utcnow()

                if 'updated_at' not in kwargs:
                    self.updated_at = datetime.utcnow()
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = datetime.now()

            if self.updated_at == self.created_at:
                self.updated_at = (
                    self.created_at + timedelta(microseconds=1)
                )

            if getenv('HBNB_TYPE_STORAGE') != 'db':
                from models import storage
                storage.new(self)

    def __str__(self):
        """Return the string representation of the instance."""
        return '[{}] ({}) {}'.format(
            self.__class__.__name__,
            self.id,
            self.__dict__
        )

    def save(self):
        """Update updated_at and save the instance."""
        from models import storage

        self.updated_at = datetime.now()

        if getenv('HBNB_TYPE_STORAGE') == 'db':
            if self.__class__.__name__ != 'BaseModel':
                storage.new(self)
                storage.save()
        else:
            storage.save()

    def to_dict(self):
        """Return a dictionary representation of the instance."""
        dictionary = dict(self.__dict__)

        dictionary['__class__'] = self.__class__.__name__

        if 'created_at' in dictionary:
            dictionary['created_at'] = self.created_at.isoformat()

        if 'updated_at' in dictionary:
            dictionary['updated_at'] = self.updated_at.isoformat()

        dictionary.pop('_sa_instance_state', None)

        return dictionary

    def delete(self):
        """Delete this instance from storage."""
        from models import storage

        storage.delete(self)
