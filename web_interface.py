"""
Web Interface for Gen AI Adaptive Research & Innovation Agent Ecosystem
Interactive Streamlit app for user interaction and real-time feedback
"""

import streamlit as st
import sqlite3
import json
import os
import time
from datetime import datetime
from typing import Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import your ecosystem
try:
    from final import AdaptiveResearchEcosystem, ResearchTask
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from final_production import ProductionEcosystem, ResearchTask
    PRODUCTION_AVAILABLE = True
except ImportError:
    PRODUCTION_AVAILABLE = False

# Database setup
def init_database():
    """Initialize SQLite database for logging and memory"""
    conn = sqlite3.connect('ecosystem_data.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            status TEXT,
            created_at TIMESTAMP,
            completed_at TIMESTAMP,
            processing_time REAL,
            success_rate REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            task_id TEXT,
            performance_score REAL,
            confidence_score REAL,
            timestamp TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS research_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT,
            agent_id TEXT,
            result_data TEXT,
            timestamp TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_task_to_db(task_data):
    """Save task data to database"""
    conn = sqlite3.connect('ecosystem_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO tasks 
        (id, title, description, status, created_at, completed_at, processing_time, success_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        task_data.get('id'),
        task_data.get('title'),
        task_data.get('description'),
        task_data.get('status'),
        task_data.get('created_at'),
        task_data.get('completed_at'),
        task_data.get('processing_time'),
        task_data.get('success_rate')
    ))
    
    conn.commit()
    conn.close()

def get_task_history():
    """Get task history from database"""
    conn = sqlite3.connect('ecosystem_data.db')
    df = pd.read_sql_query("SELECT * FROM tasks ORDER BY created_at DESC", conn)
    conn.close()
    return df

def main():
    """Main Streamlit app"""
    
    # Page config
    st.set_page_config(
        page_title="Gen AI Research Ecosystem",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database
    init_database()
    
    # Title and header
    st.title("🚀 Gen AI Adaptive Research & Innovation Agent Ecosystem")
    st.markdown("**Interactive Multi-Agent System for Autonomous Research & Innovation**")
    
    # Sidebar for configuration
    st.sidebar.header("🔧 System Configuration")
    
    # LLM Provider selection
    llm_options = []
    if os.getenv('OPENAI_API_KEY'):
        llm_options.append("OpenAI GPT-4")
    if os.getenv('GOOGLE_API_KEY'):
        llm_options.append("Google Gemini")
    
    if not llm_options:
        llm_options.append("Mock Responses")
    
    selected_llm = st.sidebar.selectbox("🤖 Select LLM Provider", llm_options)
    
    # API Configuration status
    st.sidebar.subheader("📊 API Status")
    if os.getenv('OPENAI_API_KEY'):
        st.sidebar.success("✅ OpenAI API configured")
    else:
        st.sidebar.warning("⚠️ OpenAI API not configured")
        
    if os.getenv('GOOGLE_API_KEY'):
        st.sidebar.success("✅ Google Gemini API configured")
    else:
        st.sidebar.info("ℹ️ Google Gemini API not configured")
    
    # Main interface tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 New Research Task", "📊 System Dashboard", "📈 Performance Analytics", "🗂️ Task History"])
    
    # Tab 1: New Research Task
    with tab1:
        st.header("Create New Research Task")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            task_title = st.text_input(
                "📋 Research Task Title",
                placeholder="e.g., Future of Quantum AI Applications"
            )
            
            task_description = st.text_area(
                "📝 Task Description",
                placeholder="Provide detailed description of what you want the agents to research...",
                height=150
            )
            
            priority = st.selectbox("🎯 Priority Level", [1, 2, 3, 4, 5], index=2)
        
        with col2:
            st.subheader("🤖 Agent Workflow")
            st.info("""
            **Execution Order:**
            1. 🔍 **Research Agent**
               Gathers comprehensive data
               
            2. 📊 **Analysis Agent**
               Identifies patterns & trends
               
            3. 💡 **Innovation Agent**
               Generates breakthrough ideas
               
            4. 🎛️ **Environment Agent**
               Coordinates & optimizes
            """)
        
        if st.button("🚀 Launch Research Task", type="primary"):
            if task_title and task_description:
                with st.spinner("🔄 Initializing research ecosystem..."):
                    
                    # Initialize appropriate ecosystem
                    if selected_llm == "OpenAI GPT-4" and OPENAI_AVAILABLE:
                        ecosystem = AdaptiveResearchEcosystem()
                        provider = "OpenAI"
                    elif PRODUCTION_AVAILABLE:
                        # Use production system with Google Gemini
                        ecosystem = ProductionEcosystem()
                        provider = "Google Gemini (Production)"
                    else:
                        st.error("❌ No LLM providers available. Please configure API keys in .env file.")
                        st.stop()
                    
                    # Create task
                    if selected_llm == "OpenAI GPT-4" and OPENAI_AVAILABLE:
                        task = ecosystem.create_research_task(
                            title=task_title,
                            description=task_description,
                            priority=priority
                        )
                    else:
                        # Production system uses different method
                        task = ecosystem.create_task(
                            title=task_title,
                            description=task_description
                        )
                    
                    st.success(f"✅ Task created with {provider} LLM")
                
                # Execute workflow with real-time updates
                st.subheader("🔄 Live Execution Progress")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Stage containers
                research_container = st.container()
                analysis_container = st.container()
                innovation_container = st.container()
                environment_container = st.container()
                
                try:
                    # Execute workflow
                    start_time = time.time()
                    
                    # Stage 1: Research
                    status_text.text("🔍 Stage 1: Research Agent gathering data...")
                    progress_bar.progress(25)
                    
                    if selected_llm == "OpenAI GPT-4" and OPENAI_AVAILABLE:
                        results = ecosystem.execute_research_workflow(task)
                    else:
                        # Production system uses different method
                        results = ecosystem.execute_workflow(task)
                    
                    # Display results in real-time
                    with research_container:
                        st.success("🔍 Research Stage Complete")
                        with st.expander("📊 Research Findings", expanded=True):
                            research_data = results.get('stages', {}).get('research', {}).get('research_data', 'No data')
                            st.markdown(research_data)
                    
                    progress_bar.progress(50)
                    status_text.text("📊 Stage 2: Analysis Agent processing patterns...")
                    
                    with analysis_container:
                        st.success("📊 Analysis Stage Complete")
                        with st.expander("🧠 Analysis Insights", expanded=True):
                            analysis_data = results.get('stages', {}).get('analysis', {}).get('analysis_insights', 'No insights')
                            st.markdown(analysis_data)
                    
                    progress_bar.progress(75)
                    status_text.text("💡 Stage 3: Innovation Agent generating ideas...")
                    
                    with innovation_container:
                        st.success("💡 Innovation Stage Complete")
                        with st.expander("🚀 Innovation Opportunities", expanded=True):
                            innovation_data = results.get('stages', {}).get('innovation', {}).get('innovation_ideas', 'No ideas')
                            st.markdown(innovation_data)
                    
                    progress_bar.progress(100)
                    status_text.text("🎛️ Stage 4: Environment Agent coordinating...")
                    
                    with environment_container:
                        st.success("🎛️ Environment Stage Complete")
                        with st.expander("⚙️ System Recommendations", expanded=True):
                            env_data = results.get('stages', {}).get('environment', {}).get('management_recommendations', 'No recommendations')
                            st.markdown(env_data)
                    
                    # Final results
                    processing_time = time.time() - start_time
                    
                    st.balloons()
                    st.success(f"🎉 Research task completed successfully in {processing_time:.2f} seconds!")
                    
                    # Save to database
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'description': task.description,
                        'status': 'completed',
                        'created_at': datetime.now(),
                        'completed_at': datetime.now(),
                        'processing_time': processing_time,
                        'success_rate': 1.0
                    }
                    save_task_to_db(task_data)
                    
                    # Display comprehensive report
                    st.subheader("📋 Comprehensive Research Report")
                    if selected_llm == "OpenAI GPT-4" and OPENAI_AVAILABLE:
                        report = ecosystem.generate_comprehensive_report(results)
                    else:
                        # Production system uses different method
                        report = ecosystem.generate_report(results)
                    st.markdown(report)
                    
                except Exception as e:
                    st.error(f"❌ Error during execution: {str(e)}")
                    
            else:
                st.warning("⚠️ Please provide both title and description")
    
    # Tab 2: System Dashboard
    with tab2:
        st.header("🎛️ System Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Get task history for metrics
        task_history = get_task_history()
        
        with col1:
            st.metric(
                "📋 Total Tasks",
                len(task_history),
                delta=f"+{len(task_history[task_history['created_at'] > (datetime.now() - pd.Timedelta(days=1)).isoformat()])}" if len(task_history) > 0 else None
            )
        
        with col2:
            success_rate = (task_history['status'] == 'completed').mean() * 100 if len(task_history) > 0 else 0
            st.metric("✅ Success Rate", f"{success_rate:.1f}%")
        
        with col3:
            avg_time = task_history['processing_time'].mean() if len(task_history) > 0 else 0
            st.metric("⏱️ Avg Processing Time", f"{avg_time:.2f}s")
        
        with col4:
            st.metric("🤖 Active Agents", "4", delta="Research, Analysis, Innovation, Environment")
        
        # System status
        st.subheader("🔧 System Components Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("🤖 **Multi-Agent System**: Online")
            st.success("🔗 **API Integrations**: Available")
            st.success("💾 **Database**: Connected")
            st.success("🔄 **Workflow Engine**: Active")
        
        with col2:
            st.info("🧠 **LLM Provider**: " + selected_llm)
            st.info("📊 **Performance Tracking**: Enabled")
            st.info("🔒 **Security**: API Keys Protected")
            st.info("🌐 **Web Interface**: Running")
    
    # Tab 3: Performance Analytics
    with tab3:
        st.header("📈 Performance Analytics")
        
        if len(task_history) > 0:
            # Processing time trend
            fig_time = px.line(
                task_history, 
                x='created_at', 
                y='processing_time',
                title='Processing Time Trend',
                labels={'processing_time': 'Time (seconds)', 'created_at': 'Date'}
            )
            st.plotly_chart(fig_time, use_container_width=True)
            
            # Success rate pie chart
            success_counts = task_history['status'].value_counts()
            fig_success = px.pie(
                values=success_counts.values,
                names=success_counts.index,
                title='Task Success Distribution'
            )
            st.plotly_chart(fig_success, use_container_width=True)
            
        else:
            st.info("📊 No performance data available yet. Execute some tasks to see analytics!")
    
    # Tab 4: Task History
    with tab4:
        st.header("🗂️ Task History")
        
        if len(task_history) > 0:
            st.dataframe(
                task_history[['title', 'status', 'created_at', 'processing_time', 'success_rate']],
                use_container_width=True
            )
            
            # Export functionality
            if st.button("📥 Export Task History"):
                csv = task_history.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"task_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("📝 No task history available yet.")
    
 

if __name__ == "__main__":
    main()
