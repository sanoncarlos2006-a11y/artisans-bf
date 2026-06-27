import unicodedata


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    value = value.strip().lower()
    value = unicodedata.normalize("NFD", value)
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    return value


def normalize_category(value: str | None) -> str:
    text = normalize_text(value)
    aliases = {
        "mecanicien": "mecanicien",
        "mecano": "mecanicien",
        "mecanique": "mecanicien",
        "couture": "couturier",
        "couturier": "couturier",
        "coiffeur": "coiffeur",
        "coiffure": "coiffeur",
        "soudeur": "soudeur",
        "soudure": "soudeur",
        "electricien": "electricien",
        "electricite": "electricien",
        "plombier": "plombier",
        "plomberie": "plombier",
        "menuisier": "menuisier",
        "menuiserie": "menuisier",
        "reparateur telephone": "reparateur-telephone",
        "reparation telephone": "reparateur-telephone",
        "telephone": "reparateur-telephone",
    }
    return aliases.get(text, text)
