import streamlit as st
import cv2
import time
import numpy as np
import pandas as pd
from datetime import datetime
from src.mood import MoodDetector
from src.focus import FocusLogger
from src.recommender import TaskRecommender

st.set_page_config(page_title="StudyMood", layout="wide", page_icon="🎯")

# Load CSS from external file
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Session state
if 'session_active' not in st.session_state:
    st.session_state.session_active = False
if 'last_suggestion_time' not in st.session_state:
    st.session_state.last_suggestion_time = None
if 'current_suggestion' not in st.session_state:
    st.session_state.current_suggestion = "🌟 Start your study session to get personalized recommendations!"
if 'session_data' not in st.session_state:
    st.session_state.session_data = []

# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h1 style='background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%); 
                   -webkit-background-clip: text; 
                   -webkit-text-fill-color: transparent;
                   font-size: 2rem;
                   margin-bottom: 1rem;'>🎯 StudyMood</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("**✨ Navigate to:**")
    page = st.radio(
        "",
        ["Dashboard", "Mood Analysis", "Focus Tracking", "Recommendations"],
        key="nav",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 🎬 Session Control")
    
    if not st.session_state.session_active:
        if st.button("🚀 Start Session", use_container_width=True, key="start_btn"):
            st.session_state.session_active = True
            st.session_state.session_start = datetime.now()
            st.session_state.last_suggestion_time = datetime.now()
            st.session_state.session_data = []
            st.session_state.current_suggestion = "🎉 Session started! Tracking your mood and focus..."
            st.rerun()
    else:
        if st.button("⏹️ Stop Session", use_container_width=True, key="stop_btn"):
            st.session_state.session_active = False
            st.session_state.current_suggestion = "🏁 Session ended. Start a new session to continue tracking!"
            st.rerun()
    
    # Session info in sidebar
    if st.session_state.session_active:
        st.markdown("---")
        duration = datetime.now() - st.session_state.session_start
        minutes = duration.seconds // 60
        st.metric("⏱️ Session Time", f"{minutes} minutes")

# Initialize components
@st.cache_resource
def load_components():
    return MoodDetector(), FocusLogger(), TaskRecommender()

mood_detector, focus_logger, recommender = load_components()

# Mood emoji mapping
def get_mood_emoji(mood):
    emoji_map = {
        "Happy": "😊",
        "Neutral": "😌", 
        "Serious": "🤔",
        "sad": "😔"
    }
    return emoji_map.get(mood, "🤖")

# Focus level with color coding
def get_focus_level(focus_score):
    if focus_score >= 0.7:
        return "High Focus 🚀", "#10b981"
    elif focus_score >= 0.4:
        return "Medium Focus 💪", "#f59e0b"
    else:
        return "Low Focus 😴", "#ef4444"

# Camera initialization function
def initialize_camera():
    """Initialize camera with cloud compatibility"""
    try:
        # Try different camera indices for cloud compatibility
        for camera_index in [0, 1, 2]:
            camera = cv2.VideoCapture(camera_index)
            if camera.isOpened():
                # Test if camera can read frames
                ret, frame = camera.read()
                if ret:
                    st.success(f"✅ Camera {camera_index} initialized successfully!")
                    return camera
                camera.release()
        
        st.warning("⚠️ No functional camera found. The app will run with simulated camera feed.")
        return None
    except Exception as e:
        st.warning(f"⚠️ Camera initialization failed: {str(e)}")
        return None

# Dashboard Page
if page == "Dashboard":
    st.markdown('<h1 class="main-header">📊 Study Dashboard</h1>', unsafe_allow_html=True)
    
    if not st.session_state.session_active:
        # Welcome state
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""
            <div class='metric-card'>
                <h3>🎯 Ready to Boost Your Productivity?</h3>
                <p>Start a session to track your mood, focus, and get smart recommendations!</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='metric-card'>
                <h3>✨ How It Works</h3>
                <p>• Real-time mood detection using your camera</p>
                <p>• Focus level tracking with activity monitoring</p>
                <p>• Smart task suggestions based on your state</p>
            </div>
            """, unsafe_allow_html=True)
        
    else:
        # Active session
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📹 Live Camera Feed")
            
            # Initialize camera
            camera = initialize_camera()
            FRAME_WINDOW = st.image([])
            
            if camera is None:
                # Create a static informational frame
                static_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(static_frame, "Camera Not Available", (150, 200), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(static_frame, "Running in Analysis Mode", (120, 250), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                FRAME_WINDOW.image(static_frame)

        with col2:
            st.markdown("### 📈 Live Metrics")
            
            # Real-time metrics
            mood_placeholder = st.empty()
            focus_placeholder = st.empty()
            timer_placeholder = st.empty()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Suggestion box
        st.markdown("### 💫 Current Recommendation")
        suggestion_box = st.empty()
        
        with suggestion_box.container():
            st.markdown(f'''
            <div class="suggestion-box">
                <h3>✨ Smart Suggestion</h3>
                <p style="font-size: 1.2rem;">{st.session_state.current_suggestion}</p>
            </div>
            ''', unsafe_allow_html=True)

        # Main monitoring loop
        while st.session_state.session_active:
            # Handle camera frame
            if camera and camera.isOpened():
                ret, frame = camera.read()
                if not ret:
                    # Camera failed, create a placeholder
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(frame, "Camera Feed Unavailable", (120, 240), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            else:
                # No camera, create analysis mode frame
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Study Analysis Mode", (160, 220), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, "Tracking Focus & Activity", (140, 260), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Detect metrics (mood detector will handle no-face scenarios)
            mood, face_focus = mood_detector.detect_mood(frame)
            activity_focus = focus_logger.get_focus_score()
            total_focus = round((face_focus * 0.6 + activity_focus * 0.4), 2)
            
            # Store session data
            st.session_state.session_data.append({
                'timestamp': datetime.now(),
                'mood': mood,
                'focus': total_focus
            })

            # Update suggestion every 2 minutes
            current_time = datetime.now()
            if (st.session_state.last_suggestion_time is None or 
                (current_time - st.session_state.last_suggestion_time).seconds >= 120):
                
                new_suggestion = recommender.suggest(mood, total_focus)
                st.session_state.current_suggestion = new_suggestion
                st.session_state.last_suggestion_time = current_time
                
                # Update the suggestion box
                with suggestion_box.container():
                    st.markdown(f'''
                    <div class="suggestion-box">
                        <h3>✨ Smart Suggestion</h3>
                        <p style="font-size: 1.2rem;">{st.session_state.current_suggestion}</p>
                    </div>
                    ''', unsafe_allow_html=True)

            # Update real-time metrics
            with col2:
                with mood_placeholder.container():
                    mood_emoji = get_mood_emoji(mood)
                    st.markdown(f"""
                    <div class='metric-card'>
                        <div class='mood-emoji'>{mood_emoji}</div>
                        <h3>Current Mood</h3>
                        <h2 style='color: #5a67d8;'>{mood}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with focus_placeholder.container():
                    focus_text, focus_color = get_focus_level(total_focus)
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h3>Focus Level</h3>
                        <h2 style='color: {focus_color};'>{focus_text}</h2>
                        <p>Score: {total_focus}/1.0</p>
                        <div class='focus-bar' style='width: {total_focus * 100}%'></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with timer_placeholder.container():
                    session_duration = current_time - st.session_state.session_start
                    minutes = session_duration.seconds // 60
                    st.markdown(f"""
                    <div class='session-card'>
                        <h3>⏱️ Session Timer</h3>
                        <h2>{minutes} minutes</h2>
                        <p>Stay focused! 💫</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Add overlay to frame
            cv2.putText(frame, f"Mood: {mood}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (90, 103, 216), 2)
            cv2.putText(frame, f"Focus: {total_focus}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (107, 70, 193), 2)
            
            if not camera:
                cv2.putText(frame, "Cloud Mode", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame, use_container_width=True)
            
            time.sleep(0.5)
        
        # Cleanup
        if camera:
            camera.release()

# Mood Analysis Page
elif page == "Mood Analysis":
    st.markdown('<h1 class="page-header">😊 Mood Analysis</h1>', unsafe_allow_html=True)
    
    if not st.session_state.session_data:
        st.info("🎯 Start a session to see your mood analysis here!")
    else:
        mood_df = pd.DataFrame(st.session_state.session_data)
        mood_counts = mood_df['mood'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class='metric-card'>
                <h3>📊 Mood Summary</h3>
            """, unsafe_allow_html=True)
            st.metric("Total Samples", len(mood_df))
            if len(mood_counts) > 0:
                st.metric("Most Common Mood", mood_counts.index[0])
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='metric-card'>
                <h3>📈 Mood Distribution</h3>
            """, unsafe_allow_html=True)
            st.bar_chart(mood_counts)
            st.markdown("</div>", unsafe_allow_html=True)

# Focus Tracking Page
elif page == "Focus Tracking":
    st.markdown('<h1 class="page-header">🎯 Focus Tracking</h1>', unsafe_allow_html=True)
    
    if not st.session_state.session_data:
        st.info("🎯 Start a session to track your focus patterns!")
    else:
        focus_df = pd.DataFrame(st.session_state.session_data)
        if not focus_df.empty:
            focus_df = focus_df.set_index('timestamp')
            
            col1, col2 = st.columns(2)
            
            with col1:
                avg_focus = focus_df['focus'].mean()
                max_focus = focus_df['focus'].max()
                st.markdown("""
                <div class='metric-card'>
                    <h3>📊 Focus Metrics</h3>
                """, unsafe_allow_html=True)
                st.metric("Average Focus", f"{avg_focus:.2f}/1.0")
                st.metric("Peak Focus", f"{max_focus:.2f}/1.0")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class='metric-card'>
                    <h3>📈 Focus Trend</h3>
                """, unsafe_allow_html=True)
                st.line_chart(focus_df['focus'])
                st.markdown("</div>", unsafe_allow_html=True)

# Recommendations Page
elif page == "Recommendations":
    st.markdown('<h1 class="page-header">💡 Smart Recommendations</h1>', unsafe_allow_html=True)
    
    st.markdown(f'''
    <div class="suggestion-box">
        <h3>✨ Current Recommendation</h3>
        <p style="font-size: 1.2rem;">{st.session_state.current_suggestion}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("""
    <div class='metric-card'>
        <h3>🎯 How It Works</h3>
        <p>• <strong>Low Focus (< 0.3)</strong>: Suggests breaks and relaxation</p>
        <p>• <strong>Sad Mood</strong>: Recommends easier, creative tasks</p>
        <p>• <strong>Happy + High Focus</strong>: Suggests deep work sessions</p>
        <p>• <strong>Other cases</strong>: Balanced task recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Example recommendations
    st.markdown("### 💫 Example Recommendations")
    examples = [
        {"emoji": "🎯", "text": "Take a 5-min break, stretch and relax"},
        {"emoji": "💡", "text": "Do an easy/creative task to lift mood"}, 
        {"emoji": "🚀", "text": "Great time for deep work (Pomodoro 25m)"},
        {"emoji": "📚", "text": "Continue with medium tasks and stay consistent"}
    ]
    
    cols = st.columns(2)
    for idx, example in enumerate(examples):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>{example['emoji']} {example['text']}</h3>
            </div>
            """, unsafe_allow_html=True)
