import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from pathlib import Path


class LegalStructureParser:
    """
    Парсит реальный формат RusLawOD XML и извлекает структуру (статьи, пункты).
    Поддерживает разные форматы: Конституция (без точки), ГК РФ (с точкой).
    """
    
    def parse_article_structure(self, text: str) -> List[Dict]:
        """
        Извлекает статьи и пункты из текста закона.
        """
        structure = []
        
        # УНИВЕРСАЛЬНЫЙ ПАТТЕРН: учитываем точку и без точки
        # Ищем: "Статья 1" или "Статья 1." с последующим текстом
        article_pattern = r'(?:^|\n)\s*Статья\s+(\d+)(?:\.|\s*\n)(.*?)(?=(?:\n\s*Статья\s+\d+(?:\.|\s*\n))|$)'
        articles = re.findall(article_pattern, text, re.DOTALL)
        
        for article_num, article_content in articles:
            article_content = article_content.strip()
            
            # Паттерн для пунктов: "1.", "2." и т.д. в начале строки
            clause_pattern = r'^\s*(\d+)\.\s+(.*?)(?=(?:^\s*\d+\.\s+)|$)'
            clauses = re.findall(clause_pattern, article_content, re.DOTALL | re.MULTILINE)
            
            if clauses:
                # Статья с пунктами
                for clause_num, clause_text in clauses:
                    structure.append({
                        'type': 'clause',
                        'article_num': article_num,
                        'clause_num': clause_num,
                        'text': clause_text.strip(),
                        'metadata': f"Статья {article_num}, пункт {clause_num}"
                    })
            else:
                # Статья без пунктов (цельная статья)
                if article_content:
                    structure.append({
                        'type': 'article',
                        'article_num': article_num,
                        'clause_num': None,
                        'text': article_content,
                        'metadata': f"Статья {article_num}"
                    })
        
        return structure
    
    def extract_metadata_from_text(self, text: str) -> Dict:
        """
        Извлекает метаданные (название, дата, номер) из самого текста.
        """
        meta = {
            'heading': '',
            'doc_date': '',
            'doc_number': '',
            'doc_type': ''
        }
        
        lines = text.strip().split('\n')
        header_text = '\n'.join(lines[:30])
        
        # Ищем название кодекса или закона
        # Сначала ищем "Гражданский кодекс Российской Федерации"
        code_patterns = [
            r'(Гражданский кодекс Российской Федерации)',
            r'(Трудовой кодекс Российской Федерации)',
            r'(Семейный кодекс Российской Федерации)',
            r'(Уголовный кодекс Российской Федерации)',
            r'(Кодекс Российской Федерации об административных правонарушениях)',
            r'(КОНСТИТУЦИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ)',
        ]
        
        for pattern in code_patterns:
            match = re.search(pattern, header_text, re.IGNORECASE)
            if match:
                meta['heading'] = match.group(1)
                if 'кодекс' in match.group(1).lower():
                    meta['doc_type'] = 'Кодекс'
                elif 'конституция' in match.group(1).lower():
                    meta['doc_type'] = 'Конституция'
                break
        
        # Если не нашли кодекс, берём первую значимую строку
        if not meta['heading']:
            for line in lines[:10]:
                line_stripped = line.strip()
                if line_stripped and len(line_stripped) > 10:
                    meta['heading'] = line_stripped
                    break
        
        # Извлекаем дату принятия
        date_patterns = [
            r'Принят[а]?\s+(?:Государственной Думой\s+)?(\d{1,2}\s+\w+\s+\d{4})',
            r'от\s+(\d{1,2}\s+\w+\s+\d{4})',
            r'(\d{2}\.\d{2}\.\d{4})',
            r'(\d{1,2}\s+\w+\s+\d{4})\s*г'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, header_text)
            if match:
                meta['doc_date'] = match.group(1)
                break
        
        return meta
    
    def parse_xml_file(self, xml_path: str) -> Dict:
        """
        Парсит XML-файл из RusLawOD в реальном формате.
        """
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Извлекаем ID документа
        doc_id_elem = root.find('.//id')
        doc_id = doc_id_elem.text if doc_id_elem is not None else ''
        
        # Извлекаем текст из CDATA
        text_elem = root.find('.//text')
        if text_elem is not None and text_elem.text:
            text = text_elem.text.strip()
        else:
            text = ''
        
        # Извлекаем метаданные из текста
        meta = self.extract_metadata_from_text(text)
        meta['doc_id'] = doc_id
        
        # Парсим структуру
        structure = self.parse_article_structure(text)
        
        return {
            'meta': meta,
            'structure': structure,
            'source_file': xml_path
        }
