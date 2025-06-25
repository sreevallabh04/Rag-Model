import streamlit as st
import os
from datetime import datetime
from pdf_utils import extract_text_from_pdf, extract_text_from_image_file, chunk_text, check_ocr_setup, get_ocr_install_instructions
from vector_store import EnhancedVectorStore
from gemini_rag import build_enhanced_prompt, ask_smart_llm, analyze_document_content

# Enhanced page configuration
st.set_page_config(
    page_title="RAG Assistant by Sreevallabh kakarala", 
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "RAG Assistant - Intelligent Document Analysis System\nDeveloped by Sreevallabh kakarala\nPowered by Local AI (Mistral) and Advanced Vector Search"
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
    
    .status-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
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

# Sidebar for system status and controls
with st.sidebar:
    st.header("🔧 System Status")
    
    # Check Ollama status
    from gemini_rag import check_ollama_available
    is_available, status = check_ollama_available()
    
    if is_available:
        st.success(f"✅ AI Model: {status}")
    else:
        st.warning(f"⚠️ AI Status: {status}")
    
    # Check OCR status
    ocr_available, ocr_status = check_ocr_setup()
    if ocr_available:
        st.success(f"✅ OCR: Ready")
    else:
        st.warning(f"⚠️ OCR: Not available")
    
    st.divider()
    
    # Document upload section
    st.header("📁 Upload Document")
    
    # File type selection based on OCR availability
    if ocr_available:
        file_types = ["pdf", "png", "jpg", "jpeg"]
        help_text = "Upload PDF documents or images. OCR will extract text automatically."
    else:
        file_types = ["pdf"]
        help_text = "PDF files only. Install Tesseract OCR for image support."
    
    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=file_types,
        help=help_text
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
        file_type = uploaded_file.type
        file_name = uploaded_file.name
        
        with st.spinner(f"🔄 Processing {file_name}..."):
            try:
                # Save uploaded file temporarily
                temp_path = os.path.join("temp_file")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                
                # Extract text based on file type
                if file_type == "application/pdf":
                    st.info("📄 Processing PDF (with OCR for scanned pages if available)...")
                    text = extract_text_from_pdf(temp_path, use_ocr=ocr_available)
                    st.session_state['file_type'] = "PDF"
                else:  # Image files
                    if ocr_available:
                        st.info("📷 Processing image with OCR...")
                        text = extract_text_from_image_file(temp_path)
                        st.session_state['file_type'] = "Image"
                    else:
                        st.error("❌ OCR not available. Cannot process image files.")
                        text = ""
                
                if not text.strip():
                    st.error("❌ No text could be extracted from the file.")
                elif text.startswith("OCR not available") or text.startswith("OCR Error"):
                    st.error(f"❌ {text}")
                else:
                    # Process the extracted text with enhanced chunking
                    chunks = chunk_text(text, chunk_size=400, overlap=100)  # Better overlap
                    st.session_state['chunks'] = chunks
                    st.session_state['vector_store'] = EnhancedVectorStore()
                    st.session_state['vector_store'].add_chunks(chunks)
                    st.session_state['vector_store'].save(chunks)
                    st.session_state['file_uploaded'] = True
                    
                    # Analyze document content
                    st.session_state['document_metadata'] = analyze_document_content(chunks)
                    
                    # Show success message with enhanced stats
                    doc_summary = st.session_state['vector_store'].get_document_summary()
                    st.success(f"✅ {st.session_state['file_type']} processed successfully!")
                    
                    with st.expander("📊 Document Analysis", expanded=True):
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Total Words", doc_summary['total_words'])
                        with col_b:
                            st.metric("Chunks Created", doc_summary['total_chunks'])
                        with col_c:
                            st.metric("Avg Chunk Size", f"{doc_summary['avg_chunk_size']} words")
                        
                        st.write(f"**Document Type:** {st.session_state['document_metadata']['type'].title()}")
                        if doc_summary['chunks_with_numbers'] > 0:
                            st.write(f"📊 Contains numerical data ({doc_summary['chunks_with_numbers']} chunks)")
                        if doc_summary['chunks_with_dates'] > 0:
                            st.write(f"📅 Contains dates ({doc_summary['chunks_with_dates']} chunks)")
                        if doc_summary['chunks_with_money'] > 0:
                            st.write(f"💰 Contains financial information ({doc_summary['chunks_with_money']} chunks)")
                
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
                <div class="chat-message user-message" style="color: #1565c0 !important;">
                    <strong style="color: #0d47a1 !important;">🙋 You:</strong> <span style="color: #1565c0 !important;">{question}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="chat-message assistant-message" style="color: #2c3e50 !important;">
                    <strong style="color: #1b5e20 !important;">🤖 Assistant:</strong> <span style="color: #2c3e50 !important;">{answer}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Question input with suggestions
        st.markdown("### Ask a Question")
        
        # Smart question suggestions based on document type
        doc_type = st.session_state.get('document_metadata', {}).get('type', 'document')
        
        if doc_type == "legal document":
            suggestions = [
                "What are the key terms and conditions?",
                "What are the parties' obligations?",
                "What are the payment terms?",
                "What happens in case of breach?"
            ]
        elif doc_type == "financial document":
            suggestions = [
                "What is the total amount?",
                "What are the payment details?",
                "What are the dates mentioned?",
                "Are there any fees or charges?"
            ]
        elif doc_type == "instructional document":
            suggestions = [
                "What are the main steps?",
                "What are the requirements?",
                "How do I get started?",
                "What are the important warnings?"
            ]
        else:
            suggestions = [
                "What is this document about?",
                "Summarize the main points",
                "What are the key details?",
                "Extract the important information"
            ]
        
        # Quick question buttons
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
                    # Enhanced search with metadata
                    search_results = st.session_state['vector_store'].enhanced_search(question, top_k=search_k)
                    context_chunks = [chunk for chunk, score, metadata in search_results]
                    
                    # Build enhanced prompt with chat history
                    prompt = build_enhanced_prompt(
                        context_chunks, 
                        question, 
                        chat_history=st.session_state['chat_history'][-3:],  # Last 3 exchanges
                        document_metadata=st.session_state['document_metadata']
                    )
                    
                    # Get AI response
                    answer = ask_smart_llm(prompt, st.session_state['chat_history'])
                    
                    # Add to chat history
                    st.session_state['chat_history'].append((question, answer))
                    
                    # Display the new answer
                    st.markdown("### 🎯 Latest Response")
                    st.markdown(f"""
                    <div class="chat-message user-message" style="color: #1565c0 !important;">
                        <strong style="color: #0d47a1 !important;">🙋 You:</strong> <span style="color: #1565c0 !important;">{question}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="chat-message assistant-message" style="color: #2c3e50 !important;">
                        <strong style="color: #1b5e20 !important;">🤖 Assistant:</strong> <span style="color: #2c3e50 !important;">{answer}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Clear current question
                    if 'current_question' in st.session_state:
                        del st.session_state['current_question']
                    
                    # Show sources with enhanced information
                    with st.expander("📚 Sources & Confidence", expanded=False):
                        for i, (chunk, score, metadata) in enumerate(search_results):
                            relevance = "High" if score > 0.8 else "Medium" if score > 0.6 else "Low"
                            st.markdown(f"**Source {i+1}** (Relevance: {relevance}, Score: {score:.3f})")
                            
                            # Show metadata insights
                            if metadata:
                                insights = []
                                if metadata.get('has_numbers'): insights.append("📊 Contains numbers")
                                if metadata.get('has_dates'): insights.append("📅 Contains dates")
                                if metadata.get('has_money'): insights.append("💰 Contains financial info")
                                if insights:
                                    st.caption(" | ".join(insights))
                            
                            st.text_area(f"Content {i+1}:", chunk, height=100, key=f"source_{i}")
                    
                except Exception as e:
                    st.error(f"❌ Error generating response: {str(e)}")

with col2:
    # Right sidebar with additional features
    if not ocr_available:
        st.markdown("### 📷 Enable Image Support")
        with st.expander("Installation Guide"):
            st.markdown(get_ocr_install_instructions())
    
    if st.session_state['file_uploaded']:
        st.markdown("### 📊 Document Insights")
        doc_summary = st.session_state['vector_store'].get_document_summary()
        
        st.metric("Search Quality", "Enhanced", help="Using advanced search with re-ranking")
        st.metric("AI Model", status.split(':')[0] if ':' in status else status)
        st.metric("Context Size", f"{search_k} chunks", help="Number of relevant chunks used")
        
        # Export chat history
        if st.session_state['chat_history']:
            st.markdown("### 💾 Export Chat")
            if st.button("📥 Download Conversation"):
                chat_export = []
                for q, a in st.session_state['chat_history']:
                    chat_export.append(f"Q: {q}\nA: {a}\n" + "="*50 + "\n")
                
                export_text = f"Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n" + "\n".join(chat_export)
                st.download_button(
                    label="Download as TXT",
                    data=export_text,
                    file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )

# Professional Footer
st.markdown('''
<div class="footer">
    <h3 style="margin-bottom: 1rem; color: #495057;">🚀 Production-Ready Features</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
        <div class="feature-card">
            <h4>🧠 AI-Powered Analysis</h4>
            <p>Advanced Mistral LLM with conversation memory and context awareness</p>
        </div>
        <div class="feature-card">
            <h4>🔍 Smart Search</h4>
            <p>Vector-based similarity search with FAISS indexing and re-ranking</p>
        </div>
        <div class="feature-card">
            <h4>📊 Document Intelligence</h4>
            <p>Automatic content analysis, metadata extraction, and type detection</p>
        </div>
        <div class="feature-card">
            <h4>🔒 Privacy First</h4>
            <p>100% local processing - your data never leaves your machine</p>
        </div>
    </div>
    <hr style="margin: 1.5rem 0; border: 1px solid #dee2e6;">
    <p style="margin-bottom: 0.5rem; font-weight: 600; color: #495057;">
        ⚡ Intelligent RAG Assistant v2.0
    </p>
    <p style="margin-bottom: 0; color: #6c757d; font-size: 0.9rem;">
        Developed with ❤️ by <strong>Sreevallabh kakarala</strong> | 
        Powered by Mistral AI & Advanced Vector Search | 
        © 2024 All Rights Reserved
    </p>
</div>
''', unsafe_allow_html=True)

if not st.session_state['file_uploaded']:
    st.info("👆 Upload a document to start chatting with your AI assistant!")
    
    # Demo instructions
    with st.expander("🎯 How to get the best results"):
        st.markdown("""
        **For better accuracy:**
        - Ask specific questions rather than general ones
        - Include context in follow-up questions
        - Use the suggested questions for your document type
        
        **Question examples:**
        - ✅ "What is the payment deadline mentioned in the contract?"
        - ✅ "How much does the service cost according to the pricing section?"
        - ❌ "Tell me about this document" (too general)
        
        **Follow-up questions:**
        - "Can you explain that in more detail?"
        - "What are the consequences if this deadline is missed?"
        - "Are there any exceptions to this rule?"
        """) 