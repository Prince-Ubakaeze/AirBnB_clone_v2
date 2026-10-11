#!/usr/bin/python3
"""Common model behavior and SQLAlchemy declarative metadata."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class BaseModel:
    """Shared fields and persistence helpers for all models.

    BaseModel is a mixin; it deliberately does not inherit from Base.
    """

    id = Column(String(60), primary_key=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, *args, **kwargs):
        """Create an object from optional serialized attributes."""
        if kwargs:
            for key, value in kwargs.items():
                if key in ('__class__', '_sa_instance_state'):
                    continue
                if key in ('created_at', 'updated_at') and isinstance(value, str):
                    value = datetime.fromisoformat(value)
                setattr(self, key, value)

        # BaseModel is not mapped; class-level SQLAlchemy Column objects
        # must not be mistaken for populated instance attributes.
        if not isinstance(self.__dict__.get('id'), str) or not self.__dict__['id']:
            self.id = str(uuid4())
        if not isinstance(self.__dict__.get('created_at'), datetime):
            self.created_at = datetime.utcnow()
        if not isinstance(self.__dict__.get('updated_at'), datetime):
            self.updated_at = datetime.utcnow()

    def __str__(self):
        """Return the project's existing string representation."""
        return '[{}] ({}) {}'.format(type(self).__name__, self.id,
                                     self.__dict__)

    def save(self):
        """Add or update this object through the selected storage engine."""
        import models
        self.updated_at = datetime.utcnow()
        models.storage.new(self)
        models.storage.save()

    def to_dict(self):
        """Serialize scalar state, excluding SQLAlchemy instrumentation."""
        result = dict(self.__dict__)
        result.pop('_sa_instance_state', None)
        result['__class__'] = type(self).__name__
        for key in ('created_at', 'updated_at'):
            if isinstance(result.get(key), datetime):
                result[key] = result[key].isoformat()
        return result

    def delete(self):
        """Mark this object for deletion in the selected engine."""
        import models
        models.storage.delete(self)
