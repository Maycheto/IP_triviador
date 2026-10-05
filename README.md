# miador

A clone of the quiz game Triviador (Conquiztador) for 3 players. Players answer trivia questions to conquer territories on a map, and the player with the most points at the end wins.

School project for the Internet Programming course.

## Tech stack

- Backend: Python 3.12+, Django 5.2, Django REST Framework
- Frontend: React, Vite
- Database: SQLite
- Auth: Django session authentication with CSRF

## Project structure

```text
backend/    Django project (package "config")
frontend/   React + Vite app
```

## Running the backend (Windows PowerShell)

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py check
python manage.py runserver
```

The backend runs on http://127.0.0.1:8000/

## Loading the question bank

From the `backend` folder, with the virtual environment active:

```powershell
python manage.py migrate
python manage.py loaddata questions/question_bank.json
```

This loads 6 categories, 12 choice questions (48 answer options) and 12 numeric questions.

## Running the frontend (Windows PowerShell)

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs on http://localhost:5173/
