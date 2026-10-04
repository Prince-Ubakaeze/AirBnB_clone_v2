#!/usr/bin/python3
"""Tests for SQLAlchemy model mappings."""
import unittest
from os import getenv

from sqlalchemy import inspect

from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User


@unittest.skipUnless(
    getenv('HBNB_TYPE_STORAGE') == 'db',
    'SQLAlchemy mappings require DBStorage'
)
class TestDatabaseModels(unittest.TestCase):
    """Validate DB model mappings."""

    def test_table_names(self):
        """Models map to the correct tables."""
        self.assertEqual(State.__tablename__, 'states')
        self.assertEqual(City.__tablename__, 'cities')
        self.assertEqual(User.__tablename__, 'users')
        self.assertEqual(Amenity.__tablename__, 'amenities')
        self.assertEqual(Place.__tablename__, 'places')
        self.assertEqual(Review.__tablename__, 'reviews')

    def test_state_columns(self):
        """State has required SQL columns."""
        columns = State.__table__.columns

        self.assertIn('id', columns)
        self.assertIn('name', columns)
        self.assertFalse(columns.name.nullable)

    def test_city_foreign_key(self):
        """City.state_id references State."""
        column = City.__table__.columns.state_id

        targets = {
            str(key.column)
            for key in column.foreign_keys
        }

        self.assertIn('states.id', targets)

    def test_place_foreign_keys(self):
        """Place references City and User."""
        city_targets = {
            str(key.column)
            for key in Place.__table__.columns.city_id.foreign_keys
        }

        user_targets = {
            str(key.column)
            for key in Place.__table__.columns.user_id.foreign_keys
        }

        self.assertIn('cities.id', city_targets)
        self.assertIn('users.id', user_targets)

    def test_review_foreign_keys(self):
        """Review references Place and User."""
        place_targets = {
            str(key.column)
            for key in Review.__table__.columns.place_id.foreign_keys
        }

        user_targets = {
            str(key.column)
            for key in Review.__table__.columns.user_id.foreign_keys
        }

        self.assertIn('places.id', place_targets)
        self.assertIn('users.id', user_targets)

    def test_state_city_relationship(self):
        """State has a cities relationship."""
        relationships = inspect(State).relationships

        self.assertIn('cities', relationships)

    def test_user_relationships(self):
        """User maps places and reviews."""
        relationships = inspect(User).relationships

        self.assertIn('places', relationships)
        self.assertIn('reviews', relationships)

    def test_place_relationships(self):
        """Place maps reviews and amenities."""
        relationships = inspect(Place).relationships

        self.assertIn('reviews', relationships)
        self.assertIn('amenities', relationships)


if __name__ == '__main__':
    unittest.main()
