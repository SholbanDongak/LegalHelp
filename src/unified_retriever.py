from sentence_transformers import SentenceTransformer
import chromadb
from typing import List, Dict, Tuple

class UnifiedRetriever:
    """
    Универсальный retriever для работы с несколькими кодексами.
    Ищет по всем коллекциям одновременно.
    """
    
    def __init__(self):
        self.model = SentenceTransformer('intfloat/multilingual-e5-large')
        self.client = chromadb.PersistentClient(path="./chroma_db_structured")
        
        # Получаем все коллекции
        self.collections = {}
        try:
            self.collections['constitution'] = self.client.get_collection("legal_corpus_structured")
            print(f"✅ Конституция РФ: {self.collections['constitution'].count()} чанков")
        except:
            print("⚠️  Коллекция Конституции не найдена")
        
        try:
            self.collections['gk_rf'] = self.client.get_collection("gk_rf_structured")
            print(f"✅ ГК РФ: {self.collections['gk_rf'].count()} чанков")
        except:
            print("⚠️  Коллекция ГК РФ не найдена")
    
    def query(self, query_text: str, top_k: int = 5, code_filter: str = None) -> Tuple[str, List[Dict]]:
        """
        Поиск по всем кодексам или конкретному кодексу.
        
        Args:
            query_text: текст запроса
            top_k: количество результатов
            code_filter: фильтр по кодексу ('constitution', 'gk_rf' или None для всех)
        """
        query_embedding = self.model.encode(query_text).tolist()
        
        all_results = []
        
        # Определяем, по каким коллекциям искать
        if code_filter:
            collections_to_search = {code_filter: self.collections.get(code_filter)}
        else:
            collections_to_search = self.collections
        
        # Ищем по каждой коллекции
        for code_name, collection in collections_to_search.items():
            if collection is None:
                continue
            
            # Распределяем top_k между коллекциями
            k_per_collection = max(1, top_k // len(collections_to_search))
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=k_per_collection
            )
            
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                all_results.append({
                    'code': code_name,
                    'text': doc,
                    'metadata': metadata
                })
        
        # Сортируем по релевантности (упрощённо — по порядку выдачи)
        all_results = all_results[:top_k]
        
        # Формируем контекст
        context = ""
        sources = []
        
        for result in all_results:
            code_name = result['code']
            metadata = result['metadata']
            
            # Определяем название кодекса
            if code_name == 'constitution':
                code_display = "Конституция РФ"
            elif code_name == 'gk_rf':
                part_name = metadata.get('part_name', '')
                code_display = f"ГК РФ ({part_name})"
            else:
                code_display = code_name
            
            context += f"\n{'='*60}\n"
            context += f"[{code_display}] {metadata.get('metadata', '')}\n"
            context += f"{'='*60}\n"
            context += f"{result['text']}\n"
            
            sources.append({
                'code': code_name,
                'code_display': code_display,
                'article_num': metadata.get('article_num', ''),
                'article_eid': metadata.get('article_eid', ''),
                'metadata': metadata.get('metadata', '')
            })
        
        return context, sources


# Тест
if __name__ == "__main__":
    retriever = UnifiedRetriever()
    
    # Тестовые запросы
    test_queries = [
        "Какие права на образование гарантирует Конституция?",
        "Что такое договор купли-продажи по ГК РФ?",
        "Как наследуется имущество?",
        "Какие результаты интеллектуальной деятельности охраняются законом?",
        "Что такое свобода договора?"
    ]
    
    for query in test_queries:
        print(f"\n{'#'*60}")
        print(f"🔍 ЗАПРОС: {query}")
        print(f"{'#'*60}")
        
        context, sources = retriever.query(query, top_k=3)
        
        print("\n📄 КОНТЕКСТ:")
        print(context[:500] + "...")
        
        print("\n📚 ИСТОЧНИКИ:")
        for source in sources:
            print(f"  - [{source['code_display']}] {source['metadata']}")
