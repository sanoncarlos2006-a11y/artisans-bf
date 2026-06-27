DAY_LABELS = {
    0: "lundi",
    1: "mardi",
    2: "mercredi",
    3: "jeudi",
    4: "vendredi",
    5: "samedi",
    6: "dimanche",
}


def opening_days_to_labels(opening_days: str | None) -> list[str]:
    if not opening_days:
        return []

    labels: list[str] = []
    for item in opening_days.split(","):
        item = item.strip()
        if item.isdigit():
            day = int(item)
            if day in DAY_LABELS:
                labels.append(DAY_LABELS[day])
    return labels


def build_hours_label(opening_days: str | None, open_time: str | None, close_time: str | None) -> str:
    days = opening_days_to_labels(opening_days)
    if not days or not open_time or not close_time:
        return "Horaires non précisés"

    if days == ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]:
        days_label = "lundi à samedi"
    elif days == ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]:
        days_label = "lundi à vendredi"
    elif days == ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]:
        days_label = "tous les jours"
    else:
        days_label = ", ".join(days)

    return f"{days_label}, {open_time} - {close_time}"
