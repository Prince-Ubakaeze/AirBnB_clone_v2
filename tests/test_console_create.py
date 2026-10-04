#!/usr/bin/python3
"""Tests for console create parameters."""
import os
import unittest
from io import StringIO
from unittest.mock import patch

from console import HBNBCommand
from models import storage
from models.place import Place
from models.state import State


@unittest.skipIf(
    os.getenv('HBNB_TYPE_STORAGE') == 'db',
    'Parameterized create is tested with FileStorage'
)
class TestConsoleCreateParameters(unittest.TestCase):
    """Test create command parameters."""

    def setUp(self):
        """Initialize created objects list."""
        self.created = []

    def tearDown(self):
        """Remove objects created during tests."""
        for obj in self.created:
            storage.delete(obj)
        storage.save()

    def test_create_state_with_name(self):
        """Create State with a string parameter."""
        with patch('sys.stdout', new=StringIO()) as output:
            HBNBCommand().onecmd(
                'create State name="California"'
            )

        obj_id = output.getvalue().strip()
        key = 'State.{}'.format(obj_id)
        obj = storage.all(State).get(key)

        self.assertIsNotNone(obj)
        self.assertEqual(obj.name, 'California')
        self.created.append(obj)

    def test_create_place_parameter_types(self):
        """Create Place with strings, integers and floats."""
        command = (
            'create Place '
            'city_id="0001" '
            'user_id="0001" '
            'name="My_little_house" '
            'number_rooms=4 '
            'latitude=37.773972 '
            'longitude=-122.431297'
        )

        with patch('sys.stdout', new=StringIO()) as output:
            HBNBCommand().onecmd(command)

        obj_id = output.getvalue().strip()
        key = 'Place.{}'.format(obj_id)
        obj = storage.all(Place).get(key)

        self.assertIsNotNone(obj)
        self.assertEqual(obj.name, 'My little house')
        self.assertEqual(obj.number_rooms, 4)
        self.assertIsInstance(obj.number_rooms, int)
        self.assertEqual(obj.latitude, 37.773972)
        self.assertIsInstance(obj.latitude, float)

        self.created.append(obj)


if __name__ == '__main__':
    unittest.main()
