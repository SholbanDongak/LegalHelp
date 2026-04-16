"""Классификация типа входящего документа"""

def classify_document(text: str) -> str:
    """
    Определяет тип документа по тексту.
    Возвращает: fns, court, counterparty, roskomnadzor, fas, labor_inspection, prosecutor, other
    """
    text_lower = text.lower()
    
    # ФНС
    if any(word in text_lower for word in ['налоговая', 'фнс', 'предоставить документы', 'требование о представлении']):
        return "fns"
    
    # Прокуратура
    if any(word in text_lower for word in ['прокуратура', 'прокурор', 'представление прокурора']):
        return "prosecutor"
    
    # Суд
    if any(word in text_lower for word in ['суд', 'определение', 'исковое заявление', 'судебное заседание']):
        return "court"
    
    # Контрагент
    if any(word in text_lower for word in ['претензия', 'оферта', 'договор', 'рекламация', 'требование оплаты']):
        return "counterparty"
    
    # Роскомнадзор
    if any(word in text_lower for word in ['роскомнадзор', 'персональные данные', '152-фз']):
        return "roskomnadzor"
    
    # ФАС
    if any(word in text_lower for word in ['фас', 'антимонопольная', 'жалоба', 'нарушение антимонопольного']):
        return "fas"
    
    # Трудовая инспекция
    if any(word in text_lower for word in ['трудовая инспекция', 'гит', 'охрана труда', 'трудовой кодекс']):
        return "labor_inspection"
    
    return "other"
