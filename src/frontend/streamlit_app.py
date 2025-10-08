"""
Streamlit frontend for the Financial Intelligence Platform.
Phase 1 implementation with basic RAG search interface.
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Financial Intelligence Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"


def make_api_request(endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
    """Make API request to the backend."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if data:
            response = requests.post(url, json=data)
        else:
            response = requests.get(url, params=params or {})
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return {}


def display_search_results(results: Dict[str, List[Dict[str, Any]]], query: str):
    """Display search results in a formatted way."""
    st.subheader(f"Search Results for: '{query}'")
    
    # Display transaction results
    if results.get('transactions'):
        st.markdown("### 💳 Transaction Data")
        for i, result in enumerate(results['transactions']):
            with st.expander(f"Transaction {i+1} (Score: {result['similarity_score']:.3f})"):
                st.write("**Document:**")
                st.write(result['document'])
                st.write("**Metadata:**")
                metadata = result['metadata']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Amount", f"${metadata.get('amount', 0):.2f}")
                with col2:
                    st.metric("Fraud", "Yes" if metadata.get('is_fraud') else "No")
                with col3:
                    st.metric("Card Type", metadata.get('card_type', 'Unknown'))
    
    # Display SEBI results
    if results.get('sebi_orders'):
        st.markdown("### 🏛️ SEBI Orders")
        for i, result in enumerate(results['sebi_orders']):
            with st.expander(f"SEBI Order {i+1} (Score: {result['similarity_score']:.3f})"):
                st.write("**Document:**")
                st.write(result['document'])
                st.write("**Metadata:**")
                metadata = result['metadata']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Entity", metadata.get('entity_name', 'Unknown'))
                with col2:
                    st.metric("Penalty", f"₹{metadata.get('penalty_amount', 0):,.2f}")
                with col3:
                    st.metric("Violation", metadata.get('violation_type', 'Unknown'))


def display_database_stats(stats: Dict[str, Any]):
    """Display database statistics."""
    st.subheader("📊 Database Statistics")
    
    if 'error' in stats:
        st.error(f"Error retrieving stats: {stats['error']}")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Transaction Records", stats.get('transaction_count', 0))
    
    with col2:
        st.metric("SEBI Orders", stats.get('sebi_count', 0))
    
    with col3:
        st.metric("Total Documents", stats.get('total_documents', 0))
    
    # Create a simple chart
    if stats.get('total_documents', 0) > 0:
        fig = go.Figure(data=[
            go.Bar(
                name='Transactions',
                x=['Transactions'],
                y=[stats.get('transaction_count', 0)],
                marker_color='lightblue'
            ),
            go.Bar(
                name='SEBI Orders',
                x=['SEBI Orders'],
                y=[stats.get('sebi_count', 0)],
                marker_color='lightcoral'
            )
        ])
        
        fig.update_layout(
            title="Document Distribution",
            xaxis_title="Collection",
            yaxis_title="Number of Documents",
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)


def main():
    """Main Streamlit application."""
    st.title("🔍 Financial Intelligence Platform")
    st.markdown("**Phase 1: RAG Proof-of-Concept Demo**")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Status
        st.subheader("API Status")
        health_data = make_api_request("/health")
        if health_data.get('status') == 'healthy':
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
            st.stop()
        
        # Database Stats
        st.subheader("Database Stats")
        stats_data = make_api_request("/stats")
        if stats_data:
            st.write(f"**Total Documents:** {stats_data.get('total_documents', 0)}")
            st.write(f"**Transactions:** {stats_data.get('transaction_count', 0)}")
            st.write(f"**SEBI Orders:** {stats_data.get('sebi_count', 0)}")
        
        # Search Options
        st.subheader("Search Options")
        collection_filter = st.selectbox(
            "Search Collection",
            ["All", "Transactions Only", "SEBI Orders Only"]
        )
        
        n_results = st.slider("Number of Results", 1, 20, 5)
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["🔍 Search", "📊 Analytics", "ℹ️ About"])
    
    with tab1:
        st.header("Semantic Search")
        st.markdown("Search through financial fraud data using natural language queries.")
        
        # Search form
        with st.form("search_form"):
            query = st.text_input(
                "Enter your search query:",
                placeholder="e.g., 'fraudulent credit card transactions' or 'insider trading violations'",
                help="Use natural language to describe what you're looking for"
            )
            
            submitted = st.form_submit_button("🔍 Search", use_container_width=True)
        
        if submitted and query:
            with st.spinner("Searching..."):
                # Determine collection filter
                collection_map = {
                    "All": None,
                    "Transactions Only": "transactions",
                    "SEBI Orders Only": "sebi_orders"
                }
                
                search_data = {
                    "query": query,
                    "n_results": n_results,
                    "collection": collection_map[collection_filter]
                }
                
                results = make_api_request("/search", data=search_data)
                
                if results:
                    display_search_results(results['results'], query)
                else:
                    st.error("No results found or API error occurred")
    
    with tab2:
        st.header("Analytics Dashboard")
        
        # Get fresh stats
        stats_data = make_api_request("/stats")
        if stats_data:
            display_database_stats(stats_data)
        else:
            st.error("Unable to retrieve analytics data")
        
        # Sample queries section
        st.subheader("💡 Sample Queries")
        st.markdown("Try these example queries to explore the system:")
        
        sample_queries = [
            "fraudulent credit card transactions",
            "high value suspicious payments",
            "insider trading violations",
            "market manipulation cases",
            "money laundering activities",
            "corporate governance issues"
        ]
        
        cols = st.columns(2)
        for i, query in enumerate(sample_queries):
            with cols[i % 2]:
                if st.button(f"🔍 {query}", key=f"sample_{i}"):
                    st.session_state.sample_query = query
                    st.rerun()
        
        # Handle sample query selection
        if 'sample_query' in st.session_state:
            st.text_input("Search Query", value=st.session_state.sample_query, key="query_input")
            if st.button("Search with Sample Query"):
                with st.spinner("Searching..."):
                    search_data = {
                        "query": st.session_state.sample_query,
                        "n_results": n_results,
                        "collection": collection_map[collection_filter]
                    }
                    
                    results = make_api_request("/search", data=search_data)
                    
                    if results:
                        display_search_results(results['results'], st.session_state.sample_query)
    
    with tab3:
        st.header("About the Platform")
        
        st.markdown("""
        ### 🎯 Project Vision
        This is a state-of-the-art, dual-audience financial intelligence platform:
        - **Analyst's Cockpit**: Next-generation fraud detection using GraphRAG
        - **Consumer Security Suite**: AI-powered personal financial fraud prevention
        
        ### 🏗️ Current Phase: Foundation & RAG Proof-of-Concept
        - ✅ Environment setup and data ingestion
        - ✅ Baseline RAG pipeline with ChromaDB
        - ✅ FastAPI backend with semantic search
        - ✅ Streamlit frontend for demonstrations
        
        ### 🔧 Technology Stack
        - **Vector Database**: ChromaDB (local)
        - **Embeddings**: all-MiniLM-L12-v2
        - **Backend**: FastAPI (Python)
        - **Frontend**: Streamlit
        - **Data**: IEEE-CIS transactions, SEBI orders
        
        ### 🚀 Next Steps
        - Phase 2: Production-grade RAG with fine-tuned models
        - Phase 3: Advanced UI/UX and case management
        - Phase 4: GraphRAG and network intelligence
        - Phase 5: Production deployment
        - Phase 6: Consumer security suite
        """)


if __name__ == "__main__":
    main()
