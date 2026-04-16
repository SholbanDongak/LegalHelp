"""Модуль для распознавания текста из файлов (OCR)"""

import os
import pdfplumber
from PIL import Image
import pytesseract


def extract_text_from_pdf(file_path: str) -> str:
    """Извлекает текст из PDF-файла"""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Ошибка при чтении PDF: {e}")
    return text.strip()


def extract_text_from_image(file_path: str) -> str:
    """Извлекает текст из изображения через Tesseract OCR"""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang="rus")
        return text.strip()
    except Exception as e:
        print(f"Ошибка при распознавании изображения: {e}")
        return ""


def extract_text_from_file(file_path: str) -> str:
    """Определяет тип файла и извлекает текст"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        return extract_text_from_image(file_path)
    else:
        return f"Неподдерживаемый формат файла: {ext}"
