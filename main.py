import sys
import time
from datetime import datetime, date
import questionary

from db import (
    get_db,
    get_habits_for_user,
    get_habit_data,
    get_all_users
)

from habit import Habit

from analysis import (
    calculate_count,
    calculate_streak_by_period,
    longest_streak_by_period,
    count_mood_improvements
)


# Adding a typewriter effect and greeting the user when the app starts
# --------------------------------------------

def type_writer(text, delay=0.05):
   
    """
    Print text to the console with a typewriter effect.

    Args:
        text (str): The text to display.
        delay (float): Delay between each character in seconds.
    """

    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def greet_user():
   
    """
    Display a welcome message using the typewriter effect.
    """

    type_writer("""
🌞  Welcome to Habitly — your motivating habit tracking companion!

    No pressure, no perfection — just consistent, kind progress.
    Let's do this together!
""")


# User selection: choose existing or register a new user
# ------------------------------------------------------

def select_or_create_user(db):
    
    """
    Let the user select an existing username or create a new one.

    Args:
        db: SQLite database connection.

    Returns:
        str: The selected or newly created username.
    """
    all_users = get_all_users(db)
    options = all_users + ["(Register new user)"]

    #Selecting a user or adding a new one 
    selected = questionary.select("Who are you?", choices=options).ask()

    if selected == "(Register new user)":
        while True:
            name = questionary.text("Enter your name:").ask()
            
            #Exception handling if user already exists 
            if name in all_users:
                print(f"\n⚠️  The name '{name}' is already taken. Please choose a different one.\n")
            else:
                return name
    else:
        return selected
        


# Main features of Habitly: create new habits, log completions, view analytics, and manage data
# --------------------------------------------

def create_new_habit(db):
    
    """
    Prompt the user to create a new habit and store it in the database.

    Args:
        db: SQLite database connection.
    """

    user_name = select_or_create_user(db)
    existing_habits = get_habits_for_user(db, user_name)

    while True:
        #Prompting user to enter a new habit or go back to main menue 
        name = questionary.text("Enter a name for your new habit (or type 'menu' to go back):").ask()
        if name.lower() == "menu":
            print("\n↩️  Returning to main menu...\n")
            return
        #Exception if user already exists 
        if name in existing_habits:
            print(f"\n⚠️  You already have a habit named '{name}'. Please choose a different name.\n")
            continue
        break
    
    
    #Prompting user to insert a description of the new habit 
    description = questionary.text("Write a short description:").ask()
    period = questionary.select("How often do you want to track this habit?", choices=["daily", "weekly"]).ask()

    #storing user input in database 
    habit = Habit(name, description, period, user_name)
    habit.store(db)
    
    #reassuring user input worked out and motivate user to keep up the habit 
    type_writer(f"\n  ✅  Alright, {user_name}, your habit '{name}' was created successfully!\n")
    type_writer(f"\n  ⏳  Remember to keep it up {period}!\n")



def increment_existing_habit(db):
   
    """
    Log an event for a selected habit, including mood and date.

    Args:
        db: SQLite database connection.
    """

    user_name = select_or_create_user(db)
    habits = get_habits_for_user(db, user_name)

    #Exception handling if there is no habit to increment 
    if not habits:
        print("\n  ⚠️  No habits found. Please create one first.\n")
        return
    
    #Prompting user to select a habit to increment 
    chosen = questionary.select("Which habit did you complete?", choices=habits).ask()
    
    #Guiding user to input a date (today or any other) 
    use_today = questionary.confirm("Did you complete it today?").ask()
    if use_today:
        event_date = str(date.today())
    else:
        date_input = questionary.text("When did you do it? (YYYY-MM-DD)").ask()
        try:
            parsed = datetime.strptime(date_input, "%Y-%m-%d").date()
            event_date = str(parsed)
            
        #Exception handling for wrong data input
        except ValueError:
            print("\n  ⚠️  Invalid date format. Please use YYYY-MM-DD.\n")
            return

    #prompting user to record mood before and after the completion of the habit 
    mood_before = questionary.select(f"How did you feel before doing '{chosen}'?", choices=["😄", "😐", "😞"]).ask()
    mood_after = questionary.select(f"How did you feel after doing '{chosen}'?", choices=["😄", "😐", "😞"]).ask()

    #retrieving metadata from choosen habit 
    cur = db.cursor()
    cur.execute(
        "SELECT description, period FROM habit WHERE name = ? AND user_name = ?",
        (chosen, user_name)
    )
    result = cur.fetchone()

    #incrementing the habit 
    description, period = result
    habit = Habit(name=chosen, description=description, period=period, user_name=user_name)
    habit.add_event(db, date=event_date, mood_before=mood_before, mood_after=mood_after)

    # reassuring user that input worked 
    message = f" Thanks for showing up for '{chosen}' today!"
    
    print(f"\n{message}\n")


def show_habit_analytics(db):
    
    """
    Display analytics for a selected habit: streaks, completion count, mood improvement.

    Args:
        db: SQLite database connection.
    """
    #choosing a user for habit analysis 
    all_users = get_all_users(db)
    selected_user = questionary.select(
        "Whose habits would you like to analyze?",
        choices=all_users
    ).ask()
    
    #Exception handling if user has no habits 
    habits = get_habits_for_user(db, selected_user)
    if not habits:
        print("\n  ⚠️  No habits found.\n")
        return

    #retrieving name and period of choosen user for summary statement: User X has Y habits 
    cur = db.cursor()
    cur.execute("SELECT name, period FROM habit WHERE user_name = ?", (selected_user,))
    rows = cur.fetchall()
    if rows:
        summary = f"{selected_user} has {len(rows)} habit(s): "
        summary += ", ".join([f"{name} ({period})" for name, period in rows])
        print(f"\n🗞️  {summary}\n")
        
    #choosing habit of user to analyse  
    chosen = questionary.select("Which habit would you like to analyze?", choices=habits).ask()
    
    #retrieving habit data for chosen habit  
    data = get_habit_data(db, chosen, selected_user)

    #exception handling if no events tracked   
    if not data:
        print("\n📬 No events tracked yet.\n")
        return
   
    #retrieving period, description, creation date from choosen habit and selected user   
    cur.execute(
        "SELECT period, description, created_at FROM habit WHERE name = ? AND user_name = ?",
        (chosen, selected_user)
    )
    result = cur.fetchone()
   
    #exception handling if no events tracked  
    if not result:
        print("\n⚠️ Could not retrieve habit information.\n")
        return

    #unpacking result 
    period, description, created_at = result

    #all variables for habit analysis summary 
    dates = [datetime.strptime(row[0], "%Y-%m-%d").date() for row in data if row[0]]
    moods_before = [row[3] for row in data if len(row) > 3 and row[3]]
    moods_after = [row[4] for row in data if len(row) > 4 and row[4]]
    mood_improved = count_mood_improvements(moods_before, moods_after)
    total = calculate_count(db, chosen, selected_user)
    current = calculate_streak_by_period(dates, period)
    longest = longest_streak_by_period(dates, period)
    unit = "day(s)" if period == "daily" else "week(s)"
    
    #displaying analytics summary  
    print(f"\n  📈  Analytics for '{chosen}' ({period} habit):\n")
    print(f" 📝  Description: {description}")
    print(f" 🗓️  Created on: {created_at}")
    print(f" ✅  Total completions: {total}")
    print(f" 🔥  Current streak: {current} {unit}")
    print(f" 🏆  Longest streak: {longest} {unit}")
    print(f" 😄  {mood_improved} time(s) {selected_user}'s mood improved after '{chosen}'\n")
    
    #offering the possibility to see the full log 
    if questionary.confirm("Would you like to see the full log?").ask():
        print(f"\n🗓️  Habit log for '{chosen}':")
        for row in data:
            mood_b = row[3] or "—"
            mood_a = row[4] if len(row) > 4 and row[4] else "—"
            print(f"  - {row[0]} | Before: {mood_b} | After: {mood_a}")
        print()


def delete_existing_habit(db):
    """
    Allow the user to select and delete a habit and all its events.

    Args:
        db: SQLite database connection.
    """
    user_name = select_or_create_user(db)
    habits = get_habits_for_user(db, user_name)
    if not habits:
        print("\n⚠️  No habits to delete.\n")
        return

    #prompting user to choose a habit to delete 
    chosen = questionary.select("Which habit do you want to delete?", choices=habits).ask()

    # Retrieve metadata to fully initialize the Habit object
    cur = db.cursor()
    cur.execute("SELECT description, period FROM habit WHERE name = ? AND user_name = ?", (chosen, user_name))
    result = cur.fetchone()
    if not result:
        print("\n⚠️ Could not find that habit in the database.\n")
        return

    description, period = result
    habit = Habit(chosen, description, period, user_name)

    #Prompting user to confirm deletion of habit 
    confirm = questionary.confirm(f"Are you sure you want to delete '{chosen}' and all its data?").ask()
    if confirm:
        habit.delete(db)
        
        #Let user know that deleting the habit actually worked out 
        print(f"\n🗑️  Habit '{chosen}' deleted successfully.\n")


def delete_specific_event(db):
    """
    Allow the user to delete a single event (by date) for a selected habit.

    Args:
        db: SQLite database connection.
    """
    user_name = select_or_create_user(db)
    habits = get_habits_for_user(db, user_name)
    if not habits:
        print("\n⚠️  No habits found.\n")
        return

    #Let user choose a habit for which to delete an event 
    chosen = questionary.select("Which habit?", choices=habits).ask()
    data = get_habit_data(db, chosen, user_name)
    if not data:
        print("\n⚠️  No events found for this habit.\n")
        return

    #retriving metadata for habit/event to delete 
    cur = db.cursor()
    cur.execute("SELECT description, period FROM habit WHERE name = ? AND user_name = ?", (chosen, user_name))
    result = cur.fetchone()
    if not result:
        print("\n⚠️ Could not retrieve habit metadata.\n")
        return

    description, period = result
    habit = Habit(chosen, description, period, user_name)

    #letting user choose which event to delete 
    dates = [row[0] for row in data]
    date_to_delete = questionary.select("Which event date do you want to delete?", choices=dates).ask()

    #asking user for confirmation + letting user know that event deletion actually worked out  
    confirm = questionary.confirm(f"Delete event on {date_to_delete} for '{chosen}'?").ask()
    if confirm:
        habit.delete_event(db, date_to_delete)
        print(f"\n❌  Event on {date_to_delete} deleted.\n")



# Main application loop for Habitly: Welcomes the user, guides them through the main menu options, and ends with a friendly farewell.
# --------------------------------------------

def main():
    
    """
    Launch the Habitly application and display the main menu loop.
    """

    db = get_db()
    greet_user()

   #letting user choose what to do with "Habitly" 
    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "➕   Create new habit",
                "✅   Mark habit as completed",
                "📊   View habit analytics",
                "🗑️   Delete a habit",
                "❌   Delete a specific event",
                "🚪   Exit"
            ]
        ).ask()

        if choice == "➕   Create new habit":
            create_new_habit(db)
        elif choice == "✅   Mark habit as completed":
            increment_existing_habit(db)
        elif choice == "📊   View habit analytics":
            show_habit_analytics(db)
        elif choice == "🗑️   Delete a habit":
            delete_existing_habit(db)
        elif choice == "❌   Delete a specific event":
            delete_specific_event(db)
        elif choice == "🚪   Exit":
            type_writer("\n  🚪  Goodbye and keep up the good habits!\n")
            break

if __name__ == "__main__":
    main()

