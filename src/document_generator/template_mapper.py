"""
Умный маппинг запроса пользователя → тип документа.
Использует pymorphy3 для морфологии + расширенные паттерны.
"""
import re
from typing import Optional, Tuple
import pymorphy3

# Инициализация морфологического анализатора
morph = pymorphy3.MorphAnalyzer()

# Базовые паттерны (для быстрого поиска)
KEYWORD_MAPPING = {
    "claim_consumer": [
        r"защит.*прав.*потребител", r"вернуть.*товар", r"некачественн.*товар",
        r"брак.*товар", r"неисправн.*товар", r"потребител.*иск",
        r"купил.*сломал", r"сломал.*недел", r"телефон.*сломал",
        r"хочу.*вернуть.*деньг", r"вернуть.*деньг.*магазин",
        r"купил.*магазин.*вернуть", r"неисправн.*вернуть.*деньг",
        r"товар.*ненадлежащ.*качеств", r"ноутбук.*не работа",
        r"вернуть.*деньг.*не работа"
    ],
    "claim_labor_wage": [
        r"взыск.*зарплат", r"задолженност.*зарплат", r"не выплат.*зарплат",
        r"задержк.*зарплат", r"трудов.*иск.*зарплат",
        r"не плат.*зарплат", r"зарплат.*не получа", r"задержк.*выплат",
        r"задерж.*выплат.*зарплат", r"работодат.*задерж.*зарплат",
        r"зарплат.*задерж", r"не получа.*зарплат.*месяц",
        r"куда.*обрат.*зарплат",
        # Новые паттерны для синонимов
        r"жалованье.*не выплач", r"не выплач.*жалованье",
        r"жалованье.*задерж", r"задерж.*жалованье"
    ],
    "claim_labor_reinstatement": [
        r"восстанов.*работ", r"увольн.*незаконн", r"неправом.*увольн",
        r"трудов.*иск.*восстанов", r"уволил.*незаконн",
        r"уволил.*без причин", r"увольн.*без основ", r"уволил.*незакон",
        r"меня.*уволил", r"уволен.*что.*делать", r"неправ.*уволил"
    ],
    "claim_divorce": [
        r"развод", r"расторж.*брак", r"развест.*суд", r"хочу.*развест",
        r"развест.*муж", r"развест.*жен",
        # Новые паттерны
        r"расторгнуть.*брак", r"хочу.*расторгнуть"
    ],
    "claim_alimony": [
        r"алименты", r"взыск.*алимент", r"содержан.*ребенок",
        r"подать.*алимент", r"ребенок.*алимент"
    ],
    "claim_parental_rights": [
        r"лишен.*родит.*прав", r"огранич.*родит.*прав",
        r"определ.*мест.*жит.*ребен", r"спор.*о.*детях"
    ],
    "claim_housing": [
        r"жилищн.*иск", r"высел.*квартир", r"призн.*прав.*собственн.*жилищ",
        r"раздел.*квартир", r"жилищн.*спор"
    ],
    "claim_land": [
        r"земельн.*участок", r"границ.*участок", r"сервитут.*земельн",
        r"земельн.*спор"
    ],
    "claim_arbitration": [
        r"арбитражн.*иск", r"эконом.*спор", r"хозяйств.*спор",
        r"взыск.*долг.*организ", r"арбитражн.*суд"
    ],
    "claim_civil_general": [
        r"исков.*заявлен", r"взыск.*долг", r"возмещ.*ущерб",
        r"граждан.*иск", r"подать.*иск.*суд", r"иск.*суд.*на"
    ],
    "appeal_civil": [
        r"апелляц.*жалоб", r"обжалов.*решен.*суд",
        r"обжаловать.*суд", r"апелляция.*суд"
    ],
    "appeal_arbitration": [r"апелляц.*жалоб.*арбитраж"],
    "cassation_civil": [r"кассац.*жалоб"],
    "cassation_arbitration": [r"кассац.*жалоб.*арбитраж"],
    "complaint_koap": [
        r"жалоб.*коап", r"обжалов.*постанов.*администр",
        r"администр.*правонаруш", r"штраф.*гибдд.*обжалов"
    ],
    "objection_to_court_order": [
        r"возраж.*суд.*приказ", r"отмен.*суд.*приказ"
    ],
    "application_for_court_order": [
        r"заявл.*суд.*приказ", r"выда.*суд.*приказ"
    ]
}

# Синонимы привязаны к ТИПАМ ДОКУМЕНТОВ (исправлено!)
SYNONYMS_BY_DOCTYPE = {
    "claim_consumer": [
        "телефон", "ноутбук", "продукт", "продукция", "покупка",
        "неисправность", "дефект", "сломался", "не работает", "неисправен"
    ],
    "claim_labor_wage": [
        "зарплата", "жалованье", "заработный", "вознаграждение",
        "выплачивать", "получать", "задолженность"
    ],
    "claim_divorce": [
        "расторгнуть", "брак", "развод", "развестись", "супруг"
    ],
    "claim_alimony": [
        "алименты", "содержание", "ребенок", "дети"
    ],
    "claim_labor_reinstatement": [
        "увольнение", "восстановление", "работа", "трудовой"
    ]
}


def normalize_text(text: str) -> str:
    """
    Нормализует текст с помощью pymorphy3.
    Приводит все слова к нормальной форме.
    """
    words = text.lower().split()
    normalized = []
    for word in words:
        # Убираем знаки препинания
        clean_word = re.sub(r'[^\w]', '', word)
        if clean_word:
            parsed = morph.parse(clean_word)
            if parsed:
                normalized.append(parsed[0].normal_form)
            else:
                normalized.append(clean_word)
    return ' '.join(normalized)


def map_query_to_template(user_query: str) -> Tuple[Optional[str], float]:
    """
    Определяет тип документа по запросу пользователя.
    Использует 2 уровня: быстрый (regex) + точный (морфология).
    """
    query_lower = user_query.lower()
    query_normalized = normalize_text(user_query)
    
    scores = {}
    
    # Уровень 1: Быстрый поиск по regex в исходном тексте
    for doc_type, keywords in KEYWORD_MAPPING.items():
        score = 0.0
        for keyword in keywords:
            if re.search(keyword, query_lower):
                score += 1.0
        if score > 0:
            scores[doc_type] = score
    
    # Уровень 2: Морфологический поиск (если regex не дал уверенного результата)
    if not scores or max(scores.values()) < 2:
        for doc_type, synonyms in SYNONYMS_BY_DOCTYPE.items():
            match_count = 0
            for synonym in synonyms:
                # Ищем синоним в нормализованном тексте
                if synonym in query_normalized:
                    match_count += 1
            
            # Если найдено 2+ синонимов — добавляем очко
            if match_count >= 2:
                scores[doc_type] = scores.get(doc_type, 0) + 0.5
    
    if not scores:
        return None, 0.0
    
    best_match = max(scores, key=scores.get)
    best_score = scores[best_match]
    
    # Нормализуем уверенность
    confidence = min(0.5 + (best_score - 1) * 0.25, 1.0)
    
    return best_match, confidence


def test_mapping():
    """Тест маппинга запросов."""
    test_cases = [
        # Стандартные
        ("Хочу подать иск о защите прав потребителей", "claim_consumer"),
        ("Мне не платят зарплату уже 3 месяца", "claim_labor_wage"),
        ("Меня незаконно уволили", "claim_labor_reinstatement"),
        ("Хочу развестись с мужем", "claim_divorce"),
        ("Нужно подать на алименты", "claim_alimony"),
        
        # Разговорные
        ("Купил телефон, он сломался через неделю", "claim_consumer"),
        ("Работодатель задерживает выплату зарплаты", "claim_labor_wage"),
        ("Меня уволили без причины", "claim_labor_reinstatement"),
        
        # Синонимы (морфология)
        ("Жалованье не выплачивают уже полгода", "claim_labor_wage"),
        ("Хочу расторгнуть брак", "claim_divorce"),
        ("Ноутбук не работает, хочу вернуть деньги", "claim_consumer"),
        
        # Сложные
        ("Подать иск в суд на соседа за шум", "claim_civil_general"),
        ("Меня уволили с работы, я хочу восстановиться", "claim_labor_reinstatement"),
    ]
    
    print("🧪 ТЕСТ УМНОГО МАППИНГА (ИСПРАВЛЕННАЯ ВЕРСИЯ)")
    print("="*60)
    
    correct = 0
    for query, expected in test_cases:
        doc_type, confidence = map_query_to_template(query)
        status = "✅" if doc_type == expected else "❌"
        if doc_type == expected:
            correct += 1
        print(f"\n{status} Запрос: {query[:60]}...")
        print(f"   Ожидалось: {expected}")
        print(f"   Получено: {doc_type} (уверенность: {confidence:.2f})")
    
    print(f"\n{'='*60}")
    print(f"📊 РЕЗУЛЬТАТ: {correct}/{len(test_cases)} ({correct/len(test_cases)*100:.0f}%)")


if __name__ == "__main__":
    test_mapping()
