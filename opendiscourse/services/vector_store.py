"""Vector database implementation using ChromaDB and sentence-transformers."""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, TypeVar, cast, final

from typing_extensions import NotRequired, TypedDict  # noqa: F401

# Type aliases
DocumentScore = Tuple[Dict[str, str], float]
DocumentMetadata = Dict[str, str]  # Enforce string values for metadata

import torch
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from typing_extensions import override


@final
class SentenceTransformerEmbeddings(Embeddings):
    """Wrapper around SentenceTransformer models for use with LangChain."""

    def __init__(
        self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> None:
        """Initialize with model name."""
        self.model: SentenceTransformer = SentenceTransformer(
            model_name, device="cuda" if torch.cuda.is_available() else "cpu"
        )

    @override
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs.

        Args:
            texts: List of text documents to embed.

        Returns:
            List of embeddings, one for each input text.
        """
        return cast(
            List[List[float]], self.model.encode(texts, convert_to_numpy=True).tolist()
        )

    @override
    def embed_query(self, text: str) -> List[float]:
        """Embed query text.

        Args:
            text: The text to embed.

        Returns:
            The embedding vector for the input text.
        """
        return cast(
            List[float], self.model.encode(text, convert_to_numpy=True).tolist()
        )


T = TypeVar("T")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("vector_database.log"), logging.StreamHandler()],
)

# Load environment variables
load_dotenv()


class VectorDatabaseError(Exception):
    """Base exception for vector database errors."""


class VectorDatabaseInitializationError(VectorDatabaseError):
    """Raised when vector database initialization fails."""


class VectorDatabaseOperationError(VectorDatabaseError):
    """Raised when vector database operations fail."""


class VectorDatabase:
    """A vector database implementation using ChromaDB for document storage and retrieval.

    This class provides methods to add, search, and manage documents with their vector
    embeddings. It uses sentence-transformers for generating embeddings and ChromaDB
    for efficient similarity search.
    """

    persist_directory: Path
    embeddings: "SentenceTransformerEmbeddings"
    collection_name: str
    _vector_store: Optional[Chroma] = None

    @property
    def vector_store(self) -> Chroma:
        """Lazily initialize and return the vector store."""
        if self._vector_store is None:
            self._vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_directory),
            )
        return cast(Chroma, self._vector_store)

    def __init__(
        self,
        embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        collection_name: str = "documents",
        persist_directory: str = "./chroma_db",
    ) -> None:
        """Initialize the VectorDatabase.

        Args:
            embeddings_model: Name of the sentence transformer model to use for embeddings.
            collection_name: Name of the collection to store documents in.
            persist_directory: Directory to persist the database to.
        """
        self.persist_directory = Path(persist_directory)
        self.embeddings = SentenceTransformerEmbeddings(model_name=embeddings_model)
        self.collection_name = collection_name
        self._vector_store: Optional[Chroma] = None
        self._ensure_initialized()

    def _ensure_initialized(self) -> None:
        """Ensure the vector store is initialized.

        Creates the persist directory if it doesn't exist.
        The vector store itself is lazily initialized when accessed.
        """
        os.makedirs(self.persist_directory, exist_ok=True)

    def _chunk_text(self, content: str) -> List[str]:
        """Split text into chunks.

        Args:
            content: The text content to split.

        Returns:
            List of chunks.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        return text_splitter.split_text(content)

    def add_document(
        self, document_id: int, content: str, metadata: Dict[str, str]
    ) -> None:
        """Add a document to the vector database.

        Args:
            document_id: Unique identifier for the document
            content: The text content of the document
            metadata: Additional metadata for the document

        Raises:
            VectorDatabaseOperationError: If adding the document fails
        """
        if not content.strip():
            raise VectorDatabaseOperationError("Document content cannot be empty")

        try:
            # Split document into chunks
            chunks = self._chunk_text(content)

            # Prepare documents and metadata
            documents: List[str] = []
            metadatas: List[Dict[str, str]] = []

            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append(
                    {
                        "document_id": str(document_id),
                        "chunk_index": str(i),
                        "chunk_size": str(len(chunk)),
                        **metadata,
                    }
                )

            # Add to vector store
            self.vector_store.add_texts(
                texts=documents,
                metadatas=metadatas,
                ids=[f"{document_id}_{i}" for i in range(len(chunks))],
            )
            logging.info("Added document %s with %d chunks", document_id, len(chunks))

        except Exception as e:
            error_msg = "Failed to add document %s: %s"
            logging.error(error_msg, document_id, e, exc_info=True)
            raise VectorDatabaseOperationError(error_msg % (document_id, e)) from e

    def search(
        self, query: str, k: int = 5, filter_dict: Optional[Dict[str, str]] = None
    ) -> List[Tuple[Dict[str, str], float]]:
        """Search for similar documents.

        Args:
            query: The search query string.
            k: Number of results to return.
            filter_dict: Optional dictionary of filters to apply to the search.

        Returns:
            List of tuples containing (document_metadata, score) pairs.

        Raises:
            VectorDatabaseOperationError: If the search fails.
        """
        if not query.strip():
            raise VectorDatabaseOperationError("Query cannot be empty")
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query, k=k, filter=filter_dict
            )
            # Convert Document objects to metadata dictionaries
            return [
                ({k: str(v) for k, v in doc.metadata.items()}, score)
                for doc, score in results
            ]
        except Exception as e:
            error_msg = "Search failed for query '%s': %s"
            logging.error(error_msg, query, exc_info=True)
            raise VectorDatabaseOperationError(error_msg % (query, e)) from e

    def get_document_chunks(
        self, document_id: int
    ) -> List[Tuple[int, str, Dict[str, str]]]:
        """
        Retrieve all chunks for a specific document.

        Args:
            document_id: ID of the document to retrieve

        Returns:
            List of tuples containing (chunk_index, chunk_text, metadata)

        Raises:
            VectorDatabaseOperationError: If retrieval fails
        """
        try:
            # Fetch all documents with matching document_id in metadata
            docs = self.vector_store.get(where={"document_id": str(document_id)})

            # Sort chunks by index
            metadatas = cast(List[Dict[str, str]], docs.get("metadatas", []))
            documents = cast(List[str], docs.get("documents", []))

            # Create list of (index, document, metadata) tuples
            chunks_data = [
                (int(meta.get("chunk_index", "0")), doc, meta)
                for meta, doc in zip(metadatas, documents)
            ]

            # Sort by chunk index
            chunks = sorted(chunks_data, key=lambda x: x[0])

            logging.info(
                "Retrieved %d chunks for document %s", len(chunks), document_id
            )
            return chunks

        except Exception as e:
            error_msg = "Failed to get chunks for document %s: %s"
            logging.error(error_msg, document_id, e, exc_info=True)
            raise VectorDatabaseOperationError(error_msg % (document_id, e)) from e

    def delete_documents(self, ids: Optional[List[str]] = None) -> None:
        """Delete documents from the vector store.

        Args:
            ids: Optional list of document IDs to delete. If None, all documents will be deleted.

        Raises:
            VectorDatabaseOperationError: If the deletion fails.
        """
        try:
            if ids is None:
                # Delete all documents by getting all document IDs first
                all_docs = self.vector_store.get(include=[])
                doc_ids: List[str] = all_docs.get("ids", [])  # type: ignore[assignment]
                if doc_ids:
                    self.vector_store.delete(ids=doc_ids)
                    logging.info(
                        "Deleted all %d documents from the vector store.", len(doc_ids)
                    )
                else:
                    logging.info("No documents to delete.")
            elif ids:
                self.vector_store.delete(ids=ids)
                logging.info("Deleted %d documents from the vector store.", len(ids))
        except Exception as e:
            error_msg = "Failed to delete documents: %s"
            logging.error(error_msg, str(e), exc_info=True)
            raise VectorDatabaseOperationError(error_msg % str(e)) from e

        # Prepare documents and metadata
        documents: List[str] = []
        metadatas: List[Dict[str, str]] = []

        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append(
                {
                    "document_id": str(document_id),
                    "chunk_index": str(i),
                    "chunk_size": str(len(chunk)),
                    **metadata,
                }
            )

        try:
            # Add to vector store
            _ = self.vector_store.add_texts(
                texts=documents,
                metadatas=metadatas,
                ids=[f"{document_id}_{i}" for i in range(len(chunks))],
            )
            logging.info("Added document %s with %d chunks", document_id, len(chunks))

        except Exception as e:
            error_msg = "Failed to add document %s: %s"
            logging.error(error_msg, document_id, e, exc_info=True)
            raise VectorDatabaseOperationError(error_msg % (document_id, e)) from e

    def search(
        self, query: str, k: int = 5, filter_dict: Optional[Dict[str, str]] = None
    ) -> List[Tuple[Dict[str, str], float]]:
        """Search for similar documents.

        Args:
            query: The search query string.
            k: Number of results to return.
            filter_dict: Optional dictionary of filters to apply to the search.

        Returns:
            List of tuples containing (document_metadata, score) pairs.

        Raises:
            VectorDatabaseOperationError: If the search fails.
        """
        if not query.strip():
            raise VectorDatabaseOperationError("Query cannot be empty")
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query, k=k, filter=filter_dict
            )
            # Convert Document objects to metadata dictionaries
            return [
                ({k: str(v) for k, v in doc.metadata.items()}, score)
                for doc, score in results
            ]
        except Exception as e:
            error_msg = "Search failed for query '%s': %s"
            logging.error(error_msg, query, exc_info=True)
            raise VectorDatabaseOperationError(error_msg % (query, e)) from e

    def get_document_chunks(
        self, document_id: int
    ) -> List[Tuple[int, str, Dict[str, str]]]:
        """
        Retrieve all chunks for a specific document.

        Args:
            document_id: ID of the document to retrieve

        Returns:
            List of tuples containing (chunk_index, chunk_text, metadata)

        Raises:
            VectorDatabaseOperationError: If retrieval fails
        """
        try:
            # Fetch all documents with matching document_id in metadata
            docs = self.vector_store.get(where={"document_id": str(document_id)})

            # Sort chunks by index
            metadatas = cast(List[Dict[str, str]], docs.get("metadatas", []))
            documents = cast(List[str], docs.get("documents", []))

            # Create list of (index, document, metadata) tuples
            chunks_data = [
                (int(meta.get("chunk_index", "0")), doc, meta)
                for meta, doc in zip(metadatas, documents)
            ]

            # Sort by chunk index
            chunks = sorted(chunks_data, key=lambda x: x[0])

            logging.info(
                "Retrieved %d chunks for document %s", len(chunks), document_id
            )
            return chunks

        except Exception as e:
            error_msg = "Failed to get chunks for document %s: %s"
            logging.error(error_msg, document_id, e, exc_info=True)
            raise VectorDatabaseOperationError(error_msg % (document_id, e)) from e

    def delete_documents(self, ids: Optional[List[str]] = None) -> None:
        """Delete documents from the vector store.

        Args:
            ids: Optional list of document IDs to delete. If None, all documents will be deleted.

        Raises:
            VectorDatabaseOperationError: If the deletion fails.
        """
        try:
            if ids is None:
                # Delete all documents by getting all document IDs first
                all_docs = self.vector_store.get(include=[])
                doc_ids: List[str] = all_docs.get("ids", [])  # type: ignore[assignment]
                if doc_ids:
                    self.vector_store.delete(ids=doc_ids)
                    logging.info(
                        "Deleted all %d documents from the vector store.", len(doc_ids)
                    )
                else:
                    logging.info("No documents to delete.")
            elif ids:
                self.vector_store.delete(ids=ids)
                logging.info("Deleted %d documents from the vector store.", len(ids))
        except Exception as e:
            error_msg = "Failed to delete documents: %s"
            logging.error(error_msg, str(e), exc_info=True)
            raise VectorDatabaseOperationError(error_msg % str(e)) from e

    def persist(self) -> None:
        """Persist the vector database to disk.

        This ensures all pending changes are written to disk.

        Raises:
            VectorDatabaseOperationError: If persisting fails.
        """
        try:
            if self._vector_store is not None:
                self._vector_store.persist()
                logging.info("Vector database persisted to disk")
        except Exception as e:
            error_msg = f"Failed to persist vector database: {e!s}"
            logging.error(error_msg)
            raise VectorDatabaseOperationError(error_msg) from e


# Initialize vector database
vector_db = VectorDatabase()
