"""Базовый абстрактный класс для всех классификаторов"""

from abc import ABC, abstractmethod
from typing import List, Tuple


class BaseClassifier(ABC):
    """Абстрактный базовый класс для классификации документов"""

    @abstractmethod
    def predict(self, text: str) -> str:
        """Возвращает тип документа"""
        pass

    @abstractmethod
    def predict_with_confidence(self, text: str) -> Tuple[str, float]:
        """Возвращает тип документа и уверенность (0-1)"""
        pass

    @abstractmethod
    def get_available_classes(self) -> List[str]:
        """Возвращает список всех возможных классов"""
        pass
