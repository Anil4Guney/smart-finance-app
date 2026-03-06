# Database Migration Guide

## Step 1: Clean Old Database and Migrations

**⚠️ WARNING: This will delete all existing data!**

Run these commands in PowerShell from the `backend/` directory:

```powershell
cd c:\Users\GUNEY\smart-finance-app\backend

# Delete old database
Remove-Item db.sqlite3 -ErrorAction SilentlyContinue

# Delete old migration files (keep __init__.py)
Remove-Item finance\migrations\*.py -Exclude __init__.py -ErrorAction SilentlyContinue
```

## Step 2: Re-initialize Database

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install new dependencies (djoser, simplejwt)
pip install -r requirements.txt

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser
```

## Step 3: Verify Setup

Start the server:

```powershell
python manage.py runserver
```

Test authentication endpoints:
- Register: `POST http://127.0.0.1:8000/auth/users/`
- Login: `POST http://127.0.0.1:8000/auth/jwt/create/`

## Notes

- The seed_data command will need to be updated to include a user parameter
- All transactions and savings goals now require a user
- Use the frontend login/register pages to create users
