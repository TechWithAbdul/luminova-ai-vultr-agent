# 🚀 LumiNova AI: Enterprise Insight Agent

A cutting-edge AI-powered sales lead qualification and prioritization system built with modern UI/UX design, real-time analytics, and intelligent agent technology.

## ✨ Features

### 🎨 Beautiful Modern Interface
- **Gradient Design**: Stunning purple-blue gradient theme with modern aesthetics
- **Responsive Layout**: Fully responsive design that works on all devices
- **Smooth Animations**: Hover effects, transitions, and loading animations
- **Interactive Charts**: Real-time data visualization with Plotly charts
- **Professional Typography**: Clean Inter font family for optimal readability

### 🤖 AI-Powered Lead Qualification
- **Intelligent Analysis**: Uses Groq's Llama 3 model for lead qualification
- **Priority Scoring**: 1-5 scale priority scoring system
- **Status Classification**: High Fit, Medium Fit, Low Fit, Not Fit categories
- **Detailed Reasoning**: AI provides explanations for each qualification decision

### 📊 Real-Time Analytics
- **Live Metrics**: Real-time counters for different qualification statuses
- **Interactive Charts**: Pie charts and histograms for data visualization
- **Progress Tracking**: Beautiful progress bars with live updates
- **Data Comparison**: Side-by-side original vs processed data display

### 👤 User Profile & Knowledge Graph
- **Persistent Profiles**: Firebase-powered user profiles with interaction history
- **Learning System**: AI learns from past interactions to improve over time
- **Activity Tracking**: Complete history of all processed leads
- **Session Management**: Secure user session handling

### 🔄 Agent Technology
- **Fetch.ai Integration**: Built with uAgents framework for agent communication
- **Coral Protocol**: Implements Coral Protocol for inter-agent messaging
- **Autonomous Processing**: Self-contained agent logic for lead analysis
- **Scalable Architecture**: Ready for multi-agent network deployment

## 🛠️ Technology Stack

- **Frontend**: Streamlit with custom CSS animations
- **AI/ML**: Groq API with Llama 3 model
- **Database**: Firebase Firestore for user profiles
- **Agents**: uAgents framework (Fetch.ai)
- **Visualization**: Plotly for interactive charts
- **Styling**: Custom CSS with modern design principles

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   Create a `.env` file with:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

4. **Upload Your Data**:
   - Use the sample `sample_leads.csv` file
   - Or upload your own CSV/Excel file with 'Company Name' and 'Description' columns

## 📁 Project Structure

```
luminova-ai-vultr-agent/
├── app.py                 # Main Streamlit application with beautiful UI
├── agent_logic.py         # AI agent logic and qualification engine
├── requirements.txt       # Python dependencies
├── sample_leads.csv      # Sample data for testing
├── test_agent.py         # Unit tests for agent functionality
└── README.md            # This file
```

## 🎯 How It Works

### 1. **Data Upload**
- Upload CSV or Excel files with company data
- Automatic validation of required columns
- Beautiful drag-and-drop interface

### 2. **AI Processing**
- Each lead is processed by the LumiNova AI agent
- Real-time progress tracking with animations
- Live metrics updates during processing

### 3. **Qualification & Scoring**
- **High Fit**: Tech companies, cloud/AI focus (Priority 4-5)
- **Medium Fit**: B2B with indirect tech alignment (Priority 3)
- **Low Fit**: B2B but unlikely to need advanced solutions (Priority 1-2)
- **Not Fit**: B2C, retail, local services (Priority 0)

### 4. **Results & Analytics**
- Interactive charts showing qualification distribution
- Priority score histograms
- Side-by-side data comparison
- Downloadable processed results

## 🏆 Hackathon Features

### ✅ **Agent Technology**
- Implements uAgents framework for autonomous processing
- Coral Protocol compliance for inter-agent communication
- Self-contained agent logic with reasoning capabilities

### ✅ **User Profile & Knowledge Graph**
- Firebase-powered persistent user profiles
- Complete interaction history tracking
- Learning system that improves over time

### ✅ **Modern UI/UX**
- Beautiful gradient design with animations
- Real-time data visualization
- Professional typography and spacing
- Responsive design for all devices

### ✅ **AI Integration**
- Groq API with Llama 3 model
- Intelligent lead qualification
- Detailed reasoning for decisions
- Priority scoring system

## 🎨 Design Highlights

### **Color Scheme**
- Primary: Purple-blue gradient (#667eea to #764ba2)
- Success: Green gradient (#10b981 to #059669)
- Cards: White with subtle shadows
- Text: Dark gray with proper contrast

### **Typography**
- Font: Inter (Google Fonts)
- Weights: 300, 400, 500, 600, 700
- Responsive sizing for all screen sizes

### **Animations**
- Hover effects on cards and buttons
- Smooth transitions (0.3s ease)
- Loading animations during processing
- Progress bar animations

### **Layout**
- Wide layout for maximum screen usage
- Responsive columns for data display
- Beautiful sidebar with user profile
- Card-based design for content organization

## 📊 Sample Output

The application processes leads and provides:

1. **Qualification Status**: High/Medium/Low/Not Fit
2. **Priority Score**: 0-5 scale
3. **AI Reasoning**: Detailed explanation for each decision
4. **Visual Analytics**: Charts and graphs
5. **Downloadable Results**: CSV export with all data

## 🔧 Configuration

### Environment Variables
- `GROQ_API_KEY`: Your Groq API key for AI processing
- `__firebase_config`: Firebase configuration (for deployment)
- `__app_id`: Application ID (for deployment)

### Customization
- Modify the CSS in `app.py` to change colors and styling
- Adjust the AI prompt in `agent_logic.py` for different qualification criteria
- Add new chart types in the visualization section

## 🚀 Deployment

The application is ready for deployment on:
- Streamlit Cloud
- Vercel
- Heroku
- Any platform supporting Python web applications

## 📈 Performance

- **Fast Processing**: Optimized for quick lead analysis
- **Real-time Updates**: Live progress tracking
- **Responsive Design**: Works on all devices
- **Scalable Architecture**: Ready for enterprise deployment

---

**Built with ❤️ for the Hackathon**  
*LumiNova AI - Transforming Sales Lead Qualification with AI* 