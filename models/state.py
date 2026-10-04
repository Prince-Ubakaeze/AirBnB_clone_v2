#!/usr/bin/python3
"""Defines the State model."""
from os import getenv

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from models.base_model import Base, BaseModel


class State(BaseModel, Base):
    """State model."""

    __tablename__ = 'states'

    if getenv('HBNB_TYPE_STORAGE') == 'db':
        name = Column(String(128), nullable=False)
        cities = relationship(
            'City',
            backref='state',
            cascade='all, delete, delete-orphan'
        )
    else:
        name = ''

        @property
        def cities(self):
            """Return cities belonging to this state."""
            from models import storage
            from models.city import City

            return [
                city for city in storage.all(City).values()
                if city.state_id == self.id
            ]
