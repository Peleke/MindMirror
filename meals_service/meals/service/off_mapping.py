from __future__ import annotations

from typing import Any, Dict, Optional


def _get_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def map_off_product_to_food_create(product: Dict[str, Any]) -> Dict[str, Any]:
    """Map an OFF product (v2 detail) to our FoodItem create dict.

    Strategy:
    - Prefer per-serving nutriments; fallback to per-100g and default serving to 100 g.
    - Convert sodium to mg if provided in grams.
    - Calories prefer energy-kcal; if only kJ available, convert.
    - Populate provenance and metadata.
    """
    code = product.get("code") or product.get("_id")
    name = product.get("product_name") or code or "Unknown"
    brand = product.get("brands")
    image_url = product.get("image_url")
    nutrition_grades = product.get("nutrition_grades")
    nutriscore_data = product.get("nutriscore_data")
    nutriments: Dict[str, Any] = product.get("nutriments") or {}

    # Serving determination
    serving_quantity = _get_float(product.get("serving_quantity"))
    serving_size_str = product.get("serving_size")  # e.g., "30 g"
    serving_size = serving_quantity or 100.0
    serving_unit = "g"
    if not serving_quantity and isinstance(serving_size_str, str):
        # crude parse: look for number and unit
        parts = serving_size_str.split()
        if parts:
            maybe_qty = _get_float(parts[0])
            if maybe_qty is not None:
                serving_size = maybe_qty
            if len(parts) > 1 and isinstance(parts[1], str):
                serving_unit = parts[1]

    # Helper to pick per-serving else per-100g
    def pick_nutriment(base: str) -> Optional[float]:
        val = _get_float(nutriments.get(f"{base}_serving"))
        if val is not None:
            return val
        val = _get_float(nutriments.get(f"{base}_100g"))
        return val

    # Energy kcal
    calories = _get_float(nutriments.get("energy-kcal_serving"))
    if calories is None:
        calories = _get_float(nutriments.get("energy-kcal_100g"))
    if calories is None:
        # convert kJ → kcal
        kj = _get_float(nutriments.get("energy_serving")) or _get_float(nutriments.get("energy_100g"))
        if kj is not None:
            calories = kj / 4.184
    if calories is None:
        calories = 0.0

    protein = pick_nutriment("proteins") or 0.0
    carbohydrates = pick_nutriment("carbohydrates") or 0.0
    fat = pick_nutriment("fat") or 0.0
    fiber = pick_nutriment("fiber")
    sugar = pick_nutriment("sugars")

    # Sodium: OFF often provides grams; convert to mg for our schema
    sodium_g = pick_nutriment("sodium")
    sodium_mg = sodium_g * 1000.0 if sodium_g is not None else None

    saturated_fat = pick_nutriment("saturated-fat")
    monounsaturated_fat = pick_nutriment("monounsaturated-fat")
    polyunsaturated_fat = pick_nutriment("polyunsaturated-fat")
    trans_fat = pick_nutriment("trans-fat")

    # Minerals (mg) and vitamins if available (rare)
    calcium = pick_nutriment("calcium")
    iron = pick_nutriment("iron")
    potassium = pick_nutriment("potassium")
    zinc = pick_nutriment("zinc")
    vitamin_d = pick_nutriment("vitamin-d")
    cholesterol = pick_nutriment("cholesterol")

    food_dict: Dict[str, Any] = {
        "name": name,
        "serving_size": serving_size,
        "serving_unit": serving_unit,
        "calories": float(calories),
        "protein": float(protein),
        "carbohydrates": float(carbohydrates),
        "fat": float(fat),
        "saturated_fat": saturated_fat,
        "monounsaturated_fat": monounsaturated_fat,
        "polyunsaturated_fat": polyunsaturated_fat,
        "trans_fat": trans_fat,
        "cholesterol": cholesterol,
        "fiber": fiber,
        "sugar": sugar,
        "sodium": sodium_mg,
        "vitamin_d": vitamin_d,
        "calcium": calcium,
        "iron": iron,
        "potassium": potassium,
        "zinc": zinc,
        "brand": brand,
        "thumbnail_url": image_url,
        "source": "off",
        "external_source": "openfoodfacts",
        "external_id": code,
        "external_metadata": {
            "nutrition_grades": nutrition_grades,
            "nutriscore_data": nutriscore_data,
        },
    }
    return food_dict


def map_off_product_to_autocomplete(product: Dict[str, Any]) -> Dict[str, Any]:
    """Map a Search-a-licious or v2 product to a lightweight autocomplete entry."""
    name = product.get("product_name") or product.get("product_name_en") or product.get("code")
    return {
        "source": "off",
        "id_": None,
        "external_id": product.get("code"),
        "name": name.strip() if isinstance(name, str) else name,
        "brand": product.get("brands"),
        "thumbnail_url": product.get("image_url"),
        "nutrition_grades": product.get("nutrition_grades"),
    } 