"""
Cloud-compatible RAG integration for Intelligent RAG Assistant
Author: Sreevallabh kakarala
Version: 2.0 (Cloud Edition)
"""

import os
import openai
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

def check_openai_available():
    """Check if OpenAI API is available and configured"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return False, "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
        
        openai.api_key = api_key
        
        # Test API connection with a simple request
        response = openai.models.list()
        
        # Check for available models
        models = [model.id for model in response.data]
        
        # Prefer GPT-4 models, fallback to GPT-3.5
        model_preferences = [
            'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'
        ]
        
        for preferred in model_preferences:
            if preferred in models:
                return True, preferred
        
        # Fallback to any available model
        if models:
            return True, models[0]
        
        return False, "No suitable models found"
        
    except Exception as e:
        return False, f"OpenAI API connection failed: {str(e)}"

def ask_openai_cloud(prompt, model_name="gpt-4o-mini", temperature=0.7):
    """Ask OpenAI model for cloud deployment"""
    try:
        response = openai.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert document analyst. Provide accurate, detailed answers based on the given document context."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=800,
            top_p=0.9
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error connecting to OpenAI: {str(e)}"

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
    """Enhanced LLM interaction with multiple strategies for cloud deployment"""
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
        
        # Check if OpenAI API is available
        is_available, status = check_openai_available()
        
        if is_available:
            print(f"Using OpenAI model: {status}")
            
            # Adjust temperature based on question type
            temperature = 0.3  # Lower for factual questions
            if any(word in question.lower() for word in ['explain', 'describe', 'how', 'why', 'what']):
                temperature = 0.7  # Higher for explanatory questions
            
            response = ask_openai_cloud(prompt, status, temperature)
            
            if not response.startswith("Error"):
                return response
            else:
                print(f"OpenAI error: {response}")
                return get_simple_answer(context_chunks, question, chat_history)
        else:
            print(f"OpenAI status: {status}")
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