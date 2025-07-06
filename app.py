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

# Firebase Admin SDK Imports
import firebase_admin
from firebase_admin import credentials, firestore

# Import our agent logic
from agent_logic import process_single_lead_with_agent

# Load Environment Variables
load_dotenv()

# Custom CSS for modern, beautiful design
st.set_page_config(
    layout="wide", 
    page_title="LumiNova AI: Enterprise Insight Agent",
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# Inject custom CSS for modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .upload-area {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 2px dashed #667eea;
        text-align: center;
        margin: 2rem 0;
    }
    
    .data-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .user-profile-card {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    .progress-container {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    
    .download-section {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 2rem 0;
    }
    
    .stProgress > div > div > div > div {
        background-color: #667eea;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    .stDataFrame td {
        border-bottom: 1px solid #e5e7eb;
    }
    
    .stDataFrame tr:hover {
        background-color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Firebase Admin SDK
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
        st.error("Cannot save profile: Firebase not connected.")

# Initialize Groq Client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("❌ GROQ_API_KEY not found. Please set it in your .env file.")
    st.stop()

groq_client = Groq(api_key=groq_api_key)

# Main App Header
st.markdown("""
<div class="main-header">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">🚀 LumiNova AI</h1>
    <h2 style="font-size: 1.5rem; margin-bottom: 1rem; opacity: 0.9;">Enterprise Insight Agent</h2>
    <p style="font-size: 1.1rem; opacity: 0.8;">AI-Powered Sales Lead Qualification & Prioritization</p>
</div>
""", unsafe_allow_html=True)

# User ID generation
if 'user_id' not in st.session_state:
    st.session_state.user_id = os.getenv('__initial_auth_token', str(uuid.uuid4()))
current_user_id = st.session_state.user_id

# Enhanced Sidebar with User Profile
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3 style="color: white; margin-bottom: 1rem;">👤 User Profile</h3>
        <div class="user-profile-card">
            <p style="margin: 0; font-size: 0.9rem;">User ID: <code style="background: rgba(255,255,255,0.2); padding: 0.2rem 0.5rem; border-radius: 5px;">{}</code></p>
        </div>
    </div>
    """.format(current_user_id[:8] + "..."), unsafe_allow_html=True)
    
    user_profile = get_user_profile(current_user_id)
    
    # Profile Statistics
    total_interactions = len(user_profile.get("past_interactions", []) if user_profile else [])
    created_at = user_profile.get('created_at', 'N/A') if user_profile else 'N/A'
    created_at_str = created_at[:10] if created_at != 'N/A' else 'N/A'
    st.markdown(f"""
    <div class="user-profile-card">
        <h4 style="margin-bottom: 1rem;">📊 Activity Stats</h4>
        <p style="margin: 0.5rem 0;">Total Leads Processed: <strong>{total_interactions}</strong></p>
        <p style="margin: 0.5rem 0;">Profile Created: <strong>{created_at_str}</strong></p>
    </div>
    """, unsafe_allow_html=True)

# Main Content Area
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #667eea; margin-bottom: 0.5rem;">🎯 Lead Qualification</h3>
        <p style="margin: 0; opacity: 0.8;">AI-powered analysis of sales leads</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #667eea; margin-bottom: 0.5rem;">📈 Priority Scoring</h3>
        <p style="margin: 0; opacity: 0.8;">Intelligent prioritization system</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #667eea; margin-bottom: 0.5rem;">🧠 Knowledge Graph</h3>
        <p style="margin: 0; opacity: 0.8;">Persistent user learning</p>
    </div>
    """, unsafe_allow_html=True)

# File Upload Section
st.markdown("""
<div class="upload-area">
    <h3 style="color: #667eea; margin-bottom: 1rem;">📁 Upload Your Sales Leads</h3>
    <p style="margin-bottom: 1rem; opacity: 0.8;">Upload a CSV or Excel file with 'Company Name' and 'Description' columns</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose your file",
    type=["csv", "xlsx"],
    help="Upload your sales leads data"
)

df_original = pd.DataFrame()

if uploaded_file is not None:
    try:
        with st.spinner("🔄 Loading your data..."):
            if uploaded_file.name.endswith('.csv'):
                df_original = pd.read_csv(uploaded_file)
            else:
                df_original = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Successfully loaded {len(df_original)} leads from {uploaded_file.name}")
        
        # Display original data in a beautiful card
        st.markdown("""
        <div class="data-card">
            <h3 style="color: #667eea; margin-bottom: 1rem;">📋 Original Data Preview</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(df_original.head(), use_container_width=True)
        
        # Check for required columns
        required_columns = ['Company Name', 'Description']
        if not all(col in df_original.columns for col in required_columns):
            st.error(f"❌ Missing required columns. Please ensure your file has '{required_columns[0]}' and '{required_columns[1]}' columns.")
            df_original = pd.DataFrame()
        else:
            st.success("🎯 Data format validated! Ready for AI analysis.")
            
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        df_original = pd.DataFrame()

# Processing Section
if not df_original.empty:
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Analyze Leads with AI", use_container_width=True):
            st.markdown("""
            <div class="progress-container">
                <h3 style="color: #667eea; margin-bottom: 1rem;">🤖 AI Analysis in Progress</h3>
            </div>
            """, unsafe_allow_html=True)
            
            processed_leads_data = []
            progress_bar_text = st.empty()
            progress_bar = st.progress(0)
            
            total_leads = len(df_original)
            
            # Create metrics for real-time updates
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                high_fit_metric = st.metric("High Fit", "0")
            with col2:
                medium_fit_metric = st.metric("Medium Fit", "0")
            with col3:
                low_fit_metric = st.metric("Low Fit", "0")
            with col4:
                not_fit_metric = st.metric("Not Fit", "0")
            
            high_count = medium_count = low_count = not_fit_count = 0
            
            for idx, (df_index, row) in enumerate(df_original.iterrows()):
                company = row['Company Name']
                description = row['Description']
                lead_id = f"lead_{df_index}"
                
                # Convert to strings to avoid type errors
                company_str = str(company) if company is not None else ""
                description_str = str(description) if description is not None else ""
                
                progress_bar_text.text(f"🔄 Processing: {company_str}...")
                
                # Add a small delay for visual effect
                time.sleep(0.1)
                
                result = process_single_lead_with_agent(company_str, description_str, lead_id)
                
                # Update counters
                status = result.get("qualified_status", "Not Fit")
                if status == "High Fit":
                    high_count += 1
                elif status == "Medium Fit":
                    medium_count += 1
                elif status == "Low Fit":
                    low_count += 1
                else:
                    not_fit_count += 1
                
                # Update metrics
                high_fit_metric.metric("High Fit", str(high_count))
                medium_fit_metric.metric("Medium Fit", str(medium_count))
                low_fit_metric.metric("Low Fit", str(low_count))
                not_fit_metric.metric("Not Fit", str(not_fit_count))
                
                processed_leads_data.append({
                    "Original Company Name": company,
                    "Original Description": description,
                    "Qualified Status": result.get("qualified_status", "N/A") if result else "N/A",
                    "Priority Score": result.get("priority_score", 0) if result else 0,
                    "Reasoning": result.get("reasoning", "No reasoning provided") if result else "No reasoning provided"
                })
                
                # Update user profile
                if user_profile and "past_interactions" in user_profile:
                    user_profile["past_interactions"].append({
                        "lead_id": lead_id,
                        "company": company,
                        "description": description,
                        "analysis": result,
                        "timestamp": datetime.now().isoformat()
                    })
                    save_user_profile(current_user_id, user_profile)
                
                progress_bar.progress((idx + 1) / total_leads)
            
            progress_bar_text.empty()
            progress_bar.empty()
            
            if processed_leads_data:
                processed_df = pd.DataFrame(processed_leads_data)
                
                # Create beautiful comparison section
                st.markdown("""
                <div class="chart-container">
                    <h3 style="color: #667eea; margin-bottom: 1rem;">📊 Analysis Results</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Create visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Status distribution pie chart
                    status_counts = processed_df['Qualified Status'].value_counts()
                    fig_pie = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        title="Lead Qualification Distribution",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_pie.update_layout(height=400)
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    # Priority score distribution
                    fig_hist = px.histogram(
                        processed_df,
                        x='Priority Score',
                        title="Priority Score Distribution",
                        nbins=6,
                        color_discrete_sequence=['#667eea']
                    )
                    fig_hist.update_layout(height=400)
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                # Side-by-side data comparison
                st.markdown("""
                <div class="data-card">
                    <h3 style="color: #667eea; margin-bottom: 1rem;">📋 Data Comparison</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**📥 Original Data**")
                    st.dataframe(df_original, use_container_width=True)
                
                with col2:
                    st.markdown("**🤖 AI Processed Data**")
                    st.dataframe(processed_df, use_container_width=True)
                
                # Download section
                st.markdown("""
                <div class="download-section">
                    <h3 style="margin-bottom: 1rem;">💾 Download Your Enhanced Leads</h3>
                    <p style="margin-bottom: 1rem; opacity: 0.9;">Get your AI-processed data with qualifications and priorities</p>
                </div>
                """, unsafe_allow_html=True)
                
                csv_output = processed_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Processed Leads (CSV)",
                    data=csv_output,
                    file_name=f"luminova_ai_processed_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.success("🎉 Analysis complete! Your leads have been qualified and prioritized.")
            else:
                st.warning("⚠️ No leads were processed. Please check your data and try again.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #6b7280;">
    <p>🚀 LumiNova AI - Enterprise Insight Agent | Built with Streamlit & Groq</p>
    <p style="font-size: 0.8rem;">AI-Powered Sales Lead Qualification & Prioritization</p>
</div>
""", unsafe_allow_html=True)