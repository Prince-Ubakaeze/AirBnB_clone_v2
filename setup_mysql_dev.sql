-- AirBnB_clone_v2: local development MySQL database setup.
-- Run as an administrative MySQL account (for example: mysql -u root -p).
-- Intentionally does not remove or overwrite existing databases or tables.

CREATE DATABASE IF NOT EXISTS `hbnb_dev_db`;

CREATE USER IF NOT EXISTS 'hbnb_dev'@'localhost'
    IDENTIFIED BY 'hbnb_dev_pwd';

GRANT ALL PRIVILEGES ON `hbnb_dev_db`.*
    TO 'hbnb_dev'@'localhost';

GRANT SELECT ON `performance_schema`.*
    TO 'hbnb_dev'@'localhost';

FLUSH PRIVILEGES;
