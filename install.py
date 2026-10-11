#!/usr/bin/env python3
"""Install the AirBnB checker files into your existing repo, with backups.

Usage from your AirBnB_clone_v2 project root:
    python3 AirBnB_clone_v2_checker_ready/install.py .
"""
from datetime import datetime
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
DEST = Path(sys.argv[1] if len(sys.argv) > 1 else '.').expanduser().resolve()
if not (DEST / 'console.py').is_file() or not (DEST / 'models/engine/file_storage.py').is_file():
    sys.exit('ERROR: Run from the existing AirBnB_clone_v2 checkout root.')
BACKUP = DEST / ('_checker_ready_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
PATHS = [
    'setup_mysql_dev.sql',
    'setup_mysql_test.sql',
    'models/base_model.py',
    'models/state.py',
    'models/city.py',
    'models/user.py',
    'models/place.py',
    'models/review.py',
    'models/amenity.py',
    'models/engine/db_storage.py',
    'models/__init__.py',
]
for rel in PATHS:
    target = DEST / rel
    source = ROOT / rel
    if not source.is_file():
        sys.exit('ERROR: missing source file: ' + str(source))
    if target.is_file():
        old = BACKUP / rel
        old.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, old)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    print('Installed', rel)
if BACKUP.exists():
    print('Backups:', BACKUP)
print('Ready to stage and commit. Does not change console.py or file_storage.py.')
