#!/usr/bin/python3
"""Tests for the HBNB command interpreter."""
import os
import unittest
from io import StringIO
from os import getenv
from unittest.mock import patch

from console import HBNBCommand
from models import storage
from models.city import City
from models.place import Place
from models.state import State
from models.user import User


@unittest.skipIf(
    getenv('HBNB_TYPE_STORAGE') == 'db',
    'FileStorage console tests'
)
class TestConsoleFileStorage(unittest.TestCase):
    """Test console create functionality with FileStorage."""

    def setUp(self):
        """Reset FileStorage before each test."""
        objects = getattr(storage, '_FileStorage__objects', None)
        if objects is not None:
            objects.clear()

        try:
            os.remove('file.json')
        except FileNotFoundError:
            pass

    def tearDown(self):
        """Clean FileStorage after each test."""
        objects = getattr(storage, '_FileStorage__objects', None)
        if objects is not None:
            objects.clear()

        try:
            os.remove('file.json')
        except FileNotFoundError:
            pass

    def run_command(self, command):
        """Run one console command and return its output."""
        with patch('sys.stdout', new=StringIO()) as output:
            HBNBCommand().onecmd(command)

        return output.getvalue().strip()

    def test_create_state_regular(self):
        """Test regular create State command."""
        state_id = self.run_command('create State')

        self.assertTrue(state_id)

        key = 'State.{}'.format(state_id)
        self.assertIn(key, storage.all(State))
        self.assertIsInstance(storage.all(State)[key], State)

    def test_create_state_with_name(self):
        """Test create State with a string parameter."""
        state_id = self.run_command(
            'create State name="California"'
        )

        key = 'State.{}'.format(state_id)
        state = storage.all(State)[key]

        self.assertEqual(state.name, 'California')

    def test_create_city_multiple_parameters(self):
        """Test create City with multiple parameters."""
        state_id = self.run_command(
            'create State name="California"'
        )

        city_id = self.run_command(
            'create City state_id="{}" name="Fremont"'.format(
                state_id
            )
        )

        key = 'City.{}'.format(city_id)
        city = storage.all(City)[key]

        self.assertEqual(city.state_id, state_id)
        self.assertEqual(city.name, 'Fremont')

    def test_create_city_underscore_conversion(self):
        """Test underscores become spaces in strings."""
        state_id = self.run_command(
            'create State name="California"'
        )

        city_id = self.run_command(
            'create City state_id="{}" '
            'name="San_Francisco"'.format(state_id)
        )

        city = storage.all(City)['City.{}'.format(city_id)]

        self.assertEqual(city.name, 'San Francisco')
        self.assertEqual(city.state_id, state_id)

    def test_create_complete_place(self):
        """Test strings, integers and floats during creation."""
        state_id = self.run_command(
            'create State name="California"'
        )

        city_id = self.run_command(
            'create City state_id="{}" '
            'name="San_Francisco_is_super_cool"'.format(
                state_id
            )
        )

        user_id = self.run_command(
            'create User email="my@me.com" password="pwd" '
            'first_name="FN" last_name="LN"'
        )

        place_id = self.run_command(
            'create Place city_id="{}" user_id="{}" '
            'name="My_house" '
            'description="no_description_yet" '
            'number_rooms=4 number_bathrooms=1 '
            'max_guest=3 price_by_night=100 '
            'latitude=120.12 longitude=101.4'.format(
                city_id,
                user_id
            )
        )

        key = 'Place.{}'.format(place_id)
        place = storage.all(Place)[key]

        self.assertEqual(place.city_id, city_id)
        self.assertEqual(place.user_id, user_id)
        self.assertEqual(place.name, 'My house')
        self.assertEqual(
            place.description,
            'no description yet'
        )

        self.assertEqual(place.number_rooms, 4)
        self.assertIs(type(place.number_rooms), int)

        self.assertEqual(place.number_bathrooms, 1)
        self.assertIs(type(place.number_bathrooms), int)

        self.assertEqual(place.max_guest, 3)
        self.assertIs(type(place.max_guest), int)

        self.assertEqual(place.price_by_night, 100)
        self.assertIs(type(place.price_by_night), int)

        self.assertEqual(place.latitude, 120.12)
        self.assertIs(type(place.latitude), float)

        self.assertEqual(place.longitude, 101.4)
        self.assertIs(type(place.longitude), float)

        shown = self.run_command(
            'show Place {}'.format(place_id)
        )

        self.assertIn(place_id, shown)
        self.assertIn('My house', shown)


@unittest.skipUnless(
    getenv('HBNB_TYPE_STORAGE') == 'db',
    'DBStorage console tests'
)
class TestConsoleDBStorage(unittest.TestCase):
    """Test console persistence directly against MySQL."""

    def connect(self):
        """Return a raw MySQL connection."""
        import MySQLdb

        return MySQLdb.connect(
            host=getenv('HBNB_MYSQL_HOST'),
            user=getenv('HBNB_MYSQL_USER'),
            passwd=getenv('HBNB_MYSQL_PWD'),
            db=getenv('HBNB_MYSQL_DB')
        )

    def count_rows(self, table):
        """Return number of records in table."""
        db = self.connect()
        cursor = db.cursor()

        cursor.execute(
            'SELECT COUNT(*) FROM {}'.format(table)
        )

        count = cursor.fetchone()[0]

        cursor.close()
        db.close()

        return count

    def run_command(self, command):
        """Run console command and return output."""
        with patch('sys.stdout', new=StringIO()) as output:
            HBNBCommand().onecmd(command)

        return output.getvalue().strip()

    def test_create_state_adds_database_record(self):
        """create State must insert one database row."""
        before = self.count_rows('states')

        self.run_command(
            'create State name="California"'
        )

        after = self.count_rows('states')

        self.assertEqual(after, before + 1)

    def test_create_user_adds_database_record(self):
        """create User must insert one database row."""
        before = self.count_rows('users')

        self.run_command(
            'create User email="my@me.com" password="pwd" '
            'first_name="FN" last_name="LN"'
        )

        after = self.count_rows('users')

        self.assertEqual(after, before + 1)


if __name__ == '__main__':
    unittest.main()
