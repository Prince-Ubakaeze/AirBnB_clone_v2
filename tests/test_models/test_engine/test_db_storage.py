#!/usr/bin/python3
"""Unit tests for the DBStorage class."""
import os
import unittest

from models.engine.db_storage import DBStorage


@unittest.skipUnless(
    os.getenv('HBNB_TYPE_STORAGE') == 'db',
    'DBStorage tests require HBNB_TYPE_STORAGE=db'
)
class TestDBStorage(unittest.TestCase):
    """Tests for DBStorage."""

    def test_db_storage_class(self):
        """DBStorage should be instantiable."""
        self.assertIsInstance(DBStorage(), DBStorage)

    def test_all_method_exists(self):
        """DBStorage should implement all()."""
        self.assertTrue(hasattr(DBStorage, 'all'))
        self.assertTrue(callable(DBStorage.all))

    def test_new_method_exists(self):
        """DBStorage should implement new()."""
        self.assertTrue(hasattr(DBStorage, 'new'))
        self.assertTrue(callable(DBStorage.new))

    def test_save_method_exists(self):
        """DBStorage should implement save()."""
        self.assertTrue(hasattr(DBStorage, 'save'))
        self.assertTrue(callable(DBStorage.save))

    def test_delete_method_exists(self):
        """DBStorage should implement delete()."""
        self.assertTrue(hasattr(DBStorage, 'delete'))
        self.assertTrue(callable(DBStorage.delete))

    def test_reload_method_exists(self):
        """DBStorage should implement reload()."""
        self.assertTrue(hasattr(DBStorage, 'reload'))
        self.assertTrue(callable(DBStorage.reload))


if __name__ == '__main__':
    unittest.main()
