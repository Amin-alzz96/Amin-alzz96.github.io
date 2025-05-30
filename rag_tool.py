"""
RAG Tool: Loads context documents, builds a vector DB with metadata, and provides a retriever for the agent.
Includes a LangChain Tool wrapper and a test example.
"""
import os
# Import necessary LangChain modules for document loading, splitting, embeddings, and vector DB
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.tools import Tool
from typing import List
from dotenv import load_dotenv

# Set up paths for context folder and vector DB
CONTEXT_DIR = os.path.join(os.path.dirname(__file__), "context")
VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), "vector_db")

# Load environment variables (e.g., OpenAI API key) from .env file
load_dotenv()  # Load environment variables from .env file

class RAGTool:
    """
    RAGTool handles loading documents, embedding them, building the vector DB, and searching it.
    It also supports adding new documents after initial creation.
    """
    def __init__(self, persist: bool = True):
        # If persist=True, DB is saved/loaded from disk
        self.persist = persist
        self.vector_db = None
        self._build_or_load_db()

    def _build_or_load_db(self):
        # If DB exists and persist is enabled, load it; otherwise, embed all docs and build DB
        if self.persist and os.path.exists(VECTOR_DB_PATH):
            self.vector_db = FAISS.load_local(VECTOR_DB_PATH, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        else:
            self._embed_and_save_all()

    def _embed_and_save_all(self):
        # Load all .md files from context folder
        loader = DirectoryLoader(
            CONTEXT_DIR,
            glob="*.md",
            loader_cls=TextLoader,
            use_multithreading=True,
            show_progress=True,
        )
        documents = loader.load()
        # Add metadata to each document (e.g., source)
        for doc in documents:
            doc.metadata = doc.metadata or {}
            doc.metadata["source"] = doc.metadata.get("source", doc.page_content[:30])
        # Split documents into chunks for better retrieval
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = splitter.split_documents(documents)
        # Add metadata to each chunk (e.g., length)
        for chunk in docs:
            chunk.metadata = chunk.metadata or {}
            chunk.metadata["length"] = len(chunk.page_content)
        # Embed chunks and build the FAISS vector DB
        embeddings = OpenAIEmbeddings()
        self.vector_db = FAISS.from_documents(docs, embeddings)
        # Save DB to disk if persist is enabled
        if self.persist:
            self.vector_db.save_local(VECTOR_DB_PATH)

    def add_new_documents(self, filepaths: list):
        """
        Add new documents to the vector DB and update the index.
        Only the provided filepaths are loaded and embedded.
        """
        loader = DirectoryLoader(
            CONTEXT_DIR,
            glob="*.md",
            loader_cls=TextLoader,
            use_multithreading=True,
            show_progress=True,
        )
        # Load only the new files
        documents = [TextLoader(fp).load()[0] for fp in filepaths]
        for doc in documents:
            doc.metadata = doc.metadata or {}
            doc.metadata["source"] = doc.metadata.get("source", doc.page_content[:30])
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = splitter.split_documents(documents)
        for chunk in docs:
            chunk.metadata = chunk.metadata or {}
            chunk.metadata["length"] = len(chunk.page_content)
        embeddings = OpenAIEmbeddings()
        # If DB doesn't exist, create it; otherwise, add to existing DB
        if self.vector_db is None:
            self.vector_db = FAISS.from_documents(docs, embeddings)
        else:
            self.vector_db.add_documents(docs)
        if self.persist:
            self.vector_db.save_local(VECTOR_DB_PATH)

    def get_retriever(self):
        """Return a retriever object for use in agent chains."""
        return self.vector_db.as_retriever()

    def search(self, query: str, k: int = 3) -> List[str]:
        """
        Search the vector DB and return top k relevant chunks with metadata.
        Returns a list of formatted strings with score, source, and content preview.
        """
        results = self.vector_db.similarity_search_with_score(query, k=k)
        return [f"Score: {score}, Source: {doc.metadata.get('source')}, Content: {doc.page_content[:100]}..." for doc, score in results]

# LangChain Tool wrapper for use in agent toolkits
from typing import Any

def rag_search_tool():
    """
    Tool: RAGSearch
    Description:
        This tool provides retrieval-augmented generation (RAG) over your personal context documents. It loads, embeds, and indexes all Markdown (.md) files in the 'context/' folder using OpenAI embeddings and FAISS vector store. When called, it retrieves the most relevant chunks of your personal knowledge base for a given query, including metadata such as the source document and chunk length. This enables the agent to answer questions about you (e.g., 'who are you?', 'what is your experience?', 'what are your skills?') using your own data.
        IMPORTANT: The agent MUST answer as if it is Mohammad Amin Alizadeh (Amin), using first-person language and speaking from Amin's perspective. All responses should sound as if Amin himself is talking, using the retrieved context as his own words and knowledge.
    Input:
        query (str): The user's question about you or your background.
        k (int, optional): The number of top relevant chunks to retrieve. Default is 3.
    Output:
        List[dict]: A list of dictionaries, each containing:
            - score (float): Similarity score for the chunk.
            - source (str): Source document or chunk preview.
            - content (str): The chunk content (first 100 chars).
    Usage:
        Use this tool whenever the agent needs to answer a question about you, your background, skills, or experience, based on your context folder. The answer must always be from Amin's point of view, as if Amin is speaking directly.
    """
    rag = RAGTool()
    async def async_search(query: str, k: int = 3) -> list[dict]:
        """Async version of the search method."""
        # In real async, you would use an async DB or embedding backend. Here, we wrap sync in async for compatibility.
        import asyncio
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, rag.search, query, k)
        # Parse the formatted string results into dicts
        parsed = []
        for r in results:
            # Example: 'Score: 0.123, Source: BIO.md, Content: ...'
            try:
                parts = r.split(', ')
                score = float(parts[0].split(': ')[1])
                source = parts[1].split(': ')[1]
                content = parts[2].split(': ', 1)[1]
                parsed.append({"score": score, "source": source, "content": content})
            except Exception:
                parsed.append({"raw": r})
        return parsed
    return Tool(
        name="RAGSearch",
        func=async_search,
        args_schema=None,  # Accepts query: str, k: int
        description=(rag_search_tool.__doc__ or "").strip(),
        coroutine=async_search
    )

# Example usage for testing the RAGTool functionality
def example():
    import asyncio
    rag_tool = rag_search_tool()
    print("Async example search for 'who are you?':")
    async def run():
        results = await rag_tool.func("who are you?")
        for r in results:
            print(r)
    asyncio.run(run())




# if __name__ == "__main__":
#     example()