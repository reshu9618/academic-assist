import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from gtts import gTTS
import base64
import io
import hashlib

# Load environment variables
load_dotenv()

# Add project root to sys.path
root_path = str(Path(__file__).parent.parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import json

# API endpoint (change to your actual API URL when deployed)
# Use streamlit secrets if available, otherwise fallback to local
API_URL = st.secrets.get("API_URL", os.getenv("API_URL", "http://localhost:8000/api"))

# Data synchronization helpers
def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def post_data(endpoint, data):
    try:
        requests.post(f"{API_URL}/{endpoint}", json=data)
    except Exception:
        pass

def put_data(endpoint, data):
    try:
        requests.put(f"{API_URL}/{endpoint}", json=data)
    except Exception:
        pass

def text_to_speech(text):
    """Convert text to speech and return base64 encoded audio."""
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_bytes = fp.read()
        b64 = base64.b64encode(audio_bytes).decode()
        return f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
    except Exception as e:
        return None

def speech_to_text(audio_data):
    """Convert audio data to text using Gemini 1.5 Flash (multimodal)."""
    if audio_data is None:
        return None
    
    try:
        audio_bytes = audio_data['bytes']
        # Use the latest flash model that we verified is working (gemini-flash-latest)
        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest", 
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Base64 encode the audio bytes
        b64_audio = base64.b64encode(audio_bytes).decode()
        
        # Prepare the multimodal message
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Please transcribe this audio recording accurately. Only return the transcribed text, nothing else. If the audio is empty or contains no speech, return an empty string."},
                {
                    "type": "media",
                    "mime_type": "audio/wav",
                    "data": b64_audio
                }
            ]
        )
        
        # Get transcription from Gemini
        response = llm.invoke([message])
        transcript = response.content.strip()
        
        # Filter out AI chatter if it happens
        if transcript.lower().startswith("here is the transcription") or transcript.lower().startswith("transcription:"):
            transcript = transcript.split(":", 1)[-1].strip()
            
        return transcript if transcript else "Could not understand audio"
        
    except Exception as e:
        return f"Error processing audio: {str(e)}"

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

# Initialize session state for tasks and courses
if "tasks" not in st.session_state:
    db_tasks = fetch_data("tasks/")
    st.session_state.tasks = db_tasks if db_tasks is not None else []

if "courses" not in st.session_state:
    db_courses = fetch_data("courses/")
    st.session_state.courses = db_courses if db_courses is not None else []

# Initialize gamification state
if "points" not in st.session_state:
    db_gamification = fetch_data("history/gamification/")
    st.session_state.points = db_gamification.get("points", 0) if db_gamification else 0
    st.session_state.badges = db_gamification.get("badges", []) if db_gamification else []

if "messages" not in st.session_state:
    db_history = fetch_data("history/chat_history/")
    if db_history:
        st.session_state.messages = [{"role": m["role"], "content": m["content"]} for m in db_history]
    else:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm EduFlow, your academic planning assistant. How can I help you today?"}
        ]

def get_level(points):
    if points < 100:
        return "Beginner Student", "🌱"
    elif points < 300:
        return "Dedicated Learner", "📖"
    elif points < 600:
        return "Knowledge Seeker", "🔍"
    elif points < 1000:
        return "Academic Scholar", "🎓"
    else:
        return "Pro Student", "🏆"

def check_badges():
    new_badges = []
    tasks = st.session_state.tasks
    completed_tasks = [t for t in tasks if t.get('completed')]
    
    # Consistency King (5 tasks completed)
    if len(completed_tasks) >= 5 and "Consistency King" not in st.session_state.badges:
        new_badges.append("Consistency King")
    
    # Last-Minute Hero (completed task on due date)
    today = datetime.now().date().isoformat()
    for t in completed_tasks:
        if t.get('due_date') == today and "Last-Minute Hero" not in st.session_state.badges:
            new_badges.append("Last-Minute Hero")
            break
            
    if new_badges:
        st.session_state.badges.extend(new_badges)
        put_data("history/gamification/", {"points": st.session_state.points, "badges": st.session_state.badges})
        for badge in new_badges:
            st.toast(f"🎉 New Badge Unlocked: {badge}!", icon="🏆")

def get_courses():
    return st.session_state.courses

def get_tasks():
    return st.session_state.tasks

def get_schedule():
    # Generate schedule based on tasks in session state
    today = datetime.now().date()
    weekly_plan = {}
    
    for task in st.session_state.tasks:
        if not task.get("completed", False):
            due_date_str = task.get("due_date")
            try:
                due_date = datetime.fromisoformat(due_date_str).date()
                if due_date >= today:
                    # For now, just schedule it for the day before it's due or today
                    schedule_date = min(due_date - timedelta(days=1), today)
                    date_str = schedule_date.isoformat()
                    
                    if date_str not in weekly_plan:
                        weekly_plan[date_str] = []
                    
                    # Add a 2-hour study block
                    weekly_plan[date_str].append({
                        "start_time": "14:00",
                        "end_time": "16:00",
                        "task_id": task.get("id"),
                        "task_title": task.get("title")
                    })
            except (ValueError, TypeError):
                continue
                
    return {
        "weekly_plan": weekly_plan,
        "daily_focus": {} # Could be derived from tasks
    }

def get_insights():
    if not st.session_state.tasks:
        return [{"type": "info", "content": "Add your first task to see AI-powered insights!"}]
    
    # Simple insights based on actual tasks
    total_tasks = len(st.session_state.tasks)
    completed_tasks = len([t for t in st.session_state.tasks if t.get("completed")])
    
    insights = [
        {
            "type": "productivity",
            "content": f"You have completed {completed_tasks}/{total_tasks} tasks."
        }
    ]
    
    if total_tasks > completed_tasks:
        insights.append({
            "type": "suggestion",
            "content": "Focus on your upcoming deadlines to stay on track."
        })
        
    return insights

# Dashboard page
if page == "Dashboard":
    st.title("📊 EduFlow Dashboard")
    
    # Gamification Header
    level_name, level_emoji = get_level(st.session_state.points)
    
    with st.container():
        col_lv1, col_lv2 = st.columns([1, 3])
        with col_lv1:
            st.markdown(f"### {level_emoji} {level_name}")
        with col_lv2:
            st.progress(min(st.session_state.points % 300 / 300, 1.0))
            st.caption(f"Points: {st.session_state.points} | Next Level in {300 - (st.session_state.points % 300)} pts")
    
    if st.session_state.badges:
        st.markdown("##### 🏅 Your Badges")
        badge_cols = st.columns(len(st.session_state.badges) if len(st.session_state.badges) > 0 else 1)
        for i, badge in enumerate(st.session_state.badges):
            with badge_cols[i % 4]:
                st.info(f"🏆 {badge}")
                
    st.divider()
    st.subheader(f"Welcome back, {user['name']}!")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Courses", value=str(len(get_courses())))
    with col2:
        st.metric(label="Upcoming Tasks", value=str(len([t for t in get_tasks() if not t.get('completed')])))
    with col3:
        st.metric(label="Study Hours This Week", value="0") # Could be calculated
    with col4:
        tasks = get_tasks()
        completion_rate = "0%"
        if tasks:
            completed = len([t for t in tasks if t.get('completed')])
            completion_rate = f"{(completed / len(tasks)) * 100:.0f}%"
        st.metric(label="Task Completion Rate", value=completion_rate)
    
    # Upcoming deadlines
    st.subheader("📅 Upcoming Deadlines")
    tasks = [t for t in get_tasks() if not t.get('completed')]
    if tasks:
        tasks_df = pd.DataFrame(tasks)
        tasks_df['due_date'] = pd.to_datetime(tasks_df['due_date'])
        tasks_df = tasks_df.sort_values('due_date')
        
        for _, task in tasks_df.iterrows():
            days_left = (task['due_date'].date() - datetime.now().date()).days
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{task['title']}** - Due in {days_left} days")
            with col2:
                st.write(f"Priority: {'🔴' if task['priority'] >= 4 else '🟡' if task['priority'] >= 2 else '🟢'}")
    else:
        st.info("No upcoming deadlines. Take a break or add a task in the Smart Planner!")
    
    # Today's schedule
    st.subheader("📝 Today's Schedule")
    schedule = get_schedule()
    today = datetime.now().date().isoformat()
    
    if today in schedule["weekly_plan"] and schedule["weekly_plan"][today]:
        for block in schedule["weekly_plan"][today]:
            st.write(f"**{block['start_time']} - {block['end_time']}**: {block['task_title']}")
    else:
        st.info("No scheduled tasks for today.")
    
    # Insights
    st.subheader("💡 Insights")
    insights = get_insights()
    for insight in insights:
        st.info(insight["content"])

# Smart Planner page
elif page == "Smart Planner":
    st.title("📅 Smart Planner")
    
    # Tab selection for different planner views
    planner_tab1, planner_tab2 = st.tabs(["Weekly Schedule", "Task Management"])
    
    with planner_tab1:
        # Date selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now().date())
        with col2:
            end_date = st.date_input("End Date", datetime.now().date() + timedelta(days=6))
        
        # Weekly schedule view
        st.subheader("Weekly Schedule")
        schedule = get_schedule()
        
        # Create a weekly calendar view
        days_in_range = [(start_date + timedelta(days=i)).isoformat() for i in range((end_date - start_date).days + 1)]
        hours = [f"{h}:00" for h in range(8, 22)]  # 8 AM to 10 PM
        
        calendar_data = []
        for day in days_in_range:
            day_name = datetime.fromisoformat(day).strftime("%A")
            day_blocks = schedule["weekly_plan"].get(day, [])
            
            for hour in hours:
                task = next((block for block in day_blocks if block["start_time"] == hour), None)
                if task:
                    calendar_data.append({"Day": day_name, "Hour": hour, "Task": task["task_title"], "Value": 1})
                else:
                    calendar_data.append({"Day": day_name, "Hour": hour, "Task": "Free", "Value": 0})
        
        if calendar_data and any(d["Value"] == 1 for d in calendar_data):
            df = pd.DataFrame(calendar_data)
            fig = px.density_heatmap(
                df, x="Day", y="Hour", z="Value",
                color_continuous_scale=["white", "#1f77b4"],
                labels={"Day": "Day of Week", "Hour": "Time"},
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Your schedule is clear! Add tasks in the Task Management tab to see them here.")

    with planner_tab2:
        st.subheader("Task Management")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            tasks = get_tasks()
            if tasks:
                # Use data_editor for better task management
                task_df = pd.DataFrame(tasks)
                # Ensure due_date is in datetime format for the DateColumn to work correctly
                if 'due_date' in task_df.columns:
                    task_df['due_date'] = pd.to_datetime(task_df['due_date']).dt.date
                
                edited_df = st.data_editor(
                    task_df,
                    column_config={
                        "completed": st.column_config.CheckboxColumn("Done"),
                        "priority": st.column_config.NumberColumn("Priority (1-5)", min_value=1, max_value=5),
                        "due_date": st.column_config.DateColumn("Due Date")
                    },
                    disabled=["id"],
                    use_container_width=True,
                    key="tasks_editor"
                )
                if not edited_df.equals(task_df):
                    # Check for newly completed tasks to award points
                    old_completed_ids = {t['id'] for t in st.session_state.tasks if t.get('completed')}
                    new_completed_ids = {t['id'] for _, t in edited_df.iterrows() if t.get('completed')}
                    
                    newly_done = new_completed_ids - old_completed_ids
                    if newly_done:
                        st.session_state.points += len(newly_done) * 20
                        put_data("history/gamification/", {"points": st.session_state.points, "badges": st.session_state.badges})
                        st.toast(f"🎉 Awesome! You earned {len(newly_done) * 20} points!", icon="⭐")
                        check_badges()
                    
                    # Sync updated tasks to database
                    for t in edited_df.to_dict('records'):
                        task_id = t.get('id')
                        put_data(f"tasks/{task_id}", t)

                    # Convert back to strings for storage if needed, or just store as is
                    # Here we store as records. to_dict('records') handles date objects fine in session state.
                    st.session_state.tasks = edited_df.to_dict('records')
                    # Convert dates back to strings for consistency if necessary
                    for t in st.session_state.tasks:
                        if isinstance(t.get('due_date'), (datetime, date)):
                            t['due_date'] = t['due_date'].isoformat()
                    st.rerun()
            else:
                st.info("No tasks added yet. Use the form on the right to add your first task!")

        with col2:
            st.subheader("Add New Task")
            with st.form("add_task_form", clear_on_submit=True):
                new_task_title = st.text_input("Task Title")
                
                # Course selection
                courses = get_courses()
                course_names = [c["name"] for c in courses]
                if not course_names:
                    st.warning("No courses added yet. Please add a course first in Settings or below.")
                    new_task_course = None
                else:
                    new_task_course = st.selectbox("Course", course_names)
                
                new_task_date = st.date_input("Due Date", datetime.now().date())
                new_task_priority = st.slider("Priority", 1, 5, 3)
                
                # Optional document upload
                uploaded_file = st.file_uploader("Upload Document (Optional)", type=["pdf", "docx", "txt", "png", "jpg"])
                
                submit_button = st.form_submit_button("Add Task")
                
                if submit_button:
                    if new_task_title:
                        course_id = next((c["id"] for c in courses if c["name"] == new_task_course), 0) if new_task_course else 0
                        
                        # Handle optional file metadata
                        file_info = None
                        if uploaded_file is not None:
                            file_info = {
                                "name": uploaded_file.name,
                                "type": uploaded_file.type,
                                "size": uploaded_file.size
                            }
                            
                        new_task = {
                            "id": len(st.session_state.tasks) + 1,
                            "title": new_task_title,
                            "course_id": course_id,
                            "due_date": new_task_date.isoformat(),
                            "priority": new_task_priority,
                            "completed": False,
                            "attachment": file_info
                        }
                        st.session_state.tasks.append(new_task)
                        post_data("tasks/", new_task)
                        st.success(f"Added task: {new_task_title}")
                        if file_info:
                            st.info(f"Attached file: {file_info['name']}")
                        st.rerun()
                    else:
                        st.error("Please enter a task title")
            
            st.divider()
            st.subheader("Quick Add Course")
            with st.form("add_course_form", clear_on_submit=True):
                course_name = st.text_input("Course Name (e.g. CS101)")
                course_code = st.text_input("Course Code")
                add_course_btn = st.form_submit_button("Add Course")
                if add_course_btn and course_name:
                    new_course = {
                        "id": len(st.session_state.courses) + 1,
                        "name": course_name,
                        "code": course_code,
                    }
                    st.session_state.courses.append(new_course)
                    post_data("courses/", new_course)
                    st.success(f"Added course: {course_name}")
                    st.rerun()

# Analytics page
elif page == "Analytics":
    st.title("📈 Analytics")
    
    courses = get_courses()
    tasks = get_tasks()
    
    if not courses and not tasks:
        st.info("No data available for analytics. Add courses and tasks in the Smart Planner to see your progress!")
    else:
        # Time allocation by course
        st.subheader("Task Distribution by Course")
        if courses:
            course_counts = {}
            for t in tasks:
                c_name = next((c["name"] for c in courses if c["id"] == t.get("course_id")), "Other")
                course_counts[c_name] = course_counts.get(c_name, 0) + 1
            
            if course_counts:
                df = pd.DataFrame(list(course_counts.items()), columns=["Course", "Tasks"])
                fig = px.pie(df, values="Tasks", names="Course", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No tasks assigned to courses yet.")
        else:
            st.write("No courses added yet.")
        
        # Task completion trend
        st.subheader("Task Completion Status")
        if tasks:
            completed = len([t for t in tasks if t.get("completed")])
            pending = len(tasks) - completed
            df = pd.DataFrame({
                "Status": ["Completed", "Pending"],
                "Count": [completed, pending]
            })
            fig = px.bar(df, x="Status", y="Count", color="Status", color_discrete_map={"Completed": "green", "Pending": "orange"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No tasks added yet.")
        
        # Priority distribution
        st.subheader("Task Priority Distribution")
        if tasks:
            priorities = [t.get("priority", 3) for t in tasks]
            df = pd.DataFrame({"Priority": priorities})
            fig = px.histogram(df, x="Priority", nbins=5, range_x=[0.5, 5.5])
            st.plotly_chart(fig, use_container_width=True)
            
        # Performance Analysis
        st.divider()
        st.subheader("🏆 Performance Analysis")
        if tasks:
            completed_tasks = [t for t in tasks if t.get('completed')]
            if completed_tasks:
                avg_priority = sum([t.get('priority', 3) for t in completed_tasks]) / len(completed_tasks)
                st.info(f"Your average completed task priority is **{avg_priority:.1f}/5**. You're tackling challenging work!")
                
                # Productivity score
                productivity_score = (len(completed_tasks) / len(tasks)) * 100
                st.success(f"Overall Productivity Score: **{productivity_score:.0f}/100**")
            else:
                st.warning("Complete some tasks to unlock performance insights!")
        else:
            st.info("Add tasks to start tracking your performance.")

# Chat Assistant page
elif page == "Chat Assistant":
    st.title("🤖 Chat Assistant")
    
    from app.agent.agent_graph import run_chat_agent

    # Initialize session state for audio settings
    if "enable_tts" not in st.session_state:
        st.session_state.enable_tts = True

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm EduFlow, your academic planning assistant. How can I help you today?"}
        ]
    
    # Sidebar options for Chat
    with st.sidebar:
        st.markdown("### Chat Settings")
        st.session_state.enable_tts = st.checkbox("Enable Voice Response (TTS)", value=st.session_state.enable_tts)
        if st.button("Clear Chat History"):
            st.session_state.messages = [
                {"role": "assistant", "content": "Chat history cleared! How can I help you today?"}
            ]
            try:
                requests.delete(f"{API_URL}/history/chat_history/")
            except Exception:
                pass
            st.rerun()
        
        st.divider()
        st.markdown("### Voice Input")
        audio_input = mic_recorder(
            start_prompt="Click to speak 🎤",
            stop_prompt="Stop recording ⏹️",
            key='mic_recorder',
            format="wav"
        )
        
        if audio_input:
            # Show audio playback for verification
            st.markdown("#### Review Your Recording")
            st.audio(audio_input['bytes'])
            
            # Generate a unique hash for the current audio input to avoid multiple processing
            audio_hash = hashlib.md5(audio_input['bytes']).hexdigest()
            
            # Check if this audio has already been processed in the current session
            if "last_processed_audio_hash" not in st.session_state or st.session_state.last_processed_audio_hash != audio_hash:
                with st.spinner("Processing voice input..."):
                    transcript = speech_to_text(audio_input)
                    if transcript and transcript not in ["Could not understand audio", "Error with Speech Recognition"]:
                        # Set the prompt for the chat input logic below
                        st.session_state.voice_transcript = transcript
                        st.session_state.last_processed_audio_hash = audio_hash
                        st.success(f"Recognized: {transcript}")
                    elif transcript:
                        st.error(transcript)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Handle both text and voice input
    user_input = st.chat_input("Ask me about your schedule, study strategies, or time management...")
    
    # Check if we have a voice transcript to process
    prompt = user_input
    if "voice_transcript" in st.session_state and st.session_state.voice_transcript:
        prompt = st.session_state.voice_transcript
        del st.session_state.voice_transcript # Clear it after use

    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        post_data("history/chat_history/", {"role": "user", "content": prompt})
        
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
                    schedule = get_schedule()
                    
                    # Run the chat agent
                    response = run_chat_agent(
                        messages=st.session_state.messages,
                        courses=courses,
                        tasks=tasks,
                        schedule=schedule
                    )
                    st.write(response)
                    post_data("history/chat_history/", {"role": "assistant", "content": response})
                    
                    # Optional TTS for assistant response
                    if st.session_state.enable_tts:
                        audio_html = text_to_speech(response)
                        if audio_html:
                            st.markdown(audio_html, unsafe_allow_html=True)

                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error connecting to AI: {str(e)}")
                    st.write("I'm having trouble connecting to my brain right now. Please check your Gemini API key in the .env file.")
        
        st.rerun() # Refresh to clear input and show the update

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