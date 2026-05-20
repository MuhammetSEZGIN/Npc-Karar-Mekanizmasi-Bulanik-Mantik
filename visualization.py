from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from fuzzy_system import (
    INPUT_VARIABLES,
    OUTPUT_VARIABLE,
    trimf,
    trapmf,
    infer,
    output_membership,
)


DISPLAY_NAMES = {
    "can": "NPC Canı",
    "uzaklik": "Oyuncuya Uzaklık",
    "cephane": "NPC Cephane / Enerji",
    "takim": "Oyuncu Takım Desteği",
    "aksiyon": "NPC Aksiyon Skoru",
    "dusuk": "Düşük",
    "yuksek": "Yüksek",
    "yakin": "Yakın",
    "uzak": "Uzak",
    "az": "Az",
    "fazla": "Fazla",
    "orta": "Orta",
    "yalniz": "Yalnız",
    "kalabalik": "Kalabalık",
    "kac": "Kaç",
    "savun": "Savun",
    "takip": "Takip",
    "saldir": "Saldır",
}


ACTION_TO_SCORE = {
    "Kaç": 15,
    "Savun": 42,
    "Takip": 62,
    "Saldır": 88,
}


def _eval_mf(x, mf_type, params):
    if mf_type == "trimf":
        return trimf(x, params)
    if mf_type == "trapmf":
        return trapmf(x, params)
    raise ValueError(f"Bilinmeyen üyelik fonksiyonu tipi: {mf_type}")


def plot_input_memberships(output_dir: str = "outputs") -> None:
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for var_name, info in INPUT_VARIABLES.items():
        min_val, max_val = info["range"]
        x = np.linspace(min_val, max_val, 1001)

        plt.figure(figsize=(8, 4.5))
        for label, (mf_type, params) in info["labels"].items():
            y = _eval_mf(x, mf_type, params)
            plt.plot(x, y, label=DISPLAY_NAMES.get(label, label))

        plt.title(f"{DISPLAY_NAMES.get(var_name, var_name)} Üyelik Fonksiyonları")
        plt.xlabel(DISPLAY_NAMES.get(var_name, var_name))
        plt.ylabel("Üyelik Derecesi")
        plt.ylim(-0.05, 1.05)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path / f"membership_{var_name}.png", dpi=200)
        plt.close()


def plot_output_membership(output_dir: str = "outputs") -> None:
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    min_val, max_val = OUTPUT_VARIABLE["aksiyon"]["range"]
    x = np.linspace(min_val, max_val, 1001)

    plt.figure(figsize=(8, 4.5))
    for label, (mf_type, params) in OUTPUT_VARIABLE["aksiyon"]["labels"].items():
        y = _eval_mf(x, mf_type, params)
        plt.plot(x, y, label=DISPLAY_NAMES.get(label, label))

    plt.title("NPC Aksiyon Skoru Üyelik Fonksiyonları")
    plt.xlabel("Aksiyon Skoru")
    plt.ylabel("Üyelik Derecesi")
    plt.ylim(-0.05, 1.05)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path / "membership_aksiyon.png", dpi=200)
    plt.close()


def plot_rule_activation(result: dict, output_dir: str = "outputs") -> None:
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    active_rules = result["active_rules"]
    labels = [r["code"] for r in active_rules]
    strengths = [float(r["strength"]) for r in active_rules]

    if not labels:
        labels = ["Kural yok"]
        strengths = [0]

    plt.figure(figsize=(8, 4.5))
    plt.bar(labels, strengths)
    plt.title("Kural Ateşleme Dereceleri")
    plt.xlabel("Kurallar")
    plt.ylabel("Ateşleme Gücü")
    plt.ylim(0, 1.05)
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path / "rule_activation.png", dpi=200)
    plt.close()


def plot_defuzzification(result: dict, output_dir: str = "outputs") -> None:
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    x_out = result["x_out"]
    aggregated = result["aggregated"]
    score = result["score"]

    plt.figure(figsize=(8, 4.5))

    for label in OUTPUT_VARIABLE["aksiyon"]["labels"]:
        plt.plot(x_out, output_membership(label, x_out), linestyle="--", alpha=0.6, label=DISPLAY_NAMES.get(label, label))

    plt.fill_between(x_out, aggregated, alpha=0.35, label="Birleşik Çıkış Kümesi")
    plt.axvline(score, linestyle="-", label=f"Centroid = {score:.2f}")

    plt.title("Durulaştırma Grafiği")
    plt.xlabel("Aksiyon Skoru")
    plt.ylabel("Üyelik Derecesi")
    plt.ylim(-0.05, 1.05)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path / "defuzzification.png", dpi=200)
    plt.close()


def plot_test_scenarios(test_results: list, output_dir: str = "outputs") -> None:
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    labels = [f"S{i+1}" for i in range(len(test_results))]
    scores = [r["score"] for r in test_results]

    plt.figure(figsize=(8, 4.5))
    plt.bar(labels, scores)
    plt.title("Test Senaryoları Aksiyon Skoru Karşılaştırması")
    plt.xlabel("Senaryo")
    plt.ylabel("Aksiyon Skoru")
    plt.ylim(0, 100)
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path / "test_scenarios_comparison.png", dpi=200)
    plt.close()


def plot_test_scenarios_input_output(test_results: list, output_dir: str = "outputs") -> None:
    """
    En az 5 test senaryosu için giriş ve çıkış değerlerini aynı grafikte karşılaştırır.
    Bütün değişkenler 0-100 ölçeğinde olduğu için doğrudan karşılaştırılabilir.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    labels = [f"S{i+1}" for i in range(len(test_results))]
    series = {
        "Can": [r["inputs"]["can"] for r in test_results],
        "Uzaklık": [r["inputs"]["uzaklik"] for r in test_results],
        "Cephane": [r["inputs"]["cephane"] for r in test_results],
        "Takım": [r["inputs"]["takim"] for r in test_results],
        "Aksiyon Skoru": [r["score"] for r in test_results],
        "Beklenen Davranış Skoru": [ACTION_TO_SCORE.get(r.get("expected", ""), np.nan) for r in test_results],
    }

    x = np.arange(len(labels))
    plt.figure(figsize=(10, 5.5))
    for name, values in series.items():
        plt.plot(x, values, marker="o", label=name)

    plt.title("Test Senaryoları Giriş-Çıkış Karşılaştırması")
    plt.xlabel("Senaryo")
    plt.ylabel("Değer / Skor (0-100)")
    plt.xticks(x, labels)
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3)
    plt.legend(ncol=2)
    plt.tight_layout()
    plt.savefig(output_path / "test_scenarios_input_output.png", dpi=200)
    plt.close()


def plot_surface_can_cephane(
    uzaklik: float = 30,
    takim: float = 20,
    output_dir: str = "outputs"
) -> None:
    """
    İki giriş seçilerek 3B yüzey grafiği oluşturulur.
    Bu örnekte:
        x ekseni: can
        y ekseni: cephane
    Sabit değerler:
        uzaklik = 30
        takim = 20
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    can_values = np.linspace(0, 100, 31)
    cephane_values = np.linspace(0, 100, 31)
    C, A = np.meshgrid(can_values, cephane_values)

    Z = np.zeros_like(C, dtype=float)

    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            Z[i, j] = infer(
                can=float(C[i, j]),
                uzaklik=uzaklik,
                cephane=float(A[i, j]),
                takim=takim,
            )["score"]

    fig = plt.figure(figsize=(8, 5.5))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(C, A, Z, linewidth=0, antialiased=True, alpha=0.9)

    ax.set_title("Giriş-Çıkış Yüzeyi: Can ve Cephane")
    ax.set_xlabel("NPC Canı")
    ax.set_ylabel("Cephane")
    ax.set_zlabel("Aksiyon Skoru")

    plt.tight_layout()
    plt.savefig(output_path / "surface_can_cephane.png", dpi=200)
    plt.close()


def plot_sensitivity_analysis(output_dir: str = "outputs") -> None:
    """
    Giriş değeri hassasiyet analizi:
    Cephane değeri değiştirilirken diğer girişler sabit tutulur.
    Bu grafik sistem davranışını anlamak için ek olarak bırakılmıştır.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    ammo_values = np.linspace(0, 100, 101)
    scores = []

    for ammo in ammo_values:
        score = infer(
            can=60,
            uzaklik=25,
            cephane=float(ammo),
            takim=40,
        )["score"]
        scores.append(score)

    plt.figure(figsize=(8, 4.5))
    plt.plot(ammo_values, scores)
    plt.title("Giriş Hassasiyeti: Cephane Değerinin Aksiyon Skoruna Etkisi")
    plt.xlabel("Cephane Değeri")
    plt.ylabel("Aksiyon Skoru")
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path / "sensitivity_cephane_input.png", dpi=200)
    plt.close()


def plot_membership_parameter_analysis(output_dir: str = "outputs") -> None:
    """
    Zorunlu parametre analizi:
    'Cephane fazla' yamuksal üyelik fonksiyonundaki sol başlangıç parametresi değiştirilir.

    Orijinal fonksiyon: [60, 80, 100, 100]
    Analizde değiştirilen parametre: ilk değer, yani 'fazla' üyeliğinin başlama noktası.
    Sabit test girdisi: can=20, uzaklik=90, cephane=70, takim=10.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    original = INPUT_VARIABLES["cephane"]["labels"]["fazla"]
    mf_type, params = original
    _, b, c, d = params

    start_values = np.linspace(40, 75, 15)
    scores = []

    try:
        for start in start_values:
            INPUT_VARIABLES["cephane"]["labels"]["fazla"] = (mf_type, (float(start), b, c, d))
            result = infer(can=20, uzaklik=90, cephane=70, takim=10)
            scores.append(result["score"])
    finally:
        INPUT_VARIABLES["cephane"]["labels"]["fazla"] = original

    plt.figure(figsize=(8, 4.5))
    plt.plot(start_values, scores, marker="o")
    plt.axvline(60, linestyle="--", label="Orijinal parametre = 60")
    plt.title("Parametre Analizi: 'Cephane Fazla' Başlangıç Parametresi")
    plt.xlabel("'Fazla' Üyeliğinin Başlama Parametresi")
    plt.ylabel("Aksiyon Skoru")
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path / "parameter_analysis_cephane_fazla.png", dpi=200)
    plt.close()


def generate_all_plots(example_result: dict, test_results: list, output_dir: str = "outputs") -> None:
    plot_system_architecture(output_dir)
    plot_input_memberships(output_dir)
    plot_output_membership(output_dir)
    plot_rule_activation(example_result, output_dir)
    plot_defuzzification(example_result, output_dir)
    plot_test_scenarios(test_results, output_dir)
    plot_test_scenarios_input_output(test_results, output_dir)
    plot_surface_can_cephane(output_dir=output_dir)
    plot_sensitivity_analysis(output_dir)
    plot_membership_parameter_analysis(output_dir)
