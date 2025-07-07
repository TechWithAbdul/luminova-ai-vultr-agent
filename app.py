# app.py

import streamlit as st
from dotenv import load_dotenv
import os
from groq import Groq
import pandas as pd
import json
import uuid
import plotly.express as px
import time
from datetime import datetime
import numpy as np

# Firebase Admin SDK Imports
import firebase_admin
from firebase_admin import credentials, firestore

# Import our agent logic (assuming this file exists and contains process_single_lead_with_agent)
try:
    from agent_logic import process_single_lead_with_agent
except ImportError:
    st.error("Error: agent_logic.py not found. Please ensure it's in the same directory.")


# Load Environment Variables
load_dotenv()

# --- Streamlit Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="LumiNova AI: Enterprise Insight Agent",
    page_icon="💠",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Modern, Captivating Design (Revised for Sidebar Title Visibility) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&display=swap'); /* For futuristic titles */
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #e0e6f2; /* Slightly brighter text for dark theme */
    }

    .main {
        background: linear-gradient(135deg, #0a0a1a 0%, #12122b 100%); /* Deeper, more intense dark gradient */
        color: #e0e6f2;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #12122b 100%);
    }
    
    /* Main Header Styling */
    .main-header {
        background: linear-gradient(135deg, #5b21b6 0%, #7c3aed 100%); /* Deeper purple gradient */
        padding: 3rem 2.5rem;
        border-radius: 30px;
        margin-bottom: 3.5rem;
        box-shadow: 0 30px 60px rgba(0,0,0,0.5); /* Stronger shadow */
        color: white;
        text-align: center;
        position: relative;
        overflow: hidden;
        animation: fadeIn 1s ease-out;
        border: 2px solid rgba(124, 58, 237, 0.5); /* Subtle border for depth */
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at center, rgba(255,255,255,0.15) 0%, transparent 70%); /* Brighter shine */
        transform: rotate(45deg);
        animation: headerShine 5s infinite linear;
    }
    .main-header h1 {
        font-family: 'Orbitron', sans-serif;
        font-size: 4.2rem; /* Even larger, more impactful */
        margin-bottom: 0.8rem;
        text-shadow: 0 6px 20px rgba(0,0,0,0.6); /* More pronounced text shadow */
        letter-spacing: 2px; /* A bit more space for futuristic feel */
    }
    .main-header h2 {
        font-size: 2.0rem; /* Larger sub-header */
        margin-bottom: 1.5rem;
        opacity: 0.95;
    }
    .main-header p {
        font-size: 1.3rem;
        opacity: 0.85;
    }

    /* Metric Cards */
    .metric-card {
        background: #181830; /* Darker, slightly blueish tone */
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 45px rgba(0,0,0,0.4); /* Stronger shadow */
        margin: 1.5rem 0;
        border-left: 7px solid #7c3aed; /* Deeper accent */
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        color: #e0e6f2;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before { /* Subtle background pattern/texture */
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle, rgba(124, 58, 237, 0.05) 1px, transparent 1px);
        background-size: 10px 10px;
        opacity: 0.3;
    }
    .metric-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 55px rgba(124, 58, 237, 0.3);
    }
    .metric-card h3 {
        color: #9333ea; /* Brighter accent color for titles */
        font-size: 1.8rem;
        margin-bottom: 0.8rem;
        text-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .metric-card p {
        font-size: 1.2rem;
        opacity: 0.9;
    }

    /* Upload Area */
    .upload-area {
        background: #181830;
        padding: 3rem;
        border-radius: 30px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.4);
        border: 4px dashed #7c3aed; /* Even thicker, more prominent dashed border */
        text-align: center;
        margin: 3.5rem 0;
        color: #e0e6f2;
        animation: slideInUp 0.8s ease-out;
        position: relative;
    }
    .upload-area::before { /* Animated glowing border effect */
        content: '';
        position: absolute;
        inset: -2px;
        border-radius: 32px;
        background: conic-gradient(from 0deg at 50% 50%, #7c3aed, #5b21b6, #7c3aed);
        mask: linear-gradient(#000, #000) content-box, linear-gradient(#000, #000);
        mask-composite: exclude;
        -webkit-mask-composite: exclude;
        animation: rotateBorder 4s linear infinite;
        opacity: 0.7;
        filter: blur(10px);
    }
    .upload-area h3 {
        color: #9333ea;
        font-size: 2.2rem;
        margin-bottom: 1.5rem;
        text-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .upload-area p {
        font-size: 1.3rem;
        opacity: 0.9;
    }

    /* Data Card for Previews/Comparison */
    .data-card {
        background: #181830;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 45px rgba(0,0,0,0.4);
        margin: 1.8rem 0;
        color: #e0e6f2;
        border: 1px solid rgba(124, 58, 237, 0.2); /* Subtle border */
    }
    .data-card h3 {
        color: #9333ea;
        font-size: 2.0rem;
        margin-bottom: 1.2rem;
        text-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .data-card p {
        font-size: 1.1rem;
        opacity: 0.9;
    }

    /* Sidebar Styling - CRITICAL UPDATES FOR TITLE VISIBILITY */
    /* Targets the primary sidebar background container */
    .st-emotion-cache-vk33v5 {
        background: linear-gradient(135deg, #0a0a1a 0%, #12122b 100%) !important;
        color: #e0e6f2 !important;
        border-right: 2px solid #5b21b6 !important;
        min-height: 100vh;
        padding: 2.5rem 1.2rem !important;
    }

    /* FORCE user profile and activity stats titles to be visible */
    /* Target h3 for "User Profile" (from st.markdown header) */
    .st-emotion-cache-vk33v5 h3 {
        color: #fff !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        letter-spacing: 1px;
        margin-bottom: 0.7rem !important;
        text-shadow: 0 2px 8px rgba(124,58,237,0.15);
    }

    /* Target h4 for "Activity Statistics" (from st.markdown header) */
    .st-emotion-cache-vk33v5 h4 {
        color: #fff !important; /* Keep the accent color for sub-headers within cards */
        font-size: 1.3rem !important;
        margin-bottom: 0.8rem !important;
    }

    /* Ensure generic text in sidebar is visible */
    .st-emotion-cache-vk33v5 p,
    .st-emotion-cache-vk33v5 div { /* Catch all for general div/p text */
        color: #e0e6f2 !important;
        font-size: 1.05rem;
    }


    .user-profile-card {
        background: linear-gradient(135deg, #5b21b6 0%, #7c3aed 100%) !important;
        border: 2px solid #a78bfa !important;
        color: #e0e6f2 !important;
        border-radius: 18px !important;
        box-shadow: 0 4px 18px rgba(124,58,237,0.10);
        margin-bottom: 1.2rem;
        padding: 1.3rem 1.1rem !important;
        transition: box-shadow 0.2s, transform 0.2s;
    }
    .user-profile-card:hover {
        box-shadow: 0 8px 32px rgba(124,58,237,0.25);
        transform: translateY(-4px) scale(1.02);
    }
    .user-profile-card h4 {
        color: #fff !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        letter-spacing: 1px;
        margin-bottom: 0.7rem !important;
        text-shadow: 0 2px 8px rgba(124,58,237,0.15);
    }
    .user-profile-card p {
        color: #e0e6f2 !important;
        font-size: 1.05rem;
    }
    .user-profile-card code {
        background: rgba(124, 58, 237, 0.25); /* Brighter code block */
        padding: 0.25rem 0.75rem;
        border-radius: 8px;
        color: #e0e6f2;
        font-size: 0.9rem;
    }

    /* Progress and Chart Containers */
    .progress-container, .chart-container {
        background: #181830;
        padding: 2.5rem;
        border-radius: 25px;
        box-shadow: 0 18px 40px rgba(0,0,0,0.4);
        margin: 2.5rem 0;
        color: #e0e6f2;
        border: 1px solid rgba(124, 58, 237, 0.2);
    }
    .progress-container h3, .chart-container h3 {
        color: #9333ea;
        font-size: 2.2rem;
        margin-bottom: 1.5rem;
        text-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .progress-container p, .chart-container p {
        font-size: 1.1rem;
        opacity: 0.9;
    }

    /* Download Section */
    .download-section {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%); /* Stronger green gradient */
        padding: 3rem;
        border-radius: 30px;
        color: white;
        text-align: center;
        margin: 3.5rem 0;
        box-shadow: 0 20px 50px rgba(0,0,0,0.4);
        animation: fadeIn 1s ease-out;
        border: 2px solid rgba(16, 185, 129, 0.5);
    }
    .download-section h3 {
        font-size: 2.2rem;
        margin-bottom: 1.2rem;
        text-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    .download-section p {
        font-size: 1.2rem;
        opacity: 0.95;
    }

    /* Streamlit Widget Overrides */
    .stProgress > div > div > div > div {
        background-color: #7c3aed; /* Progress bar color */
    }
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%); /* Brighter button gradient */
        color: white;
        border: none;
        padding: 1rem 2.5rem; /* Even larger button */
        border-radius: 35px; /* More rounded */
        font-weight: 700;
        font-size: 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    .stButton > button:hover {
        transform: translateY(-4px);
        box-shadow: 0 18px 40px rgba(124, 58, 237, 0.5);
    }
    
    /* DataFrame Styling - Crucial for dark theme & visibility */
    .stDataFrame {
        border-radius: 15px; /* More rounded */
        overflow: hidden;
        background: #1e1e3b; /* Slightly different dark background for tables */
        border: 1px solid #3d3d66; /* Clearer border */
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .stDataFrame th {
        background: linear-gradient(135deg, #5b21b6 0%, #7c3aed 100%) !important; /* Header gradient */
        color: white !important;
        font-weight: 600;
        padding: 14px 18px;
        border-bottom: 2px solid #4a4a75; /* Stronger separator */
        text-align: left !important; /* Ensure consistent text alignment */
    }
    .stDataFrame td {
        border-bottom: 1px solid #2a2a4a; /* Subtle row separator */
        color: #e0e6f2; /* Ensure text visibility */
        padding: 12px 18px;
    }
    .stDataFrame tr:hover {
        background-color: #25254d; /* More distinct on hover */
    }
    /* Ensure full content for tables - Streamlit handles scrollbars if content is too large */
    /* Adjust max-height for comparison tables inside expander for better visibility */
    .stDataFrame > div > div > div:nth-child(2) {
        max-height: 450px; /* Increased height for comparison tables */
        overflow-y: auto;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: #1e1e3b; /* Consistent dark input background */
        color: #e0e6f2;
        border: 1px solid #3d3d66;
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
    }
    .stTextInput > label, .stFileUploader > label {
        color: #e0e6f2;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    /* File Uploader */
    .stFileUploader > div {
        background-color: #1e1e3b;
        color: #e0e6f2;
        border: 3px dashed #7c3aed; /* Consistent dashed border */
        border-radius: 20px;
        padding: 1.8rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stFileUploader > div:hover {
        border-color: #a78bfa;
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.3);
    }

    /* Metric values */
    .stMetric > div > div:nth-child(2) {
        font-size: 3.0rem; /* Even larger metric numbers */
        font-weight: 700;
        color: #7c3aed; /* Accent color */
        text-shadow: 0 3px 8px rgba(124, 58, 237, 0.3);
    }
    .stMetric > div > div:nth-child(1) {
        font-size: 1.2rem;
        opacity: 0.95;
    }

    /* Plotly Chart Styling */
    .stPlotlyChart {
        border-radius: 15px; /* More rounded */
        overflow: hidden;
        box-shadow: 0 15px 45px rgba(0,0,0,0.4);
        border: 1px solid rgba(124, 58, 237, 0.2);
    }
    
    /* Expander styling for icon visibility and overall theme */
    .stExpander {
        border: 1px solid #3d3d66; /* Make expander container visible */
        border-radius: 15px;
        background-color: #181830; /* Consistent dark background for expander */
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        color: #e0e6f2; /* Ensure text inside expander is visible */
    }
    /* Target the expander header (the clickable part) */
    .stExpander > div:first-child {
        background-color: #1a1a35; /* Slightly different shade for header */
        border-radius: 15px; /* Apply to header */
        padding: 0.8rem 1.2rem; /* Add padding to header */
    }
    /* Target the text inside the expander header */
    .stExpander > div:first-child > div > p {
        font-size: 1.2rem;
        font-weight: 600;
        color: #a78bfa !important; /* Make title of the expander vibrant */
    }

    /* Target the expander icon (arrow) directly by its SVG */
    .stExpander > div:first-child > div > div > svg {
        color: #a78bfa !important;
        font-size: 1.7rem !important;
        transition: transform 0.3s;
    }
    /* Rotate icon when expander is open */
    .stExpander > div:first-child[aria-expanded="true"] > div > div > svg {
        transform: rotate(90deg);
    }


    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(70px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes headerShine {
        0% { transform: rotate(45deg) translateX(-100%); }
        100% { transform: rotate(45deg) translateX(100%); }
    }
    @keyframes rotateBorder {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Engaging Notifications */
    .stSuccess, .stError, .stWarning, .stInfo {
        padding: 1.2rem 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        font-size: 1.1rem;
        font-weight: 500;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        animation: fadeIn 0.5s ease-out;
    }
    .stSuccess {
        background-color: #0d6e4b; /* Deeper green */
        color: #d1fae5;
        border: 1px solid #10b981;
    }
    .stError {
        background-color: #882222; /* Deeper red */
        color: #fecaca;
        border: 1px solid #ef4444;
    }
    .stWarning {
        background-color: #a05a0f; /* Deeper orange */
        color: #fed7aa;
        border: 1px solid #fbbf24;
    }
    .stInfo {
        background-color: #2a52be; /* Deeper blue */
        color: #bfdbfe;
        border: 1px solid #3b82f6;
    }

</style>
""", unsafe_allow_html=True)

# --- Firebase Initialization ---
firebase_config_json_str = os.getenv('__firebase_config')
app_id = os.getenv('__app_id', 'luminova_test_app')

if firebase_config_json_str:
    try:
        cred_dict = json.loads(firebase_config_json_str)
        cred = credentials.Certificate(cred_dict)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        st.success("🔥 Firebase connected successfully!")
    except Exception as e:
        st.error(f"Firebase initialization error: {e}")
        db = None
else:
    st.warning("⚠️ Firebase not initialized. Set '__firebase_config' in deployment environment.")
    db = None

def get_user_profile(user_id_param):
    if db:
        doc_ref = db.collection('users').document(user_id_param)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            new_profile = {"past_interactions": [], "preferences": {}, "created_at": datetime.now().isoformat()}
            doc_ref.set(new_profile)
            return new_profile
    return {"past_interactions": [], "preferences": {}, "created_at": datetime.now().isoformat()}

def save_user_profile(user_id_param, profile_data):
    if db:
        db.collection('users').document(user_id_param).set(profile_data)
    else:
        # In a deployed scenario, this error might not be shown directly to user
        st.error("Cannot save profile: Firebase not connected. User data will not persist.")

# --- Initialize Groq Client ---
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("❌ GROQ_API_KEY not found. Please set it in your .env file.")
    st.stop()

groq_client = Groq(api_key=groq_api_key)

# --- Main App Header (with custom HTML/CSS) ---
st.markdown("""
<div class="main-header">
    <h1><span style="color: #c4b5fd;">LumiNova AI</span></h1>
    <h2>Enterprise Insight Agent</h2>
    <p>🚀 Elevate Your Sales Strategy with AI-Powered Lead Intelligence 🚀</p>
</div>
""", unsafe_allow_html=True)

# --- User ID generation and Sidebar ---
if 'user_id' not in st.session_state:
    st.session_state.user_id = os.getenv('__initial_auth_token', str(uuid.uuid4()))
current_user_id = st.session_state.user_id

# --- Sidebar Theme Toggle ---
if 'sidebar_theme' not in st.session_state:
    st.session_state.sidebar_theme = 'dark'

def toggle_sidebar_theme():
    st.session_state.sidebar_theme = 'light' if st.session_state.sidebar_theme == 'dark' else 'dark'

with st.sidebar:
    # Use a specific container for dynamic sidebar updates to control clearing
    sidebar_content_placeholder = st.empty()
    with sidebar_content_placeholder.container():
        # Using st.header/subheader instead of markdown for these titles 
        # to make CSS targeting more predictable with Streamlit's classes
        st.header("👤 User Profile") # This will now be targeted by .st-emotion-cache-vk33v5 h3
        st.markdown("""
            <div class="user-profile-card">
                <p style="margin: 0; font-size: 0.9rem;">User ID: <code style="background: rgba(124, 58, 237, 0.25); padding: 0.2rem 0.6rem; border-radius: 6px; color: #e0e6f2;">{}</code></p>
            </div>
        """.format(current_user_id[:8] + "..."), unsafe_allow_html=True) # Truncate ID for display

        user_profile = get_user_profile(current_user_id)
        
        # Profile Statistics
        total_interactions = len(user_profile.get("past_interactions", []) if user_profile else [])
        created_at = user_profile.get('created_at', 'N/A') if user_profile else 'N/A'
        created_at_str = created_at[:10] if created_at != 'N/A' else 'N/A'

        st.markdown(f"""
        <div class="user-profile-card">
            <h4>📊 Activity Statistics</h4> 
            <p style="margin: 0.5rem 0;">Total Leads Processed: <strong>{total_interactions}</strong></p>
            <p style="margin: 0.5rem 0;">Profile Created: <strong>{created_at_str}</strong></p>
            <p style="margin: 0.5rem 0;">Last Interaction: <strong>{user_profile['past_interactions'][-1]['timestamp'][:16].replace('T', ' ') if user_profile and user_profile.get('past_interactions') else 'N/A'}</strong></p>
        </div>
        """, unsafe_allow_html=True)

        # Display full user profile JSON for advanced users/debugging (within an expander)
        with st.expander("👁️ View Raw Knowledge Graph"):
            st.json(user_profile) # Display the raw profile JSON

# --- Main Content Area - Metric Cards ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>🎯Lead Qualification</h3>
        <p>Precise AI-powered lead analysis</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>📈 Priority Scoring</h3>
        <p>Intelligent  Prioritization</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>🧠Knowledge Graph</h3>
        <p>Personalized,persistent user learning</p>
    </div>
    """, unsafe_allow_html=True)

# --- File Upload Section ---
st.markdown("""
<div class="upload-area">
    <h3>Upload Your Sales Leads</h3>
    <p>Upload a <span style="color:#a78bfa; font-weight:600;">CSV</span> or <span style="color:#a78bfa; font-weight:600;">Excel</span> file with 'Company Name' and 'Description' columns.</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose your file",
    type=["csv", "xlsx"],
    help="Upload your sales leads data",
    label_visibility="collapsed" # Hide default label for cleaner design
)

df_original = pd.DataFrame()

if uploaded_file is not None:
    try:
        with st.spinner("🔄 Loading your data..."):
            if uploaded_file.name.endswith('.csv'):
                df_original = pd.read_csv(uploaded_file)
            else: # Must be .xlsx
                df_original = pd.read_excel(uploaded_file)
        
        st.success(f"Successfully loaded {len(df_original)} leads from {uploaded_file.name} 🎉. Scroll down to preview!")
        
        # Display original data in a beautiful card
        st.markdown("""
        <div class="data-card">
            <h3>Original Data Preview</h3>
            <p>First 10 rows of your uploaded file.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(df_original.head(10), use_container_width=True, height=350) # Show more rows, fixed height with scroll
        
        # Check for required columns
        required_columns = ['Company Name', 'Description']
        if not all(col in df_original.columns for col in required_columns):
            st.error(f"Missing required columns. Please ensure your file has '{required_columns[0]}' and '{required_columns[1]}' columns.")
            df_original = pd.DataFrame()
        else:
            st.success("Data format validated! Click the 'Analyze' button below to proceed. 👇")
            
    except Exception as e:
        st.error(f"Error reading file: {e}. Please ensure it's a valid CSV/Excel format and not corrupted. 😔")
        df_original = pd.DataFrame()

# --- Processing Section ---
if not df_original.empty:
    st.markdown("---") # Visual separator
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2: # Center the button
        if st.button("Analyze Leads with AI", use_container_width=True):
            st.markdown("""
            <div class="progress-container">
                <h3>AI Analysis in Progress <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f916/emoji.svg" alt="robot" width="30" height="30" style="vertical-align: middle;"></h3>
                <p>Your LumiNova AI agent is diligently qualifying and prioritizing leads. This may take a moment...</p>
            </div>
            """, unsafe_allow_html=True)
            
            processed_leads_data = []
            progress_status_placeholder = st.empty() # Placeholder for processing text
            progress_bar = st.progress(0)
            
            total_leads = len(df_original)
            
            # Create metrics for real-time updates during processing
            metric_cols = st.columns(4)
            high_fit_metric = metric_cols[0].metric("High Fit", "0")
            medium_fit_metric = metric_cols[1].metric("Medium Fit", "0")
            low_fit_metric = metric_cols[2].metric("Low Fit", "0")
            not_fit_metric = metric_cols[3].metric("Not Fit", "0")
            
            high_count = medium_count = low_count = not_fit_count = 0
            
            # Helper function to safely convert to string, handling NaN, None, pd.NA, Series, NDFrame
            def safe_str(val):
                if val is None:
                    return ""
                try:
                    # Handles np.nan, pd.NA, pd.NaT
                    if pd.isna(val):
                        return ""
                except Exception:
                    pass
                # If it's a Series or NDFrame, treat as empty
                if hasattr(val, 'ndim') and val.ndim > 0:
                    return ""
                return str(val)
            
            for idx, (df_index, row) in enumerate(df_original.iterrows()):
                # Fix 2: Use .get() for DataFrame row access to ensure scalar values
                company_val = row.get('Company Name', "")
                description_val = row.get('Description', "")
                company_str = safe_str(company_val)
                description_str = safe_str(description_val)
                
                progress_status_placeholder.markdown(f"**Processing:** <span style='color:#a78bfa;'>{company_str}</span> (Lead {idx + 1} of {total_leads})...", unsafe_allow_html=True)
                
                # Add a small delay for visual effect and to prevent overwhelming API (if many leads)
                # time.sleep(0.05) # Uncomment if you want to slow down for demo
                
                result = process_single_lead_with_agent(company_str, description_str, f"lead_{df_index}")
                
                # Update counters based on AI result
                status = result.get("qualified_status", "Not Fit")
                if status == "High Fit":
                    high_count += 1
                elif status == "Medium Fit":
                    medium_count += 1
                elif status == "Low Fit":
                    low_count += 1
                else: # Includes "Not Fit" and "Error"
                    not_fit_count += 1
                
                # Update metrics in real-time
                high_fit_metric.metric("High Fit", str(high_count))
                medium_fit_metric.metric("Medium Fit", str(medium_count))
                low_fit_metric.metric("Low Fit", str(low_count))
                not_fit_metric.metric("Not Fit", str(not_fit_count))
                
                processed_leads_data.append({
                    "Original Company Name": company_str, # Keep original object for display
                    "Original Description": description_str, # Keep original object for display
                    "Qualified Status": result.get("qualified_status", "N/A"),
                    "Priority Score": result.get("priority_score", 0),
                    "Reasoning": result.get("reasoning", "No reasoning provided")
                })
                
                # Update user profile in Firebase
                if user_profile and "past_interactions" in user_profile:
                    user_profile["past_interactions"].append({
                        "lead_id": f"lead_{df_index}",
                        "company": company_str,
                        "description": description_str,
                        "analysis": result,
                        "timestamp": datetime.now().isoformat()
                    })
                    save_user_profile(current_user_id, user_profile)
                
                # Update sidebar display to show knowledge graph growing
                # Clear and re-render sidebar content within its placeholder
                sidebar_content_placeholder.empty()
                with sidebar_content_placeholder.container():
                    # Re-using st.header/subheader for reliable CSS targeting
                    st.header("👤 User Profile") 
                    st.markdown("""
                        <div class="user-profile-card">
                            <p style="margin: 0; font-size: 0.9rem;">User ID: <code style="background: rgba(124, 58, 237, 0.25); padding: 0.2rem 0.6rem; border-radius: 6px; color: #e0e6f2;">{}</code></p>
                        </div>
                    """.format(current_user_id[:8] + "..."), unsafe_allow_html=True) # Truncate ID for display

                    # Re-fetch profile to ensure latest updates are shown
                    updated_profile_for_display = get_user_profile(current_user_id) 

                    # Fix 3: Add None checks before using .get()
                    if updated_profile_for_display:
                        total_leads = len(updated_profile_for_display.get("past_interactions", []))
                        created_at = updated_profile_for_display.get('created_at', 'N/A')[:10]
                        last_interaction = (
                            updated_profile_for_display['past_interactions'][-1]['timestamp'][:16].replace('T', ' ')
                            if updated_profile_for_display.get('past_interactions') else 'N/A'
                        )
                    else:
                        total_leads = 0
                        created_at = 'N/A'
                        last_interaction = 'N/A'
                    st.markdown(f"""
                    <div class="user-profile-card">
                        <h4>📊 Activity Statistics</h4> 
                        <p style="margin: 0.5rem 0;">Total Leads Processed: <strong>{total_leads}</strong></p>
                        <p style="margin: 0.5rem 0;">Profile Created: <strong>{created_at}</strong></p>
                        <p style="margin: 0.5rem 0;">Last Interaction: <strong>{last_interaction}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("👁️ View Raw Knowledge Graph"):
                         st.json(updated_profile_for_display)

                progress_bar.progress((idx + 1) / total_leads)
            
            # Clear progress elements after completion
            progress_status_placeholder.empty()
            progress_bar.empty()
            
            if processed_leads_data:
                processed_df = pd.DataFrame(processed_leads_data)
                
                # --- Analysis Results & Visualizations ---
                st.markdown("""
                <div class="chart-container">
                    <h3>Analysis Results & Visualizations <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f4c8/emoji.svg" alt="chart_up" width="30" height="30" style="vertical-align: middle;"></h3>
                    <p>Gain quick insights into your lead distribution and priority.</p>
                </div>
                """, unsafe_allow_html=True)
                
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    # Status distribution pie chart
                    status_counts = processed_df['Qualified Status'].value_counts()
                    fig_pie = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        title="Lead Qualification Distribution",
                        color_discrete_sequence=px.colors.qualitative.Pastel # Softer colors
                    )
                    fig_pie.update_layout(
                        height=480, # Slightly taller for better view
                        margin=dict(t=60, b=0, l=0, r=0), # Adjust margins
                        paper_bgcolor='rgba(0,0,0,0)', # Transparent background
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#e0e6f2', # Text color
                        title_font_color='#9333ea', # Title color
                        legend_font_color='#e0e6f2', # Legend text color
                        legend_title_font_color='#9333ea' # Legend title color
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with chart_col2:
                    # Priority score distribution histogram
                    fig_hist = px.histogram(
                        processed_df,
                        x='Priority Score',
                        title="Priority Score Distribution",
                        nbins=6, # 0-5
                        color_discrete_sequence=['#7c3aed'], # Accent color
                        category_orders={"Priority Score": [0, 1, 2, 3, 4, 5]}, # Ensure order
                        text_auto=True # Show values on bars
                    )
                    fig_hist.update_layout(
                        height=480, # Slightly taller
                        margin=dict(t=60, b=0, l=0, r=0),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#e0e6f2',
                        title_font_color='#9333ea',
                        xaxis_title="Priority Score",
                        yaxis_title="Number of Leads",
                        xaxis=dict(tickfont=dict(color='#e0e6f2'), title_font=dict(color='#a78bfa')),
                        yaxis=dict(tickfont=dict(color='#e0e6f2'), title_font=dict(color='#a78bfa'))
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                # --- Side-by-side data comparison ---
                st.markdown("""
                <div class="data-card">
                    <h3>Data Comparison: Original vs. AI Processed <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f50e/emoji.svg" alt="magnifying_glass" width="30" height="30" style="vertical-align: middle;"></h3>
                    <p>See the transformation of your raw leads into actionable insights.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Use st.expander for large tables to keep UI clean but allow full view
                with st.expander("👇 Click to view Full Data Comparison Tables"):
                    col_orig, col_proc = st.columns(2)
                    with col_orig:
                        st.markdown("**Original Leads**")
                        st.dataframe(df_original, use_container_width=True, height=550) # Fixed height with scroll
                    with col_proc:
                        st.markdown("**AI Processed Leads**")
                        st.dataframe(processed_df, use_container_width=True, height=550) # Fixed height with scroll
                
                # --- Download section ---
                st.markdown("""
                <div class="download-section">
                    <h3>Download Your Enhanced Leads <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f4e5/emoji.svg" alt="download" width="30" height="30" style="vertical-align: middle;"></h3>
                    <p>Get your AI-processed data with qualifications and priorities, ready for your CRM or next steps.</p>
                </div>
                """, unsafe_allow_html=True)
                
                csv_output = processed_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Processed Leads (CSV)",
                    data=csv_output,
                    file_name=f"luminova_ai_processed_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="Click to download the spreadsheet with AI-generated qualifications and priorities."
                )
                
                st.success("Analysis complete! Your leads have been qualified and prioritized. 🎉 Ready for action!")
            else:
                st.warning("No leads were processed. Please check your data and try again. 🤔")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #6d778d; font-size: 0.9rem;">
    <p>LumiNova AI - Enterprise Insight Agent | Built with <span style="color:#a78bfa;">Streamlit</span>, <span style="color:#a78bfa;">Groq</span>, <span style="color:#a78bfa;">Fetch.ai</span>, & <span style="color:#a78bfa;">Firebase</span></p>
    <p style="font-size: 0.8rem;">Empowering the Future of Work with Agentic AI and Intelligent Insights.</p>
    <p style="font-size: 0.7rem;">&copy; 2024 LumiNova AI. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)