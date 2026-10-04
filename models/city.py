#!/usr/bin/python3
"""Defines the City model."""
from os import getenv

from sqlalchemy import Column, ForeignKey, String

from models.base_model import Base, BaseModel


class City(BaseModel, Base):
    """City model."""

    __tablename__ = 'cities'

    if getenv('HBNB_TYPE_STORAGE') == 'db':
        state_id = Column(
            String(60),
            ForeignKey('states.id'),
            nullable=False
        )
        name = Column(String(128), nullable=False)
    else:
        state_id = ''
        name = ''
