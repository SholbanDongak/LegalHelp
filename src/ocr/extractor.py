import os
import easyocr
from pdf2image import convert_from_path

# Инициализация EasyOCR один раз при импорте модуля
reader = easyocr.Reader(['ru', 'en'], gpu=False)

def extract_text_from_file(file_path: str) -> str:
    """
    Извлекает текст из файла (изображение или PDF) с помощью EasyOCR.
    Поддерживаются форматы: .png, .jpg, .jpeg, .pdf.
    """
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.pdf':
            # Конвертируем PDF в список изображений
            images = convert_from_path(file_path, dpi=300)
            full_text = []
            for img in images:
                # EasyOCR работает с PIL Image напрямую
                result = reader.readtext(img, detail=0, paragraph=True)
                full_text.append("\n".join(result))
            return "\n".join(full_text)
        else:
            # Для изображений передаём путь к файлу
            result = reader.readtext(file_path, detail=0, paragraph=True)
            return "\n".join(result)
    except Exception as e:
        return f"Ошибка OCR: {str(e)}"
