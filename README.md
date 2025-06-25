# RAG PDF & Image Q&A Assistant with Local Ollama Mistral

A completely local, private RAG (Retrieval-Augmented Generation) system that uses Ollama's Mistral model to answer questions about your PDF documents and images.

## 🎯 Features

- 🔒 **100% Local & Private** - No API keys, no cloud services
- 📄 **PDF Processing** - Extract text from regular and scanned PDFs
- 📷 **Image OCR** - Extract text from PNG, JPG, JPEG images (with Tesseract)
- 🧠 **Smart Embeddings** - Using sentence-transformers for semantic search
- 🔍 **Vector Search** - FAISS for fast similarity search
- 🦙 **Mistral Model** - Local AI model via Ollama (7B parameter version for high quality)
- 🌐 **Web Interface** - Easy-to-use Streamlit UI
- 💪 **Fallback System** - Works even if OCR or Ollama is not available

## 📷 Image Support (NEW!)

The system now supports:
- **Scanned PDFs** - Automatic OCR for pages with images/scans
- **Image Files** - Direct upload of PNG, JPG, JPEG files
- **Mixed Documents** - Combination of text and images
- **Preprocessing** - Image enhancement for better OCR accuracy

## Prerequisites

### Required (Core Functionality)
1. **Python 3.8+** with pip
2. **Ollama** - Download from: https://ollama.ai/

### Optional (Image Support)
3. **Tesseract OCR** - For image text extraction
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt install tesseract-ocr`
   - macOS: `brew install tesseract`

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Ollama
```bash
# Install and start Ollama
ollama serve

# Pull the Mistral model (works with 8GB+ RAM)
ollama pull mistral:latest
```

### 3. Optional: Install Tesseract OCR
- **Windows**: Download installer from [Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux**: `sudo apt install tesseract-ocr`
- **macOS**: `brew install tesseract`

### 4. Run the Application
```bash
streamlit run main.py
```

### 5. Access the Web Interface
- Open: http://localhost:8501
- Upload a PDF or image
- Ask questions!

## Supported File Types

| Type | Formats | Description |
|------|---------|-------------|
| **PDFs** | `.pdf` | Regular PDFs and scanned documents |
| **Images** | `.png`, `.jpg`, `.jpeg` | Screenshots, photos, scanned documents |

## How It Works

1. **File Upload** → PDF or image file processing
2. **Text Extraction** → 
   - PDFs: Direct text + OCR for scanned pages
   - Images: OCR text extraction with preprocessing
3. **Chunking** → Split into 500-word chunks with overlap
4. **Embedding** → Convert chunks to vectors using sentence-transformers
5. **Vector Store** → Index chunks in FAISS for fast search
6. **Question** → Find most relevant chunks using similarity search
7. **Local AI** → Ollama Mistral generates answers from context
8. **Response** → Get intelligent answers based on your document

## System Requirements

### Minimum
- **RAM**: 8GB (for mistral model)
- **Storage**: 5GB for model + dependencies
- **CPU**: Any modern processor

### Recommended
- **RAM**: 8GB+ (for better performance)
- **CPU**: Multi-core processor
- **GPU**: Not required (CPU inference)

## Troubleshooting

### Ollama Issues
- **Not running**: Start with `ollama serve`
- **Model missing**: Run `ollama pull mistral:latest`
- **RAM error**: Mistral requires ~4GB RAM. For lower RAM, try `llama3.2:1b` instead

### OCR Issues
- **Images not supported**: Install Tesseract OCR
- **Poor OCR quality**: Try higher resolution images
- **Installation path**: Update path in `pdf_utils.py` if needed

### General Issues
- **Dependencies**: Run `pip install -r requirements.txt`
- **Port conflict**: Streamlit uses port 8501, Ollama uses 11434

## Advanced Configuration

### Custom Models
You can use different Ollama models by modifying `gemini_rag.py`:
- `mistral:latest` - High quality, balanced performance (4GB RAM)
- `mistral:7b` - Alternative Mistral version
- `llama3.2:1b` - Fastest, lowest RAM (1.5GB)
- `llama3.2:3b` - Better quality (3GB RAM)

### OCR Settings
Modify OCR settings in `pdf_utils.py`:
- PSM modes for different document types
- Image preprocessing parameters
- OCR language settings

## File Structure

```
rag_pdf_qa/
├── main.py              # Streamlit web interface
├── pdf_utils.py         # PDF & image processing with OCR
├── vector_store.py      # Embeddings and FAISS operations
├── gemini_rag.py        # Local Ollama integration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Privacy & Security

- ✅ **Completely Local** - No data sent to external servers
- ✅ **No API Keys** - No external service dependencies
- ✅ **Offline Capable** - Works without internet connection
- ✅ **No Data Storage** - Documents processed in memory only
- ✅ **Open Source** - All code is transparent and auditable

## Performance Tips

- **Use mistral:latest** for best quality, or **llama3.2:1b** for systems with limited RAM
- **Higher resolution images** improve OCR accuracy
- **Clean, well-lit documents** work best for OCR
- **Close other applications** to free up RAM for the model

## License

This project is open source and available under the MIT License. 