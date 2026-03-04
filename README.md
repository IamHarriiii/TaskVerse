<div align="center">

# 🧠 TaskVerse

**Cloud-Scale Task Management API & Dashboard**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

A production-ready task management system built with **FastAPI** and **Streamlit**, featuring JWT authentication, real-time analytics with interactive charts, pagination, full-text search, tags, subtasks, and more.

[Getting Started](#-getting-started) •
[Features](#-features) •
[API Reference](#-api-reference) •
[Architecture](#-architecture) •
[Contributing](#-contributing)

</div>

---

## ✨ Features

| Category | Details |
|---|---|
| 🔐 **Authentication** | JWT-based auth with bcrypt password hashing, token expiry, and protected endpoints |
| 📋 **Task Management** | Full CRUD with priority levels (1–5), status tracking, due dates, tags, and subtasks |
| 🔍 **Search & Filter** | Full-text search across titles/descriptions, filter by status, priority, tag, and user |
| 📄 **Pagination** | Configurable pagination with `skip` / `limit` and total count metadata |
| 🏷️ **Tags & Subtasks** | Organize tasks with comma-separated tags and nested subtask checklists |
| 📈 **Analytics Dashboard** | Interactive Plotly charts — donut, bar, treemap, and heatmap visualizations |
| 🛡️ **CORS** | Configurable cross-origin resource sharing |
| 📝 **Structured Logging** | Formatted log output across all services |
| ⚙️ **Config Management** | Environment-based settings via `.env` with pydantic-settings |
| 🧩 **Clean Architecture** | Layered design — Models → Schemas → Services → Routes with shared storage |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **pip** (or any Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/IamHarriiii/TaskVerse.git
cd TaskVerse

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and change SECRET_KEY for production!
```

### Running the Application

```bash
# Start the API server (default: http://localhost:8000)
uvicorn main:app --reload

# In a separate terminal, start the Streamlit dashboard
streamlit run frontend.py
```

| Service | URL |
|---|---|
| 🔌 API Server | [`http://localhost:8000`](http://localhost:8000) |
| 📖 Swagger Docs | [`http://localhost:8000/docs`](http://localhost:8000/docs) |
| 📘 ReDoc | [`http://localhost:8000/redoc`](http://localhost:8000/redoc) |
| 🖥️ Dashboard | [`http://localhost:8501`](http://localhost:8501) |

---

## 📖 API Reference

### Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/auth/register` | Register a new user | ❌ |
| `POST` | `/auth/login` | Login, returns JWT | ❌ |

### Users

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/users` | List all users | ❌ |
| `GET` | `/users/me` | Get current user profile | ✅ |
| `GET` | `/users/{id}` | Get user by ID | ❌ |
| `PUT` | `/users/{id}` | Update user (own profile only) | ✅ |
| `DELETE` | `/users/{id}` | Delete user + cascade tasks | ✅ |
| `GET` | `/users/{id}/tasks` | Get all tasks for a user | ❌ |

### Tasks

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/tasks` | List tasks (paginated, filterable) | ❌ |
| `GET` | `/tasks/{id}` | Get task by ID | ❌ |
| `POST` | `/tasks` | Create a new task | ✅ |
| `PUT` | `/tasks/{id}` | Update a task (own tasks only) | ✅ |
| `DELETE` | `/tasks/{id}` | Delete a task (own tasks only) | ✅ |

#### Query Parameters for `GET /tasks`

| Parameter | Type | Description |
|---|---|---|
| `status` | string | Filter by `pending`, `in_progress`, or `done` |
| `priority` | int | Filter by priority level (1–5) |
| `user_id` | UUID | Filter by assigned user |
| `tag` | string | Filter by tag name |
| `search` | string | Full-text search in title & description |
| `skip` | int | Pagination offset (default: 0) |
| `limit` | int | Results per page (default: 50, max: 200) |

### Example Request

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com", "password": "secret123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "secret123"}'

# Create a task (with token)
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<your_user_id>",
    "title": "Build TaskVerse",
    "priority": 5,
    "status": "in_progress",
    "due_date": "2026-12-31T00:00:00Z",
    "tags": ["backend", "urgent"],
    "subtasks": [
      {"title": "Set up auth", "is_completed": true},
      {"title": "Add analytics", "is_completed": false}
    ]
  }'

# Search tasks with filters
curl "http://localhost:8000/tasks?search=build&status=in_progress&priority=5&limit=10"
```

---

## 🏗️ Architecture

```
TaskVerse/
├── main.py                 # FastAPI app entry point (CORS, routes, logging)
├── config.py               # Pydantic-settings configuration
├── auth.py                 # JWT auth (bcrypt hashing, token creation)
├── exceptions.py           # Custom domain exceptions
├── logging_config.py       # Structured logging setup
├── frontend.py             # Streamlit dashboard with Plotly charts
│
├── models/                 # Pydantic domain models
│   ├── base.py             # BaseDomainModel (id, created_at)
│   ├── user.py             # User model
│   └── task.py             # Task model (+ SubTask, tags)
│
├── schemas/                # Request/response validation schemas
│   ├── user_schemas.py     # UserCreate, UserUpdate, UserResponse
│   └── task_schemas.py     # TaskCreate, TaskUpdate, TaskResponse, Paginated
│
├── services/               # Business logic layer
│   ├── storage_service.py  # Shared thread-safe JSON I/O
│   ├── user_service.py     # User CRUD + cascade delete
│   └── task_service.py     # Task CRUD + filtering + search
│
├── routes/                 # API route handlers
│   ├── auth_routes.py      # /auth/register, /auth/login
│   ├── user_routes.py      # /users CRUD + /users/{id}/tasks
│   └── task_routes.py      # /tasks CRUD with pagination
│
├── storage/
│   └── data.json           # JSON file storage
│
├── .env.example            # Environment variable template
├── .gitignore
├── requirements.txt        # Pinned dependencies
└── LICENSE
```

### Design Principles

- **Layered Architecture** — Clear separation between routes (HTTP), services (business logic), and models (data)
- **Domain Exceptions** — Services raise `NotFoundError` / `DuplicateError`; routes convert to HTTP responses
- **Shared Storage** — Single `StorageService` with thread-safe file locking eliminates duplication
- **Auth Boundary** — JWT dependency injection protects write operations while keeping reads public

---

## 🔧 Configuration

All settings are managed via environment variables. Copy `.env.example` to `.env`:

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | TaskVerse | Application name |
| `DEBUG` | false | Enable debug logging |
| `API_HOST` | 0.0.0.0 | API bind host |
| `API_PORT` | 8000 | API bind port |
| `CORS_ORIGINS` | ["*"] | Allowed CORS origins |
| `SECRET_KEY` | dev-secret… | **JWT signing key — change in production!** |
| `ALGORITHM` | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 60 | Token expiry (minutes) |

---

## 📊 Analytics Dashboard

The Streamlit frontend includes an interactive analytics tab with:

- **KPI Cards** — Total tasks, completed count, average priority, overdue count
- **Status Donut Chart** — Visual breakdown of pending / in-progress / done
- **Priority Bar Chart** — Distribution across priority levels with color scale
- **Tasks per User** — Horizontal bar chart showing workload distribution
- **Tag Treemap** — Hierarchical view of tag usage across all tasks
- **Status × Priority Heatmap** — Cross-tabulation revealing workload patterns

---

## 🛣️ Roadmap

- [ ] Migrate from JSON to **PostgreSQL** with SQLAlchemy + Alembic
- [ ] Add **unit & integration tests** with pytest
- [ ] **Docker** & docker-compose support
- [ ] **WebSocket** support for real-time updates
- [ ] **Rate limiting** with SlowAPI
- [ ] **Email notifications** for due dates
- [ ] **Role-based access control** (admin / user)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by [IamHarriiii](https://github.com/IamHarriiii)**

</div>
