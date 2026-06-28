from sentence_transformers import SentenceTransformer
import chromadb

class StructuredRetriever:
    def __init__(self, collection_name="legal_corpus_structured"):
        self.model = SentenceTransformer('intfloat/multilingual-e5-large')
        self.client = chromadb.PersistentClient(path="./chroma_db_structured")
        self.collection = self.client.get_collection(collection_name)
    
    def query(self, query_text: str, work_filter: str = None, top_k: int = 5):
        """
        Поиск с учетом FRBR-структуры.
        """
        # Векторизуем запрос
        query_embedding = self.model.encode(query_text).tolist()
        
        # Фильтр по закону (если указан)
        where_filter = None
        if work_filter:
            where_filter = {"work_uri": work_filter}
        
        # Поиск
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )
        
        # Формируем структурированный контекст
        context = ""
        sources = []
        
        for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
            context += f"\n{'='*60}\n"
            context += f"{metadata['metadata']}\n"
            context += f"{'='*60}\n"
            context += f"{doc}\n"
            
            sources.append({
                'work_uri': metadata['work_uri'],
                'article_eid': metadata['article_eid'],
                'article_num': metadata['article_num'],
                'clause_eid': metadata.get('clause_eid')
            })
        
        return context, sources

# Тест
if __name__ == "__main__":
    retriever = StructuredRetriever()
    
    query = "Что говорит Конституция о праве на образование?"
    context, sources = retriever.query(
        query,
        work_filter="/ru/act/12 декабря 1993",
        top_k=3
    )
    
    print("🔍 ЗАПРОС:", query)
    print("\n📄 КОНТЕКСТ:")
    print(context)
    print("\n📚 ИСТОЧНИКИ:")
    for source in sources:
        print(f"  - {source['article_num']} ({source['article_eid']})")
