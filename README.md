# SmartFinance

Personal finance application with Django backend and Nuxt 3 + PrimeVue (Aura) + Tailwind CSS frontend. Structure prepared for LLM integration (OpenAI/Gemini).

## Tech Stack

- **Backend:** Python, Django, Django REST Framework, SQLite
- **Frontend:** Nuxt 3, PrimeVue (Aura Theme), Tailwind CSS
- **AI:** Placeholder for OpenAI / Gemini

---

## Setup Commands

### Backend

```powershell
# From project root
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# (Optional) Create superuser for admin
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Backend API: **http://127.0.0.1:8000**  
Admin: **http://127.0.0.1:8000/admin**  
API endpoints: **http://127.0.0.1:8000/api/transactions/** and **http://127.0.0.1:8000/api/savings-goals/**

### Frontend

```powershell
# From project root
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend: **http://localhost:3000**

---

## Project Structure

```
smart-finance-app/
├── backend/
│   ├── config/                 # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ...
│   ├── finance/                # Finance app
│   │   ├── models.py           # Transaction, SavingsGoal
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── layouts/
│   │   └── default.vue         # Sidebar + Navbar layout
│   ├── pages/
│   │   ├── index.vue           # Dashboard
│   │   ├── transactions/
│   │   └── savings/
│   ├── plugins/
│   │   └── primevue.client.ts
│   ├── nuxt.config.ts
│   └── package.json
└── README.md
```

---

## Backend Models

- **Transaction:** `amount`, `type` (income/expense), `category`, `date`, `description`
- **SavingsGoal:** `name`, `target_amount`, `current_amount`, `deadline`

---

## License

Private / Educational use.
