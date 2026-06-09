class RuleBasedClassifier:
    def __init__(self):
        self.default_category = "other"
        self.categories = {
            "fns": ["налог", "фнс", "ндс", "пояснение", "налоговая"],
            "court": ["суд", "исковое заявление", "иск", "судебный акт"],
            "counterparty": ["контрагент", "поставка", "договор", "претензия", "письмо"],
            "judicial_review": [
                "апелляционная жалоба", "кассационная жалоба", "возражение",
                "судебный приказ", "обжалование", "мировой судья",
                "гражданское судопроизводство", "административное судопроизводство",
                "административное правонарушение", "дело об административном правонарушении",
                "кассационная инстанция", "апелляционная инстанция"
            ],
            "other": []
        }

    def classify(self, text: str) -> str:
        lower_text = text.lower()
        for category, keywords in self.categories.items():
            if any(keyword in lower_text for keyword in keywords):
                return category
        return self.default_category
