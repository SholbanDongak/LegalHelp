import chromadb
from sentence_transformers import SentenceTransformer
from bm25_chroma import HybridRetriever

class LawRetriever:
    def __init__(self, db_path="./legal_chromadb", collection_name="ruslawod", top_k=5, bm25_ratio=0.5):
        self.db_path = db_path
        self.collection_name = collection_name
        self.top_k = top_k
        self.bm25_ratio = bm25_ratio  # 0 = только векторный, 1 = только BM25
        self.retriever = None
        self._initialize_retriever()

    def _initialize_retriever(self):
        # Создаём гибридный ретривер (BM25 + векторный) на основе существующей коллекции ChromaDB
        self.retriever = HybridRetriever(
            chroma_path=self.db_path,
            collection_name=self.collection_name
        )
        print("Гибридный ретривер (BM25 + векторный) инициализирован.")

    def retrieve(self, query: str):
        if not query:
            return [], []
        # Выполняем гибридный поиск
        results = self.retriever.query(
            query_texts=[query],
            n_results=self.top_k,
            bm25_ratio=self.bm25_ratio,
            include=['documents', 'metadatas']
        )
        contexts = results['documents'][0] if results['documents'] else []
        sources = []
        if results['metadatas'] and results['metadatas'][0]:
            sources = [meta.get('source', '') for meta in results['metadatas'][0]]
        return contexts, sources
