# AirBnB_clone_v2: all five mandatory DBStorage tasks + SQL setup scripts

This folder contains ACTUAL source files, not placeholder examples. It is an overlay for your existing `AirBnB_clone_v2` repo, not a standalone clone. It preserves your original `console.py`, `file_storage.py`, and test suite.

## The file locations the checker expects

At repository ROOT, next to console.py:
- `setup_mysql_dev.sql` (creates hbnb_dev_db and grants to hbnb_dev)
- `setup_mysql_test.sql` (creates hbnb_test_db and grants to hbnb_test)

Inside `models/`:
- `__init__.py`, `base_model.py`, `state.py`, `city.py`, `user.py`, `place.py`, `review.py`, `amenity.py`

Inside `models/engine/`:
- `db_storage.py`

## One-time installation in Git Bash

```bash
cd ~/developer/AirBnB_clone_v2
python3 -m zipfile -e ~/Downloads/AirBnB_clone_v2_checker_ready.zip .
python3 AirBnB_clone_v2_checker_ready/install.py .
python3 -m compileall -q models
```

The installer makes a unique timestamped backup for any file replaced. It will not overwrite console.py or file_storage.py. Inspect `git diff` before committing, especially if you have custom changes in model files.

## MUST DO for the online checker

```bash
git add setup_mysql_dev.sql setup_mysql_test.sql models/__init__.py models/base_model.py models/state.py models/city.py models/user.py models/place.py models/review.py models/amenity.py models/engine/db_storage.py
git commit -m "Implement AirBnB MySQL DBStorage models and SQL setup"
git push origin master
```

If the files were already committed, `git commit` may say there is nothing to commit; check `git status` and push as appropriate. The online checker reads the uploaded GitHub branch. Merely copying files locally or running the SQL is not enough to fix a `Missing: setup_mysql_dev.sql` checker message.

## Local database setup is optional for submission, required for MySQL tests

The SQL scripts need a running MySQL Server, MySQL admin credentials, and the MySQL CLI (or another SQL client) before they can be executed locally. If `mysql: command not found`, you can STILL commit and push these source files to GitHub. Do NOT bypass Windows security settings just for this.

```bash
mysql -u root -p < setup_mysql_dev.sql
mysql -u root -p < setup_mysql_test.sql
```

Default MySQL accounts in the scripts:
- hbnb_dev / hbnb_dev_pwd / hbnb_dev_db
- hbnb_test / hbnb_test_pwd / hbnb_test_db

Do not set `HBNB_ENV=test` when pointing at valuable data. The project's DBStorage intentionally drops its mapped tables in that mode.

## Limits

Since your actual current repo files were not provided, the overlay is tested independently using SQLite-backed SQLAlchemy and a FileStorage mock; running MySQL integration tests and verifying the console against your exact existing console.py remain necessary before claiming full checker compliance.
