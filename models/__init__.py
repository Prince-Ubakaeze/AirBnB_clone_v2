#!/usr/bin/python3
"""Initialize the appropriate HBNB storage engine."""
from os import getenv


if getenv('HBNB_TYPE_STORAGE') == 'db':
    from models.engine.db_storage import DBStorage

    storage = DBStorage()
else:
    from models.engine.file_storage import FileStorage

    storage = FileStorage()

storage.reload()
