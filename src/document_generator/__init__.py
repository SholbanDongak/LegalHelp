"""
Модуль генерации юридических документов.
"""
from .document_generator import generate_document, list_available_templates
from .template_mapper import map_query_to_template
from .field_extractor import extract_fields
from .docx_exporter import create_docx, fill_template, load_template_text
from .pdf_exporter import create_pdf

__all__ = [
    "generate_document",
    "list_available_templates",
    "map_query_to_template",
    "extract_fields",
    "create_docx",
    "create_pdf",
    "fill_template",
    "load_template_text",
]
