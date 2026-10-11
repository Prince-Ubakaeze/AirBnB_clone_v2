#!/usr/bin/python3
"""Review model and its DBStorage relationships."""
import os

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from models.base_model import BaseModel, Base


class Review(BaseModel, Base):
    """A review attached to a place and a user."""

    __tablename__ = 'reviews'
    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        text = Column(String(1024), nullable=False)
        place_id = Column(String(60), ForeignKey('places.id'), nullable=False)
        user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
        place = relationship('Place', back_populates='reviews')
        user = relationship('User', back_populates='reviews')
    else:
        text = ''
        place_id = ''
        user_id = ''
