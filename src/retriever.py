import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions

class LawRetriever:
    def __init__(self, db_path="./legal_chromadb", collection_name="ruslawod", top_k=5, use_hybrid=True):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(collection_name)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.top_k = top_k