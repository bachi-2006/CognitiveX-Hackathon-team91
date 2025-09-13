import streamlit as st
import requests
import os
import time
from datetime import datetime

BACKEND = os.environ.get("BACKEND_URL","http://localhost:8000")

st.set_page_config(page_title="MediScan - Drug Recognition", layout="wide", page_icon="💊")

# Initialize session state for authentication and page navigation
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'landing'

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Base styles with improved typography and color scheme */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #2c3e50;
        background: linear-gradient(135deg, #1E2F3E, #2980B9);
    }
    
    .main-header {
        text-align: center;
        color: #ffffff;
        font-size: 3em;
        margin-bottom: 20px;
        font-weight: 700;
    }
    .sub-header {
        text-align: center;
        color: #e3f2fd;
        font-size: 1.5em;
        margin-bottom: 30px;
    }
    /* Enhanced button styles with better transitions */
    .stButton>button {
        background: linear-gradient(135deg, #2980B9, #6DD5FA);
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2980B9, #6DD5FA);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stButton>button:active {
        transform: translateY(0);
        box-shadow: 0 2px 3px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background-color: #ecf0f1;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .card {
        background: linear-gradient(135deg, #2980B9, #1E2F3E);
        color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
        border-left: 4px solid #2980B9;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .feature-icon {
        font-size: 2.5em;
        margin-bottom: 10px;
        color: #2980B9;
    }
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 30px;
        background: linear-gradient(135deg, #2980B9, #1E2F3E);
        color: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-top: 4px solid #2980B9;
    }
    .login-header {
        text-align: center;
        color: #2980B9;
        margin-bottom: 25px;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    /* Chat interface styles */
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background: linear-gradient(135deg, #2980B9, #1E2F3E);
        color: white;
        border-left: 5px solid #2980B9;
    }
    .chat-message.bot {
        background: linear-gradient(135deg, #1E2F3E, #2980B9);
        color: white;
        border-left: 5px solid #6DD5FA;
    }
    .chat-message .message-content {
        margin-top: 0;
    }
    /* BMI Calculator styles */
    .bmi-result {
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        text-align: center;
    }
    .bmi-value {
        font-size: 3rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .bmi-category {
        font-size: 1.5rem;
        margin-bottom: 10px;
    }
    .bmi-advice {
         font-style: italic;
         margin-top: 15px;
     }
    .logout-btn {
        position: absolute;
        top: 20px;
        right: 20px;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        color: #666;
        font-size: 0.9em;
        border-top: 1px solid #eee;
    }
    /* Hover highlight for dosage/frequency */
    .hover-highlight {
        transition: background 0.3s, color 0.3s;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .hover-highlight:hover {
        background: #FF6E7F33;
        color: #FF6E7F;
        cursor: pointer;
    }
    /* Enhanced animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-fadeIn {
        animation: fadeIn 0.5s ease-out forwards;
    }
    /* New pulse animation for call-to-action elements */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .animate-pulse {
        animation: pulse 2s infinite;
    }
    /* Tab styling improvements */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        background-color: #1E2F3E;
        color: #e3f2fd;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2980B9, #6DD5FA) !important;
        color: white !important;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
    }
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5em;
        }
        .sub-header {
            font-size: 1.2em;
        }
        .card {
            padding: 15px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Function to display the landing page
def show_landing_page():
    st.markdown("<h1 class='main-header animate-fadeIn'>💊 MediScan</h1>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header animate-fadeIn'>Advanced Drug Recognition & Health Information System</div>", unsafe_allow_html=True)
    
    # Hero section with animation
    st.markdown("""
    <div class='animate-fadeIn' style='text-align: center; margin: 30px 0;'>
        <img src='https://img.icons8.com/color/240/000000/pharmacy.png' style='max-width: 180px;'>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards with hover effects
    st.markdown("<h2 style='text-align: center; margin: 40px 0 20px;'>Key Features</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='card animate-fadeIn' style='animation-delay: 0.1s;'>
            <div class='feature-icon'>📋</div>
            <h3>Prescription Parser</h3>
            <p>Extract drug names, dosages, and frequencies from prescription text automatically.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='card animate-fadeIn' style='animation-delay: 0.3s;'>
            <div class='feature-icon'>💊</div>
            <h3>Dosage Information</h3>
            <p>Get recommended dosages based on age and other factors for safer medication use.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='card animate-fadeIn' style='animation-delay: 0.5s;'>
            <div class='feature-icon'>📏</div>
            <h3>BMI Calculator</h3>
            <p>Calculate your Body Mass Index and get personalized health insights based on your results.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='card animate-fadeIn' style='animation-delay: 0.2s;'>
            <div class='feature-icon'>⚠️</div>
            <h3>Interaction Checker</h3>
            <p>Identify potential interactions between multiple medications to ensure safety.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='card animate-fadeIn' style='animation-delay: 0.4s;'>
            <div class='feature-icon'>💬</div>
            <h3>MediBot Chat</h3>
            <p>Chat with our AI-powered medical assistant for information about medications and health advice.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='card animate-fadeIn' style='animation-delay: 0.6s;'>
            <div class='feature-icon'>🔄</div>
            <h3>Alternative Medications</h3>
            <p>Discover alternative medications when your prescribed drug is unavailable or causing side effects.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to action buttons
    st.markdown("<div style='text-align: center; margin: 50px 0;'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🔐 Login to Access", key="login_btn", use_container_width=True):
            st.session_state.current_page = 'login'
            st.rerun()
        
        if st.button("ℹ️ Learn More", key="learn_btn", use_container_width=True):
            st.session_state.current_page = 'about'
            st.rerun()
    
    # Footer
    st.markdown("""
    <div class='footer'>
        <p>© 2023 MediScan - Drug Recognition System. All rights reserved.</p>
        <p>This application is for informational purposes only. Always consult a healthcare professional.</p>
    </div>
    """, unsafe_allow_html=True)

# Function to display the login page
def show_login_page():
    st.markdown("<div class='login-container animate-fadeIn'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-header'>🔐 Login to MediScan</h2>", unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Home", key="back_btn"):
        st.session_state.current_page = 'landing'
        st.rerun()
    
    # Login form
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    col1, col2 = st.columns([1,1])
    with col1:
        st.checkbox("Remember me", key="remember")
    with col2:
        st.markdown("<div style='text-align: right;'><a href='#'>Forgot password?</a></div>", unsafe_allow_html=True)
    
    if st.button("Login", key="submit_login", use_container_width=True):
        # For demo purposes, accept any non-empty username/password
        if username.strip() and password.strip():
            # Show a spinner for login animation
            with st.spinner("Logging in..."):
                time.sleep(1)  # Simulate login process
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.current_page = 'app'
                st.success("Login successful!")
                time.sleep(0.5)
                st.rerun()
        else:
            st.error("Please enter both username and password")
    
    st.markdown("<div style='text-align: center; margin-top: 20px;'>Don't have an account? <a href='#'>Sign up</a></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Function to display the about page
def show_about_page():
    st.markdown("<h1 class='main-header animate-fadeIn'>About MediScan</h1>", unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Home", key="back_to_home"):
        st.session_state.current_page = 'landing'
        st.rerun()
    
    st.markdown("""
    <div class='card animate-fadeIn'>
        <h2>Our Mission</h2>
        <p>MediScan is designed to help healthcare professionals and patients better understand medication information, 
        dosages, and potential interactions. Our goal is to improve medication safety and accessibility of pharmaceutical information.</p>
    </div>
    
    <div class='card animate-fadeIn' style='animation-delay: 0.1s;'>
        <h2>How It Works</h2>
        <p>MediScan uses advanced natural language processing to extract medication information from prescription text. 
        It then cross-references this information with our comprehensive drug database and external APIs to provide 
        accurate dosage information, potential interactions, and alternative medications.</p>
    </div>
    
    <div class='card animate-fadeIn' style='animation-delay: 0.2s;'>
        <h2>Important Disclaimer</h2>
        <p>MediScan is an informational tool only and should not replace professional medical advice. 
        Always consult with a qualified healthcare provider before making any decisions about medications.</p>
    </div>
    """, unsafe_allow_html=True)

# Function to display the main application
def show_main_app():
    # Logout button
    col_logout = st.columns([6, 1])
    with col_logout[1]:
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.current_page = 'landing'
            st.rerun()
    
    st.markdown(f"<h1 class='main-header'>💊 MediScan</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: right;'>Welcome, {st.session_state.get('username', 'User')} | {datetime.now().strftime('%d %b %Y, %H:%M')}</p>", unsafe_allow_html=True)
    
    # Sidebar for additional info
    with st.sidebar:
        st.header("ℹ️ About")
        st.write("This app helps parse prescription text and provides drug information.")
        st.write("**Features:**")
        st.write("- Parse drug names, dosages, frequencies")
        st.write("- Get dosage recommendations")
        st.write("- Check drug interactions")
        st.write("- Suggest alternatives")
        st.warning("⚠️ Always consult a healthcare professional before making medical decisions.")
    
    # Main content area with tabs for different functions
    tabs = st.tabs(["📝 Prescription Parser", "🔍 Drug Lookup", "💬 MediBot Chat", "📏 BMI Calculator", "📊 Dashboard"])
    
    # Tab 1: Prescription Parser
    with tabs[0]:
        st.header("📝 Paste prescription / notes")
        text = st.text_area("Enter prescription text here", height=240, placeholder="e.g. Paracetamol 500 mg twice daily, Amoxicillin 500 mg q8h", key="text_input")
        col_parse, col_clear = st.columns(2)
        with col_parse:
            if st.button("🔍 Parse", key="parse_btn"):
                if not text.strip():
                    st.warning("Please enter prescription text first.")
                else:
                    with st.spinner("Parsing prescription..."):
                        resp = requests.post(f"{BACKEND}/extract", json={"text": text})
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success("✅ Parsing complete!")
                        st.subheader("📋 Parsed (neat text)")
                        st.code(data.get("plain_text",""), language=None)
                        
                        # Display structured data in a more visual way with hover and animation
                        st.subheader("Structured Data")
                        structured = data.get("structured", [])
                        if structured:
                            for i, drug_info in enumerate(structured):
                                with st.container():
                                    st.markdown(f"""
                                    <div class='card animate-fadeIn' style='animation-delay: {0.1 + i*0.1}s;'>
                                        <h3>{drug_info.get('name', 'Unknown Drug')}</h3>
                                        <p><strong>Dosage:</strong> <span class='hover-highlight'>{drug_info.get('dosage', 'Not specified')}</span></p>
                                        <p><strong>Frequency:</strong> <span class='hover-highlight'>{drug_info.get('frequency', 'Not specified')}</span></p>
                                        <p><strong>Symptom:</strong> <span class='hover-highlight'>{drug_info.get('symptom', 'Not specified')}</span></p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        st.markdown('<div class="warning-box">⚠️ This is for informational purposes only. Consult a doctor before taking any medicine.</div>', unsafe_allow_html=True)
                    else:
                        st.error("Backend error: " + resp.text)
        with col_clear:
            if st.button("🗑️ Clear", key="clear_btn"):
                st.rerun()
    
    # Tab 2: Drug Lookup
    with tabs[1]:
        st.header("🔍 Quick lookup")
        drug = st.text_input("Drug name", key="drug_input")
        age = st.number_input("Age", min_value=0, max_value=120, value=30, key="age_input")
    
        subtabs = st.tabs(["💊 Dosage", "⚠️ Interactions", "🔄 Alternatives"])
    
        with subtabs[0]:
            if age < 18:
                weight = st.number_input("Weight (kg) [for children]", min_value=5.0, max_value=150.0, value=30.0, step=0.1, key="weight_input")
            else:
                weight = None
            if st.button("Get Dosage", key="dosage_btn"):
                if not drug.strip():
                    st.warning("Please enter a drug name.")
                else:
                    with st.spinner("Fetching dosage..."):
                        if age < 18:
                            r = requests.post(f"{BACKEND}/get_child_dosage", json={"drug": drug, "age": age, "weight": weight})
                        else:
                            r = requests.post(f"{BACKEND}/get_dosage", json={"drug": drug, "age": age})
                    if r.status_code == 200:
                            dosage_val = r.json().get("dosage")
                            if age < 18:
                                # Only show the dosage amount, no text
                                st.info(f"{dosage_val}")
                            else:
                                st.markdown("**💊 Dosage:**")
                                st.info(dosage_val)
                    else:
                        st.error("Error fetching dosage.")
    
        with subtabs[1]:
            drugs_raw = st.text_input("Comma separated drug list", value=drug, key="interactions_input")
            if st.button("Check Interactions", key="interactions_btn"):
                drug_list = [d.strip() for d in drugs_raw.split(",") if d.strip()]
                if not drug_list:
                    st.warning("Please enter drug names.")
                else:
                    with st.spinner("Checking interactions..."):
                        r = requests.post(f"{BACKEND}/check_interactions", json={"drugs": drug_list})
                    if r.status_code == 200:
                        st.markdown("**⚠️ Interactions:**")
                        interactions = r.json().get("interactions", {})
                        if interactions:
                            for drug_name, inters in interactions.items():
                                if inters:
                                    st.error(f"{drug_name}: {', '.join(inters)}")
                                else:
                                    st.success(f"{drug_name}: No known interactions")
                        else:
                            st.info("No interactions found.")
                    else:
                        st.error("Error checking interactions.")
    
        with subtabs[2]:
            if st.button("Suggest Alternatives", key="alternatives_btn"):
                if not drug.strip():
                    st.warning("Please enter a drug name.")
                else:
                    with st.spinner("Suggesting alternatives..."):
                        r = requests.post(f"{BACKEND}/suggest_alternatives", json={"drug": drug, "age": age})
                    if r.status_code == 200:
                        st.markdown("**🔄 Alternatives:**")
                        alts = r.json().get("alternatives", [])
                        if alts:
                            for alt in alts:
                                st.write(f"- {alt}")
                        else:
                            st.info("No alternatives suggested.")
                        st.markdown('<div class="warning-box">⚠️ Always consult a clinician before switching medications.</div>', unsafe_allow_html=True)
                    else:
                        st.error("Error suggesting alternatives.")
    
    # Tab 3: MediBot Chat Interface
    with tabs[2]:
        st.header("💬 MediBot Chat")
        st.markdown("<p>Chat with our AI-powered medical assistant for information about medications, health conditions, and general medical advice.</p>", unsafe_allow_html=True)
        
        # Initialize chat history in session state if it doesn't exist
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat messages
        for message in st.session_state.chat_history:
            with st.container():
                if message['role'] == 'user':
                    st.markdown(f"<div class='chat-message user'><p class='message-content'>{message['content']}</p></div>", unsafe_allow_html=True)
                else:  # bot message
                    st.markdown(f"<div class='chat-message bot'><p class='message-content'>{message['content']}</p></div>", unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input("Ask MediBot about medications, dosages, or health advice...", key="chat_input")
        
        # Process user input
        if st.button("Send", key="send_chat") or user_input:
            if user_input.strip():
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                # Get context from previous messages (last 3 exchanges)
                context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history[-6:] if msg['role'] == 'bot'])
                
                # Call backend API
                with st.spinner("MediBot is thinking..."):
                    try:
                        response = requests.post(f"{BACKEND}/chat", json={"message": user_input, "context": context})
                        if response.status_code == 200:
                            bot_response = response.json().get("response", "I'm sorry, I couldn't process your request.")
                            # Add bot response to chat history
                            st.session_state.chat_history.append({"role": "bot", "content": bot_response})
                        else:
                            st.error(f"Error: {response.status_code}")
                            st.session_state.chat_history.append({"role": "bot", "content": "I'm having trouble connecting to my knowledge base. Please try again later."})
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.session_state.chat_history.append({"role": "bot", "content": "I'm having trouble processing your request. Please try again later."})
                
                # Clear input
                st.rerun()
        
        # Clear chat button
        if st.button("Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
            
        st.markdown("<div class='warning-box'>⚠️ MediBot provides general information only. Always consult a healthcare professional for medical advice.</div>", unsafe_allow_html=True)
    
    # Tab 4: BMI Calculator
    with tabs[3]:
        st.header("📏 BMI Calculator")
        st.markdown("<p>Calculate your Body Mass Index (BMI) and get personalized health insights.</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.1)
            height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.1)
        
        with col2:
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
            gender = st.selectbox("Gender (optional)", options=["Not specified", "Male", "Female", "Other"])
        
        if st.button("Calculate BMI", key="calc_bmi"):
            with st.spinner("Calculating..."):
                try:
                    # Prepare gender parameter
                    gender_param = "" if gender == "Not specified" else gender.lower()
                    
                    # Call backend API
                    response = requests.post(
                        f"{BACKEND}/calculate_bmi", 
                        json={"weight": weight, "height": height, "age": age, "gender": gender_param}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display BMI result with appropriate color
                        st.markdown(f"<div class='bmi-result' style='background-color: {result['color']}20; border-left: 5px solid {result['color']}; color: {result['color']}'>" +
                                    f"<div class='bmi-value'>{result['bmi']}</div>" +
                                    f"<div class='bmi-category'>{result['category']}</div>" +
                                    f"</div>", unsafe_allow_html=True)
                        
                        # Display advice
                        st.markdown(f"<p><strong>Advice:</strong> {result['advice']}</p>", unsafe_allow_html=True)
                        
                        # Display age-specific advice if present
                        if result.get('age_advice'):
                            st.info(result['age_advice'])
                        
                        # Display disclaimer
                        st.markdown("<div class='warning-box'>" + result['disclaimer'] + "</div>", unsafe_allow_html=True)
                    else:
                        st.error(f"Error calculating BMI: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # BMI information
        with st.expander("About BMI"):
            st.markdown("""
            **What is BMI?**
            
            Body Mass Index (BMI) is a value derived from a person's weight and height. It provides a simple numeric measure of a person's thickness or thinness, allowing health professionals to discuss weight problems more objectively with their patients.
            
            **BMI Categories:**
            - Below 18.5: Underweight
            - 18.5 to 24.9: Normal weight
            - 25.0 to 29.9: Overweight
            - 30.0 and above: Obese
            
            **Limitations of BMI:**
            - Does not account for muscle mass, bone density, or overall body composition
            - May not be accurate for athletes, elderly, or during pregnancy
            - Does not indicate the distribution of fat in the body
            
            Always consult with healthcare professionals for a comprehensive health assessment.
            """)
    
    # Tab 5: Dashboard (placeholder for future enhancement)
    with tabs[4]:
        st.header("📊 Dashboard")
        st.info("This feature is coming soon! The dashboard will provide analytics and insights about your medication queries.")
        
        # Placeholder charts
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class='card'>
                <h3>Most Queried Medications</h3>
                <p style='color: #999;'>Visualization coming soon</p>
                <div style='background-color: #f5f5f5; height: 200px; border-radius: 5px; display: flex; justify-content: center; align-items: center;'>
                    <span style='color: #aaa;'>Chart Placeholder</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='card'>
                <h3>Interaction Analysis</h3>
                <p style='color: #999;'>Visualization coming soon</p>
                <div style='background-color: #f5f5f5; height: 200px; border-radius: 5px; display: flex; justify-content: center; align-items: center;'>
                    <span style='color: #aaa;'>Chart Placeholder</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Main app logic - determine which page to show
if st.session_state.authenticated:
    show_main_app()
else:
    if st.session_state.current_page == 'landing':
        show_landing_page()
    elif st.session_state.current_page == 'login':
        show_login_page()
    elif st.session_state.current_page == 'about':
        show_about_page()
    else:
        show_landing_page()


