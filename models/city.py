#!/usr/bin/python3
"""City model and its DBStorage relationships."""
import os

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from models.base_model import BaseModel, Base


class City(BaseModel, Base):
    """A city located in a state."""

    __tablename__ = 'cities'
    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        name = Column(String(128), nullable=False)
        state_id = Column(String(60), ForeignKey('states.id'), nullable=False)
        state = relationship('State', back_populates='cities')
        places = relationship('Place', back_populates='cities',
                              cascade='all, delete-orphan')
    else:
        name = ''
        state_id = ''
