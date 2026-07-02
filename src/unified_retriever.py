from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import chromadb
import numpy as np
import pymorphy3
import re
from typing import List, Dict, Tuple


# Умный роутинг: для каждого типа документа — свои коллекции
DOC_TYPE_COLLECTIONS = {
    'claim_civil_general': ['gk_rf', 'all_codes', 'ruslawod'],  # Гражданские споры
    'claim_consumer': ['zozpp_rf', 'gk_rf', 'ruslawod'],       # Защита прав потребителей
    'claim_labor_wage': ['all_codes', 'ruslawod'],             # Трудовые споры
    'claim_labor_reinstatement': ['all_codes', 'ruslawod'],    # Трудовые споры
    'claim_divorce': ['all_codes', 'ruslawod'],                # Семейные споры
    'claim_alimony': ['all_codes', 'ruslawod'],                # Семейные споры
    'admin_claim_kas': ['all_codes', 'ruslawod'],              # Административные
    'complaint_koap': ['all_codes', 'ruslawod'],               # КоАП
    'appeal_civil': ['all_codes', 'ruslawod'],                 # Процессуальные
    'cassation_civil': ['all_codes', 'ruslawod'],              # Процессуальные
    'default': ['constitution', 'gk_rf', 'all_codes', 'zozpp_rf', 'ruslawod']  # Всё
}


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
        
        # Bi-encoder для семантического поиска (кодексы, размерность 1024)
        self.bi_encoder = SentenceTransformer('intfloat/multilingual-e5-large')
        print("✅ Bi-encoder (E5-Large, dim=1024) загружен")
        
        # Bi-encoder для большой базы RusLawOD (размерность 384)
        try:
            self.bi_encoder_small = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("✅ Bi-encoder (MiniLM, dim=384) загружен для RusLawOD")
        except Exception as e:
            print(f"⚠️  Не удалось загрузить MiniLM: {e}")
            self.bi_encoder_small = None
        
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
            'неосновательное обогащение': ['необоснованное получение', 'безвозмездное получение', 'глава 60', 'ошибочный перевод', 'случайный перевод', 'перевод не тому'],
            'ошибочный перевод': ['неосновательное обогащение', 'случайный перевод', 'перевод по ошибке', 'статья 1102', 'возврат денег'],
            'возврат денег': ['неосновательное обогащение', 'статья 1102', 'глава 60', 'ошибочный перевод'],
            'долг': ['задолженность', 'обязательство', 'статья 309', 'статья 310', 'не возвращает'],
            'занять': ['договор займа', 'статья 807', 'статья 808', 'долг', 'заём'],
            'вернуть': ['возврат', 'статья 1102', 'неосновательное обогащение'],
            'расписка': ['договор займа', 'статья 808', 'статья 807'],
            'перевод': ['банковский перевод', 'безналичный расчёт', 'платёж'],
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
        
        # ChromaDB — МАЛЕНЬКАЯ база (кодексы, структурированные данные)
        self.client = chromadb.PersistentClient(path="./chroma_db_structured")
        self.collections = {}
        
        # ChromaDB — БОЛЬШАЯ база (RusLawOD, 5 млн чанков)
        self.big_client = chromadb.PersistentClient(path="./legal_chromadb")
        self.big_collections = {}
        
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
        
        # Закон РФ О защите прав потребителей
        try:
            self.collections['zozpp_rf'] = self.client.get_collection("zozpp_structured")
            print(f"✅ ЗоЗПП РФ: {self.collections['zozpp_rf'].count()} чанков")
        except:
            print("⚠️  Коллекция zozpp_structured не найдена")
        
        # Загружаем БОЛЬШУЮ базу (только семантический поиск, без BM25)
        try:
            self.big_collections['ruslawod'] = self.big_client.get_collection("ruslawod")
            print(f"✅ RusLawOD (полная база): {self.big_collections['ruslawod'].count():,} чанков")
        except Exception as e:
            print(f"⚠️  Коллекция ruslawod не найдена: {e}")
        
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
            print(f"   Расширенный: '{expanded_query}'")
            print(f"   Найдено ключевых слов: {found_keywords}")
        else:
            expanded_query = query
            print(f"⚠️  Query Expansion: не найдено ключевых слов для '{query}'")
            print(f"   Леммы запроса: {query_lemmas[:10]}")
            print(f"   Леммы запроса: {query_lemmas}")
            print(f"   Найдено ключевых слов: {found_keywords}")
            print(f"   Расширенный: '{expanded_query}'")
            return expanded_query
        
        print(f"🔍 Query Expansion: ключевых слов не найдено в словаре")
        return query
    
    def _search_big_collection(self, query: str, top_k: int = 10) -> List[Dict]:
        """Семантический поиск в большой базе RusLawOD (без BM25)."""
        results = []
        
        # Используем модель с размерностью 384 для RusLawOD
        if not self.bi_encoder_small:
            print("⚠️  Модель MiniLM не загружена, пропускаем поиск в RusLawOD")
            return results
        
        for coll_name, collection in self.big_collections.items():
            try:
                query_embedding = self.bi_encoder_small.encode(query).tolist()
                res = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k * 2  # Берём больше для reranking
                )
                
                if res and res.get('documents'):
                    for doc, meta, doc_id in zip(
                        res['documents'][0],
                        res.get('metadatas', [[]])[0] if res.get('metadatas') else [{}] * len(res['documents'][0]),
                        res['ids'][0]
                    ):
                        results.append({
                            'code': 'ruslawod',  # Добавляем ключ 'code'
                            'text': doc,
                            'metadata': meta if isinstance(meta, dict) else {},
                            'source': meta.get('source', coll_name) if isinstance(meta, dict) else coll_name,
                            'id': doc_id,
                            'score': 0.5  # Базовый score, будет улучшен reranking'ом
                        })
            except Exception as e:
                print(f"⚠️  Ошибка в коллекции {coll_name}: {e}")
        return results
    
    def _merge_results(self, primary: List[Dict], secondary: List[Dict], top_k: int) -> List[Dict]:
        """Объединяет результаты из двух источников, убирая дубликаты."""
        seen_texts = set()
        merged = []
        
        # Сначала добавляем результаты из основной базы (они уже reranked)
        for res in primary:
            text_key = res.get('text', '')[:100]
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                merged.append(res)
        
        # Потом добавляем из большой базы, если их нет в основной
        for res in secondary:
            text_key = res.get('text', '')[:100]
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                merged.append(res)
        
        # Если есть reranking — переранжируем всё вместе
        if self.use_reranking and len(merged) > top_k:
            try:
                merged = self._rerank(merged[0].get('query', ''), merged, top_k)
            except:
                merged = merged[:top_k]
        else:
            merged = merged[:top_k]
        
        return merged
    
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
        
        candidates_to_retrieve = top_k * 10 if self.use_reranking else top_k * 2
        
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
        
        # Этап 5: RusLawOD отключён по умолчанию (даёт шумные результаты)
        # Раскомментируйте, если нужно искать по полной базе ФЗ
        # if self.big_collections:
        #     try:
        #         big_results = self._search_big_collection(query_text, top_k=top_k)
        #         final_results = self._merge_results(final_results, big_results, top_k)
        #         print(f"🔍 Добавлено {len(big_results)} результатов из RusLawOD")
        #     except Exception as e:
        #         print(f"⚠️  Ошибка поиска в RusLawOD: {e}")
        
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
