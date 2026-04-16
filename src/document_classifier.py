"""Классификация типа входящего документа"""


def classify_document(text: str) -> str:
    """
    Определяет тип документа по тексту.
    Возвращает: fns, court, counterparty, roskomnadzor, fas, labor_inspection, prosecutor, other
    """
    text_lower = text.lower()

    if any(word in text_lower for word in ['налоговая', 'фнс', 'предоставить документы']):
        return "fns"

    if any(word in text_lower for word in ['прокуратура', 'прокурор', 'представление']):
        return "prosecutor"

    if any(word in text_lower for word in ['суд', 'определение', 'исковое заявление']):
        return "court"

    if any(word in text_lower for word in ['претензия', 'оферта', 'договор', 'рекламация']):
        return "counterparty"

    if any(word in text_lower for word in ['роскомнадзор', 'персональные данные', '152-фз']):
        return "roskomnadzor"

    if any(word in text_lower for word in ['фас', 'антимонопольная', 'жалоба']):
        return "fas"

    if any(word in text_lower for word in ['трудовая инспекция', 'гит', 'охрана труда']):
        return "labor_inspection"

    return "other"
