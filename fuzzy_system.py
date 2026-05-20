"""
üyelik fonksiyonlarını
Mamdani çıkarım mekanizmasını
durulaştırma işlemi
"""

from typing import Dict, List, Tuple
import numpy as np

from definitions import (
    INPUT_VARIABLES,
    OUTPUT_VARIABLE,
    Rule,
    RULES,
    TEST_SCENARIOS,
)

__all__ = [
    "INPUT_VARIABLES",
    "OUTPUT_VARIABLE",
    "Rule",
    "RULES",
    "TEST_SCENARIOS",
    "trimf",
    "trapmf",
    "membership_value",
    "fuzzify",
    "evaluate_rules",
    "output_membership",
    "aggregate_output",
    "defuzzify_centroid",
    "interpret_action",
    "infer",
    "validate_inputs",
]


def trimf(x: np.ndarray, params: Tuple[float, float, float]) -> np.ndarray:
    """Üçgensel üyelik fonksiyonu. params = (a, b, c)."""
    a, b, c = params
    y = np.zeros_like(x, dtype=float)

    left = (a < x) & (x <= b)
    right = (b < x) & (x < c)

    if b != a:
        y[left] = (x[left] - a) / (b - a)
    y[x == b] = 1.0
    if c != b:
        y[right] = (c - x[right]) / (c - b)

    return np.clip(y, 0, 1)


def trapmf(x: np.ndarray, params: Tuple[float, float, float, float]) -> np.ndarray:
    """Yamuksal üyelik fonksiyonu. params = (a, b, c, d)."""
    a, b, c, d = params
    y = np.zeros_like(x, dtype=float)

    if b != a:
        rising = (a < x) & (x < b)
        y[rising] = (x[rising] - a) / (b - a)

    plateau = (b <= x) & (x <= c)
    y[plateau] = 1.0

    if d != c:
        falling = (c < x) & (x < d)
        y[falling] = (d - x[falling]) / (d - c)

    return np.clip(y, 0, 1)


def membership_value(value: float, mf_type: str, params: Tuple[float, ...]) -> float:
    x = np.array([value], dtype=float)
    if mf_type == "trimf":
        return float(trimf(x, params)[0])
    if mf_type == "trapmf":
        return float(trapmf(x, params)[0])
    raise ValueError(f"Bilinmeyen üyelik fonksiyonu tipi: {mf_type}")


def validate_inputs(can: float, uzaklik: float, cephane: float, takim: float) -> None:
    values = {
        "can": can,
        "uzaklik": uzaklik,
        "cephane": cephane,
        "takim": takim,
    }
    for name, value in values.items():
        min_val, max_val = INPUT_VARIABLES[name]["range"]
        if not (min_val <= value <= max_val):
            raise ValueError(f"{name} değeri {min_val}-{max_val} aralığında olmalıdır. Girilen: {value}")


def fuzzify(inputs: Dict[str, float]) -> Dict[str, Dict[str, float]]:
    result: Dict[str, Dict[str, float]] = {}

    for var_name, crisp_value in inputs.items():
        result[var_name] = {}
        labels = INPUT_VARIABLES[var_name]["labels"]

        for label, (mf_type, params) in labels.items():
            result[var_name][label] = membership_value(crisp_value, mf_type, params)

    return result


def evaluate_rules(fuzzy_inputs: Dict[str, Dict[str, float]]) -> List[Dict[str, object]]:
    """Mamdani AND = min. Kural ağırlığı = ateşleme gücü * weight."""
    fired_rules = []

    for rule in RULES:
        degrees = []
        for variable, label in rule.antecedents.items():
            degrees.append(fuzzy_inputs[variable][label])

        raw_strength = min(degrees) if degrees else 0.0
        weighted_strength = raw_strength * rule.weight

        fired_rules.append(
            {
                "code": rule.code,
                "antecedents": rule.antecedents,
                "consequent": rule.consequent,
                "weight": rule.weight,
                "raw_strength": raw_strength,
                "strength": weighted_strength,
                "explanation": rule.explanation,
            }
        )

    return fired_rules


def output_membership(label: str, x: np.ndarray) -> np.ndarray:
    mf_type, params = OUTPUT_VARIABLE["aksiyon"]["labels"][label]
    if mf_type == "trimf":
        return trimf(x, params)
    if mf_type == "trapmf":
        return trapmf(x, params)
    raise ValueError(f"Bilinmeyen çıktı üyelik fonksiyonu tipi: {mf_type}")


def aggregate_output(fired_rules: List[Dict[str, object]], resolution: int = 1001) -> Tuple[np.ndarray, np.ndarray]:
    """Mamdani çıkarımı: her kuralın sonucu ateşleme gücü kadar kırpılır,
    kırpılmış kümeler maksimum işlemiyle birleştirilir."""
    x_out = np.linspace(0, 100, resolution)
    aggregated = np.zeros_like(x_out, dtype=float)

    for item in fired_rules:
        strength = float(item["strength"])
        if strength <= 0:
            continue

        consequent = str(item["consequent"])
        consequent_mf = output_membership(consequent, x_out)
        clipped = np.fmin(strength, consequent_mf)
        aggregated = np.fmax(aggregated, clipped)

    return x_out, aggregated


def defuzzify_centroid(x: np.ndarray, aggregated: np.ndarray) -> float:
    area = np.trapz(aggregated, x)
    if area == 0:
        # Hiçbir kural ateşlenmezse nötr değer verilir.
        return 50.0

    return float(np.trapz(x * aggregated, x) / area)


def interpret_action(score: float) -> str:
    if score < 30:
        return "Kaç"
    if score < 55:
        return "Savun"
    if score < 75:
        return "Takip"
    return "Saldır"


def infer(can: float, uzaklik: float, cephane: float, takim: float) -> Dict[str, object]:
    validate_inputs(can, uzaklik, cephane, takim)

    inputs = {
        "can": can,
        "uzaklik": uzaklik,
        "cephane": cephane,
        "takim": takim,
    }

    fuzzy_inputs = fuzzify(inputs)
    fired_rules = evaluate_rules(fuzzy_inputs)
    x_out, aggregated = aggregate_output(fired_rules)
    score = defuzzify_centroid(x_out, aggregated)
    action = interpret_action(score)

    active_rules = [r for r in fired_rules if float(r["strength"]) > 0]

    return {
        "inputs": inputs,
        "fuzzy_inputs": fuzzy_inputs,
        "fired_rules": fired_rules,
        "active_rules": active_rules,
        "x_out": x_out,
        "aggregated": aggregated,
        "score": score,
        "action": action,
    }
