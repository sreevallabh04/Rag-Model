import streamlit as st
import os
from datetime import datetime
from pdf_utils import extract_text_from_pdf, extract_text_from_image_file, chunk_text, check_ocr_setup, get_ocr_install_instructions
from vector_store import EnhancedVectorStore

# Import cloud_rag for OpenAI integration
from cloud_rag import build_enhanced_prompt, ask_smart_llm, analyze_document_content, check_openai_available

# Try to import OCR utilities with fallback
try:
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Enhanced page configuration
st.set_page_config(
    page_title="RAG Assistant by Sreevallabh kakarala", 
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "RAG Assistant - Intelligent Document Analysis System\nDeveloped by Sreevallabh kakarala\nPowered by AI and Advanced Vector Search"
    }
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 0.5rem;
        font-style: italic;
    }
    
    .creator-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        text-align: center;
        margin: 1rem auto;
        width: fit-content;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .cloud-badge {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-align: center;
        margin: 0.5rem auto;
        width: fit-content;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        color: #2c3e50 !important;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    
    .chat-message:hover {
        transform: translateY(-2px);
    }
    
    .user-message {
        background: linear-gradient(135deg, #e8f4fd 0%, #d6eaff 100%);
        border-left-color: #667eea;
        color: #1565c0 !important;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left-color: #28a745;
        color: #2c3e50 !important;
        border: 1px solid #dee2e6;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    /* Ensure all text in chat messages is visible */
    .chat-message strong {
        color: #212529 !important;
        font-weight: 700;
    }
    
    /* Fix any white text issues */
    .chat-message * {
        color: inherit !important;
    }
    
    /* Override Streamlit's default styles that might cause white text */
    div[data-testid="stMarkdown"] p {
        color: #2c3e50 !important;
    }
    
    /* Ensure text is visible in all containers */
    .stMarkdown, .stText, .element-container {
        color: #2c3e50 !important;
    }
    
    /* Force dark text in all markdown content */
    .stMarkdown * {
        color: #2c3e50 !important;
    }
    
    /* Specifically target the response areas */
    div[data-testid="column"] div[data-testid="stMarkdown"] {
        color: #2c3e50 !important;
    }
    
    /* Professional button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        margin-top: 2rem;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Professional Header
st.markdown('<h1 class="main-header">🧠 Intelligent RAG Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Advanced Document Analysis & Q&A System</p>', unsafe_allow_html=True)
st.markdown('''
<div class="creator-badge">
    ✨ Developed by <strong>Sreevallabh kakarala</strong> ✨
</div>
''', unsafe_allow_html=True)

# Cloud mode indicator
if OCR_AVAILABLE:
    st.markdown('''
    <div class="cloud-badge">
        ☁️ Cloud Edition - Powered by OpenAI
    </div>
    ''', unsafe_allow_html=True)

# Sidebar for system status and controls
with st.sidebar:
    st.header("🔧 System Status")
    
    # Check OpenAI API status
    is_available, status = check_openai_available()
    if is_available:
        st.success(f"✅ AI Model: {status}")
    else:
        st.warning(f"⚠️ AI Status: {status}")
        if "API key not found" in status:
            st.info("💡 Add your OpenAI API key as OPENAI_API_KEY environment variable")
    
    st.divider()
    
    # Document upload section
    st.header("📁 Upload Document")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type=["pdf"],
        help="Upload PDF documents for analysis"
    )
    
    # Advanced settings
    st.header("⚙️ Settings")
    search_k = st.slider("Search Results", min_value=3, max_value=10, value=5, 
                        help="Number of relevant chunks to use for answering")
    
    temperature = st.slider("AI Creativity", min_value=0.1, max_value=1.0, value=0.7, step=0.1,
                           help="Higher values make responses more creative but less precise")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state['chat_history'] = []
        st.rerun()

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state['vector_store'] = None
    st.session_state['chunks'] = []
    st.session_state['file_uploaded'] = False
    st.session_state['file_type'] = None
    st.session_state['chat_history'] = []
    st.session_state['document_metadata'] = None

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # File processing
    if uploaded_file is not None:
        file_name = uploaded_file.name
        
        with st.spinner(f"🔄 Processing {file_name}..."):
            try:
                # Save uploaded file temporarily
                temp_path = "temp_file.pdf"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                
                # Extract text from PDF
                st.info("📄 Processing PDF...")
                text = extract_pdf_text_simple(temp_path)
                st.session_state['file_type'] = "PDF"
                
                if not text.strip() or text.startswith("Error"):
                    st.error("❌ No text could be extracted from the file.")
                else:
                    # Process the extracted text with chunking
                    chunks = simple_chunk_text(text, chunk_size=400, overlap=100)
                    st.session_state['chunks'] = chunks
                    st.session_state['vector_store'] = EnhancedVectorStore()
                    st.session_state['vector_store'].add_chunks(chunks)
                    st.session_state['vector_store'].save(chunks)
                    st.session_state['file_uploaded'] = True
                    
                    # Analyze document content
                    st.session_state['document_metadata'] = analyze_document_content(chunks)
                    
                    # Show success message with stats
                    doc_summary = st.session_state['vector_store'].get_document_summary()
                    st.success(f"✅ PDF processed successfully!")
                    
                    with st.expander("📊 Document Analysis", expanded=True):
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Total Words", doc_summary['total_words'])
                        with col_b:
                            st.metric("Chunks Created", doc_summary['total_chunks'])
                        with col_c:
                            st.metric("Avg Chunk Size", f"{doc_summary['avg_chunk_size']} words")
                        
                        st.write(f"**Document Type:** {st.session_state['document_metadata']['type'].title()}")
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    # Chat Interface
    if st.session_state['file_uploaded']:
        st.divider()
        st.subheader("💬 Chat with your Document")
        
        # Display chat history
        if st.session_state['chat_history']:
            st.markdown("### Conversation History")
            for i, (question, answer) in enumerate(st.session_state['chat_history']):
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>🙋 You:</strong> {question}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Assistant:</strong> {answer}
                </div>
                """, unsafe_allow_html=True)
        
        # Question input
        st.markdown("### Ask a Question")
        
        # Quick question suggestions
        suggestions = [
            "What is this document about?",
            "Summarize the main points",
            "What are the key details?",
            "Extract the important information"
        ]
        
        st.markdown("**💡 Quick Questions:**")
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(suggestion, key=f"suggestion_{i}"):
                    st.session_state['current_question'] = suggestion
        
        # Question input
        question = st.text_area(
            "Your question:",
            value=st.session_state.get('current_question', ''),
            placeholder="Ask anything about your document...",
            height=100,
            key="question_input"
        )
        
        # Answer generation
        col_send, col_clear = st.columns([3, 1])
        with col_send:
            ask_button = st.button("🚀 Ask Question", type="primary", disabled=not question.strip())
        with col_clear:
            if st.button("🔄 New Question"):
                st.session_state['current_question'] = ""
                st.rerun()
        
        if ask_button and question.strip():
            with st.spinner("🧠 Analyzing document and generating response..."):
                try:
                    # Enhanced search
                    search_results = st.session_state['vector_store'].enhanced_search(question, top_k=search_k)
                    context_chunks = [chunk for chunk, score, metadata in search_results]
                    
                    # Build enhanced prompt
                    prompt = build_enhanced_prompt(
                        context_chunks, 
                        question, 
                        chat_history=st.session_state['chat_history'][-3:],
                        document_metadata=st.session_state['document_metadata']
                    )
                    
                    # Get AI response
                    answer = ask_smart_llm(prompt, st.session_state['chat_history'])
                    
                    # Add to chat history
                    st.session_state['chat_history'].append((question, answer))
                    
                    # Display the new answer
                    st.markdown("### 🎯 Latest Response")
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>🙋 You:</strong> {question}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>🤖 Assistant:</strong> {answer}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Clear current question
                    if 'current_question' in st.session_state:
                        del st.session_state['current_question']
                    
                except Exception as e:
                    st.error(f"❌ Error generating response: {str(e)}")

with col2:
    if st.session_state['file_uploaded']:
        st.markdown("### 📊 Document Insights")
        doc_summary = st.session_state['vector_store'].get_document_summary()
        
        st.metric("Search Quality", "Enhanced")
        ai_model_display = status.split(':')[0] if ':' in status else status
        st.metric("AI Model", ai_model_display)
        st.metric("Context Size", f"{search_k} chunks")

# Footer
st.markdown("""
---
### 🚀 **Cloud-Ready Features:**
- 🧠 **AI-Powered Analysis** with OpenAI integration
- 🔍 **Advanced Search** with vector similarity
- 💬 **Chat Interface** with conversation memory
- ☁️ **Cloud Deployment** ready for production
- 🔒 **Secure** with API key management

**⚡ Intelligent RAG Assistant v2.0 - Cloud Edition**

*Developed with ❤️ by **Sreevallabh kakarala** | © 2024 All Rights Reserved*
""")

if not st.session_state['file_uploaded']:
    st.info("👆 Upload a PDF document to start chatting with your AI assistant!")
    
    st.markdown("""
    ### 🎯 How to get started:
    1. **Upload** a PDF document using the sidebar
    2. **Wait** for processing to complete
    3. **Ask** questions about your document
    4. **Get** intelligent AI-powered responses
    
    **Note:** This cloud edition uses OpenAI API. Make sure to set your `OPENAI_API_KEY` environment variable.
    """) 