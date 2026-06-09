def fill_template(template_text: str, data: dict) -> str:
    result = template_text
    for key, value in data.items():
        placeholder = f"[{key}]"
        if value is not None and str(value).strip():
            result = result.replace(placeholder, str(value))
    return result

def get_judicial_prompt(doc_type: str, data: dict, contexts: str, template: str = None) -> str:
    base = f"Контекст законов:\n{contexts}\n\n"
    if template:
        filled = fill_template(template, data)
        return base + f"На основе следующего шаблона и данных составь итоговый документ в официально-деловом стиле. Замени все [плейсхолдеры] на конкретные значения из данных пользователя. Если каких-то данных нет, оставь [плейсхолдер] или предложи ввести.\n\n{filled}"
    else:
        return base + f"Составь документ типа {doc_type} с данными: {data}"
