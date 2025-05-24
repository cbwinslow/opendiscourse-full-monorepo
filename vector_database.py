import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging
from typing import List, Dict, Optional, Tuple, Any, Set
from collections import defaultdict
import numpy as np
import torch

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vector_database.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

class VectorDatabase:
    def __init__(self):
        # Initialize embeddings model
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize Chroma vector store
        self.vector_store = Chroma(
            collection_name="documents",
            embedding_function=self.model.encode,
            persist_directory="./chroma_db"
        )
        
    def add_document(self, document_id: int, content: str, metadata: Dict[str, str]) -> None:
        """Add a document to the vector database."""
        try:
            # Split document into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_text(content)
            
            # Create embeddings and add to vector store
            for i, chunk in enumerate(chunks):
                self.vector_store.add_texts(
                    texts=[chunk],
                    metadatas=[{
                        "document_id": document_id,
                        "chunk_index": i,
                        **metadata
                    }]
                )
            
            logging.info(f"Added document {document_id} to vector database")
            
        except Exception as e:
            logging.error(f"Error adding document to vector database: {str(e)}")
            raise
    
    def search_similar(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents based on query."""
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k
            )
            return results
            
        except Exception as e:
            logging.error(f"Error searching vector database: {str(e)}")
            raise
    
    def persist(self) -> None:
        """Persist the vector database to disk."""
        try:
            self.vector_store.persist()
            logging.info("Vector database persisted to disk")
            
        except Exception as e:
            logging.error(f"Error persisting vector database: {str(e)}")
            raise

# Initialize vector database
vector_db = VectorDatabase()
