import sqlite3
from datetime import date


# Database setup: connect to SQLite and initialize required tables
# ---------------------------------------------------------------

def get_db(name="main.db"):
    """
    Connect to the SQLite database and initialize tables if they don't exist.

    Args:
        name (str): Database file name. Defaults to "main.db".

    Returns:
        sqlite3.Connection: Database connection object.
    """
    db = sqlite3.connect(name)
    create_tables(db)
    return db


def create_tables(db):
    """
    Create necessary tables for habits and tracked events if they don't already exist.

    Args:
        db (sqlite3.Connection): Database connection object.
    """
    cur = db.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS habit (
            name TEXT NOT NULL,
            description TEXT,
            period TEXT,
            created_at TEXT DEFAULT (DATE('now')),
            user_name TEXT NOT NULL,
            PRIMARY KEY (name, user_name)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS tracker (
            date TEXT,
            habitName TEXT,
            user_name TEXT,
            mood_before TEXT,
            mood_after TEXT,
            FOREIGN KEY (habitName, user_name) REFERENCES habit(name, user_name)
        )
    ''')

    db.commit()


# Manage habit data: create new habits, log events, and remove habits or specific entries
# ---------------------------------------------------------------------------------------

def add_habit(db, name, description, period, user_name):
    """
    Add a new habit for a user to the database.

    Args:
        db (sqlite3.Connection): Database connection object.
        name (str): Name of the habit.
        description (str): Description of the habit.
        period (str): 'daily' or 'weekly'.
        user_name (str): User's name.
    """
    cur = db.cursor()
    try:
        cur.execute('''
            INSERT INTO habit (name, description, period, user_name)
            VALUES (?, ?, ?, ?)
        ''', (name, description, period, user_name))
        db.commit()
    except sqlite3.IntegrityError:
        print(f"\n⚠️  You already have a habit named '{name}'. Please choose a different name.\n")


def increment_habit(db, name, user_name, event_date, mood_before, mood_after):
    """
    Log a habit completion event.

    Args:
        db (sqlite3.Connection): Database connection object.
        name (str): Name of the habit.
        user_name (str): Name of the user.
        event_date (str): Date of the event in 'YYYY-MM-DD'. Defaults to today.
        mood_before (str): User's mood before the habit.
        mood_after (str, optional): User's mood after the habit.
    """
    if not event_date:
        event_date = str(date.today())

    cur = db.cursor()
    cur.execute(
        "INSERT INTO tracker (date, habitName, user_name, mood_before, mood_after) VALUES (?, ?, ?, ?, ?)",
        (event_date, name, user_name, mood_before, mood_after)
    )
    db.commit()


def delete_habit(db, name, user_name):
    """
    Delete a habit and all its associated tracking events.

    Args:
        db (sqlite3.Connection): Database connection object.
        name (str): Name of the habit.
        user_name (str): Name of the user.
    """
    cur = db.cursor()
    cur.execute("DELETE FROM tracker WHERE habitName = ? AND user_name = ?", (name, user_name))
    cur.execute("DELETE FROM habit WHERE name = ? AND user_name = ?", (name, user_name))
    db.commit()


def delete_event(db, name, user_name, date):
    """
    Delete a specific event (by date) for a given habit and user.

    Args:
        db (sqlite3.Connection): Database connection object.
        name (str): Name of the habit.
        user_name (str): Name of the user.
        date (str): Date of the event to delete.
    """
    cur = db.cursor()
    cur.execute("DELETE FROM tracker WHERE habitName = ? AND user_name = ? AND date = ?", (name, user_name, date))
    db.commit()


# Functions to retrieve habit data, user lists, and tracking history from the database
# -------------------------------------------------------------------------------------

def get_habit_data(db, name, user_name):
    """
    Retrieve all tracker entries for a specific habit and user.

    Args:
        db (sqlite3.Connection): Database connection object.
        name (str): Name of the habit.
        user_name (str): Name of the user.

    Returns:
        list: List of rows containing event data.
    """
    cur = db.cursor()
    cur.execute("SELECT * FROM tracker WHERE habitName=? AND user_name=?", (name, user_name))
    return cur.fetchall()


def get_habits_for_user(db, user_name):
    """
    Get a list of all habit names belonging to a user.

    Args:
        db (sqlite3.Connection): Database connection object.
        user_name (str): Name of the user.

    Returns:
        list: List of habit names.
    """
    cur = db.cursor()
    cur.execute("SELECT name FROM habit WHERE user_name=?", (user_name,))
    return [row[0] for row in cur.fetchall()]


def get_all_users(db):
    """
    Get a list of all distinct users in the database.

    Args:
        db (sqlite3.Connection): Database connection object.

    Returns:
        list: List of unique user names.
    """
    cur = db.cursor()
    cur.execute("SELECT DISTINCT user_name FROM habit")
    return [row[0] for row in cur.fetchall()]


def get_period_for_habit(db, habit_name, user_name):
    """
    Get the period ('daily' or 'weekly') for a specific habit.

    Args:
        db (sqlite3.Connection): Database connection object.
        habit_name (str): Name of the habit.
        user_name (str): Name of the user.

    Returns:
        str or None: The period string, or None if not found.
    """
    cursor = db.cursor()
    cursor.execute(
        "SELECT period FROM habit WHERE name = ? AND user_name = ?",
        (habit_name, user_name)
    )
    result = cursor.fetchone()
    return result[0] if result else None



