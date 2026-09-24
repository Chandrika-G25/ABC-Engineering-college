"# Student Management System

A **Student Management System** built with **Django** that provides a web interface for managing students, courses, and enrollments. This project demonstrates core CRUD operations, authentication, and integration with both **MySQL** and **SQLite** databases.

---
Live deploy Link:https://abc-engineering-college-1.onrender.com/

## Features

- **Student CRUD** – Create, read, update, and delete student records.
- **Course Management** – Manage course catalog with details.
- **Enrollment Tracking** – Associate students with courses.
- **Authentication** – Admin login powered by Django's built‑in auth system.
- **Database Flexibility** – Switch between **MySQL** and **SQLite** via an environment flag.
- **Responsive UI** – Basic Bootstrap styling for a clean look.

---

## Tech Stack

| Layer | Technology |
|-------|-------------|
| Backend | Python 3.11, Django 4.x |
| Database | MySQL (default) or SQLite (fallback) |
| Frontend | HTML5, CSS3, Bootstrap 5 |
| Environment | `.env` with **django‑environ** |
| Deployment | Render |

---
## Project Structure

```
Student_Management_System/
├─ config/                 # Django settings package
│   ├─ __init__.py
│   └─ settings.py
├─ students/               # Core app – models, views, templates
│   ├─ migrations/
│   ├─ admin.py
│   ├─ models.py
│   ├─ views.py
│   └─ templates/
├─ static/                 # Static assets (CSS, JS, images)
├─ .env.example            # Example env file
├─ .env                    # Your local environment variables (git‑ignored)
├─ manage.py               # Django CLI entry point
├─ requirements.txt        # Python dependencies
├─ start_server.bat        # Helper script to activate venv & run server
└─ README.md               # **You are here**
```

---



*Happy coding!*" 
