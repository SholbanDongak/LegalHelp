"""
Экспорт заполненного документа в формат PDF.
"""
import os
import re
from datetime import datetime
from typing import Dict, Optional
from fpdf import FPDF


TEMPLATES_DIR = "./templates"
OUTPUT_DIR = "./output/documents"

# Пути к шрифтам с поддержкой кириллицы (macOS)
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_ITALIC = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"
FONT_BOLD_ITALIC = "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf"


def ensure_output_dir():
    """Создаёт директорию для выходных файлов, если её нет."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_template_text(doc_type: str) -> Optional[str]:
    """Загружает текстовый шаблон."""
    path = os.path.join(TEMPLATES_DIR, f"{doc_type}.txt")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def fill_template(template: str, fields: Dict[str, str]) -> str:
    """Заполняет шаблон значениями полей."""
    result = template
    for key, value in fields.items():
        if value:
            result = result.replace(f"[{key}]", str(value))
    
    # Заменяем оставшиеся незаполненные плейсхолдеры на прочерки
    result = re.sub(r'\[([^\]]+)\]', '___________', result)
    
    # Если в шаблоне была дата и она не заполнена — ставим текущую
    if "___________" in result and "[date]" in template:
        today = datetime.now().strftime("%d.%m.%Y")
        result = result.replace("___________", today, 1)
    
    return result


class LegalPDF(FPDF):
    """Кастомный PDF класс для юридических документов."""
    
    def __init__(self):
        super().__init__()
        self._setup_fonts()
    
    def _setup_fonts(self):
        """Настраивает шрифты с поддержкой кириллицы."""
        if os.path.exists(FONT_REGULAR):
            # uni=True больше не нужен в fpdf2 2.5.1+, но оставим для совместимости
            self.add_font("Arial", "", FONT_REGULAR)
            if os.path.exists(FONT_BOLD):
                self.add_font("Arial", "B", FONT_BOLD)
            else:
                self.add_font("Arial", "B", FONT_REGULAR)
            
            if os.path.exists(FONT_ITALIC):
                self.add_font("Arial", "I", FONT_ITALIC)
            
            if os.path.exists(FONT_BOLD_ITALIC):
                self.add_font("Arial", "BI", FONT_BOLD_ITALIC)
            
            print(f"✅ Шрифты загружены: Arial")
        else:
            raise FileNotFoundError(f"Шрифт не найден: {FONT_REGULAR}")
    
    def _reset_x(self):
        """Сбрасывает позицию X в левый margin."""
        self.set_x(self.l_margin)
    
    def header_line(self, text: str):
        """Добавляет строку шапки (по правому краю)."""
        self._reset_x()
        self.set_font("Arial", "", 14)
        # Для правого выравнивания используем multi_cell с шириной страницы
        page_width = self.w - self.l_margin - self.r_margin
        self.multi_cell(page_width, 7, text, align="R")
    
    def title_line(self, text: str):
        """Добавляет заголовок (по центру, жирный)."""
        self._reset_x()
        self.set_font("Arial", "B", 14)
        page_width = self.w - self.l_margin - self.r_margin
        self.multi_cell(page_width, 7, text, align="C")
    
    def body_text(self, text: str):
        """Добавляет обычный абзац с отступом."""
        self.set_font("Arial", "", 14)
        # Отступ первой строки (красная строка)
        indent = 12.5
        self.set_x(self.l_margin + indent)
        # Ширина с учётом отступа
        width = self.w - self.l_margin - self.r_margin - indent
        self.multi_cell(width, 7, text, align="J")
        # После multi_cell X сбрасывается в l_margin
    
    def list_item(self, text: str):
        """Добавляет пункт списка."""
        self._reset_x()
        self.set_font("Arial", "", 14)
        page_width = self.w - self.l_margin - self.r_margin
        self.multi_cell(page_width, 7, text, align="L")
    
    def signature_line(self, text: str):
        """Добавляет строку подписи."""
        self._reset_x()
        self.set_font("Arial", "", 14)
        page_width = self.w - self.l_margin - self.r_margin
        self.multi_cell(page_width, 7, text, align="L")


def create_pdf(text: str, doc_type: str, fields: Dict[str, str]) -> str:
    """
    Создаёт PDF документ из заполненного текста.
    
    Args:
        text: Заполненный текст документа
        doc_type: Тип документа
        fields: Словарь с полями
    
    Returns:
        Путь к созданному PDF файлу
    """
    ensure_output_dir()
    
    pdf = LegalPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # Настройка полей страницы
    pdf.set_left_margin(30)  # 3 см
    pdf.set_right_margin(15)  # 1.5 см
    pdf.set_top_margin(20)  # 2 см
    
    # Разбиваем текст на абзацы
    paragraphs = text.split('\n')
    
    for para_text in paragraphs:
        para_text = para_text.strip()
        if not para_text:
            pdf.ln(3)  # Пустая строка
            continue
        
        # Определяем тип абзаца и форматируем
        if _is_header(para_text, fields):
            pdf.header_line(para_text)
        elif _is_title(para_text):
            pdf.title_line(para_text)
            pdf.ln(3)
        elif _is_signature_line(para_text):
            pdf.ln(5)
            pdf.signature_line(para_text)
        elif _is_list_item(para_text):
            pdf.list_item(para_text)
        else:
            pdf.body_text(para_text)
    
    # Формируем имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{doc_type}_{timestamp}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    pdf.output(filepath)
    
    print(f"✅ PDF создан: {filepath}")
    return filepath


def _is_header(text: str, fields: Dict[str, str]) -> bool:
    """Определяет, является ли абзац шапкой документа."""
    header_keywords = ['В ', 'в ', 'Истец:', 'Ответчик:', 'Заявитель:', 
                      'адрес:', 'по делу №', 'судья']
    
    if any(text.startswith(kw) for kw in header_keywords):
        return True
    
    court_name = fields.get('court_name') or fields.get('appeal_court_name')
    plaintiff = fields.get('plaintiff_name') or fields.get('applicant_name')
    defendant = fields.get('defendant_name')
    
    if court_name and court_name in text:
        return True
    if plaintiff and plaintiff in text and len(text) < 150:
        return True
    if defendant and defendant in text and len(text) < 150:
        return True
    
    return False


def _is_title(text: str) -> bool:
    """Определяет, является ли абзац заголовком."""
    title_keywords = [
        'Исковое заявление', 'Заявление', 'Жалоба', 'Возражение',
        'Ходатайство', 'Апелляционная', 'Кассационная', 'Претензия'
    ]
    return any(kw in text for kw in title_keywords) and len(text) < 150


def _is_signature_line(text: str) -> bool:
    """Определяет, является ли абзац строкой подписи."""
    if re.match(r'^\d{2}\.\d{2}\.\d{4}', text):
        return True
    if '_________________' in text or '_______________' in text:
        return True
    return False


def _is_list_item(text: str) -> bool:
    """Определяет, является ли абзац пунктом списка."""
    if re.match(r'^\d+[\.\)]\s', text):
        return True
    if re.match(r'^[а-я]\)\s', text):
        return True
    if re.match(r'^[IVX]+\.\s', text):
        return True
    return False


def test_pdf_generation():
    """Тест генерации PDF."""
    print("🧪 ТЕСТ ГЕНЕРАЦИИ PDF")
    print("="*60)
    
    # Тестовые поля
    fields = {
        "court_name": "Ленинский районный суд г. Кызыла",
        "plaintiff_name": "Петров Петр Петрович",
        "plaintiff_address": "г. Кызыл, ул. Титова, д. 10, кв. 5",
        "defendant_name": "ООО «Технопарк»",
        "defendant_address": "г. Кызыл, ул. Ленина, д. 10",
        "product_name": "Samsung Galaxy S23",
        "amount": "80000",
        "defect_description": "мерцание экрана через неделю после покупки",
        "moral_damage": "10000",
        "date": "29.06.2026"
    }
    
    # Загружаем шаблон
    template = load_template_text("claim_consumer")
    if not template:
        print("❌ Шаблон claim_consumer не найден")
        return
    
    # Заполняем шаблон
    filled_text = fill_template(template, fields)
    print(f"\n📄 Заполненный текст:\n{filled_text}\n")
    
    # Создаём PDF
    filepath = create_pdf(filled_text, "claim_consumer", fields)
    
    print(f"\n✅ Файл создан: {filepath}")
    print(f"   Размер: {os.path.getsize(filepath)} байт")
    print(f"\n💡 Откройте файл в Preview для проверки:")
    print(f"   open {filepath}")


if __name__ == "__main__":
    test_pdf_generation()
