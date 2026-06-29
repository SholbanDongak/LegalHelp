"""
Полный парсер для garant.ru - скачивание всех статей кодексов.
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from typing import List, Dict, Tuple

class GarantFullParser:
    """Полный парсер HTML-страниц кодексов с garant.ru"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9',
        }
        self.session = requests.Session()
    
    def extract_article_urls(self, main_url: str) -> List[str]:
        """Извлекает все URL-ы статей со страницы кодекса"""
        print(f"🔍 Извлечение URL-ов статей из {main_url}")
        
        response = self.session.get(main_url, headers=self.headers, timeout=15)
        html = response.text
        
        # Ищем URL-ы вида /12124624/[hash]/
        pattern = r'/12124624/[a-f0-9]{32}/'
        if '12138258' in main_url:  # ГрК РФ
            pattern = r'/12138258/[a-f0-9]{32}/'
        
        urls = list(set(re.findall(pattern, html)))
        print(f"   Найдено уникальных URL-ов: {len(urls)}")
        
        return urls
    
    def extract_article_text(self, url: str) -> Tuple[str, str, str]:
        """
        Извлекает текст статьи со страницы
        
        Returns:
            (article_num, article_title, article_text)
        """
        try:
            response = self.session.get(url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                return None, None, None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            
            # Ищем номер статьи в начале текста
            # Паттерн: "Статья N." или "Статья N.N."
            match = re.search(r'Статья\s+(\d+(?:\.\d+(?:-\d+)?))[\.\s]+([^\n]+)', text)
            
            if not match:
                return None, None, None
            
            article_num = match.group(1)
            article_title = match.group(2).strip()
            
            # Извлекаем чистый текст статьи
            # Находим начало текста статьи (после "Статья N.")
            start_idx = match.end()
            
            # Находим конец текста (до навигации)
            # Ищем маркеры конца статьи
            end_markers = [
                'ГАРАНТ:',
                'См. комментарии',
                'Информация об изменениях',
                'Поделиться документом',
                'Главная',
                'ДОКУМЕНТ',
                'Купить систему ГАРАНТ',
            ]
            
            end_idx = len(text)
            for marker in end_markers:
                marker_idx = text.find(marker, start_idx)
                if marker_idx > 0 and marker_idx < end_idx:
                    end_idx = marker_idx
            
            # Извлекаем текст
            article_text = text[start_idx:end_idx].strip()
            
            # Убираем лишние пустые строки
            lines = [line.strip() for line in article_text.split('\n') if line.strip()]
            article_text = '\n'.join(lines)
            
            return article_num, article_title, article_text
            
        except Exception as e:
            print(f"   ❌ Ошибка при извлечении {url}: {e}")
            return None, None, None
    
    def parse_code(self, main_url: str, code_name: str, full_name: str) -> Dict:
        """
        Парсит все статьи кодекса
        
        Args:
            main_url: URL главной страницы кодекса
            code_name: Краткое название (например, "ЗК РФ")
            full_name: Полное название
        
        Returns:
            Словарь с метаданными и статьями
        """
        print(f"\n{'='*60}")
        print(f"🔍 ПАРСИНГ {code_name}")
        print(f"{'='*60}")
        
        # Извлекаем URL-ы статей
        article_urls = self.extract_article_urls(main_url)
        
        if not article_urls:
            print(f"❌ Не найдены URL-ы статей!")
            return None
        
        # Скачиваем каждую статью
        articles = []
        seen_nums = set()
        
        for i, url in enumerate(article_urls):
            full_url = f"https://base.garant.ru{url}"
            
            article_num, article_title, article_text = self.extract_article_text(full_url)
            
            if article_num and article_text and len(article_text) > 50:
                # Проверяем дубликаты
                if article_num not in seen_nums:
                    seen_nums.add(article_num)
                    articles.append({
                        'num': article_num,
                        'title': article_title,
                        'text': article_text,
                        'url': full_url
                    })
                    
                    if (i + 1) % 20 == 0:
                        print(f"   ✅ Обработано {i+1}/{len(article_urls)}, найдено {len(articles)} статей")
            
            # Небольшая задержка, чтобы не перегружать сервер
            time.sleep(0.3)
        
        # Сортируем статьи по номеру
        def sort_key(article):
            try:
                parts = article['num'].split('.')
                return tuple(int(p) for p in parts)
            except:
                return (9999,)
        
        articles.sort(key=sort_key)
        
        print(f"\n✅ Всего найдено статей: {len(articles)}")
        
        # Показываем примеры
        if articles:
            print(f"\n📄 Примеры статей:")
            for i, article in enumerate(articles[:3]):
                print(f"  {i+1}. Статья {article['num']}: {article['title'][:50]}")
                print(f"     Размер: {len(article['text'])} символов")
        
        return {
            'code_name': code_name,
            'full_name': full_name,
            'url': main_url,
            'total_articles': len(articles),
            'articles': articles
        }


if __name__ == "__main__":
    parser = GarantFullParser()
    
    # Парсим ЗК РФ
    zk_data = parser.parse_code(
        main_url='https://base.garant.ru/12124624/',
        code_name='ЗК РФ',
        full_name='Земельный кодекс Российской Федерации'
    )
    
    # Сохраняем ЗК РФ
    if zk_data:
        output_file = 'data/zk_rf_garant.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(zk_data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ ЗК РФ сохранён в {output_file}")
        print(f"   Размер: {len(json.dumps(zk_data, ensure_ascii=False))} символов")
    
    # Парсим ГрК РФ
    grk_data = parser.parse_code(
        main_url='https://base.garant.ru/12138258/',
        code_name='ГрК РФ',
        full_name='Градостроительный кодекс Российской Федерации'
    )
    
    # Сохраняем ГрК РФ
    if grk_data:
        output_file = 'data/grk_rf_garant.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(grk_data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ ГрК РФ сохранён в {output_file}")
        print(f"   Размер: {len(json.dumps(grk_data, ensure_ascii=False))} символов")

