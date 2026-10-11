#!/usr/bin/python3
"""Place model with file-based and SQL many-to-many amenities."""
import os

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from models.base_model import BaseModel, Base


place_amenity = Table(
    'place_amenity', Base.metadata,
    Column('place_id', String(60), ForeignKey('places.id'),
           primary_key=True, nullable=False),
    Column('amenity_id', String(60), ForeignKey('amenities.id'),
           primary_key=True, nullable=False),
)


class Place(BaseModel, Base):
    """A rentable place."""

    __tablename__ = 'places'
    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        city_id = Column(String(60), ForeignKey('cities.id'), nullable=False)
        user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
        name = Column(String(128), nullable=False)
        description = Column(String(1024), nullable=True)
        number_rooms = Column(Integer, nullable=False, default=0)
        number_bathrooms = Column(Integer, nullable=False, default=0)
        max_guest = Column(Integer, nullable=False, default=0)
        price_by_night = Column(Integer, nullable=False, default=0)
        latitude = Column(Float, nullable=True)
        longitude = Column(Float, nullable=True)
        user = relationship('User', back_populates='places')
        # The assignment explicitly calls for the Place -> City name "cities".
        cities = relationship('City', back_populates='places')
        reviews = relationship('Review', back_populates='place',
                               cascade='all, delete-orphan')
        amenities = relationship(
            'Amenity', secondary=place_amenity,
            back_populates='place_amenities', viewonly=False)
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
            """Review objects linked to this place in FileStorage."""
            from models import storage
            from models.review import Review
            return [review for review in storage.all().values()
                    if isinstance(review, Review) and review.place_id == self.id]

        @property
        def amenities(self):
            """Amenity objects matching this place's amenity_ids."""
            from models import storage
            from models.amenity import Amenity
            ids = getattr(self, 'amenity_ids', []) or []
            return [amenity for amenity in storage.all().values()
                    if isinstance(amenity, Amenity) and amenity.id in ids]

        @amenities.setter
        def amenities(self, value):
            """Append an Amenity id; ignore other object types."""
            from models.amenity import Amenity
            if not isinstance(value, Amenity):
                return
            if 'amenity_ids' not in self.__dict__:
                self.amenity_ids = list(getattr(self, 'amenity_ids', []) or [])
            if value.id not in self.amenity_ids:
                self.amenity_ids.append(value.id)
