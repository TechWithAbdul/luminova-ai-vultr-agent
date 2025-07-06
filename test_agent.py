# test_agent.py
from agent_logic import qualify_lead_with_ai, process_single_lead_with_agent
from dotenv import load_dotenv
import os

# Load environment variables for testing (e.g., GROQ_API_KEY)
load_dotenv()

if __name__ == "__main__":
    print("--- Testing AI Lead Qualification ---")
    sample_leads = [
        {"company": "Quantum Innovations Inc.", "desc": "A startup developing cutting-edge AI software for enterprise data analysis, leveraging cloud infrastructure."},
        {"company": "GreenGrocer Co.", "desc": "Local organic food delivery service for residential customers in urban areas."},
        {"company": "CyberSecure Solutions", "desc": "Provides advanced cybersecurity consulting and cloud migration services for large corporations and government agencies."},
        {"company": "Pawsitive Pet Care", "desc": "Offers personalized dog walking and pet sitting services primarily for individual pet owners."}
    ]

    for i, lead in enumerate(sample_leads):
        print(f"\nProcessing Lead {i+1}: {lead['company']}")
        # Directly call the AI logic for a quick test
        result = qualify_lead_with_ai(lead['company'], lead['desc'])
        print(f"  Qualified Status: {result.get('qualified_status')}")
        print(f"  Priority Score:   {result.get('priority_score')}")
        print(f"  Reasoning:        {result.get('reasoning')}")
        print("-" * 30)

    print("\n--- Testing Agent Processing & Coral Protocol Simulation ---")
    # This calls the function that Streamlit will use, demonstrating Coral integration
    process_single_lead_with_agent("Sample Manufacturing Co.", "Traditional manufacturing company exploring automation and supply chain optimization.", "test_id_999")