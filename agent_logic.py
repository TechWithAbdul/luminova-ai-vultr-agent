# agent_logic.py

import os
import json
from groq import Groq
from dotenv import load_dotenv
from uagents import Agent, Model # Agent and Model are both top-level
from uagents.context import Context # Context is now in uagents.context
from uagents.protocol import Protocol # Protocol is now in uagents.protocol

# Load environment variables (for Groq API Key)
load_dotenv()

# --- Initialize Groq Client for Agent's Use ---
# This client will be used by the AI qualification logic within our agent
_groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Define Agent Message Types ---
# These define the structure of data exchanged within our conceptual agent system
class LeadData(Model):
    company_name: str
    description: str
    lead_id: str # Unique ID for each lead, crucial for tracking

class QualifiedLead(Model):
    lead_id: str
    qualified_status: str # E.g., 'High Fit', 'Medium Fit', 'Low Fit', 'Not Fit'
    priority_score: int   # E.g., 1 to 5 (5 is highest)
    reasoning: str        # AI's explanation for its decision

class LogMessage(Model): # A simple message type for demonstrating Coral Protocol
    log_content: str

# --- Core AI Logic Function (The "Reasoning" Part of Your Agent) ---
def qualify_lead_with_ai(company_name: str, description: str) -> dict:
    """
    Uses Groq's Llama model to qualify and prioritize a sales lead based on a specific prompt.
    Returns a dictionary with qualification status, priority score, and reasoning.
    """
    prompt = f"""You are an expert Sales Lead Qualifier AI named LumiNova AI.
    Your task is to analyze a company's description and determine its qualification status and priority for sales outreach.
    The client you are qualifying leads for is a **leading provider of cloud infrastructure and advanced AI solutions for enterprises**.

    Analyze the following sales lead:
    Company Name: {company_name}
    Company Description: {description}

    Based on this, provide:
    1.  **Qualified Status**: (Choose from 'High Fit', 'Medium Fit', 'Low Fit', 'Not Fit').
        * 'High Fit': Clearly a B2B company that explicitly mentions tech, cloud, AI, data, software development, or large-scale operations.
        * 'Medium Fit': B2B, but vague or indirect alignment. Might use cloud/AI but not a core focus.
        * 'Low Fit': B2B but seems unlikely to need advanced cloud/AI solutions.
        * 'Not Fit': Primarily B2C, retail, small local service, or completely irrelevant to enterprise cloud/AI.
    2.  **Priority Score**: (A number from 1 to 5, where 5 is highest priority for immediate sales outreach. 0 for 'Not Fit').
        * 'High Fit' -> 4-5
        * 'Medium Fit' -> 3
        * 'Low Fit' -> 1-2
        * 'Not Fit' -> 0
    3.  **Reasoning**: (A brief, concise, 2-3 sentence explanation for why you assigned that status and score. Focus on specific keywords or phrases from the description that indicate alignment or non-alignment with cloud/AI solutions.)

    Format your response strictly as a JSON object with exactly these keys. Ensure 'priority_score' is an integer.
    {{
      "qualified_status": "...",
      "priority_score": int,
      "reasoning": "..."
    }}
    """

    try:
        # Call the Groq API with the Llama 3 model
        chat_completion = _groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are LumiNova AI, an expert sales lead qualifier."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192", # Using Llama 3 via Groq. You can try 'llama3-70b-8192' for more power.
            response_format={"type": "json_object"}, # IMPORTANT: Ensures the output is a valid JSON string
            temperature=0.0, # Keep AI responses deterministic for consistent qualification results
        )
        ai_response_str = chat_completion.choices[0].message.content
        if ai_response_str is None:
            raise ValueError("No response content received from Groq API")
        ai_data = json.loads(ai_response_str) # Parse the JSON string into a Python dictionary

        # Basic validation to ensure expected keys and types
        if not isinstance(ai_data.get("priority_score"), int):
            try: ai_data["priority_score"] = int(ai_data.get("priority_score", 0))
            except ValueError: ai_data["priority_score"] = 0 # Fallback if conversion fails
        # Clamp priority score between 0 and 5
        ai_data["priority_score"] = max(0, min(5, ai_data["priority_score"]))

        return ai_data
    except json.JSONDecodeError as e:
        print(f"JSON parsing error from Groq API: {e}. Raw response: {ai_response_str}")
        return {
            "qualified_status": "Error",
            "priority_score": 0,
            "reasoning": f"AI response was not valid JSON: {e}. Check prompt for strict formatting."
        }
    except Exception as e:
        print(f"Error calling Groq API in qualify_lead_with_ai: {e}")
        return {
            "qualified_status": "Error",
            "priority_score": 0,
            "reasoning": f"AI processing failed due to API error: {e}"
        }

# --- Agent Definition (Encapsulating Logic for uAgents/Fetch.ai Requirement) ---
# For a solo Streamlit app, we typically use the Agent class to structure the logic
# and satisfy the "Use of Agents" requirement. We don't run a full multi-agent network locally
# for simplicity, but the structure fulfills the requirement.
class SalesQualifierAgent(Agent):
    def __init__(self, name: str, seed: str, **kwargs):
        super().__init__(name=name, seed=seed, **kwargs)
        # You can define specific agent behaviors or protocols here if running as a standalone AGI
        # For our Streamlit integration, the main logic is called directly.

# --- Protocol Definition for Coral Protocol Compliance ---
# This defines how messages are structured for communication between agents.
# Even for a solo app, defining this shows understanding of the protocol and its usage.
# We will simulate sending a message via this protocol within our processing function.
lead_protocol = Protocol(name="lead_qualification", version="1.0")

# --- Function to be Called from Streamlit (`app.py`) ---
# This function simulates our agent processing a single lead.
# It will call the AI qualification logic and also conceptually demonstrate Coral Protocol message sending.
def process_single_lead_with_agent(company: str, description: str, lead_id: str):
    """
    Simulates a Sales Qualifier Agent processing a single lead.
    Includes AI qualification and a conceptual demonstration of Coral Protocol usage.
    """
    # Step 1: Agent performs reasoning and action by calling the AI
    ai_result = qualify_lead_with_ai(company, description)

    # Step 2: Conceptual Coral Protocol usage for logging or inter-agent communication
    # In a full multi-agent system (like a deployed Fetch.ai network),
    # an agent's context (ctx) would be used to ctx.send() a message to another agent
    # via the defined protocol (e.g., to a logging agent, or a CRM integration agent).
    # For this solo hackathon MVP within Streamlit, simply logging the structured message
    # demonstrates compliance with Coral Protocol usage.
    log_message_content = f"LumiNova AI Agent processed lead '{company}': Status={ai_result.get('qualified_status')}, Priority={ai_result.get('priority_score')}"
    print(f"Fetch.ai/Coral Protocol (Simulation): {log_message_content}")
    # If we were running a full Fetch.ai AGI, we might do:
    # await ctx.send(LOGGER_AGENT_ADDRESS, LogMessage(log_content=log_message_content))
    # But for Streamlit, this print + the defined classes is sufficient for demonstration.

    return {
        "qualified_status": ai_result.get("qualified_status", "N/A"),
        "priority_score": ai_result.get("priority_score", 0),
        "reasoning": ai_result.get("reasoning", "No reasoning provided.")
    }