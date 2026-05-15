# 🎓 Placement Portal — Campus Recruitment Management System

<div align="center">

![Vue.js](https://img.shields.io/badge/Vue.js_3-35495E?style=for-the-badge&logo=vue.js&logoColor=4FC08D)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
![Python](https://img.shields.io/badge/Python_3-3776AB?style=for-the-badge&logo=python&logoColor=white)

A full-stack web application that streamlines campus recruitment by connecting **students**, **companies**, and **administrators** through a centralized, role-based platform.

[📺 Video Demo](https://drive.google.com/file/d/1ADR_F6QxJHd3SnJyjx3tEU9MhTCuXOOH/view?usp=sharing) · [📄 Project Report](#) · [🐛 Report Bug](#) · [💡 Request Feature](#)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Database Schema](#-database-schema)
- [API Endpoints](#-api-endpoints)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Background Tasks](#-background-tasks)
- [Author](#-author)

---

## 🌐 Overview

The **Placement Portal** is a comprehensive web-based Placement Management System designed to modernize and centralize the campus recruitment process. It provides tailored dashboards and workflows for three distinct user roles — **Admin**, **Company**, and **Student** — with secure JWT-based authentication and fully asynchronous background job processing.

**Key Highlights:**
- ✅ Role-based access control (RBAC) with Flask-Security-Too
- ✅ Asynchronous job processing via Celery + Redis (Memurai on Windows)
- ✅ Automated daily deadline reminders & monthly report generation
- ✅ CSV export of student applications
- ✅ Real-time caching with Redis for high-performance dashboard queries

---

## 🏗 Architecture

The application follows a clean **3-tier architecture**:

```
┌─────────────────────────────────────────────┐
│              CLIENT LAYER                   │
│  Vue.js 3  ·  Pinia  ·  Vue Router          │
│  Admin UI / Student UI / Company UI         │
│  Port: 5173                                 │
└───────────────────┬─────────────────────────┘
                    │  HTTP/HTTPS (Port 5000)
                    │  JWT Tokens
┌───────────────────▼─────────────────────────┐
│           BACKEND API LAYER                 │
│  Flask  ·  CORS  ·  Auth Middleware         │
│  Rate Limiting  ·  RESTful APIs             │
└───────────────────┬─────────────────────────┘
                    │
┌───────────────────▼─────────────────────────┐
│       INFRASTRUCTURE & SERVICES             │
│  SQLite (DB) · Redis/Memurai (Cache+Broker) │
│  Celery (Task Queue) · File Storage         │
│  Gmail / Google Chat Webhook (Notifications)│
└─────────────────────────────────────────────┘
```

> See the full architecture diagram in [`/docs/architecture.png`](./docs/architecture.png).

---

## ✨ Features

### 👨‍💼 Admin
- Dashboard with aggregated placement statistics
- Approve / reject / blacklist companies and students
- Manage and moderate all placement drives
- Trigger monthly PDF reports (async via Celery)
- Global search across all entities

### 🏢 Company
- Register and manage company profile
- Create, update, and delete placement drives
- Review applicants — shortlist, schedule interviews, select, or reject
- View drive-specific and overall application dashboards

### 🎓 Student
- Build and manage personal profile with resume upload
- Browse and apply to eligible placement drives
- Track application status in real time
- Export personal application history as CSV
- View placement history

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Vue.js 3 | Reactive SPA framework |
| **State Management** | Pinia | Centralized store for auth, messages, cache |
| **Routing** | Vue Router | Client-side SPA navigation |
| **HTTP Client** | Axios | API communication from frontend |
| **UI Framework** | Bootstrap 5 | Responsive design & components |
| **Backend** | Flask | REST API server |
| **ORM** | SQLAlchemy | Database abstraction layer |
| **Database** | SQLite | Lightweight relational data store |
| **Authentication** | Flask-Security-Too | RBAC, session management, JWT |
| **API Layer** | Flask-RESTful | Structured REST endpoint building |
| **Task Queue** | Celery | Async background job processing |
| **Message Broker** | Memurai (Redis) | Windows-native Redis for Celery & caching |
| **Caching** | Flask-Caching | Redis-backed API response caching |
| **CORS** | Flask-CORS | Cross-origin request handling |
| **Email (Dev)** | MailHog | Email capture & testing in development |

> **Note on Memurai:** Used instead of Redis directly for Windows-native compatibility — no WSL or Docker required.

---

## 🗃 Database Schema

### Tables

| Table | Description |
|---|---|
| `User` | Authentication credentials, login timestamps, security tokens |
| `Role` | Role definitions: `admin`, `company`, `student` |
| `UserRoles` | Many-to-many association table between User and Role |
| `Student` | Student profile: name, roll number, branch, CGPA, resume metadata |
| `Company` | Company profile: HR contact, industry, location, approval status |
| `PlacementDrive` | Drive details: eligibility, CGPA cutoff, deadline, approval status |
| `Application` | Application tracking: status (applied/shortlisted/selected/rejected), timestamps |

### Relationships

```
User ◄──many-to-many──► Role         (via UserRoles)
User ◄──one-to-one────► Student
User ◄──one-to-one────► Company
Company ◄──one-to-many─► PlacementDrive
Student ◄──one-to-many─► Application
PlacementDrive ◄─one-to-many─► Application
```

---

## 🔌 API Endpoints

<details>
<summary><strong>🔐 Authentication APIs</strong></summary>

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/login` | Authenticate user |
| `POST` | `/api/logout` | Logout current session |
| `POST` | `/api/register` | Register new user |
| `POST` | `/api/check-email` | Check email availability |
| `GET` | `/api/profile` | Get current user profile |
| `POST` | `/api/change-password` | Change user password |

</details>

<details>
<summary><strong>👨‍💼 Admin APIs</strong> <code>/api/admin/*</code></summary>

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/admin/dashboard` | Dashboard statistics |
| `GET` | `/api/admin/companies` | List all companies |
| `POST` | `/api/admin/companies/<id>/approve` | Approve company |
| `POST` | `/api/admin/companies/<id>/reject` | Reject company |
| `POST` | `/api/admin/companies/<id>/blacklist` | Blacklist company |
| `GET` | `/api/admin/drives` | List all drives |
| `POST` | `/api/admin/drives/<id>/approve` | Approve drive |
| `POST` | `/api/admin/drives/<id>/close` | Close drive |
| `GET` | `/api/admin/students` | List all students |
| `POST` | `/api/admin/students/<id>/blacklist` | Blacklist student |
| `GET` | `/api/admin/search` | Global entity search |
| `POST` | `/api/admin/reports/monthly` | Generate monthly report (async) |
| `GET` | `/api/admin/tasks/<task_id>` | Check Celery task status |

</details>

<details>
<summary><strong>🎓 Student APIs</strong> <code>/api/student/*</code></summary>

| Method | Endpoint | Description |
|---|---|---|
| `GET/PUT` | `/api/student/profile` | Get or update profile |
| `GET` | `/api/student/dashboard` | Student dashboard |
| `GET` | `/api/student/drives` | Browse available drives |
| `POST` | `/api/student/drives/<id>/apply` | Apply to a drive |
| `GET` | `/api/student/applications` | List my applications |
| `DELETE` | `/api/student/applications/<id>` | Withdraw application |
| `GET` | `/api/student/history` | Placement history |
| `POST` | `/api/student/export/applications` | Export applications as CSV |

</details>

<details>
<summary><strong>🏢 Company APIs</strong> <code>/api/company/*</code></summary>

| Method | Endpoint | Description |
|---|---|---|
| `GET/PUT` | `/api/company/profile` | Get or update profile |
| `GET` | `/api/company/dashboard` | Company dashboard |
| `GET/POST` | `/api/company/drives` | List or create drives |
| `GET/PUT/DELETE` | `/api/company/drives/<id>` | Manage specific drive |
| `GET` | `/api/company/drives/<id>/applications` | Drive applicants list |
| `POST` | `/api/company/applications/<id>/shortlist` | Shortlist applicant |
| `POST` | `/api/company/applications/<id>/select` | Select applicant |
| `POST` | `/api/company/applications/<id>/reject` | Reject applicant |
| `POST` | `/api/company/applications/<id>/scheduleinterview` | Schedule interview |

</details>

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- [Memurai](https://www.memurai.com/) (Windows) or Redis (Linux/macOS)
- [MailHog](https://github.com/mailhog/MailHog) (for email testing)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/placement-portal.git
cd placement-portal/backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize the database
flask db upgrade

# Start the Flask development server
flask run --port 5000
```

### Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start the Vue.js dev server
npm run dev
# App available at http://localhost:5173
```

### Celery Worker

```bash
# In a separate terminal (with venv activated)
cd backend
celery -A app.celery worker --loglevel=info
```

### Celery Beat (Scheduler)

```bash
celery -A app.celery beat --loglevel=info
```

### Environment Variables

Create a `.env` file in `/backend`:

```env
SECRET_KEY=your-secret-key
SECURITY_PASSWORD_SALT=your-password-salt
SQLALCHEMY_DATABASE_URI=sqlite:///placement.db
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
MAIL_SERVER=localhost
MAIL_PORT=1025
GOOGLE_CHAT_WEBHOOK_URL=https://chat.googleapis.com/...
```

---

## 📁 Project Structure

```
placement-portal/
├── backend/
│   ├── app.py                  # Flask app factory & entry point
│   ├── models.py               # SQLAlchemy models
│   ├── resources/
│   │   ├── auth.py             # Auth API resources
│   │   ├── admin.py            # Admin API resources
│   │   ├── student.py          # Student API resources
│   │   └── company.py          # Company API resources
│   ├── tasks/
│   │   ├── reminders.py        # Daily deadline reminder tasks
│   │   ├── reports.py          # Monthly report generation
│   │   └── exports.py          # CSV export tasks
│   ├── utils/
│   │   ├── email.py            # Email utilities
│   │   └── cache.py            # Cache helpers
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── admin/          # Admin dashboard views
│   │   │   ├── student/        # Student views
│   │   │   └── company/        # Company views
│   │   ├── stores/
│   │   │   ├── auth.js         # Pinia auth store
│   │   │   └── message.js      # Pinia message store
│   │   ├── router/index.js     # Vue Router config
│   │   └── main.js
│   └── package.json
├── docs/
│   └── architecture.png
└── README.md
```

---

## ⚙️ Background Tasks

Powered by **Celery** with **Memurai/Redis** as the message broker:

| Task | Trigger | Description |
|---|---|---|
| `send_deadline_reminders` | Daily (Celery Beat) | Emails students about upcoming application deadlines |
| `generate_monthly_report` | On-demand / Monthly | Produces a placement summary report (PDF) |
| `export_applications_csv` | On-demand | Exports student application data as CSV |
| `send_email_notification` | Event-driven | Sends status update emails on application changes |

---

## 📺 Video Presentation

Watch the full project walkthrough here:
👉 [Google Drive Demo Video](https://drive.google.com/file/d/1ADR_F6QxJHd3SnJyjx3tEU9MhTCuXOOH/view?usp=sharing)

---

## 👤 Author

**Abhinu Yadav**
- 🎓 B.Tech (ECE), AKTU | BS Degree Candidate, IIT Madras
- 📧 [23f3004444@ds.study.iitm.ac.in](mailto:23f3004444@ds.study.iitm.ac.in)
- 🔖 Roll Number: 23F3004444

---

## 📜 License

This project was developed as part of the **App Development 2** course at **IIT Madras**. All rights reserved © 2024.

---

<div align="center">
  <sub>Built with ❤️ using Flask, Vue.js, Celery, and SQLite</sub>
</div>
