# Deployment Guide

This project is ready for deployment on various cloud platforms.

## Prerequisites
- A GitHub repository containing this code.

## Backend Deployment (Railway / Render / Heroku)
The backend uses **Django** with **MySQL**.

### 1. Database (MySQL)
You need a cloud MySQL database.
- **Railway/Render**: Create a new MySQL service. Note down the `Host`, `User`, `Password`, `Database Name`, and `Port`.

### 2. Environment Variables
Set these environment variables in your cloud provider's dashboard:
- `SECRET_KEY`: (Generate a random string)
- `DEBUG`: `False`
- `glibc` issues? (If using Python alpine images, stick to standard python:3.10-slim)

**Wait!** The current `settings.py` has the database credentials hardcoded for local development. For production:
1.  **Modify `settings.py`** to read from environment variables:
    ```python
    import os
    # ...
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'playto_db'),
            'USER': os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'raju143'),
            'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
            'PORT': os.environ.get('DB_PORT', '3306'),
        }
    }
    ```

### 3. Build Command
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

### 4. Start Command
```bash
gunicorn playto_backend.wsgi --log-file -
```

---

## Frontend Deployment (Vercel / Netlify)
The frontend is a **Vite + React** app.

### 1. Setup
- Push code to GitHub.
- Import project into Vercel.
- Set **Root Directory** to `playto_frontend`.

### 2. Build Settings (Auto-detected usually)
- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### 3. Environment Variables
The frontend needs to know where the backend API is.
1.  Create `.env.production` in `playto_frontend`:
    ```
    VITE_API_URL=https://your-backend-url.com/api/
    ```
2.  Update `api.js` to use this variable:
    ```javascript
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/';
    ```
