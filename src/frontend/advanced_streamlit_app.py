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
API_KEY = "dev-api-key"  # Default API key for development

# Initialize session state
if 'cases' not in st.session_state:
    st.session_state.cases = {}
if 'current_case' not in st.session_state:
    st.session_state.current_case = None
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = API_KEY


def make_api_request(endpoint: str, params: Dict = None, data: Dict = None, method: str = "GET") -> Dict:
    """Make API request to the advanced backend with API key authentication."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {"X-API-Key": st.session_state.api_key}
        
        if method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=120)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        elif method == "GET":
            response = requests.get(url, params=params or {}, headers=headers, timeout=30)
        else:
            response = requests.request(method, url, json=data, params=params, headers=headers, timeout=30)
        
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


def load_cases_from_api():
    """Load cases from API."""
    result = make_api_request("/cases")
    if result and 'cases' in result:
        return result['cases']
    return []


def display_case_management():
    """Display case management interface."""
    st.header("📁 Case Management")
    
    # Create new case
    create_case()
    
    # Load cases from API
    cases = load_cases_from_api()
    
    # Display existing cases
    if cases:
        st.subheader("📋 Active Cases")
        
        # Case selection
        case_options = {f"{case['case_id']} - {case['description'][:50]}...": case['case_id'] 
                       for case in cases}
        
        if case_options:
            selected_case = st.selectbox(
                "Select Case",
                options=list(case_options.keys()),
                index=0
            )
            
            if selected_case:
                case_id = case_options[selected_case]
                st.session_state.current_case = case_id
                
                # Get detailed case data from API
                case_result = make_api_request(f"/cases/{case_id}")
                
                if case_result:
                    case_data = case_result
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Case ID", case_id)
                    with col2:
                        st.metric("Priority", case_data.get('priority', 'N/A').upper())
                    with col3:
                        st.metric("Analyst", case_data.get('analyst', 'N/A'))
                    with col4:
                        st.metric("Queries", case_data.get('query_count', 0))
                    
                    # Display case details
                    with st.expander("📋 Case Details", expanded=True):
                        st.write(f"**Description:** {case_data.get('description', 'N/A')}")
                        st.write(f"**Status:** {case_data.get('status', 'N/A')}")
                        st.write(f"**Created:** {case_data.get('created_at', 'N/A')}")
                        st.write(f"**Tags:** {', '.join(case_data.get('tags', []))}")
                    
                    # Display query history
                    if case_data.get('queries'):
                        with st.expander(f"📜 Query History ({len(case_data['queries'])} queries)", expanded=False):
                            for query in case_data['queries']:
                                st.markdown(f"**Query:** {query.get('query', 'N/A')}")
                                st.markdown(f"**Confidence:** {query.get('confidence_score', 0):.3f}")
                                st.markdown(f"**Time:** {query.get('timestamp', 'N/A')}")
                                st.divider()
                    
                    # Case actions
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🔍 Analyze Case", use_container_width=True):
                            st.session_state.active_tab = "search"
                            st.rerun()
                    with col2:
                        if st.button("📊 Generate SAR", use_container_width=True):
                            st.session_state.active_tab = "sar"
                            st.rerun()
                    with col3:
                        if st.button("🗑️ Delete Case", use_container_width=True, type="secondary"):
                            # Delete case via API
                            delete_result = make_api_request(f"/cases/{case_id}", method="DELETE")
                            if delete_result:
                                st.success(f"✅ {delete_result.get('message', 'Case deleted')}")
                                st.session_state.current_case = None
                                time.sleep(1)
                                st.rerun()
    else:
        st.info("📝 No cases found. Create a new case to get started!")


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
        st.subheader("📚 Supporting Evidence & Citations")
        
        # Create citation reference list
        st.markdown("**Quick Citation Links:**")
        citation_cols = st.columns(min(len(result['evidence']), 5))
        for i, evidence in enumerate(result['evidence'][:5]):
            with citation_cols[i]:
                if st.button(f"[{i+1}]", key=f"cite_link_{i}", help=f"Jump to Evidence {i+1}"):
                    st.session_state[f'expanded_evidence_{i}'] = True
        
        st.divider()
        
        for i, evidence in enumerate(result['evidence']):
            # Determine if this evidence should be expanded
            is_expanded = st.session_state.get(f'expanded_evidence_{i}', i == 0)
            
            # Create enhanced evidence card
            with st.expander(
                f"📄 Evidence [{i+1}] - Relevance: {evidence.get('score', 0):.1%} - Source: {evidence.get('source', 'Unknown').replace('_', ' ').title()}", 
                expanded=is_expanded
            ):
                # Source attribution
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    source_type = evidence.get('source', 'unknown')
                    if 'sebi' in source_type.lower():
                        st.markdown("🏛️ **Source:** SEBI Regulatory Document")
                    elif 'transaction' in source_type.lower():
                        st.markdown("💳 **Source:** Transaction Data")
                    else:
                        st.markdown(f"📂 **Source:** {source_type}")
                with col2:
                    st.markdown(f"**Rank:** #{evidence.get('rank', i+1)}")
                with col3:
                    st.markdown(f"**Score:** {evidence.get('score', 0):.3f}")
                
                # Document content in a highlighted box
                st.markdown("**📝 Evidence Content:**")
                st.info(evidence.get('document', 'No content available'))
                
                # Metadata in structured format
                if evidence.get('metadata'):
                    st.markdown("**🔍 Document Metadata:**")
                    metadata = evidence['metadata']
                    
                    # Display key metadata fields
                    meta_col1, meta_col2 = st.columns(2)
                    
                    with meta_col1:
                        if metadata.get('title'):
                            st.markdown(f"**Title:** {metadata['title']}")
                        if metadata.get('document_type'):
                            st.markdown(f"**Type:** {metadata['document_type']}")
                        if metadata.get('violation_types'):
                            st.markdown(f"**Violations:** {metadata['violation_types']}")
                    
                    with meta_col2:
                        if metadata.get('date'):
                            st.markdown(f"**Date:** {metadata['date']}")
                        if metadata.get('entities'):
                            st.markdown(f"**Entities:** {metadata['entities']}")
                        if metadata.get('keywords'):
                            st.markdown(f"**Keywords:** {metadata['keywords']}")
                    
                    # Full metadata expander
                    with st.expander("View Full Metadata", expanded=False):
                        st.json(metadata)
                
                # Citation action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"📋 Copy Citation", key=f"copy_{i}", use_container_width=True):
                        citation_text = f"[{i+1}] {evidence.get('source', 'Unknown')} - Score: {evidence.get('score', 0):.3f}"
                        st.code(citation_text, language=None)
                with col2:
                    if st.button(f"🔗 Trace Source", key=f"trace_{i}", use_container_width=True):
                        st.success(f"✅ Source traced: {evidence.get('source', 'Unknown')}")
                with col3:
                    if metadata.get('url'):
                        st.link_button(f"🌐 View Original", metadata['url'], use_container_width=True)
                    else:
                        st.button(f"🌐 View Original", disabled=True, use_container_width=True)


def display_analytics_dashboard():
    """Display comprehensive analytics dashboard."""
    st.header("📊 Analytics Dashboard")
    
    # Get system stats
    stats_data = make_api_request("/stats")
    
    if stats_data and stats_data.get('rag_engine_stats'):
        stats = stats_data['rag_engine_stats']
        case_stats = stats.get('case_statistics', {})
        
        # Key System Metrics
        st.subheader("🎯 System Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Documents", stats.get('total_documents', 0))
        with col2:
            st.metric("SEBI Documents", stats.get('sebi_document_count', 0))
        with col3:
            st.metric("Transaction Records", stats.get('transaction_count', 0))
        with col4:
            st.metric("Total Cases", case_stats.get('total_cases', 0))
        
        # Case Management Metrics
        if case_stats:
            st.subheader("📁 Case Management Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Active Cases", case_stats.get('active_cases', 0), 
                         delta=None, delta_color="normal")
            with col2:
                st.metric("Closed Cases", case_stats.get('closed_cases', 0))
            with col3:
                st.metric("Total Queries", case_stats.get('total_queries', 0))
            with col4:
                avg_queries = case_stats.get('average_queries_per_case', 0)
                st.metric("Avg Queries/Case", f"{avg_queries:.1f}")
            
            # Priority breakdown
            if case_stats.get('priority_breakdown'):
                st.subheader("⚡ Case Priority Distribution")
                priority_data = case_stats['priority_breakdown']
                
                # Create pie chart
                fig_priority = go.Figure(data=[go.Pie(
                    labels=list(priority_data.keys()),
                    values=list(priority_data.values()),
                    hole=0.3,
                    marker=dict(colors=['#FF6B6B', '#FFA500', '#FFD700', '#90EE90'])
                )])
                fig_priority.update_layout(
                    title="Cases by Priority Level",
                    height=400
                )
                st.plotly_chart(fig_priority, use_container_width=True)
        
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
    
    case_id = st.session_state.current_case
    
    # Get case data from API
    case_result = make_api_request(f"/cases/{case_id}")
    
    if not case_result:
        st.error("❌ Failed to load case data")
        return
    
    case_data = case_result
    
    st.subheader(f"SAR Generation for Case: {case_id}")
    
    # Display case summary
    with st.expander("📋 Case Summary", expanded=True):
        st.write(f"**Case ID:** {case_id}")
        st.write(f"**Description:** {case_data.get('description', 'N/A')}")
        st.write(f"**Priority:** {case_data.get('priority', 'N/A')}")
        st.write(f"**Analyst:** {case_data.get('analyst', 'N/A')}")
        st.write(f"**Status:** {case_data.get('status', 'N/A')}")
        st.write(f"**Queries Performed:** {case_data.get('query_count', 0)}")
    
    # Load existing SAR reports
    sar_reports_result = make_api_request(f"/cases/{case_id}/sar")
    existing_reports = sar_reports_result.get('reports', []) if sar_reports_result else []
    
    # Display existing reports
    if existing_reports:
        st.subheader(f"📄 Existing SAR Reports ({len(existing_reports)})")
        
        for i, report in enumerate(existing_reports):
            with st.expander(f"Report #{i+1} - {report.get('status', 'draft').upper()} - {report.get('generated_at', 'N/A')[:16]}", expanded=False):
                st.markdown(report.get('report_content', 'No content'))
                st.write(f"**Generated by:** {report.get('analyst', 'N/A')}")
                st.write(f"**Status:** {report.get('status', 'draft')}")
    
    st.divider()
    
    # Generate new SAR
    st.subheader("🤖 Generate New SAR")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🤖 Generate SAR with AI", use_container_width=True, type="primary"):
            with st.spinner("🤖 Generating comprehensive SAR with AI analysis... This may take a minute."):
                # Call SAR generation API endpoint
                sar_result = make_api_request(f"/cases/{case_id}/sar", method="POST")
                
                if sar_result and sar_result.get('report_content'):
                    st.success("✅ SAR Generated Successfully!")
                    
                    st.subheader("🤖 AI-Generated SAR Report")
                    st.markdown("---")
                    st.markdown(sar_result['report_content'])
                    st.markdown("---")
                    
                    # Display metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Confidence", f"{sar_result.get('confidence', 0):.3f}")
                    with col2:
                        st.metric("SAR ID", sar_result.get('sar_id', 'N/A'))
                    with col3:
                        st.metric("Status", sar_result.get('status', 'draft').upper())
                    
                    # Download option
                    st.download_button(
                        label="💾 Download SAR Report",
                        data=sar_result['report_content'],
                        file_name=f"SAR_{case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Failed to generate SAR")
    
    with col2:
        st.info("💡 **Tip:** The AI will analyze all case queries and evidence to generate a comprehensive SAR report.")


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
