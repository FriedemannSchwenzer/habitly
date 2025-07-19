# Habitly — A Minimalist Habit Tracker

Habitly is a simple command-line habit tracker written in Python. It allows users to create and manage personal habits, log completions with mood tracking, and analyze their consistency and improvements over time.

Habitly is first and foremost a learning project ;) 

## Features

- Create habits with daily or weekly periodicity
- Mark habits as completed with mood logging (before and after)
- View streaks, longest streaks, and mood improvement stats
- Delete habits or specific tracked events
- Multiple user support
- tests with fixture data 

## Requirements

### Python Version
- Python 3.8 or higher recommended

### Dependencies

Install dependencies with:

```
pip install -r requirements.txt
```

Main dependencies include:

- questionary – for interactive CLI prompts  
- pytest – for running tests (optional)

## Getting Started

### 1. Clone the Repository

```
git clone https://github.com/your-username/habitly.git
cd habitly

```

### 2. Install Dependencies

```
pip install -r requirements.txt
```

### 3. Run the App

```
python main.py
```

The app will guide you through selecting a user, creating habits, and analyzing a habit.


## Running Tests

To run automated tests:

```
pytest test_project.py

```

## Project Structure

```
├── main.py             # Main application logic: Command-line interface (CLI) for interacting with the user
├── habit.py            # Habit class: Defines and manages habits (creation, updating, deletion)
├── db.py               # Database operations: Functions for connecting to and interacting with the database
├── analysis.py         # Analytical functions: Data analysis related to habit tracking
├── test_project.py     # Tests: Unit tests for all core functionalities of the application
├── requirements.txt    # Dependencies: Lists the necessary Python packages and their versions

```
