#!/usr/bin/python3
"""Defines the Place model."""
from os import getenv

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Table
)
from sqlalchemy.orm import relationship

from models.base_model import Base, BaseModel


if getenv('HBNB_TYPE_STORAGE') == 'db':
    place_amenity = Table(
        'place_amenity',
        Base.metadata,
        Column(
            'place_id',
            String(60),
            ForeignKey('places.id'),
            primary_key=True,
            nullable=False
        ),
        Column(
            'amenity_id',
            String(60),
            ForeignKey('amenities.id'),
            primary_key=True,
            nullable=False
        )
    )


class Place(BaseModel, Base):
    """Place model."""

    __tablename__ = 'places'

    if getenv('HBNB_TYPE_STORAGE') == 'db':
        city_id = Column(
            String(60),
            ForeignKey('cities.id'),
            nullable=False
        )
        user_id = Column(
            String(60),
            ForeignKey('users.id'),
            nullable=False
        )
        name = Column(String(128), nullable=False)
        description = Column(String(1024), nullable=True)
        number_rooms = Column(Integer, nullable=False, default=0)
        number_bathrooms = Column(Integer, nullable=False, default=0)
        max_guest = Column(Integer, nullable=False, default=0)
        price_by_night = Column(Integer, nullable=False, default=0)
        latitude = Column(Float, nullable=False, default=0)
        longitude = Column(Float, nullable=False, default=0)

        reviews = relationship(
            'Review',
            backref='place',
            cascade='all, delete, delete-orphan'
        )

        amenities = relationship(
            'Amenity',
            secondary=place_amenity,
            back_populates='place_amenities'
        )
    else:
        city_id = ''
        user_id = ''
        name = ''
        description = ''
        number_rooms = 0
        number_bathrooms = 0
        max_guest = 0
        price_by_night = 0
        latitude = 0.0
        longitude = 0.0
        amenity_ids = []

        @property
        def reviews(self):
            """Return reviews belonging to this place."""
            from models import storage
            from models.review import Review

            return [
                review for review in storage.all(Review).values()
                if review.place_id == self.id
            ]

        @property
        def amenities(self):
            """Return amenities associated with this place."""
            from models import storage
            from models.amenity import Amenity

            amenities = []
            all_amenities = storage.all(Amenity)

            for amenity_id in self.amenity_ids:
                key = 'Amenity.{}'.format(amenity_id)

                if key in all_amenities:
                    amenities.append(all_amenities[key])

            return amenities

        @amenities.setter
        def amenities(self, obj):
            """Associate an amenity with this place."""
            from models.amenity import Amenity

            if isinstance(obj, Amenity):
                if obj.id not in self.amenity_ids:
                    self.amenity_ids.append(obj.id)
