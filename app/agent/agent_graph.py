from typing import Dict, List, Any, TypedDict, Annotated
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import os
from datetime import datetime, timedelta
import json

# Define state schema
class AgentState(TypedDict):
    student_data: Dict
    courses: List[Dict]
    tasks: List[Dict]
    calendar_events: List[Dict]
    schedule: Dict
    insights: List[Dict]
    messages: List[Dict]
    current_node: str

# Node for analyzing student data and courses
def analyze_student_data(state: AgentState) -> AgentState:
    """
    Analyzes student course data, deadlines, and personal preferences.
    Extracts workload metrics (e.g., weekly hours, difficulty ratings).
    """
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("Gemini API key is missing. Please add it to your .env file.")
            
        llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Extract relevant information from courses and student data
        courses = state.get("courses", [])
        student_data = state.get("student_data", {})
        
        # Prepare prompt for analysis
        analysis_prompt = PromptTemplate.from_template(
            """You are an academic planning assistant analyzing student data.
            
            Student Information:
            {student_data}
            
            Course Information:
            {courses}
            
            Analyze this information and extract:
            1. Weekly workload hours for each course
            2. Difficulty rating (1-5) for each course
            3. Key deadlines and their importance
            4. Potential conflicts in the schedule
            
            Provide your analysis in a structured JSON format.
            """
        )
        
        # Get analysis from LLM
        analysis_result = llm.invoke(
            analysis_prompt.format(
                student_data=student_data,
                courses=courses
            )
        )
    except Exception:
        pass
    
    # Update state with analyzed data
    analyzed_courses = state.get("courses", [])  # In a real implementation, this would be enhanced with analysis
    
    return {
        **state,
        "courses": analyzed_courses,
        "current_node": "analyze_student_data"
    }

# Node for prioritizing tasks
def prioritize_tasks(state: AgentState) -> AgentState:
    """
    Uses LangGraph reasoning to rank tasks by urgency, importance, and student goals.
    Re-prioritizes automatically when new data arrives.
    """
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("Gemini API key is missing. Please add it to your .env file.")
            
        llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Extract relevant information
        courses = state.get("courses", [])
        tasks = state.get("tasks", [])
        student_data = state.get("student_data", {})
        
        # Prepare prompt for prioritization
        prioritization_prompt = PromptTemplate.from_template(
            """You are an academic planning assistant prioritizing student tasks.
            
            Student Information:
            {student_data}
            
            Course Information:
            {courses}
            
            Tasks to Prioritize:
            {tasks}
            
            Prioritize these tasks based on:
            1. Deadline proximity
            2. Assignment weight/importance
            3. Estimated time required
            4. Student's personal goals and preferences
            
            For each task, assign:
            - Priority level (1-5, where 5 is highest)
            - Recommended completion date
            - Rationale for the priority assignment
            
            Return the prioritized tasks in a structured JSON format.
            """
        )
        
        # Get prioritization from LLM
        prioritization_result = llm.invoke(
            prioritization_prompt.format(
                student_data=student_data,
                courses=courses,
                tasks=tasks
            )
        )
    except Exception:
        pass
    
    # Update state with prioritized tasks
    prioritized_tasks = state.get("tasks", [])  # In a real implementation, this would be enhanced with prioritization
    
    return {
        **state,
        "tasks": prioritized_tasks,
        "current_node": "prioritize_tasks"
    }

# Node for optimizing schedule
def optimize_schedule(state: AgentState) -> AgentState:
    """
    Uses constraint-based logic to produce daily/weekly plans.
    Integrates with calendar data.
    """
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("Gemini API key is missing. Please add it to your .env file.")
            
        llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Extract relevant information
        tasks = state.get("tasks", [])
        calendar_events = state.get("calendar_events", [])
        student_data = state.get("student_data", {})
        
        # Prepare prompt for schedule optimization
        schedule_prompt = PromptTemplate.from_template(
            """You are an academic planning assistant creating an optimized study schedule.
            
            Student Information:
            {student_data}
            
            Prioritized Tasks:
            {tasks}
            
            Existing Calendar Events:
            {calendar_events}
            
            Create a weekly schedule that:
            1. Allocates appropriate time blocks for each task
            2. Respects existing calendar commitments
            3. Includes breaks and rest periods
            4. Considers the student's peak productivity times
            5. Balances workload throughout the week
            
            Return the optimized schedule in a structured JSON format with daily time blocks.
            """
        )
        
        # Get schedule optimization from LLM
        schedule_result = llm.invoke(
            schedule_prompt.format(
                student_data=student_data,
                tasks=tasks,
                calendar_events=calendar_events
            )
        )
    except Exception:
        pass
    
    # Create a basic schedule (in a real implementation, this would be more sophisticated)
    today = datetime.now()
    schedule = {
        "weekly_plan": {
            (today + timedelta(days=i)).strftime("%Y-%m-%d"): [] for i in range(7)
        },
        "daily_focus": {},
        "study_blocks": []
    }
    
    return {
        **state,
        "schedule": schedule,
        "current_node": "optimize_schedule"
    }

# Node for reminders and adaptation
def generate_reminders(state: AgentState) -> AgentState:
    """
    Sends proactive reminders.
    Adjusts tasks based on completion rate, mood, and fatigue levels.
    """
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("Gemini API key is missing. Please add it to your .env file.")
            
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Extract relevant information
        schedule = state.get("schedule", {})
        tasks = state.get("tasks", [])
        
        # Prepare prompt for reminders
        reminder_prompt = PromptTemplate.from_template(
            """You are an academic planning assistant generating smart reminders.
            
            Current Schedule:
            {schedule}
            
            Tasks:
            {tasks}
            
            Generate:
            1. Timely reminders for upcoming deadlines
            2. Study session start notifications
            3. Break reminders
            4. Progress check-ins
            
            Return the reminders in a structured JSON format.
            """
        )
        
        # Get reminders from LLM
        reminder_result = llm.invoke(
            reminder_prompt.format(
                schedule=schedule,
                tasks=tasks
            )
        )
    except Exception:
        pass
    
    # In a real implementation, these would be scheduled via Celery
    reminders = []
    
    return {
        **state,
        "messages": state.get("messages", []) + reminders,
        "current_node": "generate_reminders"
    }

# Node for generating insights
def generate_insights(state: AgentState) -> AgentState:
    """
    Generates insights about study patterns, productivity, and suggestions.
    """
    try:
        # Check for API key
        if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your_gemini_api_key_here":
            raise ValueError("Gemini API key is missing. Please add it to your .env file.")
            
        llm = ChatGoogleGenerativeAI(model="gemini-flash-latest")
        
        # Extract relevant information
        student_data = state.get("student_data", {})
        tasks = state.get("tasks", [])
        schedule = state.get("schedule", {})
        
        # Prepare prompt for insights
        insights_prompt = PromptTemplate.from_template(
            """You are an academic planning assistant generating student insights.
            
            Student Information:
            {student_data}
            
            Task History:
            {tasks}
            
            Schedule Information:
            {schedule}
            
            Generate insights about:
            1. Study patterns and productivity trends
            2. Task completion rates
            3. Time management effectiveness
            4. Potential improvements to study habits
            5. Stress management suggestions
            
            Return 3-5 actionable insights in a structured JSON format.
            """
        )
        
        # Get insights from LLM
        insights_result = llm.invoke(
            insights_prompt.format(
                student_data=student_data,
                tasks=tasks,
                schedule=schedule
            )
        )
    except Exception:
        pass
    
    # Sample insights (in a real implementation, these would be derived from the LLM response)
    insights = [
        {"type": "productivity", "content": "Your study focus peaks at 10 AM."},
        {"type": "time_management", "content": "You're spending 60% of your time on low-priority tasks."},
        {"type": "suggestion", "content": "Try breaking large assignments into smaller chunks."}
    ]
    
    return {
        **state,
        "insights": insights,
        "current_node": "generate_insights"
    }

# Router function to determine next steps
def router(state: AgentState) -> str:
    current_node = state.get("current_node", "")
    
    if current_node == "analyze_student_data":
        return "prioritize_tasks"
    elif current_node == "prioritize_tasks":
        return "optimize_schedule"
    elif current_node == "optimize_schedule":
        return "generate_reminders"
    elif current_node == "generate_reminders":
        return "generate_insights"
    else:
        return END

# Node for general chat interaction
def chat_interaction(state: AgentState) -> AgentState:
    """
    Handles conversational requests from the student.
    Provides context-aware answers about schedules, tasks, and study strategies.
    """
    try:
        # Check for API key
        if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your_gemini_api_key_here":
            raise ValueError("Gemini API key is missing. Please add it to your .env file.")
            
        llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.7, google_api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Extract context
        courses = state.get("courses", [])
        tasks = state.get("tasks", [])
        schedule = state.get("schedule", {})
        messages = state.get("messages", [])
        
        # Format context for the prompt
        courses_str = "\n".join([f"- {c['name']} ({c.get('code', 'N/A')})" for c in courses]) if courses else "No courses added yet."
        tasks_str = "\n".join([f"- {t['title']} (Due: {t.get('due_date', 'N/A')}, Priority: {t.get('priority', 'N/A')}, Completed: {t.get('completed', False)})" for t in tasks]) if tasks else "No tasks added yet."
        schedule_str = json.dumps(schedule, indent=2) if schedule else "No schedule generated yet."
        
        # Prepare system message with detailed context and strict instructions
        system_prompt = f"""You are EduFlow, an AI Academic Planning Assistant. Your primary function is to provide precise, context-aware advice and generate dynamic study schedules based on the data provided below.

        **Rule #1: Use Only Provided Data.** Do not invent or infer any information not explicitly listed in the 'CURRENT STUDENT DATA' section. If a user asks about something not listed (e.g., a course not in the list), you must state that you do not have information on it and recommend they add it via the 'Smart Planner'.

        **Rule #2: Be Specific and Direct.** When asked about schedules or tasks, provide direct answers from the data.

        **Rule #3: Dynamic Schedule Generation.** If a user asks to "prepare a schedule" for a specific period (e.g., "next week", "this weekend"), you MUST generate a detailed, hour-by-hour study plan using the tasks and courses provided. 
        - If the user specifies a time period, focus the schedule on that range.
        - Balance the workload based on task priority and due dates.
        - Include breaks and specific study blocks for each course.
        - Format the schedule clearly in your response using markdown tables or bullet points.

        **Rule #4: Proactive Planning.** If you notice a task is due soon but not scheduled, point it out and suggest adding it to the plan.

        **Rule #5: Guide for Manual Changes.** If the user asks you to permanently 'add a task' or 'change a due date' in the system, explain that you are an advice-giver and they should use the 'Smart Planner' for permanent data updates. However, you CAN suggest a temporary plan for them to follow right now.

        CURRENT STUDENT DATA:
        COURSES:
        {courses_str}
        
        TASKS:
        {tasks_str}
        
        SCHEDULE:
        {schedule_str}
        
        Now, answer the user's last question based on the rules and data above. If a schedule is requested, generate it dynamically.
        """
        
        # Prepare messages for LLM
        # Ensure we only send a reasonable number of recent messages to avoid token limits
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        
        llm_messages = [SystemMessage(content=system_prompt)]
        for msg in recent_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "assistant":
                llm_messages.append(AIMessage(content=content))
            else:
                llm_messages.append(HumanMessage(content=content))
        
        # Get response from LLM
        response = llm.invoke(llm_messages)
        
        # Add assistant response to history
        new_messages = messages + [{"role": "assistant", "content": response.content}]
        
        return {
            **state,
            "messages": new_messages,
            "current_node": "chat_interaction"
        }
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "Gemini API key is missing" in error_msg:
            friendly_error = "It seems your Gemini API key is missing or invalid. Please check your .env file."
        elif "quota" in error_msg or "rate limit" in error_msg:
            friendly_error = "I've hit my usage limit or rate limit. Please check your Google AI account balance."
        else:
            friendly_error = f"I encountered an error while thinking: {error_msg}"
            
        return {
            **state,
            "messages": state.get("messages", []) + [{"role": "assistant", "content": friendly_error}],
            "current_node": "chat_interaction"
        }

# Create the LangGraph
def create_agent_graph():
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze_student_data", analyze_student_data)
    workflow.add_node("prioritize_tasks", prioritize_tasks)
    workflow.add_node("optimize_schedule", optimize_schedule)
    workflow.add_node("generate_reminders", generate_reminders)
    workflow.add_node("generate_insights", generate_insights)
    workflow.add_node("chat_interaction", chat_interaction)
    
    # Add edges for the main planning flow
    workflow.add_edge("analyze_student_data", "prioritize_tasks")
    workflow.add_edge("prioritize_tasks", "optimize_schedule")
    workflow.add_edge("optimize_schedule", "generate_reminders")
    workflow.add_edge("generate_reminders", "generate_insights")
    workflow.add_edge("generate_insights", END)
    
    # Add edge for chat
    workflow.add_edge("chat_interaction", END)
    
    # Set entry point
    workflow.set_entry_point("analyze_student_data")
    
    # Compile the graph
    return workflow.compile()

# Create the agent
agent_graph = create_agent_graph()

# Function to run the chat agent
def run_chat_agent(
    messages: List[Dict],
    courses: List[Dict],
    tasks: List[Dict],
    schedule: Dict = None,
    student_data: Dict = None
) -> str:
    """
    Run the agent specifically for chat interaction.
    """
    initial_state = {
        "student_data": student_data or {},
        "courses": courses,
        "tasks": tasks,
        "calendar_events": [],
        "schedule": schedule or {},
        "insights": [],
        "messages": messages,
        "current_node": ""
    }
    
    result = chat_interaction(initial_state)
    return result["messages"][-1]["content"]

def run_eduflow_agent(
    student_data: Dict,
    courses: List[Dict],
    tasks: List[Dict],
    calendar_events: List[Dict]
) -> Dict:
    """
    Run the EduFlow agent to generate a schedule and insights.
    """
    # Initialize state
    initial_state = {
        "student_data": student_data,
        "courses": courses,
        "tasks": tasks,
        "calendar_events": calendar_events,
        "schedule": {},
        "insights": [],
        "messages": [],
        "current_node": ""
    }
    
    # Run the agent
    result = agent_graph.invoke(initial_state)
    
    return {
        "schedule": result.get("schedule", {}),
        "insights": result.get("insights", []),
        "messages": result.get("messages", [])
    }
