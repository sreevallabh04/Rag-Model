import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import pickle
from typing import List, Tuple
import re

class EnhancedVectorStore:
    def __init__(self, embedding_model_name='all-MiniLM-L6-v2', index_path='faiss.index', mapping_path='chunks.pkl'):
        self.model = SentenceTransformer(embedding_model_name)
        self.index_path = index_path
        self.mapping_path = mapping_path
        self.metadata_path = 'chunk_metadata.pkl'
        self.index = None
        self.chunks = []
        self.chunk_metadata = []
        self.embeddings = None

    def embed_chunks(self, chunks: List[str]) -> np.ndarray:
        """Enhanced embedding with better normalization"""
        print("Creating embeddings for document chunks...")
        embeddings = self.model.encode(
            chunks, 
            show_progress_bar=True, 
            convert_to_numpy=True, 
            normalize_embeddings=True,
            batch_size=32  # Process in batches for efficiency
        )
        self.embeddings = embeddings
        return embeddings

    def build_faiss_index(self, embeddings: np.ndarray):
        """Build FAISS index with better configuration"""
        dim = embeddings.shape[1]
        # Use IndexFlatIP for cosine similarity (with normalized vectors)
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)
        print(f"Built FAISS index with {embeddings.shape[0]} chunks")

    def save(self, chunks: List[str]):
        """Save index and metadata"""
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
        with open(self.mapping_path, 'wb') as f:
            pickle.dump(chunks, f)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.chunk_metadata, f)

    def load(self):
        """Load index and metadata"""
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        if os.path.exists(self.mapping_path):
            with open(self.mapping_path, 'rb') as f:
                self.chunks = pickle.load(f)
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'rb') as f:
                self.chunk_metadata = pickle.load(f)

    def create_chunk_metadata(self, chunks: List[str]):
        """Create metadata for each chunk for better retrieval"""
        metadata = []
        for i, chunk in enumerate(chunks):
            # Analyze chunk content
            word_count = len(chunk.split())
            
            # Identify if chunk contains important elements
            has_numbers = bool(re.search(r'\d+', chunk))
            has_dates = bool(re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', chunk))
            has_money = bool(re.search(r'[$€£¥]\d+|\b\d+\s*(?:dollars?|euros?|pounds?)\b', chunk))
            has_names = bool(re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', chunk))
            
            # Calculate content richness
            unique_words = len(set(chunk.lower().split()))
            richness_score = unique_words / max(word_count, 1)
            
            metadata.append({
                'chunk_id': i,
                'word_count': word_count,
                'has_numbers': has_numbers,
                'has_dates': has_dates,
                'has_money': has_money,
                'has_names': has_names,
                'richness_score': richness_score,
                'chunk_preview': chunk[:100] + "..." if len(chunk) > 100 else chunk
            })
        
        self.chunk_metadata = metadata
        return metadata

    def add_chunks(self, chunks: List[str]):
        """Add chunks with enhanced processing"""
        self.chunks = chunks
        self.create_chunk_metadata(chunks)
        embeddings = self.embed_chunks(chunks)
        self.build_faiss_index(embeddings)

    def enhanced_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, dict]]:
        """Enhanced search with re-ranking and metadata"""
        # Initial semantic search
        query_emb = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        D, I = self.index.search(query_emb, min(top_k * 2, len(self.chunks)))  # Get more candidates
        
        results = []
        query_lower = query.lower()
        
        for idx, score in zip(I[0], D[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx]
                metadata = self.chunk_metadata[idx] if idx < len(self.chunk_metadata) else {}
                
                # Enhanced scoring with multiple factors
                final_score = float(score)
                
                # Boost score for exact keyword matches
                query_words = query_lower.split()
                chunk_lower = chunk.lower()
                exact_matches = sum(1 for word in query_words if word in chunk_lower)
                if exact_matches > 0:
                    final_score += 0.1 * exact_matches
                
                # Boost based on content type relevance
                if 'number' in query_lower and metadata.get('has_numbers', False):
                    final_score += 0.05
                if any(word in query_lower for word in ['date', 'when', 'time']) and metadata.get('has_dates', False):
                    final_score += 0.05
                if any(word in query_lower for word in ['cost', 'price', 'money', 'pay']) and metadata.get('has_money', False):
                    final_score += 0.05
                if any(word in query_lower for word in ['who', 'name', 'person']) and metadata.get('has_names', False):
                    final_score += 0.05
                
                # Boost for content richness
                final_score += metadata.get('richness_score', 0) * 0.02
                
                results.append((chunk, final_score, metadata))
        
        # Sort by enhanced score and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Backward compatible search method"""
        enhanced_results = self.enhanced_search(query, top_k)
        return [(chunk, score) for chunk, score, metadata in enhanced_results]

    def get_document_summary(self) -> dict:
        """Get a summary of the loaded document"""
        if not self.chunks:
            return {"status": "No document loaded"}
        
        total_words = sum(len(chunk.split()) for chunk in self.chunks)
        avg_chunk_size = total_words / len(self.chunks)
        
        # Analyze content types
        chunks_with_numbers = sum(1 for meta in self.chunk_metadata if meta.get('has_numbers', False))
        chunks_with_dates = sum(1 for meta in self.chunk_metadata if meta.get('has_dates', False))
        chunks_with_money = sum(1 for meta in self.chunk_metadata if meta.get('has_money', False))
        
        return {
            "total_chunks": len(self.chunks),
            "total_words": total_words,
            "avg_chunk_size": round(avg_chunk_size),
            "chunks_with_numbers": chunks_with_numbers,
            "chunks_with_dates": chunks_with_dates,
            "chunks_with_money": chunks_with_money,
            "document_preview": self.chunks[0][:200] + "..." if self.chunks else ""
        }

# Backward compatibility
VectorStore = EnhancedVectorStore

# Example usage
if __name__ == "__main__":
    store = VectorStore()
    store.add_chunks(["This is a sample document.", "Another chunk of text here."])
    print(store.search("sample"))
    print(store.get_document_summary()) 