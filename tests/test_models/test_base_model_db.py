#!/usr/bin/python3
"""DBStorage-specific BaseModel tests."""
import unittest
from datetime import datetime
from os import getenv

from models.base_model import BaseModel


@unittest.skipUnless(
    getenv('HBNB_TYPE_STORAGE') == 'db',
    'BaseModel DB tests require DBStorage'
)
class TestBaseModelDB(unittest.TestCase):
    """Test BaseModel behavior with DBStorage enabled."""

    def test_id_is_string(self):
        """A new model has a string id."""
        obj = BaseModel()

        self.assertIs(type(obj.id), str)
        self.assertTrue(len(obj.id) > 0)

    def test_created_at_datetime(self):
        """created_at is a datetime."""
        obj = BaseModel()

        self.assertIsInstance(obj.created_at, datetime)

    def test_updated_at_datetime(self):
        """updated_at is a datetime."""
        obj = BaseModel()

        self.assertIsInstance(obj.updated_at, datetime)

    def test_to_dict(self):
        """to_dict returns serializable model fields."""
        obj = BaseModel()
        dictionary = obj.to_dict()

        self.assertEqual(
            dictionary['__class__'],
            'BaseModel'
        )

        self.assertIs(type(dictionary['created_at']), str)
        self.assertIs(type(dictionary['updated_at']), str)

    def test_kwargs_round_trip(self):
        """A dictionary recreates the model correctly."""
        obj = BaseModel()
        dictionary = obj.to_dict()

        copy = BaseModel(**dictionary)

        self.assertEqual(copy.id, obj.id)
        self.assertEqual(copy.created_at, obj.created_at)
        self.assertEqual(copy.updated_at, obj.updated_at)

    def test_extra_kwargs(self):
        """DB models accept additional keyword attributes."""
        obj = BaseModel(Name='test')

        self.assertEqual(obj.Name, 'test')

    def test_save_updates_timestamp(self):
        """save() changes updated_at."""
        obj = BaseModel()
        previous = obj.updated_at

        obj.save()

        self.assertGreaterEqual(
            obj.updated_at,
            previous
        )


if __name__ == '__main__':
    unittest.main()
