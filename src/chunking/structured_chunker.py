import xml.etree.ElementTree as ET
from typing import List, Dict
from pathlib import Path


class StructuredChunker:
    """
    Создает структурированные чанки из Akoma Ntoso XML.
    """
    
    def create_chunks(self, xml_path: str) -> List[Dict]:
        """
        Создает чанки с метаданными из Akoma Ntoso XML.
        """
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        work_uri = root.find('.//FRBRWork').get('uri') if root.find('.//FRBRWork') is not None else ''
        expression_uri = root.find('.//FRBRExpression').get('uri') if root.find('.//FRBRExpression') is not None else ''
        
        heading_elem = root.find('.//meta/heading')
        heading = heading_elem.text if heading_elem is not None else ''
        
        chunks = []
        
        for article in root.findall('.//article'):
            article_eid = article.get('eId', '')
            article_num_elem = article.find('num')
            article_num = article_num_elem.text if article_num_elem is not None else ''
            
            clauses = article.findall('.//clause')
            if clauses:
                for clause in clauses:
                    clause_eid = clause.get('eId', '')
                    content_elem = clause.find('.//content/p')
                    clause_text = content_elem.text if content_elem is not None else ''
                    
                    if clause_text.strip():
                        chunk = {
                            'id': f"{article_eid}_{clause_eid}",
                            'work_uri': work_uri,
                            'expression_uri': expression_uri,
                            'article_eid': article_eid,
                            'article_num': article_num,
                            'clause_eid': clause_eid,
                            'heading': heading,
                            'text': clause_text.strip(),
                            'metadata': f"[{heading}, {article_num}, Пункт: {clause_eid}]"
                        }
                        chunks.append(chunk)
            else:
                content_elem = article.find('.//content/p')
                article_text = content_elem.text if content_elem is not None else ''
                
                if article_text.strip():
                    chunk = {
                        'id': article_eid,
                        'work_uri': work_uri,
                        'expression_uri': expression_uri,
                        'article_eid': article_eid,
                        'article_num': article_num,
                        'clause_eid': None,
                        'heading': heading,
                        'text': article_text.strip(),
                        'metadata': f"[{heading}, {article_num}]"
                    }
                    chunks.append(chunk)
        
        return chunks
