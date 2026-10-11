#!/usr/bin/python3
"""State model with DBStorage and FileStorage-compatible cities."""
import os

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from models.base_model import BaseModel, Base


class State(BaseModel, Base):
    """A state containing cities."""

    __tablename__ = 'states'
    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        name = Column(String(128), nullable=False)
        cities = relationship('City', back_populates='state',
                              cascade='all, delete-orphan')
    else:
        name = ''

        @property
        def cities(self):
            """The associated City objects in FileStorage."""
            from models import storage
            from models.city import City
            return [city for city in storage.all().values()
                    if isinstance(city, City) and city.state_id == self.id]
