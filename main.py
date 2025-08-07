"""
Event Situational Awareness Dashboard - Streamlit Application
"""
import streamlit as st
import time
from datetime import datetime
import traceback
from typing import Dict, Any, List

# Import our agents
from agents.coordinator import CoordinatorAgent
from config import config

# Configure Streamlit page
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .zone-card {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: white;
    }
    .status-green { background-color: #d4edda; border-color: #c3e6cb; }
    .status-yellow { background-color: #fff3cd; border-color: #ffeaa7; }
    .status-orange { background-color: #ffe8a1; border-color: #ffb347; }
    .status-red { background-color: #f8d7da; border-color: #f5c6cb; }
    .threat-level {
        font-size: 1.2em;
        font-weight: bold;
        padding: 0.3rem 0.6rem;
        border-radius: 0.3rem;
        text-align: center;
    }
    .confidence-score {
        font-size: 0.9em;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'coordinator' not in st.session_state:
    st.session_state.coordinator = None
    st.session_state.last_analysis = None
    st.session_state.analysis_running = False
    st.session_state.chat_history = []

def initialize_coordinator():
    """Initialize the coordinator agent"""
    try:
        if st.session_state.coordinator is None:
            with st.spinner("Initializing AI agents..."):
                st.session_state.coordinator = CoordinatorAgent()
                
        return st.session_state.coordinator.status == "ready"
    except Exception as e:
        st.error(f"Failed to initialize system: {str(e)}")
        return False

def get_threat_level_color(threat_level: str) -> str:
    """Get CSS class for threat level"""
    colors = {
        'green': 'status-green',
        'darkyellow': 'status-yellow',
        'orange': 'status-orange',
        'red': 'status-red'
    }
    return colors.get(threat_level.lower(), 'status-yellow')

def format_confidence_score(score: float) -> str:
    """Format confidence score as percentage"""
    try:
        return f"{float(score) * 100:.1f}%"
    except (ValueError, TypeError):
        return "N/A"

def render_system_status():
    """Render system status in sidebar"""
    st.sidebar.header("🔧 System Status")
    
    if st.session_state.coordinator:
        system_status = st.session_state.coordinator.get_system_status()
        
        # Overall status
        coordinator_status = system_status.get('coordinator_status', 'unknown')
        status_color = '🟢' if coordinator_status == 'ready' else '🔴'
        st.sidebar.write(f"{status_color} **Coordinator:** {coordinator_status}")
        
        # API Key status
        api_configured = system_status.get('api_key_configured', False)
        api_color = '🟢' if api_configured else '🔴'
        st.sidebar.write(f"{api_color} **Gemini API:** {'Configured' if api_configured else 'Not configured'}")
        
        # Last analysis
        last_analysis = system_status.get('last_analysis')
        if last_analysis:
            st.sidebar.write(f"🕐 **Last Analysis:** {last_analysis}")
        
        # Data status
        data_status = system_status.get('data_status', {})
        vision_count = data_status.get('vision_analyses_count', 0)
        st.sidebar.write(f"📊 **Vision Analyses:** {vision_count}")
        
        report_available = data_status.get('report_analysis_available', False)
        report_color = '🟢' if report_available else '🟡'
        st.sidebar.write(f"{report_color} **Field Reports:** {'Available' if report_available else 'Pending'}")
        
    else:
        st.sidebar.write("🔴 **System:** Not initialized")

def render_summary_panel():
    """Render main summary panel"""
    st.header("📊 Event Overview")
    
    if not st.session_state.coordinator:
        st.warning("System not initialized. Please check system status.")
        return
    
    summary = st.session_state.coordinator.get_current_summary()
    
    if summary.get('status') == 'no_data':
        st.info("No analysis data available. Click 'Run Analysis' to start.")
        return
    elif summary.get('status') == 'error':
        st.error(f"Analysis error: {summary.get('message', 'Unknown error')}")
        return
    elif summary.get('status') != 'success':
        st.warning("Analysis data incomplete or unavailable.")
        return
    
    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        threat_level = summary.get('threat_level', 'yellow')
        threat_color = "white"
        st.markdown(f"""
        <div class="threat-level {threat_color}">
            🚨 Threat Level: {threat_level.upper()}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        zone_count = summary.get('zone_count', 0)
        st.metric("Zones Monitored", zone_count)
    
    with col3:
        confidence = summary.get('confidence', 0.5)
        st.metric("Confidence", format_confidence_score(confidence))
    
    with col4:
        last_update = summary.get('last_update', 'Unknown')
        if last_update != 'Unknown':
            try:
                update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                formatted_time = update_time.strftime('%H:%M:%S')
                st.metric("Last Update", formatted_time)
            except:
                st.metric("Last Update", "Unknown")
        else:
            st.metric("Last Update", "Unknown")
    
    # Overall situation
    st.subheader("Current Situation")
    overall_situation = summary.get('overall_situation', 'No information available')
    st.write(overall_situation)
    
    # Immediate concerns
    immediate_concerns = summary.get('immediate_concerns', [])
    if immediate_concerns:
        st.subheader("⚠️ Immediate Concerns")
        for concern in immediate_concerns:
            st.warning(f"• {concern}")

def render_zone_cards():
    """Render zone status cards"""
    st.header("🏢 Zone Status")
    
    if not st.session_state.coordinator:
        st.warning("System not initialized.")
        return
    
    summary = st.session_state.coordinator.get_current_summary()
    
    if summary.get('status') != 'success':
        st.info("No zone data available.")
        return
    
    zones = summary.get('zones', [])
    
    if not zones:
        st.info("No zone analysis data available.")
        return
    
    # Create columns for zone cards
    cols_per_row = 2
    for i in range(0, len(zones), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            zone_idx = i + j
            if zone_idx < len(zones):
                zone = zones[zone_idx]
                
                with col:
                    render_zone_card(zone)

def render_zone_card(zone: Dict[str, Any]):
    """Render individual zone card"""
    zone_name = zone.get('zone_name', 'Unknown Zone')
    status = zone.get('status_assessment', 'Unknown')
    
    # Determine status color
    status_lower = status.lower()
    if 'normal' in status_lower or 'operational' in status_lower:
        status_class = 'status-green'
    elif 'concern' in status_lower or 'moderate' in status_lower:
        status_class = 'status-yellow'
    elif 'high' in status_lower or 'critical' in status_lower:
        status_class = 'status-red'
    else:
        status_class = 'status-yellow'
    
    st.markdown(f"""
    <div class="zone-card {status_class}">
        <h4>{zone_name}</h4>
        <p><strong>Status:</strong> {status}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Crowd situation
    crowd_situation = zone.get('crowd_situation', {})
    if crowd_situation:
        density = crowd_situation.get('density_level', 'unknown')
        behavior = crowd_situation.get('crowd_behavior', 'unknown')
        estimate = crowd_situation.get('reconciled_estimate', 'unknown')
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Crowd Density", density.title())
        with col2:
            st.metric("Behavior", behavior.title())
        
        if estimate != 'unknown':
            st.write(f"**Estimate:** {estimate} people")
    
    # Risk assessment
    risk_assessment = zone.get('risk_assessment', {})
    if risk_assessment:
        risk_level = risk_assessment.get('combined_risk_level', 'unknown')
        primary_concerns = risk_assessment.get('primary_concerns', [])
        
        st.write(f"**Risk Level:** {risk_level.title()}")
        
        if primary_concerns:
            st.write("**Primary Concerns:**")
            for concern in primary_concerns[:3]:  # Show top 3
                st.write(f"• {concern}")
    
    # Recommended actions
    recommended_actions = zone.get('recommended_actions', [])
    if recommended_actions:
        st.write("**Recommended Actions:**")
        for action in recommended_actions[:2]:  # Show top 2
            st.write(f"• {action}")

def render_query_interface():
    """Render user query interface"""
    st.header("❓ Ask Questions")
    
    if not st.session_state.coordinator:
        st.warning("System not initialized.")
        return
    
    # Suggested questions
    with st.expander("💡 Suggested Questions", expanded=False):
        try:
            suggested_questions = st.session_state.coordinator.get_suggested_questions()
            
            for question in suggested_questions:
                if st.button(question, key=f"suggest_{hash(question)}"):
                    st.session_state.current_question = question
                    # Process the question
                    process_question(question)
        
        except Exception as e:
            st.write("Unable to load suggested questions.")
    
    # Question input
    user_question = st.text_input(
        "Enter your question about the current situation:",
        value=st.session_state.get('current_question', ''),
        placeholder="e.g., What's the situation in Zone A?"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Ask Question", disabled=not user_question.strip()):
            process_question(user_question)
    
    with col2:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Display chat history
    if st.session_state.chat_history:
        st.subheader("💬 Conversation")
        
        for i, (question, answer_data) in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5
            with st.container():
                st.markdown(f"**Q:** {question}")
                
                if answer_data.get('error'):
                    st.error(f"Error: {answer_data.get('error_message', 'Unknown error')}")
                else:
                    answer = answer_data.get('answer', 'No answer available')
                    confidence = answer_data.get('confidence', 0.5)
                    
                    st.markdown(f"**A:** {answer}")
                    
                    # Show confidence and supporting evidence
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.markdown(f"<span class='confidence-score'>Confidence: {format_confidence_score(confidence)}</span>", 
                                  unsafe_allow_html=True)
                    
                    # Supporting evidence in expander
                    supporting_evidence = answer_data.get('supporting_evidence', [])
                    if supporting_evidence:
                        with st.expander("📋 Supporting Evidence"):
                            for evidence in supporting_evidence:
                                st.write(f"• {evidence}")
                
                st.divider()

def process_question(question: str):
    """Process user question"""
    try:
        with st.spinner("Processing your question..."):
            answer_data = st.session_state.coordinator.answer_question(question)
            
            # Add to chat history
            st.session_state.chat_history.append((question, answer_data))
            
            # Clear current question
            if 'current_question' in st.session_state:
                del st.session_state.current_question
            
            st.rerun()
    
    except Exception as e:
        st.error(f"Error processing question: {str(e)}")

def render_control_panel():
    """Render control panel"""
    st.sidebar.header("🎛️ Control Panel")
    
    # API Key configuration
    st.sidebar.subheader("Configuration")
    current_key = config.GOOGLE_API_KEY
    api_status = "✅ Configured" if current_key else "❌ Not configured"
    st.sidebar.write(f"**Gemini API:** {api_status}")
    
    if not current_key:
        st.sidebar.warning("Please configure your Google Gemini API key in the .env file")
        st.sidebar.code("GOOGLE_API_KEY=your_api_key_here")
    
    # Analysis controls
    st.sidebar.subheader("Analysis Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.sidebar.button("🔄 Run Analysis", disabled=st.session_state.analysis_running):
            run_analysis()
    
    with col2:
        if st.sidebar.button("♻️ Refresh", disabled=st.session_state.analysis_running):
            refresh_analysis()
    
    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5 min)", value=False)
    if auto_refresh:
        # This would need to be implemented with st.rerun() and timer logic
        st.sidebar.info("Auto-refresh enabled")

def run_analysis():
    """Run full analysis"""
    if not st.session_state.coordinator:
        st.error("System not initialized")
        return
    
    st.session_state.analysis_running = True
    
    try:
        with st.spinner("Running full analysis... This may take a few minutes."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Update progress
            status_text.text("Initializing analysis...")
            progress_bar.progress(10)
            
            # Run analysis
            results = st.session_state.coordinator.run_full_analysis()
            progress_bar.progress(50)
            
            status_text.text("Processing results...")
            progress_bar.progress(80)
            
            st.session_state.last_analysis = results
            progress_bar.progress(100)
            
            status_text.text("Analysis complete!")
            time.sleep(1)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            if results.get('status') == 'completed':
                st.success("Analysis completed successfully!")
                
                # Show warnings if any
                warnings = results.get('warnings', [])
                if warnings:
                    for warning in warnings:
                        st.warning(warning)
            else:
                st.error("Analysis failed. Check system status.")
                
                # Show errors
                errors = results.get('errors', [])
                if errors:
                    for error in errors:
                        st.error(error)
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        st.error(traceback.format_exc())
    
    finally:
        st.session_state.analysis_running = False
        st.rerun()

def refresh_analysis():
    """Refresh current analysis"""
    run_analysis()

def main():
    """Main application function"""
    st.title("🚨 Event Situational Awareness Dashboard")
    st.markdown("*Real-time AI-powered event monitoring and analysis*")
    
    # Initialize system
    if not initialize_coordinator():
        st.error("Failed to initialize the system. Please check your configuration.")
        st.stop()
    
    # Render control panel
    render_control_panel()
    
    # Render system status
    render_system_status()
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🏢 Zones", "❓ Query"])
    
    with tab1:
        render_summary_panel()
    
    with tab2:
        render_zone_cards()
    
    with tab3:
        render_query_interface()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8em;'>"
        f"Event Situational Awareness System v1.0 | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()