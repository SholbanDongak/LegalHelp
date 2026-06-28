import re
from typing import List, Tuple, Set


class CitationVerifier:
    """
    Проверяет, что упомянутые статьи существуют в корпусе.
    """
    
    def __init__(self, available_articles: Set[str] = None):
        self.available_articles = available_articles or set()
    
    def set_available_articles(self, articles: Set[str]):
        self.available_articles = articles
    
    def extract_citations(self, text: str) -> List[str]:
        """
        Извлекает упоминания статей из текста (учитывает все падежи).
        """
        # Паттерны для поиска статей (все падежи)
        patterns = [
            r'[Сс]тать[яиюейе]\s+(\d+)',  # статья, статье, статью, статьей, статьи
            r'art\.?\s*(\d+)',              # art. 15, art15
            r'ст\.\s*(\d+)',                # ст. 15
            r'пунк[ттеу]\s+(\d+)\s+стать[яиюейе]\s+(\d+)',  # пункт 1 статьи 15
        ]
        
        cited_articles = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if isinstance(matches[0], tuple) if matches else False:
                # Для паттерна "пункт X статьи Y" берем номер статьи (второй элемент)
                cited_articles.extend([match[1] for match in matches])
            else:
                cited_articles.extend(matches)
        
        return list(set(cited_articles))
    
    def verify(self, response: str) -> Tuple[bool, List[str]]:
        """
        Проверяет цитаты.
        """
        if not self.available_articles:
            return True, []
        
        cited_articles = self.extract_citations(response)
        
        errors = []
        for article_num in cited_articles:
            if article_num not in self.available_articles:
                errors.append(f"Статья {article_num} не найдена в корпусе")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def verify_and_filter(self, response: str) -> str:
        """
        Проверяет и добавляет предупреждение при ошибках.
        """
        is_valid, errors = self.verify(response)
        
        if is_valid:
            return response
        
        warning = "\n\n⚠️ ВНИМАНИЕ: Некоторые упомянутые статьи не найдены в корпусе:\n"
        warning += "\n".join(f"  - {error}" for error in errors)
        warning += "\nПожалуйста, проверьте информацию в официальных источниках."
        
        return response + warning
