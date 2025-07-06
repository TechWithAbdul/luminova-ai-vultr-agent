# app.py

import streamlit as st
from dotenv import load_dotenv # To load API keys from .env
import os
from groq import Groq # Groq client for Llama models
import pandas as pd # For DataFrame manipulation
import json # For handling JSON from AI responses and Firebase config
import uuid # To generate a unique user ID for local testing
from agent_logic import process_single_lead_with_agent # Import our agent function

# --- Firebase Admin SDK Imports ---
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. Load Environment Variables ---
# This must be at the very top to ensure API keys are loaded
load_dotenv()

# --- 2. Initialize Firebase Admin SDK for User Profile / Knowledge Graph ---
# In hackathon deployment, these will be set as environment variables.
# Locally, firebase_config_json will likely be None unless you set up your own local Firebase project
# for testing with a service account key. For hackathon, rely on platform env vars.
firebase_config_json_str = os.getenv('__firebase_config')
# For local testing, you might need to set a dummy app_id.
# In deployment, the platform typically provides this.
app_id = os.getenv('__app_id', 'luminova_test_app') # Use a default for local testing

if firebase_config_json_str:
    try:
        # Parse the JSON string from the environment variable
        # This is a dictionary, not a file path for credentials
        cred_dict = json.loads(firebase_config_json_str)
        cred = credentials.Certificate(cred_dict)
        if not firebase_admin._apps: # Initialize Firebase app only once to avoid errors
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        st.success("Firebase connected (using contest env vars)!")
    except json.JSONDecodeError as e:
        st.error(f"Error parsing Firebase config JSON: {e}. Please check '__firebase_config' variable in deployment.")
        db = None
    except Exception as e:
        st.error(f"Firebase initialization error: {e}. Is the config JSON correctly formed?")
        db = None
else:
    st.warning("Firebase not initialized. Make sure '__firebase_config' is set in the deployment environment.")
    db = None # Firestore client will be None if not initialized

# Function to get or create a user profile in Firestore
# This fulfills the "reusable user profile" / "knowledge graph" aspect, crucial for scoring.
def get_user_profile(user_id_param):
    if db:
        doc_ref = db.collection('users').document(user_id_param)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            new_profile = {"past_interactions": [], "preferences": {}}
            doc_ref.set(new_profile) # Create new document if it doesn't exist
            return new_profile
    return {"past_interactions": [], "preferences": {}} # Default empty profile if no DB connection

# Function to save user profile to Firestore
def save_user_profile(user_id_param, profile_data):
    if db:
        db.collection('users').document(user_id_param).set(profile_data)
    else:
        st.error("Cannot save profile: Firebase not connected. User data will not persist.")


# --- 3. Initialize Groq Client ---
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ_API_KEY not found. Please set it in your .env file or environment variables.")
    st.stop() # Stop the app immediately if API key is missing

# Initialize the Groq client instance
groq_client = Groq(api_key=groq_api_key)

# --- 4. Streamlit UI Layout ---
st.set_page_config(layout="wide", page_title="LumiNova AI: Enterprise Insight Agent")
st.title("LumiNova AI: Enterprise Insight Agent 💡")
st.subheader("AI-Powered Sales Lead Qualification & Prioritization")

# Generate a unique user ID for local testing/session.
# In a real contest environment, this might come from the platform's authentication.
# This is a temporary way to simulate user authentication for profile saving.
if 'user_id' not in st.session_state:
    # Use contest-provided token if available, otherwise generate a unique UUID
    st.session_state.user_id = os.getenv('__initial_auth_token', str(uuid.uuid4()))
current_user_id = st.session_state.user_id

# Display current user profile in sidebar (for debugging/demonstration of knowledge graph)
user_profile = get_user_profile(current_user_id)
with st.sidebar:
    st.header("User Profile (Knowledge Graph)")
    st.write(f"Active User: `{current_user_id}`")
    st.json(user_profile) # Display the raw profile JSON for debugging
    st.info("This profile in Firestore allows for reusable user data and knowledge!")

# --- 5. File Uploader Section ---
st.write("---")
uploaded_file = st.file_uploader(
    "Upload your sales leads (CSV or Excel) containing 'Company Name' and 'Description' columns.",
    type=["csv", "xlsx"]
)

df_original = pd.DataFrame() # Initialize an empty DataFrame to hold uploaded data

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_original = pd.read_csv(uploaded_file)
        else: # Must be .xlsx
            df_original = pd.read_excel(uploaded_file)

        st.write("### Original Leads (First 5 Rows):")
        st.dataframe(df_original.head())

        # Check for essential columns before processing
        required_columns = ['Company Name', 'Description']
        if not all(col in df_original.columns for col in required_columns):
            st.error(f"Error: Missing required columns. Please ensure your file has '{required_columns[0]}' and '{required_columns[1]}' columns.")
            df_original = pd.DataFrame() # Clear the DataFrame if columns are missing
        else:
            st.success("File uploaded successfully! Click 'Analyze Leads with AI' to process.")

    except Exception as e:
        st.error(f"Error reading file: {e}. Please ensure it's a valid CSV/Excel format and not corrupted.")
        df_original = pd.DataFrame() # Clear DataFrame on error

# Placeholder for the processing button - will be connected to agent logic soon
if not df_original.empty:
    st.write("---")
    if st.button("Analyze Leads with AI"):
        # This is where the core agent processing logic will be called in the next step
        st.info("Initiating AI-powered lead analysis... Please wait.")
        # app.py (inside the 'if st.button("Analyze Leads with AI"):')
        st.info("Initiating AI-powered lead analysis... This might take a moment depending on the number of leads.")

        processed_leads_data = []

        # Create a progress bar to show activity during processing
        progress_bar_text = st.empty() # Placeholder for text update
        progress_bar = st.progress(0)

        total_leads = len(df_original)

        for index, row in df_original.iterrows():
            company = row['Company Name']
            description = row['Description']
            lead_id = f"lead_{index}" # Simple unique ID for each row

            progress_bar_text.text(f"Processing lead {index + 1} of {total_leads}: {company}...")

            # Call our agent's processing function from agent_logic.py
            result = process_single_lead_with_agent(company, description, lead_id)

            # Append original data plus AI results to our list
            processed_leads_data.append({
                "Original Company Name": company, # Renamed for clarity in output
                "Original Description": description, # Renamed for clarity in output
                "Qualified Status": result["qualified_status"],
                "Priority Score": result["priority_score"],
                "Reasoning": result["reasoning"]
            })

            # Update user profile in Firebase with each interaction (for knowledge graph / reusability)
            user_profile["past_interactions"].append({
                "lead_id": lead_id,
                "company": company,
                "description": description,
                "analysis": result,
                "timestamp": pd.Timestamp.now().isoformat()
            })
            save_user_profile(current_user_id, user_profile)

            # Update sidebar display immediately to show knowledge graph growing
            with st.sidebar:
                st.json(user_profile)

            # Update the progress bar
            progress_bar.progress((index + 1) / total_leads)

        # After processing all leads, clear progress bar elements
        progress_bar_text.empty()
        progress_bar.empty()

        # Convert the list of dictionaries into a DataFrame for display and download
        processed_df = pd.DataFrame(processed_leads_data)
        st.write("### AI Processed Leads: Before vs. After")

        # Display side-by-side comparison for judges to easily see the value add
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Data")
            st.dataframe(df_original)
        with col2:
            st.subheader("AI Processed Data")
            st.dataframe(processed_df)

        st.write("---")
        st.subheader("Download Your Enhanced Leads")
        # Offer download button for the new DataFrame
        csv_output = processed_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Processed Leads (CSV)",
            data=csv_output,
            file_name="processed_leads_luminova_ai.csv",
            mime="text/csv",
            help="Click to download the spreadsheet with AI-generated qualifications and priorities."
        )

        st.success("Lead analysis complete!")
# Placeholder for processed results
st.write("---")
st.subheader("AI Processed Insights:")
# This area will display the processed DataFrame after the agent runs