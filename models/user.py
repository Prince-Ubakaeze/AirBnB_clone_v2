#!/usr/bin/python3
"""User model and related places/reviews."""
import os

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from models.base_model import BaseModel, Base


class User(BaseModel, Base):
    """An account holder."""

    __tablename__ = 'users'
    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        email = Column(String(128), nullable=False)
        password = Column(String(128), nullable=False)
        first_name = Column(String(128), nullable=True)
        last_name = Column(String(128), nullable=True)
        places = relationship('Place', back_populates='user',
                              cascade='all, delete-orphan')
        reviews = relationship('Review', back_populates='user',
                               cascade='all, delete-orphan')
    else:
        email = ''
        password = ''
        first_name = ''
        last_name = ''
