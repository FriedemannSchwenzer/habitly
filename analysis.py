from db import get_habit_data, get_period_for_habit
from collections import Counter
from datetime import date, timedelta


def calculate_count(db, habit, user_name):
    """
    Count the number of completed events for a specific habit.

    Args:
        db: SQLite database connection.
        habit (str): Name of the habit.
        user_name (str): Name of the user.

    Returns:
        int: Number of completed events.
    """
    data = get_habit_data(db, habit, user_name)
    return len(data)


def calculate_streak_by_period(dates, period):
    """
    Calculate the current streak of consecutive habit completions based on periodicity.

    Args:
        dates (list of date): List of completion dates.
        period (str): Either 'daily' or 'weekly'.

    Returns:
        int: Length of the current streak.
    """
    if not dates:
        return 0

    today = date.today()
    
    # Handle current daily streak
    if period == "daily":
        streak = 0
        current = today
        
        while current in dates:
            streak += 1
            current -= timedelta(days=1)
        return streak 

    # Handle current weekly streak
    elif period == "weekly":
        today = date.today()
        sorted_dates = sorted(set(dates))
        streak = 0
    
        # Check if the last entry is today or within the last 7 days
        current_date = today
        for d in reversed(sorted_dates):  # Iterate from the most recent date backward
            if current_date - d <= timedelta(days=7):
                streak += 1
                current_date = d - timedelta(days=1)  # Move to the previous day
            else:
                break  # Stop if there's a break greater than 7 days
    
        return streak


def longest_streak_by_period(dates, period):
    """
    Calculate the longest historical streak for a habit.

    Args:
        dates (list of date): List of completion dates.
        period (str): Either 'daily' or 'weekly'.

    Returns:
        int: Longest streak observed.
    """
    if not dates:
        return 0

    sorted_dates = sorted(set(dates))

    # finding longest daily streak
    if period == "daily":
        max_streak = streak = 1
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 1
        return max_streak

    # finding longest weekly streak
    elif period == "weekly":
        # Create a list of (year, week) tuples for each date
        weeks = [(d.isocalendar()[0], d.isocalendar()[1]) for d in sorted_dates]
        
        # Get the unique weeks, sorted by (year, week)
        unique_weeks = sorted(set(weeks))

        max_streak = streak = 1  # Initialize max streak and current streak

        # Iterate through the list of unique weeks
        for i in range(1, len(unique_weeks)):
            curr_year, curr_week = unique_weeks[i]
            prev_year, prev_week = unique_weeks[i - 1]

            # Handle week 1 of the year (checking the previous year's last week because of edge case december/january)
            if curr_week == 1:
                expected_prev = (curr_year - 1, 52 if prev_week >= 52 else 53)
            else:
                expected_prev = (curr_year, curr_week - 1)

            # Check if the previous week is consecutive to the current week
            if (prev_year, prev_week) == expected_prev:
                streak += 1  # Increment streak if consecutive
                max_streak = max(max_streak, streak)  # Update max streak if necessary
            else:
                streak = 1  # Reset streak if weeks are not consecutive

        return max_streak  # Return the longest streak

    return 0  # Return 0 if no streak is found



def extract_mood_stats(data):
    """
    Extract mood data before and after the completion of a habit.

    Args:
        data (list): Tracker records, each row containing date and mood data.

    Returns:
        tuple: A tuple containing two lists, one for moods before and one for moods after the habit.
    """
    moods_before = [row[3] for row in data if row[3]]
    moods_after = [row[4] for row in data if len(row) > 4 and row[4]]
    return moods_before, moods_after



def count_mood_improvements(moods_before, moods_after):
    """
    Count how many times the user's mood improved after completing a habit.

    Args:
        moods_before (list of str): Mood values before the habit.
        moods_after (list of str): Mood values after the habit.

    Returns:
        int: Number of times the mood improved.
    """
    mood_score = {"😞": 0, "😐": 1, "😄": 2}
    return sum(
        1 for b, a in zip(moods_before, moods_after)
        if mood_score.get(a, 0) > mood_score.get(b, 0)
    )



