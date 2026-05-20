import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from fuzzy_system import (
    infer,
    INPUT_VARIABLES,
    OUTPUT_VARIABLE,
    RULES,
    TEST_SCENARIOS,
    trimf,
    trapmf,
    output_membership,
)


DISPLAY = {
    "can": "NPC Canı", "uzaklik": "Oyuncuya Uzaklık",
    "cephane": "Cephane / Enerji", "takim": "Oyuncu Takım Desteği",
    "dusuk": "Düşük", "orta": "Orta", "yuksek": "Yüksek",
    "yakin": "Yakın", "uzak": "Uzak", "az": "Az", "fazla": "Fazla",
    "yalniz": "Yalnız", "kalabalik": "Kalabalık",
    "kac": "Kaç", "savun": "Savun", "takip": "Takip", "saldir": "Saldır",
}

ACTION_COLOR = {
    "Kaç": "#e05a4f", "Savun": "#e8a13a",
    "Takip": "#4a8fd4", "Saldır": "#56a64b",
}

GAUGE_ZONES = [
    (0, 30, "#e05a4f", "Kaç"),
    (30, 55, "#e8a13a", "Savun"),
    (55, 75, "#4a8fd4", "Takip"),
    (75, 100, "#56a64b", "Saldır"),
]


def eval_mf(x, mf):
    mf_type, params = mf
    return trimf(x, params) if mf_type == "trimf" else trapmf(x, params)


def rule_text(rule):
    conds = " AND ".join(
        f"{DISPLAY.get(v, v)} {DISPLAY.get(l, l)}"
        for v, l in rule.antecedents.items()
    )
    return f"EĞER {conds}  →  {DISPLAY.get(rule.consequent, rule.consequent)}"


def draw_gauge(score):
    fig, ax = plt.subplots(figsize=(8, 1.25))
    for lo, hi, color, name in GAUGE_ZONES:
        ax.barh(0, hi - lo, left=lo, color=color, height=0.5)
        ax.text((lo + hi) / 2, 0, name, ha="center", va="center",
                color="white", fontsize=9, fontweight="bold")
    ax.scatter([score], [0.0], color="#1a1a1a", s=140, marker="v", zorder=5)
    ax.text(score, 0.5, f"{score:.1f}", ha="center", fontsize=11, fontweight="bold")
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 0.8)
    ax.set_yticks([])
    ax.set_xticks([0, 25, 50, 75, 100])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig


def _load_scenario(scenario_id: int) -> None:
    """on_click callback: widget yeniden çizilmeden önce session_state güncellenir."""
    sc = next(s for s in TEST_SCENARIOS if s["id"] == scenario_id)
    for k, v in sc["inputs"].items():
        st.session_state[k] = v


st.set_page_config(
    page_title="NPC Bulanık Karar Sistemi",
    layout="wide",
)

st.title("Bulanık Mantık Tabanlı NPC Karar Mekanizması")
st.caption(
    "BIM434 — Soldaki girişleri ayarlayın; NPC'nin kararını ve sistemin "
    "iç işleyişini canlı izleyin."
)

DEFAULT_INPUTS = {"can": 60, "uzaklik": 40, "cephane": 55, "takim": 30}
for _k, _v in DEFAULT_INPUTS.items():
    st.session_state.setdefault(_k, _v)

with st.sidebar:
    st.header("Giriş Değerleri")
    can = st.slider("NPC Canı", 0, 100, key="can")
    uzaklik = st.slider("Oyuncuya Uzaklık", 0, 100, key="uzaklik")
    cephane = st.slider("Cephane / Enerji", 0, 100, key="cephane")
    takim = st.slider("Oyuncu Takım Desteği", 0, 100, key="takim")
    st.caption(
        "Tüm değişkenler 0–100 ölçeğindedir. Hazır senaryolar "
        "**Test Senaryoları** sekmesinden seçilebilir."
    )

crisp = {"can": can, "uzaklik": uzaklik, "cephane": cephane, "takim": takim}
result = infer(**crisp)
score = result["score"]
action = result["action"]

color = ACTION_COLOR.get(action, "#888888")

st.markdown(
    f"""
    <div style="background:{color};padding:18px 26px;border-radius:14px;color:white;">
        <div style="font-size:14px;letter-spacing:1px;opacity:.85;">NPC KARARI</div>
        <div style="font-size:36px;font-weight:800;line-height:1.2;">{action}</div>
        <div style="font-size:15px;opacity:.9;">Aksiyon Skoru: {score:.1f} / 100</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.pyplot(draw_gauge(score))
plt.close("all")

n_active = len(result["active_rules"])
if n_active == 0:
    st.warning(
        "Hiçbir kural ateşlenmedi — bu giriş bileşimi kural tabanı tarafından "
        "kapsanmıyor; skor nötr (50) kabul edildi."
    )
else:
    st.caption(f"Bu giriş için {n_active} kural ateşlendi.")


tab_scenarios, tab_details = st.tabs(
    ["Test Senaryoları", "Detaylı Görselleştirmeler"]
)

with tab_scenarios:
    st.markdown(
        """
        <style>
        div[data-testid="stButton"] > button {
            text-align: left !important;
            padding: 14px 18px !important;
            height: auto !important;
            min-height: 110px;
            white-space: normal !important;
            line-height: 1.55 !important;
            border-radius: 12px !important;
            border: 1.5px solid rgba(128, 128, 128, 0.30) !important;
            font-weight: 400 !important;
        }
        div[data-testid="stButton"] > button:hover {
            border-color: rgba(99, 102, 241, 0.65) !important;
            background: rgba(99, 102, 241, 0.06) !important;
        }
        div[data-testid="stButton"] > button[kind="primary"] {
            border-color: #6366f1 !important;
            border-width: 2px !important;
            background: rgba(99, 102, 241, 0.12) !important;
            color: inherit !important;
        }
        div[data-testid="stButton"] > button p { margin: 0 0 6px 0 !important; }
        div[data-testid="stButton"] > button p:last-child { margin-bottom: 0 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Senaryo Seçimi")
    st.caption(
        "Sınır durumlarını ve aşırı değerleri içeren aşağıdaki senaryolardan "
        "birinin **üzerine tıklayarak** sistemi anlık test edebilirsiniz. "
        "Seçilen senaryonun değerleri sliderlara yüklenir ve **NPC Kararı** güncellenir."
    )

    active_id = next(
        (sc["id"] for sc in TEST_SCENARIOS if sc["inputs"] == crisp),
        None,
    )

    for sc in TEST_SCENARIOS:
        inp = sc["inputs"]
        expected = sc["expected_behavior"]
        bare_name = (
            sc["name"].split("-", 1)[1].strip() if "-" in sc["name"] else sc["name"]
        )
        is_active = sc["id"] == active_id

        label = (
            f"**Senaryo {sc['id']}: {bare_name}** ({expected})  "
            f"&nbsp;&nbsp;&nbsp; `BEKLENEN: {expected.upper()}`\n\n"
            f"Can: **{inp['can']}** &nbsp;&nbsp; "
            f"Uzak: **{inp['uzaklik']}** &nbsp;&nbsp; "
            f"Ceph: **{inp['cephane']}** &nbsp;&nbsp; "
            f"Dest: **{inp['takim']}**\n\n"
            f"_{sc['commentary']}_"
        )

        st.button(
            label,
            key=f"scenario_btn_{sc['id']}",
            on_click=_load_scenario,
            args=(sc["id"],),
            use_container_width=True,
            type="primary" if is_active else "secondary",
        )

with tab_details:
    st.subheader("Üyelik Fonksiyonları")
    st.caption("Kesik siyah çizgi, o değişkenin **anlık giriş değerini** gösterir.")
    cols = st.columns(2)
    for i, (var, info) in enumerate(INPUT_VARIABLES.items()):
        with cols[i % 2]:
            lo, hi = info["range"]
            x = np.linspace(lo, hi, 500)
            fig, ax = plt.subplots(figsize=(5, 3))
            for label, mf in info["labels"].items():
                ax.plot(x, eval_mf(x, mf), label=DISPLAY.get(label, label))
            ax.axvline(crisp[var], color="black", linestyle="--", linewidth=1.2)
            ax.set_title(DISPLAY.get(var, var))
            ax.set_xlabel("Değer")
            ax.set_ylabel("Üyelik Derecesi")
            ax.set_ylim(-0.05, 1.05)
            ax.grid(alpha=0.3)
            ax.legend(fontsize=8)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    lo, hi = OUTPUT_VARIABLE["aksiyon"]["range"]
    x = np.linspace(lo, hi, 500)
    fig, ax = plt.subplots(figsize=(9, 3))
    for label, mf in OUTPUT_VARIABLE["aksiyon"]["labels"].items():
        ax.plot(x, eval_mf(x, mf), label=DISPLAY.get(label, label))
    ax.axvline(score, color="black", linestyle="--", linewidth=1.2)
    ax.set_title("NPC Aksiyon Skoru — Çıkış Üyelik Fonksiyonları")
    ax.set_xlabel("Aksiyon Skoru")
    ax.set_ylabel("Üyelik Derecesi")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.divider()

    st.subheader("Kural Ateşleme")
    active_rules_sorted = sorted(
        result["active_rules"], key=lambda r: r["strength"], reverse=True
    )
    if not active_rules_sorted:
        st.info("Bu giriş bileşiminde ateşlenen kural yok.")
    else:
        codes = [r["code"] for r in active_rules_sorted]
        strengths = [r["strength"] for r in active_rules_sorted]

        fig, ax = plt.subplots(figsize=(8, max(2.5, 0.45 * len(active_rules_sorted))))
        ax.barh(codes, strengths, color="#4a8fd4")
        ax.invert_yaxis()
        ax.set_xlim(0, 1.05)
        ax.set_xlabel("Ateşleme Gücü (ağırlık uygulanmış)")
        ax.set_title("Aktif Kuralların Ateşleme Dereceleri")
        ax.grid(axis="x", alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        st.dataframe(
            [
                {
                    "Kural": r["code"],
                    "Çıkış": DISPLAY.get(r["consequent"], r["consequent"]),
                    "Ham Güç": round(r["raw_strength"], 3),
                    "Ağırlık": r["weight"],
                    "Sonuç Güç": round(r["strength"], 3),
                    "Gerekçe": r["explanation"],
                }
                for r in active_rules_sorted
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    st.subheader("Durulaştırma")
    x_out = result["x_out"]
    aggregated = result["aggregated"]

    fig, ax = plt.subplots(figsize=(9, 3.6))
    for label in OUTPUT_VARIABLE["aksiyon"]["labels"]:
        ax.plot(x_out, output_membership(label, x_out),
                linestyle="--", alpha=0.5, label=DISPLAY.get(label, label))
    ax.fill_between(x_out, aggregated, alpha=0.35, color="#4a8fd4",
                    label="Birleşik çıkış kümesi")
    ax.axvline(score, color="black", linewidth=2,
               label=f"Centroid = {score:.1f}")
    ax.set_title("Durulaştırma — Birleşik Çıkış Kümesi ve Ağırlık Merkezi")
    ax.set_xlabel("Aksiyon Skoru")
    ax.set_ylabel("Üyelik Derecesi")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


with st.expander(f"Kural Tabanı — {len(RULES)} kural"):
    for rule in RULES:
        weight_note = "" if rule.weight == 1.0 else f"  · ağırlık={rule.weight}"
        st.markdown(f"**{rule.code}** — {rule_text(rule)}{weight_note}")
