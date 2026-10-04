#!/usr/bin/python3
"""Defines the Review model."""
from os import getenv

from sqlalchemy import Column, ForeignKey, String

from models.base_model import Base, BaseModel


class Review(BaseModel, Base):
    """Review model."""

    __tablename__ = 'reviews'

    if getenv('HBNB_TYPE_STORAGE') == 'db':
        place_id = Column(
            String(60),
            ForeignKey('places.id'),
            nullable=False
        )
        user_id = Column(
            String(60),
            ForeignKey('users.id'),
            nullable=False
        )
        text = Column(String(1024), nullable=False)
    else:
        place_id = ''
        user_id = ''
        text = ''
