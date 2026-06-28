from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import chromadb
import numpy as np
import pymorphy3
import re
from typing import List, Dict, Tuple

class UnifiedRetriever:
    """
    Универсальный retriever с гибридным поиском, query expansion и reranking.
    
    Архитектура:
    1. Query Expansion — расширение запроса синонимами (с лемматизацией!)
    2. Семантический поиск (bi-encoder, E5-Large) → топ-30 кандидатов
    3. BM25 поиск с лемматизацией → топ-30 кандидатов
    4. Reciprocal Rank Fusion (RRF) → объединение результатов
    5. Reranking (cross-encoder, bge-reranker-v2-m3) → топ-5 финальных
    """
    
    def __init__(self, use_reranking: bool = True, use_hybrid: bool = True, use_query_expansion: bool = True):
        print("🔧 Инициализация retriever...")
        
        # Bi-encoder для семантического поиска
        self.bi_encoder = SentenceTransformer('intfloat/multilingual-e5-large')
        print("✅ Bi-encoder (E5-Large) загружен")
        
        # Cross-encoder для reranking
        self.use_reranking = use_reranking
        if use_reranking:
            try:
                self.cross_encoder = CrossEncoder('BAAI/bge-reranker-v2-m3')
                print("✅ Cross-encoder (bge-reranker-v2-m3) загружен для reranking")
            except Exception as e:
                print(f"⚠️  Не удалось загрузить cross-encoder: {e}")
                self.use_reranking = False
        
        # Морфологический анализатор для лемматизации
        self.morph = pymorphy3.MorphAnalyzer()
        print("✅ Морфологический анализатор (pymorphy3) загружен")
        
        # Query Expansion
        self.use_query_expansion = use_query_expansion
        if use_query_expansion:
            print("✅ Query Expansion включён")
        
        # Словарь юридических синонимов (ключи — в НОРМАЛЬНОЙ форме!)
        self.legal_synonyms = {
            'кража': ['тайное хищение', 'хищение чужого имущества', 'статья 158'],
            'грабеж': ['открытое хищение', 'статья 161'],
            'грабёж': ['открытое хищение', 'статья 161'],
            'разбой': ['хищение с применением насилия', 'насильственное хищение', 'статья 162'],
            'мошенничество': ['обман', 'хищение обманом', 'статья 159'],
            'неосновательное обогащение': ['необоснованное получение', 'безвозмездное получение', 'глава 60'],
            'убийство': ['лишение жизни', 'умышленное причинение смерти', 'статья 105'],
            'изнасилование': ['насильственное половое сношение', 'статья 131'],
            'взятка': ['получение должностным лицом', 'коррупция', 'статья 290'],
            'хищение': ['присвоение', 'растрата', 'статья 160'],
            'увольнение': ['расторжение трудового договора', 'прекращение трудовых отношений', 'статья 80', 'статья 81'],
            'алименты': ['содержание детей', 'обязанность содержать', 'глава 49'],
            'развод': ['расторжение брака', 'прекращение брака', 'статья 21', 'статья 22'],
            'наследство': ['наследование', 'наследник', 'глава 63'],
            'договор': ['соглашение', 'контракт', 'глава 27'],
            'исковая давность': ['срок исковой давности', 'статья 196', 'статья 195', 'глава 12'],
            'красть': ['тайное хищение', 'хищение чужого имущества', 'статья 158'],
        }
        
        # ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_db_structured")
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
            
        try:
            self.collections['all_codes'] = self.client.get_collection("all_codes_structured")
            print(f"✅ Все кодексы: {self.collections['all_codes'].count()} чанков")
        except:
            print("⚠️  Коллекция all_codes_structured не найдена")
        
        # Инициализация BM25 для гибридного поиска
        self.use_hybrid = use_hybrid
        self.bm25_indexes = {}
        
        if use_hybrid:
            print("🔧 Инициализация BM25 индексов с лемматизацией...")
            for code_name, collection in self.collections.items():
                if collection is None:
                    continue
                
                try:
                    all_docs = collection.get()
                    tokenized_docs = []
                    doc_ids = []
                    
                    for doc_id, doc_text in zip(all_docs['ids'], all_docs['documents']):
                        tokens = self._lemmatize_and_tokenize(doc_text)
                        tokenized_docs.append(tokens)
                        doc_ids.append(doc_id)
                    
                    bm25 = BM25Okapi(tokenized_docs)
                    self.bm25_indexes[code_name] = {
                        'bm25': bm25,
                        'doc_ids': doc_ids
                    }
                    
                    print(f"✅ BM25 индекс для {code_name}: {len(doc_ids)} документов (с лемматизацией)")
                except Exception as e:
                    print(f"⚠️  Не удалось создать BM25 индекс для {code_name}: {e}")
    
    def _expand_query(self, query: str) -> str:
        """
        Расширение запроса синонимами из юридического словаря.
        ВАЖНО: лемматизируем запрос ПЕРЕД поиском по словарю!
        
        Пример:
            "ответственность за кражу" → леммы: "ответственность за кража"
            → находим "кража" в словаре
            → добавляем: "тайное хищение", "хищение чужого имущества", "статья 158"
            → расширенный запрос: "ответственность за кражу тайное хищение хищение чужого имущества статья 158"
        """
        if not self.use_query_expansion:
            return query
        
        # ЛЕММАТИЗИРУЕМ запрос, чтобы найти ключевые слова в любой форме
        query_lemmas = self._lemmatize_and_tokenize(query)
        
        expanded_terms = []
        found_keywords = []
        
        # Ищем ключевые слова из словаря в ЛЕММАХ запроса
        for keyword, synonyms in self.legal_synonyms.items():
            if keyword in query_lemmas:
                expanded_terms.extend(synonyms)
                found_keywords.append(keyword)
        
        # Добавляем расширенные термины к запросу
        if expanded_terms:
            expanded_query = query + " " + " ".join(expanded_terms)
            print(f"🔍 Query Expansion:")
            print(f"   Исходный: '{query}'")
            print(f"   Леммы запроса: {query_lemmas}")
            print(f"   Найдено ключевых слов: {found_keywords}")
            print(f"   Расширенный: '{expanded_query}'")
            return expanded_query
        
        print(f"🔍 Query Expansion: ключевых слов не найдено в словаре")
        return query
    
    def _lemmatize_and_tokenize(self, text: str) -> List[str]:
        """Лемматизация и токенизация текста."""
        text = re.sub(r'[^\w\s\-]', ' ', text)
        words = text.lower().split()
        
        lemmas = []
        for word in words:
            if len(word) > 2:
                parsed = self.morph.parse(word)
                if parsed:
                    lemmas.append(parsed[0].normal_form)
                else:
                    lemmas.append(word)
            else:
                lemmas.append(word)
        
        return lemmas
    
    def _bm25_search(self, query: str, code_name: str, top_k: int = 30) -> List[str]:
        """BM25 поиск с лемматизацией."""
        if code_name not in self.bm25_indexes:
            return []
        
        bm25_data = self.bm25_indexes[code_name]
        bm25 = bm25_data['bm25']
        doc_ids = bm25_data['doc_ids']
        
        query_tokens = self._lemmatize_and_tokenize(query)
        scores = bm25.get_scores(query_tokens)
        
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [doc_ids[i] for i in top_indices if scores[i] > 0]
    
    def _reciprocal_rank_fusion(self, results_list: List[List[Dict]], k: int = 60) -> List[Dict]:
        """Reciprocal Rank Fusion (RRF)."""
        rrf_scores = {}
        
        for results in results_list:
            for rank, result in enumerate(results):
                doc_id = result['metadata'].get('article_eid', '')
                if doc_id not in rrf_scores:
                    rrf_scores[doc_id] = {
                        'score': 0.0,
                        'result': result
                    }
                rrf_scores[doc_id]['score'] += 1.0 / (k + rank + 1)
        
        sorted_results = sorted(rrf_scores.values(), key=lambda x: x['score'], reverse=True)
        return [item['result'] for item in sorted_results]
    
    def _rerank(self, query: str, candidates: List[Dict], top_k: int = 5) -> List[Dict]:
        """Пересортировка кандидатов через cross-encoder."""
        if not self.use_reranking or not candidates:
            return candidates[:top_k]
        
        pairs = [(query, cand['text']) for cand in candidates]
        scores = self.cross_encoder.predict(pairs)
        
        for cand, score in zip(candidates, scores):
            cand['rerank_score'] = float(score)
        
        sorted_candidates = sorted(candidates, key=lambda x: x['rerank_score'], reverse=True)
        return sorted_candidates[:top_k]
    
    def query(self, query_text: str, top_k: int = 5, code_filter: str = None) -> Tuple[str, List[Dict]]:
        """Гибридный поиск с query expansion, лемматизацией и reranking."""
        # Этап 0: Query Expansion (с лемматизацией!)
        expanded_query = self._expand_query(query_text)
        
        candidates_to_retrieve = top_k * 6 if self.use_reranking else top_k
        
        query_embedding = self.bi_encoder.encode(expanded_query).tolist()
        all_candidates = []
        
        if code_filter:
            collections_to_search = {code_filter: self.collections.get(code_filter)}
        else:
            collections_to_search = self.collections
        
        k_per_collection = max(10, candidates_to_retrieve // len(collections_to_search))
        
        # Этап 1: Семантический поиск (bi-encoder)
        for code_name, collection in collections_to_search.items():
            if collection is None:
                continue
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=k_per_collection
            )
            
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                all_candidates.append({
                    'code': code_name,
                    'text': doc,
                    'metadata': metadata,
                    'semantic_score': 1.0
                })
        
        # Этап 2: BM25 поиск с лемматизацией
        if self.use_hybrid:
            bm25_candidates = []
            
            for code_name, collection in collections_to_search.items():
                if collection is None or code_name not in self.bm25_indexes:
                    continue
                
                bm25_doc_ids = self._bm25_search(expanded_query, code_name, top_k=k_per_collection)
                
                if bm25_doc_ids:
                    bm25_results = collection.get(ids=bm25_doc_ids)
                    
                    for doc, metadata in zip(bm25_results['documents'], bm25_results['metadatas']):
                        bm25_candidates.append({
                            'code': code_name,
                            'text': doc,
                            'metadata': metadata,
                            'bm25_score': 1.0
                        })
            
            # Этап 3: Reciprocal Rank Fusion
            if bm25_candidates:
                all_candidates = self._reciprocal_rank_fusion([all_candidates, bm25_candidates])
        
        # Этап 4: Reranking через cross-encoder
        if self.use_reranking:
            final_results = self._rerank(query_text, all_candidates, top_k=top_k)
        else:
            final_results = all_candidates[:top_k]
        
        # Формируем контекст и источники
        context = ""
        sources = []
        
        for result in final_results:
            code_name = result['code']
            metadata = result['metadata']
            
            if code_name == 'constitution':
                code_display = "Конституция РФ"
            elif code_name == 'gk_rf':
                part_name = metadata.get('part_name', '')
                code_display = f"ГК РФ ({part_name})"
            else:
                code_display = metadata.get('code_name', code_name)
            
            rerank_info = ""
            if 'rerank_score' in result:
                rerank_info = f" [score: {result['rerank_score']:.3f}]"
            
            context += f"\n{'='*60}\n"
            context += f"[{code_display}] {metadata.get('metadata', '')}{rerank_info}\n"
            context += f"{'='*60}\n"
            context += f"{result['text']}\n"
            
            sources.append({
                'code': code_name,
                'code_display': code_display,
                'article_num': metadata.get('article_num', ''),
                'article_eid': metadata.get('article_eid', ''),
                'metadata': metadata.get('metadata', ''),
                'rerank_score': result.get('rerank_score', None)
            })
        
        return context, sources


if __name__ == "__main__":
    retriever = UnifiedRetriever(use_reranking=True, use_hybrid=True, use_query_expansion=True)
    
    test_queries = [
        "Какие статьи ГК РФ регулируют неосновательное обогащение?",
        "Какая ответственность за кражу по УК РФ?",
        "Что говорит ТК РФ об увольнении?",
        "Какая ответственность за грабеж?",
        "Какая ответственность за мошенничество?"
    ]
    
    for query in test_queries:
        print(f"\n{'#'*60}")
        print(f"🔍 ЗАПРОС: {query}")
        print(f"{'#'*60}")
        context, sources = retriever.query(query, top_k=5)
        print(f"\n📚 ТОП-5 ИСТОЧНИКОВ (после reranking):")
        for i, s in enumerate(sources, 1):
            score = f" [score: {s['rerank_score']:.3f}]" if s.get('rerank_score') else ""
            print(f"{i}. [{s['code_display']}] {s['metadata']}{score}")
