import os
import requests
import json
from datetime import datetime

def get_simple_answer(context_chunks, question, chat_history=None):
    """Enhanced rule-based answering with chat history awareness"""
    context = ' '.join(context_chunks)
    
    # Simple keyword matching for demonstration
    question_lower = question.lower()
    
    if not context.strip():
        return "I don't have enough context to answer your question. Please upload a document first."
    
    # Extract relevant sentences with better scoring
    sentences = context.split('.')
    relevant_sentences = []
    
    # Enhanced keyword matching with stemming-like approach
    question_words = [word.strip('.,!?') for word in question_lower.split() if len(word) > 3]
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        score = 0
        for word in question_words:
            if word in sentence_lower:
                score += 1
            # Partial matching for better coverage
            for sent_word in sentence_lower.split():
                if word in sent_word or sent_word in word:
                    score += 0.5
        
        if score > 0:
            relevant_sentences.append((sentence.strip(), score))
    
    # Sort by relevance score
    relevant_sentences.sort(key=lambda x: x[1], reverse=True)
    
    if relevant_sentences:
        top_sentences = [sent[0] for sent in relevant_sentences[:3]]
        return f"Based on the document: {' '.join(top_sentences)}."
    else:
        return f"I found information in the document, but couldn't find a direct answer to your question. The document mainly discusses: {context[:200]}..."

def check_ollama_available():
    """Check if Ollama is running and what models are available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            model_names = [model['name'] for model in models.get('models', [])]
            
            # Prefer Mistral models, then fallback to Llama models
            model_preferences = [
                'mistral:latest', 'mistral:7b', 'mistral', 'llama3.2:1b', 'llama3.2:3b', 'llama3.2', 'llama3'
            ]
            
            for preferred in model_preferences:
                for model_name in model_names:
                    if preferred in model_name.lower():
                        return True, model_name
            
            # Fallback to any available model
            if model_names:
                return True, model_names[0]
            
            return False, "No models found"
        return False, "Ollama not running"
    except Exception as e:
        return False, f"Ollama connection failed: {str(e)}"

def ask_ollama_local(prompt, model_name="mistral:latest", temperature=0.7):
    """Ask local Ollama model with enhanced parameters"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 800,  # Increased for more detailed responses
                    "top_k": 40,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                    "num_ctx": 4096  # Larger context window
                }
            },
            timeout=180  # Longer timeout for complex questions
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'No response received').strip()
        else:
            return f"Error: HTTP {response.status_code}"
            
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"

def build_enhanced_prompt(context_chunks, question, chat_history=None, document_metadata=None):
    """Build an enhanced prompt with conversation history and metadata"""
    context = '\n\n'.join(context_chunks)
    
    # Build chat history context
    history_context = ""
    if chat_history and len(chat_history) > 0:
        history_context = "\n\nPrevious conversation:\n"
        for i, (q, a) in enumerate(chat_history[-3:]):  # Last 3 exchanges
            history_context += f"Q{i+1}: {q}\nA{i+1}: {a}\n"
    
    # Add document metadata if available
    metadata_context = ""
    if document_metadata:
        metadata_context = f"\nDocument info: {document_metadata}\n"
    
    prompt = f"""You are an expert document analyst and question-answering assistant. Your job is to provide accurate, detailed, and helpful answers based on the provided document context.

INSTRUCTIONS:
1. Use ONLY the information provided in the context below
2. If the context doesn't contain enough information, clearly state what's missing
3. Provide specific details and examples when available
4. If this is a follow-up question, consider the previous conversation
5. Structure your answer clearly with bullet points or numbered lists when appropriate
6. Quote specific parts of the document when relevant

DOCUMENT CONTEXT:
{context}{metadata_context}
{history_context}
CURRENT QUESTION: {question}

ANSWER: Provide a comprehensive, accurate answer based on the document context above. If you need to make any assumptions or if information is unclear, explicitly state this."""

    return prompt

def ask_smart_llm(prompt, chat_history=None, model_preference="balanced"):
    """Enhanced LLM interaction with multiple strategies"""
    try:
        # Extract question and context from prompt for fallback
        lines = prompt.split('\n')
        question = ""
        context_chunks = []
        
        for i, line in enumerate(lines):
            if line.startswith("CURRENT QUESTION:"):
                question = line.replace("CURRENT QUESTION:", "").strip()
            elif line.startswith("DOCUMENT CONTEXT:"):
                # Find context section
                context_start = i + 1
                context_lines = []
                for j in range(context_start, len(lines)):
                    if lines[j].startswith("CURRENT QUESTION:"):
                        break
                    context_lines.append(lines[j])
                context_chunks = ['\n'.join(context_lines)]
        
        # Check if Ollama is available
        is_available, status = check_ollama_available()
        
        if is_available:
            print(f"Using model: {status}")
            
            # Adjust temperature based on question type
            temperature = 0.3  # Lower for factual questions
            if any(word in question.lower() for word in ['explain', 'describe', 'how', 'why', 'what']):
                temperature = 0.7  # Higher for explanatory questions
            
            response = ask_ollama_local(prompt, status, temperature)
            
            if not response.startswith("Error"):
                return response
            else:
                print(f"Ollama error: {response}")
                return get_simple_answer(context_chunks, question, chat_history)
        else:
            print(f"Ollama status: {status}")
            return get_simple_answer(context_chunks, question, chat_history)
            
    except Exception as e:
        print(f"Error in ask_smart_llm: {e}")
        context_chunks = context_chunks if 'context_chunks' in locals() else [""]
        question = question if 'question' in locals() else "your question"
        return get_simple_answer(context_chunks, question, chat_history)

def analyze_document_content(text_chunks):
    """Analyze document to provide metadata for better prompting"""
    combined_text = ' '.join(text_chunks[:5])  # First few chunks for analysis
    
    # Simple document type detection
    doc_type = "document"
    if any(word in combined_text.lower() for word in ['contract', 'agreement', 'terms']):
        doc_type = "legal document"
    elif any(word in combined_text.lower() for word in ['manual', 'instructions', 'guide']):
        doc_type = "instructional document"
    elif any(word in combined_text.lower() for word in ['report', 'analysis', 'findings']):
        doc_type = "analytical report"
    elif any(word in combined_text.lower() for word in ['invoice', 'receipt', 'payment']):
        doc_type = "financial document"
    
    word_count = len(combined_text.split())
    
    return {
        "type": doc_type,
        "estimated_length": f"~{word_count * len(text_chunks) // 5} words",
        "content_preview": combined_text[:100] + "..." if len(combined_text) > 100 else combined_text
    }