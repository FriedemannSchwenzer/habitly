import pytest
import random
from datetime import date, datetime, timedelta
from habit import Habit
from db import create_tables, get_db, add_habit, increment_habit, delete_habit, delete_event, get_all_users, get_habits_for_user, get_habit_data, get_period_for_habit
from analysis import calculate_count, calculate_streak_by_period, longest_streak_by_period, extract_mood_stats, count_mood_improvements
import sqlite3


today = date.today()
    # Define a function to adapt dates
   
def adapt_date(value):
        return value.isoformat()

  # Register the date and datetime adapters
sqlite3.register_adapter(date, adapt_date)
sqlite3.register_adapter(datetime, adapt_date)

# test fixture with 5 habits and 4 weeks of data
# --------------------------------------------

@pytest.fixture
def db():
    """
    Creates an in-memory test DB with dummy data:
    - 2 users: Jaakko, Selma
    - 5 habits: 3 daily (20 events), 2 weekly (6 events)
    - including streak simulation
    """
    db = get_db(":memory:")
   
    create_tables(db)


    # adding habits for user Jaakko and Selma 
    # --------------------------
    
    habits = [
        ("Jaakko", "Meditation", "Take 10 minutes to breathe", "daily"),
        ("Jaakko", "Reading", "Read 15 minutes", "daily"),
        ("Jaakko", "Running", "Go for a jog", "weekly"),
        ("Selma", "Stretching", "Do basic morning stretches", "daily"),
        ("Selma", "Journaling", "Reflect on the week", "weekly"),
    ]

    for user, name, desc, period in habits:
        add_habit(db, name=name, description=desc, period=period, user_name=user)

    
    # adding events 
    # --------------------------
        
    # Jaakko "Meditation": Daily habit, 20 events,current streak: /, longest streak: 7, mood improvements: 9  
    meditation_events = [
        ("2025-06-17", "Meditation", "Jaakko", "😐", "😄"),
        ("2025-06-18", "Meditation", "Jaakko", "😞", "😐"),
        ("2025-06-19", "Meditation", "Jaakko", "😐", "😄"),
        ("2025-06-20", "Meditation", "Jaakko", "😄", "😄"),
        ("2025-06-21", "Meditation", "Jaakko", "😐", "😐"),
        ("2025-06-22", "Meditation", "Jaakko", "😞", "😐"),
        ("2025-06-23", "Meditation", "Jaakko", "😐", "😄"),
        ("2025-06-24", "Meditation", "Jaakko", "😄", "😄"),
        ("2025-06-24", "Meditation", "Jaakko", "😞", "😐"),
        ("2025-06-26", "Meditation", "Jaakko", "😐", "😐"),
        ("2025-06-27", "Meditation", "Jaakko", "😐", "😐"),
        ("2025-06-29", "Meditation", "Jaakko", "😐", "😐"),
        ("2025-06-30", "Meditation", "Jaakko", "😄", "😄"),
        ("2025-07-02", "Meditation", "Jaakko", "😐", "😐"),
        ("2025-07-02", "Meditation", "Jaakko", "😞", "😄"),
        ("2025-07-03", "Meditation", "Jaakko", "😐", "😄"),
        ("2025-07-04", "Meditation", "Jaakko", "😐", "😐"),
        ("2025-07-05", "Meditation", "Jaakko", "😄", "😄"),
        ("2025-07-09", "Meditation", "Jaakko", "😐", "😄"),
        ("2025-07-11", "Meditation", "Jaakko", "😐", "😄")
         ]


    
    # Jaakko "Reading":  Daily habit, 20 events, current streak: 5 days, longest streak: 15, mood improvements: 15   
    reading_events = [
        ("2025-06-17", "Reading", "Jaakko", "😞", "😐"), 
        ("2025-06-18", "Reading", "Jaakko", "😐", "😄"), 
        ("2025-06-19", "Reading", "Jaakko", "😐", "😄"),  
        ("2025-06-20", "Reading", "Jaakko", "😄", "😄"),  
        ("2025-06-21", "Reading", "Jaakko", "😐", "😐"),
        ("2025-06-22", "Reading", "Jaakko", "😞", "😐"),  
        ("2025-06-23", "Reading", "Jaakko", "😐", "😄"),  
        ("2025-06-24", "Reading", "Jaakko", "😞", "😐"),  
        ("2025-06-25", "Reading", "Jaakko", "😐", "😐"), 
        ("2025-06-26", "Reading", "Jaakko", "😐", "😄"),  
        ("2025-06-27", "Reading", "Jaakko", "😞", "😐"), 
        ("2025-06-28", "Reading", "Jaakko", "😐", "😐"), 
        ("2025-06-29", "Reading", "Jaakko", "😐", "😄"), 
        ("2025-06-30", "Reading", "Jaakko", "😞", "😐"),  
        ("2025-07-01", "Reading", "Jaakko", "😐", "😄"), 
    
        # dynamic part to reflect a current streak
        # Use `today - timedelta` to calculate the last few days
        (today - timedelta(days=4), "Reading", "Jaakko", "😐", "😄"),
        (today - timedelta(days=3), "Reading", "Jaakko", "😞", "😐"),
        (today - timedelta(days=2), "Reading", "Jaakko", "😐", "😐"),
        (today - timedelta(days=1), "Reading", "Jaakko", "😞", "😄"),
        (today, "Reading", "Jaakko", "😐", "😐"),
    ]

 
    # Jaakko "Running": Weekly habit, 6 events, current streak: 0, longest streak: 4 weeks, mood improvements: 4  
    running_events = [
        ("2025-06-17", "Running", "Jaakko", "😐", "😄"),
        ("2025-06-21", "Running", "Jaakko", "😞", "😐"),
        ("2025-06-25", "Running", "Jaakko", "😄", "😄"),
        ("2025-06-29", "Running", "Jaakko", "😐", "😐"),
        ("2025-07-03", "Running", "Jaakko", "😞", "😄"),
        ("2025-07-07", "Running", "Jaakko", "😐", "😄")
         ]

    # Selma "Stretching": Daily habit, 20 events, current streak: 0, longest streak: 12 days, mood improvements: 10 
    stretching_events = [
        ("2025-05-14", "Stretching", "Selma", "😐", "😄"),
        ("2025-05-15", "Stretching", "Selma", "😞", "😐"),
        ("2025-05-16", "Stretching", "Selma", "😐", "😄"),
        ("2025-05-17", "Stretching", "Selma", "😄", "😄"),
        ("2025-05-20", "Stretching", "Selma", "😐", "😐"),
        ("2025-05-21", "Stretching", "Selma", "😞", "😐"),
        ("2025-05-26", "Stretching", "Selma", "😐", "😐"),
        ("2025-05-27", "Stretching", "Selma", "😄", "😄"),
        ("2025-05-28", "Stretching", "Selma", "😞", "😐"),
        ("2025-05-29", "Stretching", "Selma", "😐", "😐"),
        ("2025-05-30", "Stretching", "Selma", "😐", "😄"),
        ("2025-06-01", "Stretching", "Selma", "😐", "😄"),
        ("2025-06-02", "Stretching", "Selma", "😄", "😄"),
        ("2025-06-03", "Stretching", "Selma", "😐", "😐"),
        ("2025-06-04", "Stretching", "Selma", "😞", "😄"),
        ("2025-06-05", "Stretching", "Selma", "😐", "😄"),
        ("2025-06-06", "Stretching", "Selma", "😐", "😐"),
        ("2025-06-09", "Stretching", "Selma", "😄", "😞"),
        ("2025-06-10", "Stretching", "Selma", "😐", "😄"),
        ("2025-06-11", "Stretching", "Selma", "😐", "😞")
        ]
      
    # Selma "Journaling" weekly habit, 5 events, current streak: 3 weeks, longest streak 3 weeks, mood improvement = 4   
    journaling_events = [
    ("2025-03-18", "Journaling", "Selma", "😞", "😐"),
    ("2025-03-22", "Journaling", "Selma", "😐", "😄"),

    # Dynamic events to simulate a 3-week current streak
    (today - timedelta(days=14), "Journaling", "Selma", "😄", "😄"),
    (today - timedelta(days=7), "Journaling", "Selma", "😞", "😄"),
    (today, "Journaling", "Selma", "😐", "😄")
]

    # All event lists
    all_events = (
        meditation_events +
        reading_events +
        running_events +
        stretching_events +
        journaling_events
    )

    # Insert each event into the DB
    for event_date, habit_name, user_name, mood_before, mood_after in all_events:
        increment_habit(
            db,
            name=habit_name,
            user_name=user_name,
            event_date=event_date,
            mood_before=mood_before,
            mood_after=mood_after
        )
      
    return db 


# Testing Database Retrieval functions
# -------------------------------

def test_get_all_users(db):
    users = get_all_users(db)
    assert set(users) == {"Jaakko", "Selma"}  # check Jaakko and Selma are actually in the list 

def test_get_habits_for_user(db):
    habits_jaakko = get_habits_for_user(db, "Jaakko")
    habits_selma = get_habits_for_user(db, "Selma")
    assert set(habits_jaakko) == {"Meditation", "Reading", "Running"} # check Jaakko has the habits of Meditating, Reading and Running 
    assert set(habits_selma) == {"Stretching", "Journaling"} # check Selma has the habit of Stretching and Journaling 

def test_get_habit_data_returns_event_list(db):
    events = get_habit_data(db, "Reading", "Jaakko")
    assert len(events) == 20 # Since we inserted 20 events for daily habits, we check if combination "Reading" & Jaakko appears 20X in our table
    assert all(habit == "Reading" and user == "Jaakko" for _, habit, user, _, _ in events) # making sure we actually retrieved what we wanted  


def test_get_period_for_habit(db):
    assert get_period_for_habit(db, "Meditation", "Jaakko") == "daily" #checking that "Meditation" is a defined as a daily habit 
    assert get_period_for_habit(db, "Journaling", "Selma") == "weekly" #checking that "Journaling" is defined as a weekly habit 


# Testing Database insert and deletion functions 
# -------------------------------


def test_add_habit_creates_new_habit(db):
    new_name = "Sketching" # defining new habit 
    add_habit(db, new_name, "Draw for fun", "weekly", "Selma") # add new habit 
    habits = get_habits_for_user(db, "Selma") # retrieving all habits for Selma 
    assert new_name in habits # making sure that new habit is in list habits 

def test_increment_habit_adds_event(db):
        increment_habit(
        db,
        name="Running",
        user_name="Jaakko",
        event_date="2025-03-18",
        mood_before="😐",
        mood_after="😄") # a new habit for Jaakko "Running" 
        data = get_habit_data(db, "Running", "Jaakko")#retrieving all events of Jaakko Running 
        assert any(row[0] == "2025-03-18" for row in data) #making sure that new date is in Jaakko Running 

def test_delete_event_removes_one_event(db):
    
    test_date = "2025-05-14" # Select a known event date that already exists in habit "Stretching" (Selma) 
    before = get_habit_data(db, "Stretching", "Selma")# Get the habit data for "Stretching" and "Selma" before deletion
    assert any(event[0] == test_date for event in before) # Ensure the event is in the database before deletion
    delete_event(db, "Stretching", "Selma", test_date)# Delete the event using the delete_event function
    after = get_habit_data(db, "Stretching", "Selma") # Get the habit data for "Stretching" and "Selma" after deletion
    assert len(before) - 1 == len(after)# Assert that the event count decreased by 1
    assert all(event[0] != test_date for event in after) # Assert that the event is no longer in the database

def test_delete_habit_removes_habit_and_events(db):
    habits_before = get_habits_for_user(db, "Jaakko")#all habits before delition 
    assert "Running" in habits_before #making sure Running is among Jaakko's habits 
    
    delete_habit(db, "Running", "Jaakko") # deleting Running from Jaakkos habbits list 
    habits_after = get_habits_for_user(db, "Jaakko")#all habits after delition
    
    assert "Running" not in habits_after #checking that Running was actually removed 


# Testing Database retrival functions  
# -------------------------------

def test_get_habit_data(db):
    events = get_habit_data(db, "Reading", "Jaakko") #Retrieving all data for Jaakko "Reading" 
    assert len(events) == 20  #making sure the output is 20 as expected based on fixture data 
    assert all(event[1] == "Reading" and event[2] == "Jaakko" for event in events)  # Check that all events retrieved are for actually "Reading" and "Jaakko"

def test_get_habits_for_user(db):
    habits_Jaakko = get_habits_for_user(db, "Jaakko") #Retrieving all habits for user "Jaakko"
    habits_selma = get_habits_for_user(db, "Selma") #Retrieving all habits for user "Selma"
    assert set(habits_Jaakko) == {"Meditation", "Reading", "Running"} # Comparing retrieved habits wiht fixture data inserted 
    assert set(habits_selma) == {"Stretching", "Journaling"} # Comparing retrieved habits wiht fixture data inserted 

def test_get_all_users(db):
    users = get_all_users(db) # get all user data 
    assert set(users) == {"Jaakko", "Selma"}  # Check that the database contains both Jaakko and Selma


def test_get_period_for_habit(db):
    period_meditation = get_period_for_habit(db, "Meditation", "Jaakko")# Retrieving periodicity for Jaakko's "Medition" habit 
    period_journaling = get_period_for_habit(db, "Journaling", "Selma") # Retrieving periodicity for Selma's "Journaling" habit 
    assert period_meditation == "daily" # Check that periodicity is actually what was inserted in fixture data 
    assert period_journaling == "weekly"# Check that periodicity is actually what was inserted in fixture data 


# Testing Analysis functions
# -------------------------------

def test_calculate_count(db):
    # Retrieve events for "Reading" and "Stretching" and print them
    reading_data = get_habit_data(db, "Reading", "Jaakko")
    stretching_data = get_habit_data(db, "Stretching", "Selma")
    
    count = calculate_count(db, "Reading", "Jaakko")
    assert count == 20  # Ensure that the correct number of "Reading" events is counted

    count = calculate_count(db, "Stretching", "Selma")
    assert count == 20  # Ensure that the correct number of "Stretching" events is counted


def test_calculate_streak_by_period(db):
    
    reading_dates = [date.fromisoformat(event[0]) for event in get_habit_data(db, "Reading", "Jaakko")]
    streak = calculate_streak_by_period(reading_dates, "daily")
    assert streak == 5 # Making sure that Jaakko's latest streak matches the fixture data 

    journaling_dates = [date.fromisoformat(event[0]) for event in get_habit_data(db, "Journaling", "Selma")]
    streak = calculate_streak_by_period(journaling_dates, "weekly")
    assert streak == 3  # Making sure that Selma's latest streak matches the fixture data 
    


def longest_streak_by_period (db):
    meditation_dates = [date.fromisoformat(event[0]) for event in get_habit_data(db, "Meditation", "Jaakko")] # Retrieve Jaakko's "Meditation" habit data
    streak = longest_streak_by_period(meditation_dates, "daily") 
    assert streak == 7 # making sure outcome is in line with fixture data longest streak "Meditation" (7) 


    running_dates = [date.fromisoformat(event[0]) for event in get_habit_data(db, "Running", "Jaakko")] # Retrieve Jaakko's "Running" habit data
    streak = running_streak_by_period(running_dates, "weekly")
    assert streak == 4 # making sure outcome is in line with fixture data longest streak "Running" (4) 

def test_extract_mood_stats(db):
    meditation_data = get_habit_data(db, "Meditation", "Jaakko") # Retrieve Jaakko's "Meditation" habit data
    moods_before, moods_after = extract_mood_stats(meditation_data) # Call the extract_mood_stats function to extract moods before and after

    # Define the expected values from the input data
    expected_moods_before = ["😐", "😞", "😐"]
    expected_moods_after = ["😄", "😐", "😄"]
    
    # Assert that the first three items in moods_before and moods_after match the expected values
    assert moods_before[:3] == expected_moods_before
    assert moods_after[:3] == expected_moods_after

def test_count_mood_improvements(db):
    journaling_data = get_habit_data(db, "Journaling", "Selma") 
    moods_before, moodes_after = extract_mood_stats(journaling_data)
    mood_count = count_mood_improvements(moods_before, moodes_after) 
    
    assert mood_count == 4
