from db import add_habit, increment_habit, delete_habit, delete_event

class Habit:
    """
    A class representing a habit tracked by a user.

    Each habit has a name, description, tracking period (e.g., daily or weekly), 
    and is associated with a specific user. This class provides methods to store 
    the habit in a database and to log or remove tracking events.
    """

    def __init__(self, name: str, description: str, period: str, user_name: str):
        """
        Initialize a new Habit instance.

        Args:
            name (str): The name of the habit.
            description (str): A short description of the habit.
            period (str): The periodicity of the habit ('daily' or 'weekly').
            user_name (str): The name of the user who owns the habit.
            created_at(str): date of creation (format 'YYYY-MM-DD')
        """
        self.name = name
        self.description = description
        self.period = period
        self.user_name = user_name


    def add_event(self, db, date: str = None, mood_before: str = None, mood_after: str = None):
        """
        Record a habit completion event in the database.

        Args:
            db: The SQLite database connection.
            date (str, optional): The date of completion (format 'YYYY-MM-DD'). Defaults to today if None.
            mood_before (str, optional): The user's mood before completing the habit.
            mood_after (str, optional): The user's mood after completing the habit.
        """
        increment_habit(
            db,
            name=self.name,
            user_name=self.user_name,
            event_date=date,
            mood_before=mood_before,
            mood_after=mood_after
        )

    def store(self, db):
        """
        Save the habit to the database.

        Args:
            db: The SQLite database connection.
        """
        add_habit(db, self.name, self.description, self.period, self.user_name)
        
    def delete(self, db):
        """
        Delete this habit and all its associated events from the database.

        Args:
            db: The SQLite database connection.
        """
        delete_habit(db, self.name, self.user_name)

    def delete_event(self, db, date: str):
        """
        Delete a specific event for this habit based on date.

        Args:
            db: The SQLite database connection.
            date (str): The date of the event to delete (format 'YYYY-MM-DD').
        """
        delete_event(db, self.name, self.user_name, date)
