# EduFlow - Academic Planning AI Assistant

EduFlow is an intelligent agent designed to help university students manage time, plan academic schedules, and optimize study sessions through adaptive, reasoning-based workflows.

## Features

- Analyzes student course loads, deadlines, and personal commitments
- Generates optimized weekly and daily study schedules
- Re-prioritizes tasks dynamically as new assignments, exams, or personal events arise
- Integrates with external systems (Google Calendar, Outlook, LMS portals)
- Sends smart reminders and notifications
- Provides performance insights and stress management tips

## Tech Stack

- LangGraph: For multi-node reasoning, adaptive task orchestration, and memory graph
- FastAPI: For backend API services, calendar/course integrations
- Streamlit: For the student dashboard (visual task planner, analytics, progress tracker)
- SQLite/PostgreSQL: For persistence of user data, tasks, schedules, and analytics
- LLM Integration: GPT or compatible LLM via OpenAI API
- Background Scheduler: Celery for reminders and periodic re-evaluation

## Getting Started

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` file
4. Run the backend: `uvicorn app.main:app --reload`
5. Run the frontend: `streamlit run app/frontend/dashboard.py`

## Project Structure

```
eduflow/
├── app/
│   ├── agent/                 # LangGraph agent components
│   │   ├── __init__.py
│   │   ├── analyzer.py        # Student Data Analyzer Node
│   │   ├── prioritizer.py     # Task Prioritization Node
│   │   ├── scheduler.py       # Schedule Optimization Node
│   │   ├── reminder.py        # Reminder & Adaptation Node
│   │   └── insights.py        # Student Insights Node
│   ├── api/                   # FastAPI routes
│   │   ├── __init__.py
│   │   ├── courses.py
│   │   ├── calendar.py
│   │   ├── schedule.py
│   │   ├── progress.py
│   │   └── insights.py
│   ├── db/                    # Database models and connections
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── database.py
│   ├── frontend/              # Streamlit frontend
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── planner.py
│   │   ├── analytics.py
│   │   └── chat.py
│   ├── integrations/          # External service integrations
│   │   ├── __init__.py
│   │   ├── google_calendar.py
│   │   ├── outlook.py
│   │   └── lms.py
│   ├── scheduler/             # Background task scheduler
│   │   ├── __init__.py
│   │   ├── tasks.py
│   │   └── celery_app.py
│   ├── __init__.py
│   └── main.py                # FastAPI application entry point
├── .env.example               # Example environment variables
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```