import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to sys.path
root_path = str(Path(__file__).parent)
if root_path not in sys.path:
    sys.path.append(root_path)

import pandas as pd
import datetime
import random

# Set page configuration
st.set_page_config(
    page_title="EduFlow - Academic Planning Assistant",
    page_icon="📚",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("EduFlow")
st.sidebar.subheader("Academic Planning Assistant")

# Navigation options
page = st.sidebar.radio("Navigation", ["Dashboard", "Smart Planner", "Analytics", "Chat Assistant", "Settings"])

# Initialize session state for data persistence
if "courses" not in st.session_state:
    st.session_state.courses = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "schedule" not in st.session_state:
    st.session_state.schedule = []

# Data retrieval helpers
def get_courses():
    return st.session_state.courses

def get_tasks():
    return st.session_state.tasks

# Generate mock schedule data based on tasks (simplified)
def update_schedule_from_tasks():
    today = datetime.date.today()
    new_schedule = []
    
    courses = get_courses()
    # For now, let's create a simple study block for each task
    for task in st.session_state.tasks:
        if not task.get("completed", False):
            try:
                due_date = datetime.datetime.strptime(task["due_date"], "%Y-%m-%d").date()
                # Suggest a study block for today if the task is upcoming
                if due_date >= today:
                    day_name = today.strftime("%A")
                    course_name = next((c["name"] for c in courses if c["id"] == task["course_id"]), "Study Session")
                    
                    new_schedule.append({
                        "day": day_name,
                        "date": today.strftime("%Y-%m-%d"),
                        "start_time": "14:00",
                        "end_time": "16:00",
                        "course": course_name,
                        "activity": f"Work on {task['title']}"
                    })
            except (ValueError, KeyError):
                continue
    
    st.session_state.schedule = new_schedule

# Initial schedule update if empty
if not st.session_state.schedule and st.session_state.tasks:
    update_schedule_from_tasks()

schedule = st.session_state.schedule

def get_insights():
    if not st.session_state.tasks:
        return []
    
    total = len(st.session_state.tasks)
    completed = len([t for t in st.session_state.tasks if t.get("completed")])
    
    return [
        {"title": "Task Progress", "description": f"You have completed {completed} out of {total} tasks.", "score": int((completed/total)*100) if total > 0 else 0},
        {"title": "Study Tip", "description": "Break large tasks into smaller, manageable chunks for better focus.", "score": 100}
    ]

# Dashboard Page
if page == "Dashboard":
    st.title("📊 Student Dashboard")
    
    # Welcome message
    st.markdown("### Welcome to EduFlow!")
    st.write("Your AI-powered academic planning assistant")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    courses = get_courses()
    tasks = get_tasks()
    
    with col1:
        st.metric(label="Courses", value=str(len(courses)))
    with col2:
        st.metric(label="Upcoming Tasks", value=str(len([t for t in tasks if not t.get("completed")])))
    with col3:
        st.metric(label="Study Hours This Week", value="0")
    with col4:
        completion_rate = "0%"
        if tasks:
            completed = len([t for t in tasks if t.get("completed")])
            completion_rate = f"{(completed / len(tasks)) * 100:.0f}%"
        st.metric(label="Task Completion Rate", value=completion_rate)
    
    # Upcoming deadlines
    st.subheader("📅 Upcoming Deadlines")
    upcoming_tasks = [task for task in tasks if not task.get("completed")]
    if upcoming_tasks:
        upcoming_df = pd.DataFrame(upcoming_tasks)
        upcoming_df = upcoming_df[["title", "due_date", "priority"]]
        st.dataframe(upcoming_df, use_container_width=True)
    else:
        st.info("No upcoming deadlines. Take a break!")
    
    # Today's schedule
    st.subheader("📝 Today's Schedule")
    today = datetime.date.today().strftime("%Y-%m-%d")
    today_schedule = [s for s in st.session_state.schedule if s["date"] == today]
    if today_schedule:
        today_df = pd.DataFrame(today_schedule)
        today_df = today_df[["start_time", "end_time", "course", "activity"]]
        st.dataframe(today_df, use_container_width=True)
    else:
        st.info("No study blocks scheduled for today.")
    
    # Key insights
    st.subheader("💡 Key Insights")
    insights_list = get_insights()
    if insights_list:
        insight_cols = st.columns(len(insights_list))
        for i, insight in enumerate(insights_list):
            with insight_cols[i]:
                st.info(f"**{insight['title']}**: {insight['description']}")
    else:
        st.info("Add tasks to see insights!")

# Smart Planner Page
elif page == "Smart Planner":
    st.title("🧠 Smart Planner")
    
    planner_tab1, planner_tab2 = st.tabs(["Weekly Schedule", "Task Management"])
    
    with planner_tab1:
        # Weekly schedule view
        st.subheader("Weekly Schedule")
        
        # Group schedule by day
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Create tabs for each day
        day_tabs = st.tabs(days)
        
        if st.session_state.schedule:
            schedule_df = pd.DataFrame(st.session_state.schedule)
            for i, day in enumerate(days):
                with day_tabs[i]:
                    day_schedule = schedule_df[schedule_df["day"] == day]
                    if not day_schedule.empty:
                        st.dataframe(day_schedule[["start_time", "end_time", "course", "activity"]], use_container_width=True)
                    else:
                        st.info(f"No study blocks scheduled for {day}.")
        else:
            for i, day in enumerate(days):
                with day_tabs[i]:
                    st.info(f"No study blocks scheduled for {day}.")
    
    with planner_tab2:
        # Task management
        st.subheader("Task Management")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            tasks = get_tasks()
            if tasks:
                task_df = pd.DataFrame(tasks)
                # Ensure due_date is in datetime format for the DateColumn to work correctly
                if 'due_date' in task_df.columns:
                    task_df['due_date'] = pd.to_datetime(task_df['due_date']).dt.date
                
                # Use data_editor to allow marking as completed
                edited_df = st.data_editor(
                    task_df, 
                    use_container_width=True, 
                    key="task_editor",
                    column_config={
                        "completed": st.column_config.CheckboxColumn("Completed"),
                        "priority": st.column_config.SelectboxColumn("Priority", options=["Low", "Medium", "High"]),
                        "due_date": st.column_config.DateColumn("Due Date")
                    },
                    disabled=["id"]
                )
                
                # Update session state if changes are made
                if not edited_df.equals(task_df):
                    st.session_state.tasks = edited_df.to_dict('records')
                    # Convert dates back to strings for consistency if necessary
                    for t in st.session_state.tasks:
                        if isinstance(t.get('due_date'), (datetime.date, datetime.datetime)):
                            t['due_date'] = t['due_date'].isoformat()
                    update_schedule_from_tasks()
                    st.rerun()
            else:
                st.info("No tasks added yet. Add your first task on the right!")
        
        with col2:
            st.subheader("Add New Task")
            with st.form("add_task_form", clear_on_submit=True):
                task_title = st.text_input("Task Title")
                courses = get_courses()
                course_names = [c["name"] for c in courses]
                if course_names:
                    course = st.selectbox("Course", course_names)
                else:
                    st.warning("Add a course first!")
                    course = None
                
                due_date = st.date_input("Due Date")
                priority = st.select_slider("Priority", options=["Low", "Medium", "High"])
                
                if st.form_submit_button("Add Task"):
                    if task_title and course:
                        course_id = next((c["id"] for c in courses if c["name"] == course), 1)
                        new_task = {
                            "id": len(st.session_state.tasks) + 1,
                            "title": task_title,
                            "course_id": course_id,
                            "due_date": due_date.strftime("%Y-%m-%d"),
                            "priority": priority,
                            "completed": False
                        }
                        st.session_state.tasks.append(new_task)
                        update_schedule_from_tasks()
                        st.success(f"Task '{task_title}' added!")
                        st.rerun()
                    elif not course:
                        st.error("Please add a course first.")
                    else:
                        st.error("Please enter a task title.")
            
            st.divider()
            st.subheader("Add New Course")
            with st.form("add_course_form", clear_on_submit=True):
                c_name = st.text_input("Course Name")
                c_code = st.text_input("Course Code")
                if st.form_submit_button("Add Course"):
                    if c_name:
                        new_c = {
                            "id": len(st.session_state.courses) + 1,
                            "name": c_name,
                            "code": c_code,
                        }
                        st.session_state.courses.append(new_c)
                        st.success(f"Course '{c_name}' added!")
                        st.rerun()

# Analytics Page
elif page == "Analytics":
    st.title("📈 Analytics")
    
    courses = get_courses()
    tasks = get_tasks()
    
    if not courses and not tasks:
        st.info("Add courses and tasks to see analytics!")
    else:
        # Course distribution
        st.subheader("Task Distribution by Course")
        if courses:
            course_data = {
                "Course": [c["name"] for c in courses],
                "Tasks": [len([t for t in tasks if t.get("course_id") == c["id"]]) for c in courses]
            }
            df = pd.DataFrame(course_data)
            if not df.empty and df["Tasks"].sum() > 0:
                st.bar_chart(df.set_index("Course"))
            else:
                st.write("No tasks assigned to courses yet.")
        else:
            st.write("No courses added yet.")
        
        # Task status
        st.subheader("Task Status")
        if tasks:
            completed = len([t for t in tasks if t.get("completed")])
            total = len(tasks)
            st.write(f"Completed: {completed} / {total}")
            st.progress(completed / total if total > 0 else 0)
        else:
            st.write("No tasks added yet.")

# Chat Assistant Page
elif page == "Chat Assistant":
    st.title("💬 Chat Assistant")
    
    from app.agent.agent_graph import run_chat_agent

    st.write("Ask EduFlow about your academic schedule, get help with planning, or request insights.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm EduFlow, your academic planning assistant. How can I help you today?"}
        ]
    
    # Add a Clear Chat button
    if st.button("Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat history cleared! How can I help you today?"}
        ]
        st.rerun()

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about your schedule, study strategies, or time management..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
            
        # Generate assistant response using LangGraph agent
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Get context from session state
                    courses = get_courses()
                    tasks = get_tasks()
                    
                    # Run the chat agent
                    response = run_chat_agent(
                        messages=st.session_state.messages,
                        courses=courses,
                        tasks=tasks,
                        schedule=st.session_state.schedule
                    )
                    st.write(response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error connecting to AI: {str(e)}")
                    st.write("I'm having trouble connecting to my brain right now. Please check your OpenAI API key in the .env file.")

# Settings Page
elif page == "Settings":
    st.title("⚙️ Settings")
    
    # User preferences
    st.subheader("User Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Preferred Study Time", ["Morning", "Afternoon", "Evening", "Night"])
        st.number_input("Daily Study Goal (hours)", min_value=1, max_value=12, value=4)
        st.selectbox("Notification Frequency", ["High", "Medium", "Low", "None"])
    
    with col2:
        st.multiselect("Preferred Study Days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        st.selectbox("Calendar Integration", ["Google Calendar", "Outlook", "Apple Calendar", "None"])
        st.toggle("Enable AI Insights", value=True)
    
    # Calendar integrations
    st.subheader("Calendar Integrations")
    
    st.info("Connect your academic calendars to automatically import class schedules and deadlines.")
    
    if st.button("Connect Google Calendar"):
        st.success("Google Calendar connected successfully!")
    
    if st.button("Connect Outlook Calendar"):
        st.success("Outlook Calendar connected successfully!")
    
    # Save settings
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("EduFlow v1.0.0")
st.sidebar.caption("© 2023 EduFlow AI")