# Deployment Guide

This project is ready for deployment on various cloud platforms.

## Prerequisites
- A GitHub repository containing this code.

## Recommended Stack: Render (Backend) + Vercel (Frontend)

### Part 1: Backend on Render.com
1.  **Create Service**:
    - Sign up at [dashboard.render.com](https://dashboard.render.com/).
    - Click **New +** -> **Web Service**.
    - Connect your GitHub repo `Playto`.
    - Select `playto_backend` does not apply because root is repo root. **Root Directory**: `.` (leave empty or dot).

2.  **Settings**:
    - **Runtime**: Python 3
    - **Build Command**: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
    - **Start Command**: `gunicorn playto_backend.wsgi`

3.  **Environment Variables**:
    - Add `PYTHON_VERSION` = `3.10.0`
    - Add `SECRET_KEY` = (generate one)
    - Add `DB_ENGINE` = `django.db.backends.postgresql`
    - Add `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (Get these from your Render Database Dashboard)

### Part 2: Frontend on Vercel
1.  **Import Project**:
    - Go to [vercel.com](https://vercel.com/new).
    - Import `Playto`.

2.  **Configure Project**:
    - **Framework Preset**: Vite
    - **Root Directory**: Click "Edit" and select `playto_frontend`.

3.  **Environment Variables**:
    - Add `VITE_API_URL` = `https://<your-render-backend-name>.onrender.com/api/`

4.  **Deploy**: Click Deploy!
