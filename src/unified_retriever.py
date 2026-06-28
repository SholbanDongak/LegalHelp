from sentence_transformers import SentenceTransformer
import chromadb
from typing import List, Dict, Tuple

class UnifiedRetriever:
    """
    Универсальный retriever для работы со всеми кодексами.
    Увеличен top_k для лучшего покрытия.
    """
    
    def __init__(self):
        self.model = SentenceTransformer('intfloat/multilingual-e5-large')
        self.client = chromadb.PersistentClient(path="./chroma_db_structured")
        
        self.collections = {}
        
        # Конституция
        try:
            self.collections['constitution'] = self.client.get_collection("legal_corpus_structured")
            print(f"✅ Конституция РФ: {self.collections['constitution'].count()} чанков")
        except:
            print("⚠️  Коллекция Конституции не найдена")
        
        # ГК РФ
        try:
            self.collections['gk_rf'] = self.client.get_collection("gk_rf_structured")
            print(f"✅ ГК РФ: {self.collections['gk_rf'].count()} чанков")
        except:
            print("⚠️  Коллекция ГК РФ не найдена")
            
        # Все остальные кодексы
        try:
            self.collections['all_codes'] = self.client.get_collection("all_codes_structured")
            print(f"✅ Все кодексы: {self.collections['all_codes'].count()} чанков")
        except:
            print("⚠️  Коллекция all_codes_structured не найдена")
    
    def query(self, query_text: str, top_k: int = 15, code_filter: str = None) -> Tuple[str, List[Dict]]:
        """
        Поиск по всем кодексам. Увеличен top_k по умолчанию до 15.
        """
        query_embedding = self.model.encode(query_text).tolist()
        all_results = []
        
        if code_filter:
            collections_to_search = {code_filter: self.collections.get(code_filter)}
        else:
            collections_to_search = self.collections
        
        # Распределяем top_k между коллекциями
        k_per_collection = max(3, top_k // len(collections_to_search))
        
        for code_name, collection in collections_to_search.items():
            if collection is None:
                continue
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=k_per_collection
            )
            
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                all_results.append({
                    'code': code_name,
                    'text': doc,
                    'metadata': metadata,
                    'score': 1.0  # Placeholder для reranking
                })
        
        # Сортируем по релевантности (упрощённо — по порядку выдачи)
        all_results = all_results[:top_k]
        
        # Формируем контекст
        context = ""
        sources = []
        
        for result in all_results:
            code_name = result['code']
            metadata = result['metadata']
            
            if code_name == 'constitution':
                code_display = "Конституция РФ"
            elif code_name == 'gk_rf':
                part_name = metadata.get('part_name', '')
                code_display = f"ГК РФ ({part_name})"
            else:
                code_display = metadata.get('code_name', code_name)
            
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

if __name__ == "__main__":
    retriever = UnifiedRetriever()
    
    test_queries = [
        "Какая ответственность за кражу по УК РФ?",
        "Что говорит ТК РФ об увольнении?",
        "Как оформить развод по СК РФ?",
        "Какие налоги платят ИП по НК РФ?",
        "Сроки исковой давности по ГК РФ"
    ]
    
    for query in test_queries:
        print(f"\n{'#'*60}")
        print(f"🔍 ЗАПРОС: {query}")
        print(f"{'#'*60}")
        context, sources = retriever.query(query, top_k=15)
        print(f"\n📚 ИСТОЧНИКИ:")
        for s in sources:
            print(f"  - [{s['code_display']}] {s['metadata']}")
