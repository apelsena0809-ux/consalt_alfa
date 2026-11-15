"""Каталог материалов и рекомендательная логика Альфа-Курс."""
from functools import lru_cache
from pathlib import Path
import csv

BASE_DIR = Path(__file__).resolve().parents[1]
CATALOG_PATH = BASE_DIR / "data" / "processed" / "materials.csv"

@lru_cache(maxsize=1)
def _load_materials():
    """Читает каталог один раз; st.cache_data дополнительно кеширует слой UI."""
    if not CATALOG_PATH.exists():
        return tuple()
    try:
        with CATALOG_PATH.open(encoding="utf-8-sig", newline="") as f:
            return tuple(dict(row) for row in csv.DictReader(f))
    except (OSError, csv.Error):
        return tuple()

def _catalog():
    return [dict(row) for row in _load_materials()]

def get_all_materials():
    return sorted(_catalog(), key=lambda x: float(x.get("popularity", 0) or 0), reverse=True)

def get_popular_materials():
    return get_all_materials()[:5]

def baseline_recommend(profile):
    """Baseline: только точное совпадение основной темы."""
    task = profile.get("current_task", "")
    matches = [x for x in _catalog() if x.get("topic") == task]
    return sorted(matches, key=lambda x: float(x.get("popularity", 0) or 0), reverse=True)[:5]

def get_recommendations(profile, history=None):
    """Ранжирование: 0.5 задача + 0.3 стадия + 0.2 сфера + 0.05 история."""
    history = set(str(x) for x in (history or []))
    task = profile.get("current_task", "")
    stage = profile.get("stage", "")
    industry = profile.get("industry", "")
    scored = []
    for material in _catalog():
        score = 0.0
        if material.get("topic") == task:
            score += 0.5
        if material.get("business_stage") == stage:
            score += 0.3
        if material.get("industry") == industry:
            score += 0.2
        if str(material.get("id", "")) in history:
            score += 0.05
        item = dict(material)
        item["score"] = round(score, 3)
        scored.append(item)
    return sorted(scored, key=lambda x: (x["score"], float(x.get("popularity", 0) or 0)), reverse=True)[:5]

def get_explanation(material, profile):
    parts = []
    if material.get("topic") == profile.get("current_task"):
        parts.append(f"совпадает с задачей «{profile.get('current_task')}»")
    if material.get("business_stage") == profile.get("stage"):
        parts.append(f"подходит для стадии «{profile.get('stage')}»")
    if material.get("industry") == profile.get("industry"):
        parts.append(f"учитывает сферу «{profile.get('industry')}»")
    return ("Материал " + " и ".join(parts) + ".") if parts else "Материал может быть полезен как дополнительный ресурс по развитию бизнеса."

def get_next_step(material):
    return "Откройте материал и выполните рекомендации по порядку."
