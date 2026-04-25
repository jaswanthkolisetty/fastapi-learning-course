# =============================================================================
# CHAPTER 4: Database Setup
# =============================================================================
#
# This file handles everything related to the database connection.
# You do not need to edit this file. Just read it and understand what it does.
#
# We use SQLite as the database. SQLite stores everything in a single file
# (database.db) in your project folder. No installation or server needed.
#
# SQLModel is the ORM we use. ORM stands for Object Relational Mapper.
# It lets you work with the database using Python classes instead of raw SQL.
# SQLModel was created by the same person who made FastAPI.
# =============================================================================

from sqlmodel import SQLModel, create_engine, Session


# This is the path to the SQLite database file.
# When you run the app, this file gets created automatically in your project root.
DATABASE_URL = "sqlite:///./database.db"

# `create_engine` sets up the connection to the database.
# `connect_args={"check_same_thread": False}` is required for SQLite only.
# It allows multiple parts of the app to use the same connection safely.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def create_db_and_tables():
    # This reads all SQLModel table classes and creates their tables in the DB
    # if they do not already exist. Safe to call every time the app starts.
    SQLModel.metadata.create_all(engine)


def get_session():
    # This is a "dependency" function. FastAPI calls it automatically for each
    # request that needs a database session (via Depends, covered in items_v3.py).
    #
    # `with Session(engine) as session` opens a DB connection for one request
    # and closes it automatically when the request is done.
    # `yield` hands the session to the route function, then cleanup runs after.
    with Session(engine) as session:
        yield session
