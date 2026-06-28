import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, List
from pathlib import Path


class AkomaNtosoConverter:
    """
    Конвертирует структуру закона в Akoma Ntoso с FRBR.
    """
    
    def convert(self, parsed_data: Dict, output_path: str):
        """
        Создает XML-файл в формате Akoma Ntoso.
        """
        meta = parsed_data['meta']
        structure = parsed_data['structure']
        
        root = ET.Element('akomaNtoso')
        act = ET.SubElement(root, 'act')
        
        meta_elem = ET.SubElement(act, 'meta')
        identification = ET.SubElement(meta_elem, 'identification')
        
        # FRBR Work
        work = ET.SubElement(identification, 'FRBRWork')
        work.set('eId', 'w1')
        
        # Формируем URI
        doc_date = meta.get('doc_date', '')
        doc_number = meta.get('doc_number', '')
        
        if doc_number:
            work_uri = f"/ru/act/{doc_date}/{doc_number}"
        elif doc_date:
            work_uri = f"/ru/act/{doc_date}"
        else:
            work_uri = f"/ru/act/{meta.get('doc_id', 'unknown')}"
        
        work.set('uri', work_uri)
        
        # FRBR Expression
        expression = ET.SubElement(identification, 'FRBRExpression')
        expression.set('eId', 'e1')
        expression_uri = f"{work_uri}/rus@{doc_date}" if doc_date else f"{work_uri}/rus"
        expression.set('uri', expression_uri)
        
        language = ET.SubElement(expression, 'FRBRlanguage')
        language.set('value', 'rus')
        
        if doc_date:
            date = ET.SubElement(expression, 'FRBRdate')
            date.set('date', doc_date)
            date.set('name', 'generation')
        
        # FRBR Manifestation
        manifestation = ET.SubElement(identification, 'FRBRManifestation')
        manifestation.set('eId', 'm1')
        manifestation.set('uri', f"{expression_uri}.xml")
        
        format_elem = ET.SubElement(manifestation, 'FRBRformat')
        format_elem.set('value', 'application/xml')
        
        # Дополнительные метаданные
        heading = meta.get('heading', '')
        if heading:
            heading_elem = ET.SubElement(meta_elem, 'heading')
            heading_elem.text = heading
        
        status = meta.get('status', '')
        if status:
            status_elem = ET.SubElement(meta_elem, 'status')
            status_elem.text = status
        
        # Тело документа
        body = ET.SubElement(act, 'body')
        
        current_article_elem = None
        current_article_num = None
        
        for item in structure:
            if item['article_num'] != current_article_num:
                article = ET.SubElement(body, 'article')
                article.set('eId', f"art{item['article_num']}")
                
                num = ET.SubElement(article, 'num')
                num.text = f"Статья {item['article_num']}."
                
                current_article_elem = article
                current_article_num = item['article_num']
            
            if item['type'] == 'clause' and item['clause_num']:
                clause = ET.SubElement(current_article_elem, 'clause')
                clause.set('eId', f"art{item['article_num']}_cl{item['clause_num']}")
                
                content = ET.SubElement(clause, 'content')
                p = ET.SubElement(content, 'p')
                p.text = item['text']
            else:
                content = ET.SubElement(current_article_elem, 'content')
                p = ET.SubElement(content, 'p')
                p.text = item['text']
        
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        pretty_xml = '\n'.join(lines)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"✅ Создан Akoma Ntoso: {output_path}")
        print(f"   Work URI: {work_uri}")
        print(f"   Expression URI: {expression_uri}")
        print(f"   Структурных единиц: {len(structure)}")
