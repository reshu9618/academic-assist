import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# API endpoint (change to your actual API URL when deployed)
API_URL = "http://localhost:8000/api"

# Page configuration
st.set_page_config(
    page_title="EduFlow - Academic Planning Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("EduFlow")
st.sidebar.image("https://via.placeholder.com/150?text=EduFlow", width=150)

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Smart Planner", "Analytics", "Chat Assistant", "Settings"]
)

# User info (mock data - would be from authentication in a real app)
user = {
    "id": 1,
    "name": "Student Name",
    "email": "student@university.edu"
}

# Mock data for demonstration
def get_mock_courses():
    return [
        {
            "id": 1,
            "name": "Introduction to Computer Science",
            "code": "CS101",
            "credit_hours": 3.0,
            "difficulty_rating": 3
        },
        {
            "id": 2,
            "name": "Calculus I",
            "code": "MATH101",
            "credit_hours": 4.0,
            "difficulty_rating": 4
        },
        {
            "id": 3,
            "name": "Introduction to Psychology",
            "code": "PSYCH101",
            "credit_hours": 3.0,
            "difficulty_rating": 2
        },
        {
            "id": 4,
            "name": "English Composition",
            "code": "ENG101",
            "credit_hours": 3.0,
            "difficulty_rating": 2
        }
    ]

def get_mock_tasks():
    return [
        {
            "id": 1,
            "title": "CS101 Programming Assignment",
            "course_id": 1,
            "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "priority": 4,
            "estimated_hours": 5,
            "completed": False
        },
        {
            "id": 2,
            "title": "MATH101 Problem Set",
            "course_id": 2,
            "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "priority": 5,
            "estimated_hours": 4,
            "completed": False
        },
        {
            "id": 3,
            "title": "PSYCH101 Research Paper",
            "course_id": 3,
            "due_date": (datetime.now() + timedelta(days=10)).isoformat(),
            "priority": 3,
            "estimated_hours": 8,
            "completed": False
        },
        {
            "id": 4,
            "title": "ENG101 Essay Draft",
            "course_id": 4,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "priority": 3,
            "estimated_hours": 3,
            "completed": False
        }
    ]

def get_mock_schedule():
    today = datetime.now().date()
    return {
        "weekly_plan": {
            (today + timedelta(days=i)).isoformat(): [
                {
                    "start_time": f"{9+i}:00",
                    "end_time": f"{10+i}:00",
                    "task_id": i % 4 + 1,
                    "task_title": get_mock_tasks()[i % 4]["title"]
                }
                for j in range(2)  # 2 blocks per day
            ]
            for i in range(7)  # 7 days
        },
        "daily_focus": {
            (today + timedelta(days=0)).isoformat(): "MATH101",
            (today + timedelta(days=1)).isoformat(): "CS101",
            (today + timedelta(days=2)).isoformat(): "PSYCH101",
            (today + timedelta(days=3)).isoformat(): "ENG101",
            (today + timedelta(days=4)).isoformat(): "MATH101",
            (today + timedelta(days=5)).isoformat(): "CS101",
            (today + timedelta(days=6)).isoformat(): "Review All"
        }
    }

def get_mock_insights():
    return [
        {
            "type": "productivity",
            "content": "Your study focus peaks at 10 AM."
        },
        {
            "type": "time_management",
            "content": "You're spending 60% of your time on low-priority tasks."
        },
        {
            "type": "suggestion",
            "content": "Try breaking large assignments into smaller chunks."
        },
        {
            "type": "stress",
            "content": "Consider adding 15-minute breaks between study sessions."
        }
    ]

# Dashboard page
if page == "Dashboard":
    st.title("📊 EduFlow Dashboard")
    st.subheader(f"Welcome back, {user['name']}!")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Courses", value="4")
    with col2:
        st.metric(label="Upcoming Tasks", value="7")
    with col3:
        st.metric(label="Study Hours This Week", value="24")
    with col4:
        st.metric(label="Task Completion Rate", value="85%")
    
    # Upcoming deadlines
    st.subheader("📅 Upcoming Deadlines")
    tasks = get_mock_tasks()
    tasks_df = pd.DataFrame(tasks)
    tasks_df['due_date'] = pd.to_datetime(tasks_df['due_date'])
    tasks_df = tasks_df.sort_values('due_date')
    
    for _, task in tasks_df.iterrows():
        days_left = (task['due_date'] - datetime.now()).days
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{task['title']}** - Due in {days_left} days")
        with col2:
            st.write(f"Priority: {'🔴' if task['priority'] >= 4 else '🟡' if task['priority'] >= 2 else '🟢'}")
    
    # Today's schedule
    st.subheader("📝 Today's Schedule")
    schedule = get_mock_schedule()
    today = datetime.now().date().isoformat()
    
    if today in schedule["weekly_plan"]:
        for block in schedule["weekly_plan"][today]:
            st.write(f"**{block['start_time']} - {block['end_time']}**: {block['task_title']}")
    else:
        st.write("No scheduled tasks for today.")
    
    # Insights
    st.subheader("💡 Insights")
    insights = get_mock_insights()
    for insight in insights:
        st.info(insight["content"])

# Smart Planner page
elif page == "Smart Planner":
    st.title("📅 Smart Planner")
    
    # Date selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now().date())
    with col2:
        end_date = st.date_input("End Date", datetime.now().date() + timedelta(days=6))
    
    # Generate schedule button
    if st.button("Generate Optimized Schedule"):
        with st.spinner("Generating your optimized schedule..."):
            # In a real app, this would call the API
            st.success("Schedule generated successfully!")
    
    # Weekly schedule view
    st.subheader("Weekly Schedule")
    schedule = get_mock_schedule()
    
    # Create a weekly calendar view
    days = [(start_date + timedelta(days=i)).isoformat() for i in range((end_date - start_date).days + 1)]
    hours = [f"{h}:00" for h in range(8, 22)]  # 8 AM to 10 PM
    
    # Create a heatmap-style calendar
    calendar_data = []
    for day in days:
        day_name = datetime.fromisoformat(day).strftime("%A")
        day_blocks = schedule["weekly_plan"].get(day, [])
        
        for hour in hours:
            # Check if there's a task at this hour
            task = next((block for block in day_blocks if block["start_time"] == hour), None)
            
            if task:
                calendar_data.append({
                    "Day": day_name,
                    "Hour": hour,
                    "Task": task["task_title"],
                    "Value": 1  # For coloring
                })
            else:
                calendar_data.append({
                    "Day": day_name,
                    "Hour": hour,
                    "Task": "Free",
                    "Value": 0  # For coloring
                })
    
    if calendar_data:
        df = pd.DataFrame(calendar_data)
        fig = px.density_heatmap(
            df, 
            x="Day", 
            y="Hour",
            z="Value",
            color_continuous_scale=["white", "blue"],
            labels={"Day": "Day of Week", "Hour": "Time"},
            height=500
        )
        
        # Add task labels
        for i, row in df[df["Value"] == 1].iterrows():
            fig.add_annotation(
                x=row["Day"],
                y=row["Hour"],
                text=row["Task"],
                showarrow=False,
                font=dict(color="black", size=10)
            )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Task list with drag-and-drop (simulated)
    st.subheader("Tasks")
    tasks = get_mock_tasks()
    
    for task in tasks:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{task['title']}**")
        with col2:
            st.write(f"Due: {datetime.fromisoformat(task['due_date']).strftime('%b %d')}")
        with col3:
            st.write(f"Priority: {task['priority']}/5")

# Analytics page
elif page == "Analytics":
    st.title("📈 Analytics")
    
    # Time allocation by course
    st.subheader("Time Allocation by Course")
    courses = get_mock_courses()
    
    # Mock data for time spent
    time_data = {
        "Course": [course["name"] for course in courses],
        "Hours": [12, 15, 8, 6]  # Mock hours spent
    }
    
    df = pd.DataFrame(time_data)
    fig = px.pie(df, values="Hours", names="Course", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
    
    # Task completion trend
    st.subheader("Task Completion Trend")
    
    # Mock data for task completion
    dates = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(14, 0, -1)]
    completion_data = {
        "Date": dates,
        "Completed": [3, 2, 4, 1, 5, 2, 3, 4, 2, 3, 5, 4, 3, 2],
        "Added": [4, 3, 3, 2, 4, 3, 5, 3, 2, 4, 5, 3, 4, 3]
    }
    
    df = pd.DataFrame(completion_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Completed"], mode="lines+markers", name="Completed"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Added"], mode="lines+markers", name="Added"))
    st.plotly_chart(fig, use_container_width=True)
    
    # Focus distribution
    st.subheader("Focus Distribution by Time of Day")
    
    # Mock data for focus distribution
    focus_data = {
        "Hour": [f"{h}:00" for h in range(8, 22)],
        "Focus Score": [3, 5, 7, 8, 9, 7, 6, 4, 5, 7, 8, 6, 4, 3]
    }
    
    df = pd.DataFrame(focus_data)
    fig = px.bar(df, x="Hour", y="Focus Score")
    st.plotly_chart(fig, use_container_width=True)

# Chat Assistant page
elif page == "Chat Assistant":
    st.title("🤖 Chat Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm EduFlow, your academic planning assistant. How can I help you today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about your schedule, study strategies, or time management..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate assistant response (in a real app, this would call the LangGraph agent)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if "schedule" in prompt.lower() or "plan" in prompt.lower():
                    response = "I've analyzed your schedule for this week. You have 3 major deadlines coming up. Would you like me to help you create a study plan to prepare for them?"
                elif "stress" in prompt.lower() or "overwhelm" in prompt.lower():
                    response = "I notice you've been working long hours. Consider taking more frequent breaks using the Pomodoro technique: 25 minutes of focused work followed by a 5-minute break."
                elif "priorit" in prompt.lower():
                    response = "Based on your upcoming deadlines and course weights, I recommend focusing on your MATH101 assignment first, followed by the CS101 project."
                else:
                    response = "I'm here to help with your academic planning. You can ask me about scheduling, task prioritization, study strategies, or stress management."
                
                st.write(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Settings page
elif page == "Settings":
    st.title("⚙️ Settings")
    
    # User preferences
    st.subheader("User Preferences")
    
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Preferred Study Time", ["Morning", "Afternoon", "Evening", "Night"])
    with col2:
        st.number_input("Break Frequency (minutes)", min_value=15, max_value=120, value=50, step=5)
    
    st.number_input("Maximum Daily Study Hours", min_value=1, max_value=12, value=6)
    
    # Calendar integration
    st.subheader("Calendar Integration")
    st.checkbox("Sync with Google Calendar")
    st.checkbox("Sync with Outlook Calendar")
    
    # LMS integration
    st.subheader("Learning Management System")
    st.selectbox("LMS Platform", ["Canvas", "Moodle", "Blackboard", "None"])
    
    # Notification settings
    st.subheader("Notifications")
    st.checkbox("Email Notifications", value=True)
    st.checkbox("Browser Notifications", value=True)
    st.checkbox("Daily Schedule Summary", value=True)
    
    # Save button
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("EduFlow - Academic Planning AI Assistant")
st.sidebar.caption("© 2023 EduFlow")