import json
import re
from dataclasses import dataclass

from app.core_config import OLLAMA_ENABLED, OLLAMA_HOST, OLLAMA_MODEL
from app.utils.text_normalizer import normalize_text


@dataclass
class AIRatingResult:
    rating: int
    confidence: float
    explanation: str
    model: str


POSITIVE_WORDS = [
    "rapide", "serieux", "sérieux", "propre", "efficace", "professionnel", "bon", "bonne",
    "excellent", "excellente", "satisfait", "satisfaite", "recommande", "gentil", "ponctuel",
    "qualite", "qualité", "bien", "correct", "correcte", "merci", "parfait", "abordable",
]

NEGATIVE_WORDS = [
    "retard", "mauvais", "mauvaise", "cher", "chere", "chère", "sale", "mal fait",
    "probleme", "problème", "decu", "déçu", "lente", "lent", "irrespectueux", "arnaque",
    "pas serieux", "pas sérieux", "nul", "nulle", "horrible", "catastrophe", "deconseille", "déconseille",
]


def _clamp_rating(value: int) -> int:
    return max(1, min(5, int(value)))


def _clamp_confidence(value: float) -> float:
    return max(0.0, min(1.0, round(float(value), 2)))


def _extract_json(text: str) -> dict:
    """Qwen peut parfois ajouter du texte autour du JSON ; on récupère le premier objet JSON."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def rate_comment_with_keywords(comment: str) -> AIRatingResult:
    text = normalize_text(comment)

    if not text:
        return AIRatingResult(
            rating=3,
            confidence=0.3,
            explanation="Commentaire vide ou invalide : note neutre attribuée.",
            model="fallback-keywords-v1",
        )

    positive_score = sum(1 for word in POSITIVE_WORDS if normalize_text(word) in text)
    negative_score = sum(1 for word in NEGATIVE_WORDS if normalize_text(word) in text)
    score = positive_score - negative_score

    if score >= 3:
        rating = 5
        explanation = "Commentaire très positif : plusieurs indices de satisfaction détectés."
    elif score >= 1:
        rating = 4
        explanation = "Commentaire positif : le service semble apprécié."
    elif score == 0:
        rating = 3
        explanation = "Commentaire neutre ou mitigé : satisfaction non clairement positive ou négative."
    elif score <= -3:
        rating = 1
        explanation = "Commentaire très négatif : plusieurs indices d'insatisfaction détectés."
    else:
        rating = 2
        explanation = "Commentaire plutôt négatif : des éléments indiquent une insatisfaction."

    confidence = min(0.95, 0.55 + abs(score) * 0.12)
    return AIRatingResult(rating=rating, confidence=round(confidence, 2), explanation=explanation, model="fallback-keywords-v1")


def rate_comment_with_ollama(comment: str) -> AIRatingResult:
    if not OLLAMA_ENABLED:
        raise RuntimeError("Ollama est désactivé dans la configuration.")

    from ollama import Client

    client = Client(host=OLLAMA_HOST)
    prompt = f"""
Tu es un système d'analyse de satisfaction client pour une plateforme d'annuaire géolocalisé d'artisans au Burkina Faso.

Analyse le commentaire et attribue une note de 1 à 5 étoiles.

Règles :
1 = très mauvais service
2 = service mauvais ou décevant
3 = service moyen ou mitigé
4 = bon service
5 = excellent service

Réponds uniquement en JSON valide, sans texte avant ni après.
Format obligatoire :
{{
  "rating": 1,
  "confidence": 0.80,
  "explanation": "courte explication en français"
}}

Commentaire : {comment!r}
""".strip()

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1},
    )

    content = response["message"]["content"]
    data = _extract_json(content)

    return AIRatingResult(
        rating=_clamp_rating(data.get("rating", 3)),
        confidence=_clamp_confidence(data.get("confidence", 0.7)),
        explanation=str(data.get("explanation", "Note générée automatiquement par Ollama."))[:500],
        model=f"ollama-{OLLAMA_MODEL}",
    )


def rate_comment(comment: str) -> AIRatingResult:
    """Essaie Ollama puis revient aux mots-clés si Ollama est indisponible."""
    try:
        return rate_comment_with_ollama(comment)
    except Exception:
        return rate_comment_with_keywords(comment)


def get_ai_status() -> dict:
    status = {
        "ollama_enabled": OLLAMA_ENABLED,
        "ollama_host": OLLAMA_HOST,
        "ollama_model": OLLAMA_MODEL,
        "connection_ok": False,
        "message": "Ollama non vérifié.",
    }

    if not OLLAMA_ENABLED:
        status["message"] = "Ollama est désactivé. Le fallback mots-clés sera utilisé."
        return status

    try:
        from ollama import Client

        client = Client(host=OLLAMA_HOST)
        models_response = client.list()
        model_names = []
        for item in models_response.get("models", []):
            name = getattr(item, "model", None) or item.get("model") if isinstance(item, dict) else None
            if name:
                model_names.append(name)
        status["connection_ok"] = True
        status["available_models"] = model_names
        status["message"] = "Ollama est joignable."
    except Exception as exc:
        status["message"] = f"Ollama non joignable : {exc}"

    return status
