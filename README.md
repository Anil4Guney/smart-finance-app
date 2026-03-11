#  SmartFinance - AI-Powered Personal Finance Manager

<div align="center">
  <img src="https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D" alt="Vue.js" />
  <img src="https://img.shields.io/badge/Nuxt-002E3B?style=for-the-badge&logo=nuxtdotjs&logoColor=#00DC82" alt="Nuxt" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind" />
  <img src="https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white" alt="Gemini AI" />
</div>

<br>

# Smart Finance App

**Live Demo:** [https://smart-finance-app-kohl.vercel.app](https://smart-finance-app-kohl.vercel.app)


https://github.com/user-attachments/assets/38f081ff-1e76-4fa8-9f93-eca949cf889a





---

SmartFinance is a modern, full-stack personal finance application designed to help users track their expenses, manage monthly budgets, and achieve their savings goals. Built with a focus on automation and artificial intelligence, it acts as a smart companion for your financial journey.

###  Key Features
* **AI Financial Advisor:** Context-aware chatbot powered by Google Gemini AI that analyzes your current financial state, spending habits, and provides personalized insights.
* **OCR Receipt Scanning:** Instantly extract amounts, titles, and dates from physical receipts using AI vision models.
* **Smart Auto-Billing:** Intelligent subscription management system that automatically checks due dates and generates expense records to prevent missed tracking.
* **Secure Authentication:** Robust user authentication and persistent profile synchronization using JWT tokens and Django Djoser.
* **Advanced Analytics:** Interactive charts and a dynamic 6-month cash flow trend analyzer built with PrimeVue and Chart.js.
* **Savings Goals & Budgets:** Track your journey toward financial milestones with visual progress bars and dynamic budget limits.
* **Mobile-First Responsive Design:** Flawless UI experience across desktops, tablets, and smartphones using Tailwind CSS.
* **Fully Dockerized:** Ready for production with containerized isolated environments for both frontend and backend.

###  Tech Stack
* **Frontend:** Nuxt 3, Vue 3 (Composition API), Tailwind CSS, PrimeVue
* **Backend:** Python 3, Django, Django REST Framework (DRF), Djoser (Auth)
* **Database:** SQLite (Dev) / PostgreSQL (Prod)
* **DevOps & Tools:** Docker, Docker Compose, Git

###  Local Setup (Docker)
1. Clone the repository: `git clone https://github.com/Anil4Guney/smart-finance-app.git`
2. Add your Gemini API Key to `backend/.env`: `GEMINI_API_KEY=your_api_key_here`
3. Run the containers: `docker-compose up --build`
4. Access the App: `http://localhost:3000`
