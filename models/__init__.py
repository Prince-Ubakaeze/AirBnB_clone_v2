#!/usr/bin/python3
"""Models and environment-configurable storage engine."""
import os

# Keep model exports used by console.py, tests and existing code.
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User

if os.getenv('HBNB_TYPE_STORAGE') == 'db':
    from models.engine.db_storage import DBStorage
    storage = DBStorage()
else:
    from models.engine.file_storage import FileStorage
    storage = FileStorage()

storage.reload()
