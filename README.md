# Playto Engineering Challenge

## Overview
A "Community Feed" prototype with threaded discussions and a dynamic leaderboard, built with Django (DRF) and React.

## Stack
- **Backend**: Django 5, Django REST Framework, SQLite
- **Frontend**: React (Vite), Tailwind CSS
- **Tools**: Python, Node.js

## Features
- **Feed**: View posts with like counts.
- **Threaded Comments**: Infinite nesting with optimized fetching (O(1) queries per post).
- **Concurrency**: Secure voting logic (Atomic transactions + UniqueConstraints).
- **Dynamic Leaderboard**: Calculates top users based on Karma earned in the **last 24 hours**.

## Setup & Running

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend
1. Navigate to the project root:
   ```bash
   cd d:/Project
   ```
2. Activate virtual environment:
   ```bash
   .\venv\Scripts\Activate.ps1
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```
5. Run server:
   ```bash
   python manage.py runserver
   ```

### Frontend
1. Navigate to frontend directory:
   ```bash
   cd playto_frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run dev server:
   ```bash
   npm run dev
   ```
4. Open http://localhost:5173

## Testing
Run backend tests:
```bash
python manage.py test api
```
