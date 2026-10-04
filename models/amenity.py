#!/usr/bin/python3
"""Defines the Amenity model."""
from os import getenv

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from models.base_model import Base, BaseModel


class Amenity(BaseModel, Base):
    """Amenity model."""

    __tablename__ = 'amenities'

    if getenv('HBNB_TYPE_STORAGE') == 'db':
        name = Column(String(128), nullable=False)

        place_amenities = relationship(
            'Place',
            secondary='place_amenity',
            back_populates='amenities'
        )
    else:
        name = ''
