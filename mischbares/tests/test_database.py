""" testfile to test the database module """

import os
import configparser
import pytest

from mischbares.db.database import Database
from mischbares.db.user import Users

config = configparser.ConfigParser()
config.read(os.path.join("mischbares", "db", "config.ini"))

db  = Database(host=config["database"]["host"],
                port=config["database"]["port"],
                user=config["database"]["user"],
                password=config["database"]["password"],
                database=config["database"]["database"])

def test_connect():
    """Test the connection to the database."""

    # Connect to the database
    db.connect()

    # assert that the connection is not None and of type psycopg2.connection
    assert db.connection is not None and type(db.connection).__name__ == "connection"
    assert db.cursor is not None and type(db.cursor).__name__ == "cursor"

    # Close the connection to the database
    db.close()


def test_execute():
    """Test the execution of SQL statements."""

    # Connect to the database
    db.connect()

    # Execute a SQL statement
    sql = "SELECT * FROM users"
    result = db.execute(sql)

    # assert that the result is not None and of type list
    assert result is not None and type(result).__name__ == "list"

    # Close the connection to the database
    db.close()

def test_get_user():
    """Test the get_user method."""

    # Connect to the database
    db.connect()
    users = Users(db.connection, db.cursor)
    user = users.get_user("frahmanian")

    # Check that the user is not None and of type tuple and has username "frahmanian"
    assert user is not None and type(user).__name__ == "dict" and user["username"] == "frahmanian"

@pytest.mark.dependency()
def test_register_user():
    """Test the register_user method."""

    # Connect to the database
    db.connect()

    users = Users(db.connection, db.cursor)
    assert users.register_user("test_username", "test_fisrt_name", "test_last_name", "test_email",
                        "test_password") is True

    # Check that the user is not None and of type tuple and has username "test_username"
    test_user = users.get_user("test_username")
    assert test_user is not None and type(test_user).__name__ == "dict" and test_user["username"] == "test_username"

    db.close()

def test_login_user():
    """Test the login_user method."""

    # Connect to the database
    db.connect()

    users = Users(db.connection, db.cursor)
    assert users.login_user("test_username", "test_password") is True

    db.close()

@pytest.mark.dependency(depends=["test_register_user"])
def test_delete_user():
    """Test the delete_user method."""

    # Connect to the database
    db.connect()

    users = Users(db.connection, db.cursor)
    assert users.delete_user("test_username") is True

    # Check that the user is None
    test_user = users.get_user("test_username")
    assert test_user is None

    db.close()
