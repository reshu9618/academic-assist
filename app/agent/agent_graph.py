from typing import Dict, List, Any, TypedDict, Annotated
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import os
from datetime import datetime, timedelta

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
    llm = ChatOpenAI(model="gpt-4")
    
    # Extract relevant information from courses and student data
    courses = state["courses"]
    student_data = state["student_data"]
    
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
    
    # Update state with analyzed data
    analyzed_courses = courses  # In a real implementation, this would be enhanced with analysis
    
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
    llm = ChatOpenAI(model="gpt-4")
    
    # Extract relevant information
    courses = state["courses"]
    tasks = state["tasks"]
    student_data = state["student_data"]
    
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
    
    # Update state with prioritized tasks
    prioritized_tasks = tasks  # In a real implementation, this would be enhanced with prioritization
    
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
    llm = ChatOpenAI(model="gpt-4")
    
    # Extract relevant information
    tasks = state["tasks"]
    calendar_events = state["calendar_events"]
    student_data = state["student_data"]
    
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
    llm = ChatOpenAI(model="gpt-4")
    
    # Extract relevant information
    schedule = state["schedule"]
    tasks = state["tasks"]
    
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
    
    # In a real implementation, these would be scheduled via Celery
    reminders = []
    
    return {
        **state,
        "messages": state["messages"] + reminders,
        "current_node": "generate_reminders"
    }

# Node for generating insights
def generate_insights(state: AgentState) -> AgentState:
    """
    Generates insights about study patterns, productivity, and suggestions.
    """
    llm = ChatOpenAI(model="gpt-4")
    
    # Extract relevant information
    student_data = state["student_data"]
    tasks = state["tasks"]
    schedule = state["schedule"]
    
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
    
    # Add edges
    workflow.add_edge("analyze_student_data", "prioritize_tasks")
    workflow.add_edge("prioritize_tasks", "optimize_schedule")
    workflow.add_edge("optimize_schedule", "generate_reminders")
    workflow.add_edge("generate_reminders", "generate_insights")
    workflow.add_edge("generate_insights", END)
    
    # Set entry point
    workflow.set_entry_point("analyze_student_data")
    
    # Compile the graph
    return workflow.compile()

# Create the agent
agent_graph = create_agent_graph()

# Function to run the agent
def run_eduflow_agent(
    student_data: Dict,
    courses: List[Dict],
    tasks: List[Dict],
    calendar_events: List[Dict]
) -> Dict:
    """
    Run the EduFlow agent to generate a schedule and insights.
    
    Args:
        student_data: Student profile and preferences
        courses: List of courses with details
        tasks: List of tasks and assignments
        calendar_events: Existing calendar events
        
    Returns:
        Dict containing schedule, insights, and messages
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
        "schedule": result["schedule"],
        "insights": result["insights"],
        "messages": result["messages"]
    }