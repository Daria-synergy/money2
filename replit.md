# Money Goals Tracker

## Overview
A Flask-based web application for tracking financial savings goals. Users can create, manage, and share savings goals with others.

## Tech Stack
- Python 3.11
- Flask web framework
- SQLite database (via Flask-SQLAlchemy)
- Flask-Migrate for database migrations

## Project Structure
- `main.py` - Main application file with routes and models
- `templates/` - HTML templates (Jinja2)
- `static/` - CSS and images
- `migrations/` - Database migration files
- `instance/` - SQLite database file

## Running the Application
The Flask server runs on port 5000 with the command:
```
python main.py
```

## Features
- User registration and authentication with secure password hashing
- Create savings goals with target amounts
- Track progress towards goals
- Share goals with other users
- Session-based authentication with token expiration

## Database Models
- **User**: User accounts with hashed passwords and session tokens
- **Money**: Savings goals with title, target amount, current balance, category, and status
