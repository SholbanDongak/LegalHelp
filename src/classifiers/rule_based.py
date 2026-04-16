"""Rule-based классификатор для MVP"""

from typing import List, Tuple
from .base import BaseClassifier


class RuleBasedClassifier(BaseClassifier):
    """Классификатор на основе ключевых слов"""

    def predict(self, text: str) -> str:
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

    def predict_with_confidence(self, text: str) -> Tuple[str, float]:
        return self.predict(text), 1.0

    def get_available_classes(self) -> List[str]:
        return ["fns", "prosecutor", "court", "counterparty",
                "roskomnadzor", "fas", "labor_inspection", "other"]
