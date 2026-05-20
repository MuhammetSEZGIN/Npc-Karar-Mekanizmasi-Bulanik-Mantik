"""
- giriş ve çıkış dilsel değişkenleri
- kural tabanı 
- test senaryoları 
"""

from dataclasses import dataclass
from typing import Dict, List


INPUT_VARIABLES = {
    "can": {
        "range": (0, 100),
        "labels": {
            "dusuk": ("trapmf", (0, 0, 25, 45)),
            "orta": ("trimf", (30, 50, 70)),
            "yuksek": ("trapmf", (55, 75, 100, 100)),
        },
    },
    "uzaklik": {
        "range": (0, 100),
        "labels": {
            "yakin": ("trapmf", (0, 0, 20, 40)),
            "orta": ("trimf", (25, 50, 75)),
            "uzak": ("trapmf", (60, 80, 100, 100)),
        },
    },
    "cephane": {
        "range": (0, 100),
        "labels": {
            "az": ("trapmf", (0, 0, 20, 40)),
            "orta": ("trimf", (25, 50, 75)),
            "fazla": ("trapmf", (60, 80, 100, 100)),
        },
    },
    "takim": {
        "range": (0, 100),
        "labels": {
            "yalniz": ("trapmf", (0, 0, 20, 40)),
            "orta": ("trimf", (25, 50, 75)),
            "kalabalik": ("trapmf", (60, 80, 100, 100)),
        },
    },
}


OUTPUT_VARIABLE = {
    "aksiyon": {
        "range": (0, 100),
        "labels": {
            "kac": ("trapmf", (0, 0, 15, 30)),
            "savun": ("trimf", (20, 40, 55)),
            "takip": ("trimf", (45, 60, 75)),
            "saldir": ("trapmf", (70, 85, 100, 100)),
        },
    }
}


@dataclass
class Rule:
    code: str
    antecedents: Dict[str, str]
    consequent: str
    weight: float = 1.0
    explanation: str = ""


RULES: List[Rule] = [
    Rule(
        "R1",
        {"can": "dusuk", "uzaklik": "yakin", "takim": "kalabalik"},
        "kac",
        1.0,
        "NPC zayıf, oyuncu yakın ve kalabalık. En riskli durum.",
    ),
    Rule(
        "R2",
        {"can": "dusuk", "uzaklik": "yakin", "cephane": "az"},
        "kac",
        1.0,
        "Can ve cephane düşükken yakın çatışma sürdürülemez.",
    ),
    Rule(
        "R3",
        {"can": "dusuk", "uzaklik": "uzak", "cephane": "fazla", "takim": "yalniz"},
        "saldir",
        1.0,
        "Sezgiye aykırı kural: can düşük olsa da güvenli mesafe, cephane avantajı ve yalnız oyuncu saldırı fırsatı oluşturur.",
    ),
    Rule(
        "R4",
        {"can": "dusuk", "uzaklik": "uzak", "cephane": "az"},
        "savun",
        1.0,
        "Oyuncu uzakta olduğu için hemen kaçmak yerine siperde kalabilir.",
    ),
    Rule(
        "R5",
        {"can": "dusuk", "uzaklik": "orta", "cephane": "orta", "takim": "yalniz"},
        "savun",
        1.0,
        "Can düşük ama durum tamamen umutsuz değil; alan savunması mantıklı.",
    ),
    Rule(
        "R6",
        {"can": "orta", "uzaklik": "yakin", "cephane": "az", "takim": "orta"},
        "savun",
        1.0,
        "Oyuncu yakın ve orta düzey destekli, cephane az; doğrudan saldırı riskli.",
    ),
    Rule(
        "R7",
        {"can": "orta", "uzaklik": "orta", "cephane": "orta", "takim": "yalniz"},
        "takip",
        1.0,
        "Dengeli durumda yalnız oyuncuya karşı pozisyon alınabilir.",
    ),
    Rule(
        "R8",
        {"can": "orta", "uzaklik": "uzak", "cephane": "orta", "takim": "yalniz"},
        "takip",
        1.0,
        "Oyuncu yalnız ve uzakta; NPC mesafeyi kapatabilir.",
    ),
    Rule(
        "R9",
        {"can": "orta", "uzaklik": "yakin", "cephane": "fazla", "takim": "yalniz"},
        "saldir",
        1.0,
        "Yakın mesafe, yeterli can ve cephane avantajı var.",
    ),
    Rule(
        "R10",
        {"can": "orta", "uzaklik": "yakin", "cephane": "orta", "takim": "kalabalik"},
        "savun",
        1.0,
        "Kalabalık baskıya karşı kaçmak yerine alanı koruma davranışı.",
    ),
    Rule(
        "R11",
        {"can": "yuksek", "uzaklik": "yakin", "cephane": "fazla", "takim": "yalniz"},
        "saldir",
        1.0,
        "En güçlü saldırı durumu.",
    ),
    Rule(
        "R12",
        {"can": "yuksek", "uzaklik": "orta", "cephane": "fazla", "takim": "orta"},
        "saldir",
        1.0,
        "NPC güçlü; oyuncu orta destekli olsa bile saldırı kabul edilebilir.",
    ),
    Rule(
        "R13",
        {"can": "yuksek", "cephane": "az", "takim": "kalabalik"},
        "savun",
        0.7,
        "Can yüksek ama cephane ve sayı dezavantajı var. R15 ile çelişebileceği için ağırlığı 0.7 seçilmiştir.",
    ),
    Rule(
        "R14",
        {"can": "yuksek", "uzaklik": "uzak", "cephane": "fazla", "takim": "yalniz"},
        "takip",
        1.0,
        "NPC güçlü olduğu için uzaktan ateş etmek yerine mesafeyi kapatabilir.",
    ),
    Rule(
        "R15",
        {"uzaklik": "yakin", "cephane": "az", "takim": "kalabalik"},
        "kac",
        1.0,
        "Genel tehlike kuralı. Cephane az, oyuncu yakın ve kalabalıksa can ne olursa olsun geri çekilme mantıklıdır.",
    ),
]


TEST_SCENARIOS = [
    {
        "id": 1,
        "name": "S1 - Kritik Kaçış",
        "inputs": {
            "can": 10,
            "uzaklik": 10,
            "cephane": 15,
            "takim": 90,
        },
        "expected_behavior": "Kaç",
        "expected_score": 11.67,
        "commentary": (
            "Kritik kaçış durumudur. R1, R2 ve R15 ateşlenmiştir."
        ),
    },
    {
        "id": 2,
        "name": "S2 - Fırsat Saldırısı",
        "inputs": {
            "can": 20,
            "uzaklik": 90,
            "cephane": 90,
            "takim": 10,
        },
        "expected_behavior": "Saldır",
        "expected_score": 88.33,
        "commentary": (
            "Can düşük olsa da uzaklık ve cephane avantajı saldırı üretmiştir."
        ),
    },
    {
        "id": 3,
        "name": "S3 - Dengeli Takip",
        "inputs": {
            "can": 50,
            "uzaklik": 50,
            "cephane": 50,
            "takim": 10,
        },
        "expected_behavior": "Takip",
        "expected_score": 60.00,
        "commentary": (
            "Dengeli durumda yalnız oyuncuya karşı takip davranışı oluşmuştur."
        ),
    },
    {
        "id": 4,
        "name": "S4 - Güçlü Saldırı",
        "inputs": {
            "can": 90,
            "uzaklik": 15,
            "cephane": 90,
            "takim": 10,
        },
        "expected_behavior": "Saldır",
        "expected_score": 88.33,
        "commentary": (
            "Yüksek can, yakın mesafe ve fazla cephane saldırıyı desteklemiştir."
        ),
    },
    {
        "id": 5,
        "name": "S5 - Dezavantajlı Savunma",
        "inputs": {
            "can": 90,
            "uzaklik": 50,
            "cephane": 15,
            "takim": 90,
        },
        "expected_behavior": "Savun",
        "expected_score": 38.22,
        "commentary": (
            "Can yüksek olsa da cephane az ve oyuncu kalabalık olduğu için savunma seçilmiştir."
        ),
    },
    {
        "id": 6,
        "name": "S6 - Öncelik Çatışması",
        "inputs": {
            "can": 90,
            "uzaklik": 10,
            "cephane": 10,
            "takim": 90,
        },
        "expected_behavior": "Kaç",
        "expected_score": 22.57,
        "commentary": (
            "R13 ve R15 birlikte ateşlenmiş, R15 ağırlık avantajı ile kaçış baskın olmuştur."
        ),
    },
]
