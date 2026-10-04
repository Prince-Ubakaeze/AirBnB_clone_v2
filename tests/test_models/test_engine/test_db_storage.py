#!/usr/bin/python3
"""Tests for DBStorage."""
import unittest
from os import getenv

from models import storage
from models.state import State


@unittest.skipUnless(
    getenv('HBNB_TYPE_STORAGE') == 'db',
    'DBStorage tests require HBNB_TYPE_STORAGE=db'
)
class TestDBStorage(unittest.TestCase):
    """Functional tests for DBStorage."""

    def test_storage_type(self):
        """Global storage must be DBStorage."""
        from models.engine.db_storage import DBStorage

        self.assertIsInstance(storage, DBStorage)

    def test_all_returns_dictionary(self):
        """all() must return a dictionary."""
        self.assertIsInstance(storage.all(), dict)

    def test_new_and_save(self):
        """new() and save() must persist an object."""
        state = State(name='California')

        storage.new(state)
        storage.save()

        key = 'State.{}'.format(state.id)

        self.assertIn(key, storage.all(State))
        self.assertEqual(
            storage.all(State)[key].name,
            'California'
        )

        storage.delete(state)
        storage.save()

    def test_all_with_class_name(self):
        """all() accepts a class name string."""
        state = State(name='Nevada')

        storage.new(state)
        storage.save()

        key = 'State.{}'.format(state.id)

        self.assertIn(key, storage.all('State'))

        storage.delete(state)
        storage.save()

    def test_delete(self):
        """delete() removes a persisted object."""
        state = State(name='Arizona')

        storage.new(state)
        storage.save()

        key = 'State.{}'.format(state.id)

        self.assertIn(key, storage.all(State))

        storage.delete(state)
        storage.save()

        self.assertNotIn(key, storage.all(State))


if __name__ == '__main__':
    unittest.main()
