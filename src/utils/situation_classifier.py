"""
Классификатор правовых ситуаций.
Определяет тип документа по запросу пользователя.
"""
import re
from typing import Dict, List, Tuple, Optional
from enum import Enum


class DocumentType(Enum):
    """Типы документов"""
    CLAIM_CIVIL_GENERAL = "claim_civil_general"  # Исковое заявление (общее)
    CLAIM_CONSUMER = "claim_consumer"  # Иск о защите прав потребителей
    CLAIM_LABOR_WAGE = "claim_labor_wage"  # Взыскание заработной платы
    CLAIM_LABOR_REINSTATEMENT = "claim_labor_reinstatement"  # Восстановление на работе
    CLAIM_DIVORCE = "claim_divorce"  # Расторжение брака
    CLAIM_ALIMONY = "claim_alimony"  # Взыскание алиментов
    ADMIN_CLAIM_KAS = "admin_claim_kas"  # Административное исковое заявление
    COMPLAINT_KOAP = "complaint_koap"  # Жалоба на постановление по КоАП
    APPLICATION_COURT_ORDER = "application_for_court_order"  # Заявление о судебном приказе
    OBJECTION_COURT_ORDER = "objection_to_court_order"  # Возражение на судебный приказ
    APPEAL_CIVIL = "appeal_civil"  # Апелляционная жалоба (ГПК)
    CASSATION_CIVIL = "cassation_civil"  # Кассационная жалоба (ГПК)
    SPECIAL_PROCEEDING = "special_proceeding_fact"  # Особое производство
    UNKNOWN = "unknown"  # Не определено


# Паттерны для определения типа документа
PATTERNS = {
    DocumentType.CLAIM_CONSUMER: {
        "keywords": [
            r"вернуть.*товар", r"некачественн.*товар", r"сломался.*товар",
            r"купил.*сломал", r"магазин.*вернуть.*деньг", r"бракованн.*товар",
            r"неисправн.*товар", r"товар.*ненадлежащ.*качеств", r"потребител.*прав",
            r"защит.*прав.*потребител", r"вернуть.*денег.*магазин",
            r"телефон.*сломал", r"ноутбук.*не работа", r"холодильник.*сломал"
        ],
        "priority": 10,
        "label": "Иск о защите прав потребителей"
    },
    
    DocumentType.CLAIM_LABOR_WAGE: {
        "keywords": [
            r"зарплат.*не плат", r"задержк.*зарплат", r"не выплач.*зарплат",
            r"задолженност.*зарплат", r"работодат.*не плат", r"взыск.*зарплат",
            r"жалованье.*не выплач", r"зарплат.*задерж", r"не получа.*зарплат"
        ],
        "priority": 9,
        "label": "Иск о взыскании заработной платы"
    },
    
    DocumentType.CLAIM_LABOR_REINSTATEMENT: {
        "keywords": [
            r"увол.*незаконн", r"восстанов.*работ", r"неправ.*увольн",
            r"уволил.*без причин", r"увольн.*без основ", r"меня.*уволил",
            r"уволен.*что.*делать", r"незаконн.*уволил"
        ],
        "priority": 9,
        "label": "Иск о восстановлении на работе"
    },
    
    DocumentType.CLAIM_DIVORCE: {
        "keywords": [
            r"развод", r"расторж.*брак", r"развест.*суд", r"хочу.*развест",
            r"развест.*муж", r"развест.*жен", r"расторгнуть.*брак"
        ],
        "priority": 8,
        "label": "Иск о расторжении брака"
    },
    
    DocumentType.CLAIM_ALIMONY: {
        "keywords": [
            r"алименты", r"взыск.*алимент", r"содержан.*ребенок",
            r"подать.*алимент", r"ребенок.*алимент", r"не плат.*алимент"
        ],
        "priority": 8,
        "label": "Иск о взыскании алиментов"
    },
    
    DocumentType.CLAIM_CIVIL_GENERAL: {
        "keywords": [
            r"долг.*вернуть", r"занял.*деньги", r"не возвращ.*деньг",
            r"расписк.*долг", r"договор.*займ", r"взыск.*денеж",
            r"имуществ.*спор", r"сосед.*занял", r"друг.*занял",
            r"одолж.*деньги", r"вернуть.*долг"
        ],
        "priority": 7,
        "label": "Исковое заявление (общее)"
    },
    
    DocumentType.ADMIN_CLAIM_KAS: {
        "keywords": [
            r"орган.*власт.*незаконн", r"чиновник.*бездействи", r"административ.*иск",
            r"обжал.*действи.*должностн", r"отказ.*государствен.*орган",
            r"незаконн.*решен.*орган", r"бездействи.*орган.*власт"
        ],
        "priority": 8,
        "label": "Административное исковое заявление"
    },
    
    DocumentType.COMPLAINT_KOAP: {
        "keywords": [
            r"постановлен.*коап", r"штраф.*гибдд", r"административ.*правонаруш",
            r"протокол.*коап", r"жалоб.*постановлен.*коап", r"обжал.*штраф.*гибдд"
        ],
        "priority": 8,
        "label": "Жалоба на постановление по КоАП"
    },
    
    DocumentType.APPLICATION_COURT_ORDER: {
        "keywords": [
            r"судебн.*приказ.*выдать", r"бесспорн.*взыскани", r"прост.*долг.*приказ",
            r"заявлен.*судебн.*приказ"
        ],
        "priority": 7,
        "label": "Заявление о судебном приказе"
    },
    
    DocumentType.OBJECTION_COURT_ORDER: {
        "keywords": [
            r"возражен.*судебн.*приказ", r"отмен.*приказ.*миров",
            r"не соглас.*судебн.*приказ"
        ],
        "priority": 7,
        "label": "Возражение на судебный приказ"
    },
    
    DocumentType.APPEAL_CIVIL: {
        "keywords": [
            r"апелляц.*жалоб", r"обжал.*решен.*суд", r"несоглас.*решен.*суд",
            r"подать.*апелляц"
        ],
        "priority": 6,
        "label": "Апелляционная жалоба"
    },
    
    DocumentType.CASSATION_CIVIL: {
        "keywords": [
            r"кассац.*жалоб", r"нарушен.*норм.*прав", r"судеб.*акт.*вступ.*сил",
            r"подать.*кассац"
        ],
        "priority": 6,
        "label": "Кассационная жалоба"
    },
    
    DocumentType.SPECIAL_PROCEEDING: {
        "keywords": [
            r"установ.*факт.*юридическ", r"родствен.*отношен.*установ",
            r"иждивен.*установ", r"принадлеж.*документ.*установ",
            r"факт.*имеющ.*юридическ.*значен"
        ],
        "priority": 7,
        "label": "Заявление об установлении факта"
    }
}


def classify_situation(query: str) -> Dict:
    """
    Классифицирует правовую ситуацию и определяет тип документа.
    
    Args:
        query: Запрос пользователя
    
    Returns:
        Словарь с результатом:
        {
            'doc_type': тип документа,
            'confidence': уверенность (0-1),
            'label': название типа,
            'matched_keywords': найденные ключевые слова
        }
    """
    query_lower = query.lower()
    
    scores = {}
    
    # Проверяем каждый тип документа
    for doc_type, config in PATTERNS.items():
        matched = []
        
        for pattern in config["keywords"]:
            if re.search(pattern, query_lower):
                matched.append(pattern)
        
        if matched:
            # Score = количество совпадений × приоритет
            score = len(matched) * config["priority"]
            scores[doc_type] = {
                'score': score,
                'matched': matched,
                'priority': config["priority"]
            }
    
    # Если ничего не найдено — возвращаем UNKNOWN
    if not scores:
        return {
            'doc_type': DocumentType.UNKNOWN.value,
            'confidence': 0.0,
            'label': 'Не удалось определить тип документа',
            'matched_keywords': []
        }
    
    # Выбираем тип с максимальным score
    best_type = max(scores.items(), key=lambda x: x[1]['score'])
    doc_type, info = best_type
    
    # Нормализуем confidence (0-1)
    max_possible_score = 5 * info['priority']  # Максимум 5 совпадений
    confidence = min(1.0, info['score'] / max_possible_score)
    
    return {
        'doc_type': doc_type.value,
        'confidence': confidence,
        'label': PATTERNS[doc_type]['label'],
        'matched_keywords': info['matched']
    }


# ===== ТЕСТЫ =====
if __name__ == "__main__":
    print("=" * 70)
    print("ТЕСТЫ КЛАССИФИКАТОРА СИТУАЦИЙ")
    print("=" * 70)
    
    tests = [
        "Сосед занял 100 000 рублей и не возвращает",
        "Купил телефон, сломался через неделю, хочу вернуть деньги",
        "Меня уволили без причины, что делать?",
        "Муж не платит алименты на ребёнка",
        "Хочу развестись с женой",
        "Чиновник отказал в выдаче справки",
        "Получил штраф от ГИБДД, хочу обжаловать",
        "Нужно установить факт родственных отношений для наследства",
        "Хочу подать апелляцию на решение суда",
        "Работодатель задерживает зарплату уже 3 месяца"
    ]
    
    for query in tests:
        result = classify_situation(query)
        print(f"\n📝 Запрос: '{query}'")
        print(f"   🎯 Тип: {result['label']}")
        print(f"   📊 Уверенность: {result['confidence']:.0%}")
        print(f"   🔑 Ключевые слова: {result['matched_keywords'][:3]}")
