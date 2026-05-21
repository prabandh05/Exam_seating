# Exam Seating Management System

A smart, full-stack web-based system designed to manage exam seating arrangements, exam scheduling, invigilator duties, and student exam information with automatic conflict handling and manual control.

## 🌟 Key Features
- **Smart Seating Engine**: Automatic conflict-free seating with modes like Mixed-Subject (Anti-Cheating), Same-Subject, Department-wise, and Random.
- **Three Dedicated Portals**: Secure logins for Admin, Invigilators, and Students.
- **Real-time Conflict Management**: Prevents time overlaps, capacity issues, and duplicate assignments.
- **Dynamic Dashboards**: Real-time statistics, seating layout visualization, and duty tracking.
- **Export & Reports**: One-click Excel exports for seating arrangements and attendance sheets.
- **Premium UI**: Modern dark theme with glassmorphism effects powered by React and Ant Design.

---

## 🚀 Quick Start Guide

Follow these steps to run the complete system on your local machine. You will need to run the Backend and Frontend in separate terminal windows.

### 1. Start the Backend (FastAPI)

Open your terminal and run the following commands:

```bash
# Navigate to the backend directory
cd /backend

# Create a virtual environment (if you haven't already)
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install all required Python dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn app.main:app --reload --port 8000
```

*Note: On its first run, the backend will automatically create the SQLite database (`exam_system.db`) and seed the default admin account.*

- **Backend API URL**: `http://localhost:8000`
- **Swagger API Docs**: `http://localhost:8000/docs`

---

### 2. Start the Frontend (React + Vite)

Open a **new terminal window** and run the following commands:

```bash
# Navigate to the frontend directory
cd /frontend

# Install all Node.js dependencies
npm install

# Start the Vite development server
npm run dev
```

*Note: The frontend is configured to automatically proxy API requests to your backend on port 8000.*

- **Frontend Application URL**: `http://localhost:5173`

---

## 🔐 Default Credentials

To get started, use the auto-generated default Admin account:

- **Role**: Admin
- **Username**: `admin`
- **Password**: `admin123`

Once logged in as Admin, you can create new students and invigilators, who will then be able to log in using their respective Register Numbers / IDs and passwords.

---

## 📁 Project Structure Overview

```text
Exam/
├── backend/
│   ├── app/
│   │   ├── api/        # REST endpoint routes (Auth, Admin, Invigilator, Student)
│   │   ├── core/       # Security, settings, and Enum definitions
│   │   ├── crud/       # Database interactions and queries
│   │   ├── db/         # SQLAlchemy engine and initialization
│   │   ├── models/     # Database schemas (SQLAlchemy ORM)
│   │   ├── schemas/    # Pydantic validation models
│   │   ├── services/   # Business logic (Seating Engine, Conflict Manager)
│   │   └── main.py     # FastAPI entry point
│   ├── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── api/        # Axios API client with interceptors
    │   ├── context/    # React Context for Authentication
    │   ├── pages/      # All UI pages (Admin, Invigilator, Student, Auth)
    │   ├── App.tsx     # Route definitions
    │   ├── index.css   # Premium dark glassmorphism styling
    │   └── main.tsx    # React entry point
    ├── package.json
    └── vite.config.ts  # Vite bundler config with backend proxy
```

## 🛠 Tech Stack
- **Backend**: Python 3, FastAPI, SQLAlchemy, SQLite, PyJWT, Pandas (for Bulk Uploads)
- **Frontend**: React 18, TypeScript, Vite, Ant Design v5, React Router DOM
