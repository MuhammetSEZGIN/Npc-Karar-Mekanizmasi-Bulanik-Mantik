"""
BIM434 Bulanık Mantık Projesi
Bulanık Mantık Tabanlı NPC Karar Mekanizması

Çalıştırma:
    python main.py
"""

from definitions import TEST_SCENARIOS
from fuzzy_system import infer
from visualization import generate_all_plots


def print_result(title: str, result: dict, expected: str | None = None) -> None:
    print("=" * 80)
    print(title)
    print("-" * 80)
    print("Girişler:")
    for key, value in result["inputs"].items():
        print(f"  {key:8s}: {value}")

    print(f"\nAksiyon skoru: {result['score']:.2f}")
    print(f"Karar        : {result['action']}")

    if expected is not None:
        print(f"Beklenen     : {expected}")

    print("\nAktif kurallar:")
    active = sorted(result["active_rules"], key=lambda r: r["strength"], reverse=True)

    if not active:
        print("  Aktif kural yok.")
    else:
        for rule in active:
            print(
                f"  {rule['code']:>3s} | "
                f"çıktı={rule['consequent']:6s} | "
                f"ham={rule['raw_strength']:.3f} | "
                f"ağırlık={rule['weight']:.1f} | "
                f"son={rule['strength']:.3f}"
            )

    print()


def run_tests() -> list:
    results = []
    for scenario in TEST_SCENARIOS:
        result = infer(**scenario["inputs"])
        result["scenario_name"] = scenario["name"]
        result["expected"] = scenario["expected_behavior"]
        result["expected_score"] = scenario.get("expected_score")
        result["commentary"] = scenario.get("commentary", "")
        results.append(result)
        print_result(scenario["name"], result, scenario["expected_behavior"])

    return results


def interactive_demo() -> None:
    print("=" * 80)
    print("NPC Karar Mekanizması - Manuel Demo")
    print("Değerler 0-100 aralığında girilmelidir.")
    print("Boş geçersen manuel demo atlanır.")
    print("-" * 80)

    try:
        can_text = input("NPC canı: ").strip()
        if can_text == "":
            print("Manuel demo atlandı.")
            return

        can = float(can_text)
        uzaklik = float(input("Oyuncuya uzaklık: ").strip())
        cephane = float(input("NPC cephane / enerji: ").strip())
        takim = float(input("Oyuncu takım desteği: ").strip())

        result = infer(can=can, uzaklik=uzaklik, cephane=cephane, takim=takim)
        print_result("Manuel Demo Sonucu", result)

    except ValueError as exc:
        print(f"Hata: {exc}")


def main() -> None:
    test_results = run_tests()

    # Görselleştirmelerde örnek olarak S6 kullanılıyor.
    # Çünkü R13 ve R15 aynı anda ateşlenerek ağırlık/öncelik etkisini gösteriyor.
    example_result = test_results[-1]

    generate_all_plots(
        example_result=example_result,
        test_results=test_results,
        output_dir="outputs",
    )

    print("=" * 80)
    print("Grafikler 'outputs' klasörüne kaydedildi.")
    print("=" * 80)
    print()

    interactive_demo()


if __name__ == "__main__":
    main()
