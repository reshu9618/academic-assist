import streamlit as st
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

# Mock data for demonstration
courses = [
    {"id": 1, "name": "Introduction to Computer Science", "code": "CS101", "credits": 3, "difficulty": 3},
    {"id": 2, "name": "Calculus I", "code": "MATH201", "credits": 4, "difficulty": 4},
    {"id": 3, "name": "Introduction to Psychology", "code": "PSYCH101", "credits": 3, "difficulty": 2},
    {"id": 4, "name": "English Composition", "code": "ENG101", "credits": 3, "difficulty": 2}
]

tasks = [
    {"id": 1, "title": "CS101 Programming Assignment", "course_id": 1, "due_date": "2023-11-15", "priority": "High", "completed": False},
    {"id": 2, "title": "MATH201 Problem Set 3", "course_id": 2, "due_date": "2023-11-10", "priority": "Medium", "completed": False},
    {"id": 3, "title": "PSYCH101 Research Paper", "course_id": 3, "due_date": "2023-11-20", "priority": "High", "completed": False},
    {"id": 4, "title": "ENG101 Essay Draft", "course_id": 4, "due_date": "2023-11-12", "priority": "Low", "completed": True}
]

# Generate mock schedule data
def generate_schedule():
    today = datetime.date.today()
    schedule = []
    
    for i in range(7):  # Next 7 days
        day = today + datetime.timedelta(days=i)
        day_name = day.strftime("%A")
        
        # Generate 2-4 study blocks per day
        num_blocks = random.randint(2, 4)
        for j in range(num_blocks):
            start_hour = random.randint(9, 19)
            duration = random.randint(1, 3)
            course_id = random.choice([1, 2, 3, 4])
            course_name = next(c["name"] for c in courses if c["id"] == course_id)
            
            schedule.append({
                "day": day_name,
                "date": day.strftime("%Y-%m-%d"),
                "start_time": f"{start_hour}:00",
                "end_time": f"{start_hour + duration}:00",
                "course": course_name,
                "activity": random.choice(["Reading", "Practice Problems", "Review Notes", "Assignment Work"])
            })
    
    return schedule

schedule = generate_schedule()

# Generate mock insights
insights = [
    {"title": "Study Efficiency", "description": "Your most productive study time is between 2PM-5PM", "score": 85},
    {"title": "Assignment Completion", "description": "You complete 92% of assignments on time", "score": 92},
    {"title": "Course Balance", "description": "CS101 needs more attention based on upcoming deadlines", "score": 65},
    {"title": "Learning Progress", "description": "Consistent improvement in MATH201 performance", "score": 78}
]

# Dashboard Page
if page == "Dashboard":
    st.title("📊 Student Dashboard")
    
    # Welcome message
    st.markdown("### Welcome to EduFlow!")
    st.write("Your AI-powered academic planning assistant")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Courses", value="4")
    with col2:
        st.metric(label="Upcoming Tasks", value="3")
    with col3:
        st.metric(label="Study Hours This Week", value="24")
    with col4:
        st.metric(label="Average Course Progress", value="68%")
    
    # Upcoming deadlines
    st.subheader("📅 Upcoming Deadlines")
    upcoming_tasks = [task for task in tasks if not task["completed"]]
    upcoming_df = pd.DataFrame(upcoming_tasks)
    upcoming_df = upcoming_df[["title", "due_date", "priority"]]
    st.dataframe(upcoming_df, use_container_width=True)
    
    # Today's schedule
    st.subheader("📝 Today's Schedule")
    today = datetime.date.today().strftime("%Y-%m-%d")
    today_schedule = [s for s in schedule if s["date"] == today]
    if today_schedule:
        today_df = pd.DataFrame(today_schedule)
        today_df = today_df[["start_time", "end_time", "course", "activity"]]
        st.dataframe(today_df, use_container_width=True)
    else:
        st.info("No study blocks scheduled for today.")
    
    # Key insights
    st.subheader("💡 Key Insights")
    insight_cols = st.columns(2)
    for i, insight in enumerate(insights[:2]):
        with insight_cols[i % 2]:
            st.info(f"**{insight['title']}**: {insight['description']}")

# Smart Planner Page
elif page == "Smart Planner":
    st.title("🧠 Smart Planner")
    
    # Weekly schedule view
    st.subheader("Weekly Schedule")
    
    # Group schedule by day
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    schedule_df = pd.DataFrame(schedule)
    
    # Create tabs for each day
    tabs = st.tabs(days)
    
    for i, day in enumerate(days):
        with tabs[i]:
            day_schedule = schedule_df[schedule_df["day"] == day]
            if not day_schedule.empty:
                st.dataframe(day_schedule[["start_time", "end_time", "course", "activity"]], use_container_width=True)
            else:
                st.info(f"No study blocks scheduled for {day}.")
    
    # Task management
    st.subheader("Task Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        task_df = pd.DataFrame(tasks)
        task_df["due_date"] = pd.to_datetime(task_df["due_date"])
        task_df = task_df.sort_values("due_date")
        
        # Format for display
        display_df = task_df[["title", "due_date", "priority", "completed"]]
        display_df["due_date"] = display_df["due_date"].dt.strftime("%Y-%m-%d")
        st.dataframe(display_df, use_container_width=True)
    
    with col2:
        st.subheader("Add New Task")
        task_title = st.text_input("Task Title")
        course = st.selectbox("Course", [c["name"] for c in courses])
        due_date = st.date_input("Due Date")
        priority = st.select_slider("Priority", options=["Low", "Medium", "High"])
        
        if st.button("Add Task"):
            st.success(f"Task '{task_title}' added successfully!")

# Analytics Page
elif page == "Analytics":
    st.title("📈 Analytics")
    
    # Course performance
    st.subheader("Course Performance")
    
    # Mock performance data
    performance_data = {
        "Course": [c["name"] for c in courses],
        "Current Grade": [random.randint(70, 95) for _ in courses],
        "Completion": [random.randint(50, 100) for _ in courses]
    }
    
    perf_df = pd.DataFrame(performance_data)
    st.dataframe(perf_df, use_container_width=True)
    
    # Study time distribution
    st.subheader("Study Time Distribution")
    
    study_data = {
        "Course": [c["name"] for c in courses],
        "Hours": [random.randint(5, 20) for _ in courses]
    }
    
    st.bar_chart(pd.DataFrame(study_data).set_index("Course"))
    
    # Productivity insights
    st.subheader("Productivity Insights")
    
    for insight in insights:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"**{insight['title']}**: {insight['description']}")
        with col2:
            st.progress(insight["score"] / 100)

# Chat Assistant Page
elif page == "Chat Assistant":
    st.title("💬 Chat Assistant")
    
    st.write("Ask EduFlow about your academic schedule, get help with planning, or request insights.")
    
    # Simple chat interface
    user_input = st.text_input("Type your message here...")
    
    if st.button("Send"):
        if user_input:
            st.write("You: " + user_input)
            
            # Mock responses based on keywords
            if "schedule" in user_input.lower():
                st.write("EduFlow: Here's your schedule for today. You have 3 study blocks planned, focusing on CS101 and MATH201.")
            elif "deadline" in user_input.lower() or "due" in user_input.lower():
                st.write("EduFlow: Your next deadline is the MATH201 Problem Set 3, due on November 10th. Would you like me to help you plan study time for this?")
            elif "help" in user_input.lower() or "advice" in user_input.lower():
                st.write("EduFlow: Based on your current progress, I recommend focusing more time on CS101 this week. You have an important assignment due soon, and your current understanding of the material could use reinforcement.")
            else:
                st.write("EduFlow: I'm here to help with your academic planning. You can ask me about your schedule, deadlines, or for study advice.")

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