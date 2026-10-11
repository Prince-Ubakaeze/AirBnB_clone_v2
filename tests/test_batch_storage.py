"""Offline smoke tests for the five DBStorage tasks (no MySQL required)."""
import os
import subprocess
import sys
import textwrap
import unittest


class StorageBatchTests(unittest.TestCase):
    def run_script(self, script):
        proc = subprocess.run(
            [sys.executable, '-c', textwrap.dedent(script)],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True, text=True, timeout=35,
            env={**os.environ, 'PYTHONPATH': os.getcwd()},
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + '\n' + proc.stderr)

    def test_db_storage_sqlite_orm_smoke(self):
        self.run_script(r'''
            import os
            import sqlalchemy
            from sqlalchemy.orm import DeclarativeMeta
            real_engine = sqlalchemy.create_engine
            def sqlite_engine(url, **opts):
                assert str(url).startswith('mysql+mysqldb://')
                assert opts.get('pool_pre_ping') is True
                return real_engine('sqlite+pysqlite:///:memory:', **opts)
            sqlalchemy.create_engine = sqlite_engine
            os.environ['HBNB_TYPE_STORAGE'] = 'db'
            os.environ.pop('HBNB_ENV', None)
            from models import Amenity, City, Place, Review, State, User, storage
            from models.base_model import BaseModel, Base
            assert not isinstance(BaseModel, DeclarativeMeta)
            assert {'states', 'cities', 'users', 'places', 'reviews',
                    'amenities', 'place_amenity'} <= set(Base.metadata.tables)
            state = State(name='California')
            user = User(email='a@example.com', password='secret')
            state.save(); user.save()
            city = City(name='San Francisco', state_id=state.id)
            city.save()
            place = Place(name='House 1', user_id=user.id, city_id=city.id)
            place.save()
            rev = Review(text='Great', user_id=user.id, place_id=place.id)
            rev.save()
            amenity = Amenity(name='Wi-Fi')
            amenity.save()
            place.amenities.append(amenity)
            storage.save()
            assert place.cities.id == city.id
            assert city.state.id == state.id
            assert place.user.id == user.id
            assert rev.place.id == place.id
            assert rev.user.id == user.id
            assert amenity in place.amenities
            assert place in amenity.place_amenities
            second_amenity = Amenity(name='Cable'); second_amenity.save()
            place.amenities.append(second_amenity)
            storage.save()
            assert len(place.amenities) == 2
            assert len(storage.all()) == 7
            assert len(storage.all('Place')) == 1
            assert len(storage.all(Place)) == 1
            assert storage.all('NonExistent') == {}
            assert '_sa_instance_state' not in place.to_dict()
            assert 'created_at' in place.to_dict()
            # Deleting the state cascades through City, Place, Review
            state.delete()
            storage.save()
            assert storage.all(State) == {}
            assert storage.all(City) == {}
            assert storage.all(Place) == {}
            assert storage.all(Review) == {}
            assert len(storage.all(User)) == 1
            assert len(storage.all(Amenity)) == 2
            # A fresh place/review tests deletion cascade from User.
            state2 = State(name='Maryland'); state2.save()
            city2 = City(name='Baltimore', state_id=state2.id); city2.save()
            place2 = Place(name='House 2', user_id=user.id, city_id=city2.id)
            place2.save()
            review2 = Review(text='Nice', user_id=user.id, place_id=place2.id)
            review2.save()
            user.delete(); storage.save()
            assert storage.all(User) == {}
            assert storage.all(Place) == {}
            assert storage.all(Review) == {}
            print('DBStorage ORM smoke test passed')
        ''')

    def test_file_storage_properties_smoke(self):
        self.run_script(r'''
            import os, sys, types
            os.environ['HBNB_TYPE_STORAGE'] = 'file'
            module = types.ModuleType('models.engine.file_storage')
            class FileStorage:
                def __init__(self): self.objects = {}
                def reload(self): pass
                def new(self, obj):
                    self.objects[type(obj).__name__ + '.' + obj.id] = obj
                def save(self): pass
                def delete(self, obj=None):
                    if obj is not None:
                        self.objects.pop(type(obj).__name__ + '.' + obj.id, None)
                def all(self, cls=None):
                    if cls is None: return self.objects.copy()
                    if isinstance(cls, str):
                        return {k:v for k,v in self.objects.items()
                                if type(v).__name__ == cls}
                    return {k:v for k,v in self.objects.items()
                            if isinstance(v, cls)}
            module.FileStorage = FileStorage
            sys.modules[module.__name__] = module
            from models import State, City, Place, Review, Amenity, storage
            state = State(name='Nevada'); state.save()
            city = City(name='Reno', state_id=state.id); city.save()
            assert state.cities == [city]
            place = Place(name='Test place'); place.save()
            review = Review(text='Lovely', place_id=place.id); review.save()
            assert place.reviews == [review]
            wifi = Amenity(name='Wi-Fi'); wifi.save()
            place.amenities = wifi
            place.amenities = wifi
            place.amenities = 'wrong-type'
            assert place.amenity_ids == [wifi.id]
            assert place.amenities == [wifi]
            other_place = Place()
            assert other_place.amenity_ids == []
            assert other_place.number_rooms == 0
            assert other_place.name == ''
            assert '_sa_instance_state' not in place.to_dict()
            assert '__class__' in place.to_dict()
            place.delete()
            assert storage.all(Place) == {}
            print('FileStorage properties smoke test passed')
        ''')


if __name__ == '__main__':
    unittest.main()
