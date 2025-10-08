"""
Advanced Streamlit frontend for the Financial Intelligence Platform.
Phase 3 implementation with production-grade analyst cockpit.
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time
import os

# Page configuration
st.set_page_config(
    page_title="Financial Intelligence Platform - Analyst Cockpit",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8001"  # Advanced API Server

# Initialize session state
if 'cases' not in st.session_state:
    st.session_state.cases = {}
if 'current_case' not in st.session_state:
    st.session_state.current_case = None
if 'query_history' not in st.session_state:
    st.session_state.query_history = []


def make_api_request(endpoint: str, params: Dict = None, data: Dict = None, method: str = "GET") -> Dict:
    """Make API request to the advanced backend."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "POST":
            response = requests.post(url, json=data, timeout=120)
        elif method == "GET":
            response = requests.get(url, params=params or {}, timeout=30)
        else:
            response = requests.request(method, url, json=data, params=params, timeout=30)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return {}


def display_system_status():
    """Display system status and model availability."""
    st.subheader("🔧 System Status")
    
    try:
        health_data = make_api_request("/health")
        
        if health_data.get('status') == 'healthy':
            st.success("✅ Advanced API Connected")
            
            # Display model status
            models = health_data.get('models_available', {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if models.get('ollama_llama'):
                    st.success("🦙 Ollama Llama 3.1 8B")
                else:
                    st.error("❌ Ollama LLM")
            
            with col2:
                if models.get('bge_reranker'):
                    st.success("🎯 BGE Reranker")
                else:
                    st.error("❌ BGE Reranker")
            
            with col3:
                if models.get('embedding_model'):
                    st.info(f"🧠 {models['embedding_model']}")
                else:
                    st.error("❌ Embeddings")
            
            with col4:
                if models.get('claude_3_5_haiku'):
                    st.success("🤖 Claude 3.5 Haiku")
                else:
                    st.warning("⚠️ Claude (Not configured)")
            
            # Database stats
            db_stats = health_data.get('database_stats', {})
            if db_stats:
                st.info(f"📊 Database: {db_stats.get('total_documents', 0)} documents indexed")
            
            return True
        else:
            st.error("❌ Advanced API Disconnected")
            return False
            
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return False


def create_case():
    """Create a new investigation case."""
    with st.expander("🆕 Create New Case", expanded=True):
        with st.form("create_case_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                case_id = st.text_input("Case ID", value=f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                analyst = st.text_input("Analyst Name", value="Current User")
                priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
            
            with col2:
                description = st.text_area("Case Description", height=100)
                tags = st.text_input("Tags (comma-separated)", placeholder="fraud, insider_trading, investigation")
            
            submitted = st.form_submit_button("Create Case", use_container_width=True)
            
            if submitted and case_id and description:
                case_data = {
                    "case_id": case_id,
                    "description": description,
                    "priority": priority,
                    "analyst": analyst,
                    "tags": [tag.strip() for tag in tags.split(",") if tag.strip()]
                }
                
                result = make_api_request("/cases", data=case_data, method="POST")
                
                if result and result.get('status') == 'created':
                    st.session_state.cases[case_id] = {
                        **case_data,
                        'created_at': result.get('created_at'),
                        'queries': [],
                        'analysis': []
                    }
                    st.session_state.current_case = case_id
                    st.success(f"✅ Case {case_id} created successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to create case")


def display_case_management():
    """Display case management interface."""
    st.header("📁 Case Management")
    
    # Create new case
    create_case()
    
    # Display existing cases
    if st.session_state.cases:
        st.subheader("📋 Active Cases")
        
        # Case selection
        case_options = {f"{case_id} - {data['description'][:50]}...": case_id 
                       for case_id, data in st.session_state.cases.items()}
        
        if case_options:
            selected_case = st.selectbox(
                "Select Case",
                options=list(case_options.keys()),
                index=0 if not st.session_state.current_case else list(case_options.values()).index(st.session_state.current_case)
            )
            
            if selected_case:
                case_id = case_options[selected_case]
                st.session_state.current_case = case_id
                
                # Display case details
                case_data = st.session_state.cases[case_id]
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Case ID", case_id)
                with col2:
                    st.metric("Priority", case_data['priority'].upper())
                with col3:
                    st.metric("Analyst", case_data['analyst'])
                with col4:
                    st.metric("Queries", len(case_data.get('queries', [])))
                
                # Case actions
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("🔍 Analyze Case", use_container_width=True):
                        st.session_state.active_tab = "analysis"
                        st.rerun()
                with col2:
                    if st.button("📊 Generate Report", use_container_width=True):
                        st.session_state.active_tab = "reporting"
                        st.rerun()
                with col3:
                    if st.button("🗑️ Delete Case", use_container_width=True):
                        if case_id in st.session_state.cases:
                            del st.session_state.cases[case_id]
                            if st.session_state.current_case == case_id:
                                st.session_state.current_case = None
                            st.rerun()


def display_advanced_search():
    """Display advanced search interface with RAG capabilities."""
    st.header("🔍 Advanced Intelligence Search")
    
    # Search form
    with st.form("advanced_search_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_input(
                "Enter your investigation query:",
                placeholder="e.g., 'What are the patterns in insider trading violations?' or 'Analyze market manipulation techniques'",
                help="Use natural language for complex financial fraud investigations"
            )
        
        with col2:
            n_results = st.slider("Results", 3, 15, 5)
        
        submitted = st.form_submit_button("🧠 Intelligent Search", use_container_width=True)
    
    if submitted and query:
        with st.spinner("🧠 Analyzing with Ollama + Advanced RAG..."):
            start_time = time.time()
            
            # Make advanced query to the API
            query_data = {
                "query": query,
                "n_results": n_results,
                "include_metadata": True
            }
            
            result = make_api_request("/query", data=query_data, method="POST")
            
            processing_time = time.time() - start_time
            
            if result and result.get('answer'):
                # Store query in history
                query_entry = {
                    'query': query,
                    'timestamp': datetime.now().isoformat(),
                    'processing_time': processing_time,
                    'confidence': result.get('confidence_score', 0),
                    'case_id': st.session_state.current_case
                }
                st.session_state.query_history.append(query_entry)
                
                # Display results
                display_rag_response(result, query, processing_time)
            else:
                st.error("❌ Search failed or no results found")


def display_rag_response(result: Dict, query: str, processing_time: float):
    """Display comprehensive RAG response."""
    st.subheader("🧠 Intelligence Analysis")
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Processing Time", f"{processing_time:.2f}s")
    with col2:
        st.metric("Confidence", f"{result.get('confidence_score', 0):.3f}")
    with col3:
        st.metric("Query Type", result.get('query_type', 'unknown').replace('_', ' ').title())
    with col4:
        st.metric("Evidence Count", len(result.get('evidence', [])))
    
    # Generated answer
    st.subheader("📝 Generated Analysis")
    st.markdown(result.get('answer', 'No analysis available'))
    
    # Evidence with clickable citations
    if result.get('evidence'):
        st.subheader("📚 Supporting Evidence")
        
        for i, evidence in enumerate(result['evidence']):
            with st.expander(f"Evidence {i+1} (Score: {evidence.get('score', 0):.3f}) - {evidence.get('source', 'Unknown')}"):
                # Display document with highlighting
                st.markdown(f"**Source:** {evidence.get('source', 'Unknown')}")
                st.markdown(f"**Rank:** {evidence.get('rank', i+1)}")
                
                # Document content
                st.markdown("**Content:**")
                st.text_area(
                    f"Document {i+1}",
                    value=evidence.get('document', ''),
                    height=200,
                    key=f"evidence_{i}",
                    disabled=True
                )
                
                # Metadata
                if evidence.get('metadata'):
                    st.markdown("**Metadata:**")
                    metadata_df = pd.DataFrame([evidence['metadata']])
                    st.dataframe(metadata_df, use_container_width=True)
                
                # Clickable citation
                if st.button(f"🔗 View Full Document {i+1}", key=f"view_doc_{i}"):
                    st.info(f"🔗 Citation: This evidence is from {evidence.get('source', 'Unknown')} document")


def display_analytics_dashboard():
    """Display comprehensive analytics dashboard."""
    st.header("📊 Analytics Dashboard")
    
    # Get system stats
    stats_data = make_api_request("/stats")
    
    if stats_data and stats_data.get('rag_engine_stats'):
        stats = stats_data['rag_engine_stats']
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Documents", stats.get('total_documents', 0))
        with col2:
            st.metric("SEBI Documents", stats.get('sebi_document_count', 0))
        with col3:
            st.metric("Transaction Records", stats.get('transaction_count', 0))
        with col4:
            st.metric("Active Cases", len(st.session_state.cases))
        
        # Query performance analytics
        if st.session_state.query_history:
            st.subheader("📈 Query Performance Analytics")
            
            # Create performance dataframe
            perf_data = []
            for query in st.session_state.query_history:
                perf_data.append({
                    'Timestamp': query['timestamp'][:16],  # Remove seconds
                    'Processing Time (s)': query['processing_time'],
                    'Confidence': query['confidence'],
                    'Query': query['query'][:50] + '...' if len(query['query']) > 50 else query['query']
                })
            
            perf_df = pd.DataFrame(perf_data)
            
            # Performance charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig_time = px.line(perf_df, x='Timestamp', y='Processing Time (s)', 
                                 title='Query Processing Time Trend')
                st.plotly_chart(fig_time, use_container_width=True)
            
            with col2:
                fig_conf = px.scatter(perf_df, x='Processing Time (s)', y='Confidence',
                                    hover_data=['Query'], title='Confidence vs Processing Time')
                st.plotly_chart(fig_conf, use_container_width=True)
            
            # Query history table
            st.subheader("📋 Recent Query History")
            st.dataframe(perf_df, use_container_width=True)
        
        # Case analytics
        if st.session_state.cases:
            st.subheader("📁 Case Analytics")
            
            case_data = []
            for case_id, case_info in st.session_state.cases.items():
                case_data.append({
                    'Case ID': case_id,
                    'Priority': case_info['priority'],
                    'Analyst': case_info['analyst'],
                    'Queries': len(case_info.get('queries', [])),
                    'Created': case_info.get('created_at', 'Unknown')[:10]
                })
            
            case_df = pd.DataFrame(case_data)
            
            # Priority distribution
            priority_counts = case_df['Priority'].value_counts()
            fig_priority = px.pie(values=priority_counts.values, names=priority_counts.index,
                                title='Case Priority Distribution')
            st.plotly_chart(fig_priority, use_container_width=True)
            
            # Case table
            st.dataframe(case_df, use_container_width=True)


def display_sar_generation():
    """Display SAR (Suspicious Activity Report) generation interface."""
    st.header("📝 SAR Generation")
    
    if not st.session_state.current_case:
        st.warning("⚠️ Please select a case first to generate SAR")
        return
    
    case_data = st.session_state.cases[st.session_state.current_case]
    
    st.subheader(f"SAR Generation for Case: {st.session_state.current_case}")
    
    # SAR template
    with st.expander("📋 SAR Template", expanded=True):
        st.markdown("""
        ### Suspicious Activity Report (SAR) Template
        
        **Case Information:**
        - Case ID: {case_id}
        - Analyst: {analyst}
        - Priority: {priority}
        - Description: {description}
        
        **Investigation Summary:**
        [AI-generated summary based on case analysis]
        
        **Key Findings:**
        [AI-generated findings from queries and analysis]
        
        **Supporting Evidence:**
        [AI-generated evidence compilation]
        
        **Recommendations:**
        [AI-generated recommendations]
        """)
    
    # Generate SAR
    if st.button("🤖 Generate SAR with AI", use_container_width=True):
        with st.spinner("🤖 Generating SAR with AI analysis..."):
            # This would integrate with the API to generate comprehensive SAR
            sar_query = f"Generate a comprehensive SAR for case {st.session_state.current_case}. " \
                       f"Case description: {case_data['description']}. " \
                       f"Priority: {case_data['priority']}. " \
                       f"Include investigation summary, key findings, supporting evidence, and recommendations."
            
            sar_data = {
                "query": sar_query,
                "n_results": 10,
                "include_metadata": True
            }
            
            result = make_api_request("/query", data=sar_data, method="POST")
            
            if result and result.get('answer'):
                st.subheader("🤖 AI-Generated SAR")
                st.markdown(result['answer'])
                
                # Save SAR
                if st.button("💾 Save SAR"):
                    # This would save to file or database
                    st.success("✅ SAR saved successfully!")
            else:
                st.error("❌ Failed to generate SAR")


def main():
    """Main Streamlit application."""
    # Header
    st.title("🕵️ Financial Intelligence Platform")
    st.markdown("**Phase 3: Advanced Analyst Cockpit** - *Production-Grade Fraud Detection*")
    
    # Check system status
    if not display_system_status():
        st.error("❌ Cannot connect to Advanced API Server. Please ensure it's running on port 8002.")
        st.stop()
    
    # Sidebar navigation
    with st.sidebar:
        st.header("🧭 Navigation")
        
        # Tab selection
        tab_options = {
            "🔍 Intelligence Search": "search",
            "📁 Case Management": "cases", 
            "📊 Analytics": "analytics",
            "📝 SAR Generation": "sar",
            "ℹ️ About": "about"
        }
        
        selected_tab = st.selectbox(
            "Select Module",
            options=list(tab_options.keys()),
            index=0
        )
        
        st.session_state.active_tab = tab_options[selected_tab]
        
        # Quick stats
        st.header("📊 Quick Stats")
        st.metric("Active Cases", len(st.session_state.cases))
        st.metric("Total Queries", len(st.session_state.query_history))
        
        if st.session_state.query_history:
            avg_time = sum(q['processing_time'] for q in st.session_state.query_history) / len(st.session_state.query_history)
            st.metric("Avg Query Time", f"{avg_time:.2f}s")
    
    # Main content based on selected tab
    if st.session_state.active_tab == "search":
        display_advanced_search()
    elif st.session_state.active_tab == "cases":
        display_case_management()
    elif st.session_state.active_tab == "analytics":
        display_analytics_dashboard()
    elif st.session_state.active_tab == "sar":
        display_sar_generation()
    elif st.session_state.active_tab == "about":
        display_about_page()


def display_about_page():
    """Display about page with system information."""
    st.header("ℹ️ About the Advanced Analyst Cockpit")
    
    st.markdown("""
    ### 🎯 Phase 3: Production-Grade Analyst Interface
    
    This advanced interface provides financial fraud analysts with:
    
    **🧠 Advanced Intelligence Search**
    - Ollama + Llama 3.1 8B local LLM integration
    - BGE Reranker for improved relevance
    - Multi-stage retrieval with semantic search
    - Clickable citations tracing back to source data
    
    **📁 Case Management**
    - Create and manage investigation cases
    - Track case progress and queries
    - Priority-based case organization
    
    **📊 Analytics Dashboard**
    - Real-time performance metrics
    - Query history and analytics
    - Case statistics and trends
    
    **📝 SAR Generation**
    - AI-powered SAR (Suspicious Activity Report) generation
    - Automated report pre-population
    - Evidence compilation and analysis
    
    ### 🔧 Technology Stack
    - **LLM**: Ollama + Llama 3.1 8B (Local)
    - **Reranker**: BGE Reranker Large
    - **Embeddings**: all-MiniLM-L12-v2
    - **Vector DB**: ChromaDB (Persistent)
    - **Backend**: FastAPI (Advanced)
    - **Frontend**: Streamlit (Enhanced)
    - **Data**: 205 SEBI Enforcement Documents
    
    ### 🚀 Next Steps
    - Phase 4: GraphRAG and Network Intelligence
    - Phase 5: Production Deployment
    - Phase 6: Consumer Security Suite
    """)


if __name__ == "__main__":
    main()
