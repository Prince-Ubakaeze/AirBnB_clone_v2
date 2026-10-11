-- AirBnB_clone_v2: isolated MySQL test database setup.
-- Run as an administrative MySQL account (for example: mysql -u root -p).
-- Intentionally does not remove or overwrite existing databases or tables.

CREATE DATABASE IF NOT EXISTS `hbnb_test_db`;

CREATE USER IF NOT EXISTS 'hbnb_test'@'localhost'
    IDENTIFIED BY 'hbnb_test_pwd';

GRANT ALL PRIVILEGES ON `hbnb_test_db`.*
    TO 'hbnb_test'@'localhost';

GRANT SELECT ON `performance_schema`.*
    TO 'hbnb_test'@'localhost';

FLUSH PRIVILEGES;
