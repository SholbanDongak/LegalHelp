"""
Парсер для garant.ru - извлечение статей кодексов из HTML.
"""
import requests
from bs4 import BeautifulSoup
import re
import json
from typing import List, Dict

class GarantParser:
    """Парсер HTML-страниц кодексов с garant.ru"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9',
        }
        self.session = requests.Session()
    
    def parse_code(self, url: str, code_name: str, full_name: str) -> Dict:
        """
        Парсит кодекс с garant.ru
        
        Args:
            url: URL страницы кодекса
            code_name: Краткое название (например, "ЗК РФ")
            full_name: Полное название (например, "Земельный кодекс Российской Федерации")
        
        Returns:
            Словарь с метаданными и статьями
        """
        print(f"\n🔍 Парсинг {code_name} из {url}")
        print("="*60)
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Извлекаем текст страницы
            full_text = soup.get_text(separator='\n', strip=True)
            
            # Разбиваем на строки
            lines = full_text.split('\n')
            
            # Ищем статьи
            articles = []
            current_article = None
            
            for line in lines:
                line = line.strip()
                
                # Проверяем, начинается ли строка с "Статья N."
                match = re.match(r'^Статья\s+(\d+(?:\.\d+)?)[\.\s]*(.*)$', line)
                
                if match:
                    # Сохраняем предыдущую статью
                    if current_article and len(current_article['text']) > 50:
                        articles.append(current_article)
                    
                    # Начинаем новую статью
                    article_num = match.group(1)
                    article_title = match.group(2).strip()
                    current_article = {
                        'num': article_num,
                        'title': article_title,
                        'text': line,
                    }
                elif current_article:
                    # Добавляем строку к текущей статье
                    # Пропускаем навигацию и меню
                    if not any(skip in line for skip in [
                        'Вход в систему', 'Некоммерческие', 'О компании',
                        'Купить', 'Пробный доступ', 'Новости', 'Вакансии',
                        '©', 'Гарант', 'garant.ru', 'Обратная связь'
                    ]):
                        current_article['text'] += '\n' + line
            
            # Добавляем последнюю статью
            if current_article and len(current_article['text']) > 50:
                articles.append(current_article)
            
            print(f"✅ Найдено статей: {len(articles)}")
            
            # Показываем примеры
            if articles:
                print(f"\n📄 Примеры статей:")
                for i, article in enumerate(articles[:3]):
                    print(f"  {i+1}. Статья {article['num']}: {article['title'][:50]}")
                    print(f"     Размер: {len(article['text'])} символов")
            
            return {
                'code_name': code_name,
                'full_name': full_name,
                'url': url,
                'total_articles': len(articles),
                'articles': articles
            }
            
        except Exception as e:
            print(f"❌ Ошибка при парсинге: {e}")
            return None


if __name__ == "__main__":
    parser = GarantParser()
    
    # Парсим ЗК РФ
    zk_data = parser.parse_code(
        url='https://base.garant.ru/12124624/',
        code_name='ЗК РФ',
        full_name='Земельный кодекс Российской Федерации'
    )
    
    # Парсим ГрК РФ
    grk_data = parser.parse_code(
        url='https://base.garant.ru/12138258/',
        code_name='ГрК РФ',
        full_name='Градостроительный кодекс Российской Федерации'
    )
    
    # Сохраняем результаты
    if zk_data:
        with open('/tmp/zk_rf_garant.json', 'w', encoding='utf-8') as f:
            json.dump(zk_data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ ЗК РФ сохранён в /tmp/zk_rf_garant.json")
    
    if grk_data:
        with open('/tmp/grk_rf_garant.json', 'w', encoding='utf-8') as f:
            json.dump(grk_data, f, ensure_ascii=False, indent=2)
        print(f"✅ ГрК РФ сохранён в /tmp/grk_rf_garant.json")

