import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ==============================================================================
# 1. PAGE CONFIGURATION & CORPORATE THEME
# ==============================================================================
st.set_page_config(
    page_title="Telkom Indonesia - OPEX & Asset Depreciation Tracker",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Telkom Indonesia Corporate Color Palette
TELKOM_RED = "#E30613"
TELKOM_DARK_RED = "#B0040F"
TELKOM_DARK_GREY = "#1F2937"
TELKOM_SLATE = "#4B5563"
TELKOM_LIGHT_GREY = "#F3F4F6"
TELKOM_BORDER = "#E5E7EB"
SUCCESS_GREEN = "#10B981"
WARNING_AMBER = "#F59E0B"
ALERT_RED = "#EF4444"

# Inject Executive Corporate Styling
st.markdown(
    f"""
    <style>
        /* Global Font & Background */
        .stApp {{
            background-color: #F9FAFB;
            color: {TELKOM_DARK_GREY};
        }}
        /* Corporate Header Banner */
        .telkom-banner {{
            background: linear-gradient(90deg, {TELKOM_DARK_GREY} 0%, #374151 70%, {TELKOM_DARK_RED} 100%);
            padding: 1.5rem 2rem;
            border-radius: 10px;
            color: #FFFFFF;
            margin-bottom: 1.25rem;
            border-left: 8px solid {TELKOM_RED};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .telkom-banner h1 {{
            margin: 0;
            font-size: 1.75rem;
            font-weight: 700;
            color: #FFFFFF;
        }}
        .telkom-banner p {{
            margin: 0.35rem 0 0 0;
            font-size: 0.95rem;
            color: #E5E7EB;
        }}
        /* Executive KPI Cards */
        .kpi-card {{
            background-color: #FFFFFF;
            border: 1px solid {TELKOM_BORDER};
            border-top: 4px solid {TELKOM_RED};
            border-radius: 8px;
            padding: 1.1rem 1.25rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
            height: 100%;
        }}
        .kpi-title {{
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: {TELKOM_SLATE};
            margin-bottom: 0.35rem;
        }}
        .kpi-value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: {TELKOM_DARK_GREY};
            line-height: 1.2;
        }}
        .kpi-delta {{
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 0.4rem;
        }}
        .delta-neg {{ color: {TELKOM_RED}; }}
        .delta-pos {{ color: {SUCCESS_GREEN}; }}
        .delta-neutral {{ color: {TELKOM_SLATE}; }}
        /* Callout Boxes */
        .callout-danger {{
            background-color: #FEF2F2;
            border-left: 5px solid {TELKOM_RED};
            padding: 1rem 1.25rem;
            border-radius: 6px;
            margin-bottom: 1rem;
        }}
        .callout-warning {{
            background-color: #FFFBEB;
            border-left: 5px solid {WARNING_AMBER};
            padding: 1rem 1.25rem;
            border-radius: 6px;
            margin-bottom: 1rem;
        }}
        /* Sidebar Header */
        section[data-testid="stSidebar"] {{
            background-color: #FFFFFF;
            border-right: 1px solid {TELKOM_BORDER};
        }}
        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            border-bottom: 2px solid {TELKOM_BORDER};
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: #FFFFFF;
            border-radius: 6px 6px 0 0;
            padding: 10px 18px;
            font-weight: 600;
            color: {TELKOM_SLATE};
            border: 1px solid {TELKOM_BORDER};
            border-bottom: none;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {TELKOM_RED} !important;
            color: #FFFFFF !important;
            border-color: {TELKOM_RED} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)


# ==============================================================================
# 2. CACHED MOCK DATA GENERATOR (RECONCILED TO 2025 FINANCIAL REPORT CONTEXT)
# ==============================================================================
@st.cache_data
def load_telkom_financial_data():
    """
    Generates reconciled mock financial datasets for PT Telkom Indonesia (Persero) Tbk
    covering 2023–2025 OPEX by cost component and business segment, plus 2023–2027
    asset depreciation curves. All values are in Rp Miliar unless noted.
    """
    segments = [
        "B2C",
        "B2B Infra",
        "B2B ICT",
        "International",
        "Strategic Holding/Lainnya"
    ]

    # Consolidated Cost Line Items (Rp Miliar)
    # 2025 Total = 112,151 (+2.8% YoY vs 2024 Total = 109,096)
    cost_items_consolidated = {
        "Operasi, Pemeliharaan & Jasa Telko": {2023: 40850.0, 2024: 41193.0, 2025: 41234.0},
        "Penyusutan & Amortisasi":            {2023: 32510.0, 2024: 34195.0, 2025: 37649.0},
        "Beban Karyawan":                     {2023: 17120.0, 2024: 16799.0, 2025: 16362.0},
        "Beban Interkoneksi":                 {2023: 7450.0,  2024: 7210.0,  2025: 7065.0},
        "Sewa Sirkuit & CPE":                 {2023: 2980.0,  2024: 3423.0,  2025: 4474.0},
        "Umum, Adm & Pemasaran":              {2023: 6180.0,  2024: 6276.0,  2025: 5367.0},
    }

    # Segment share weights per cost line item (each row sums to 1.00)
    segment_weights = {
        "Operasi, Pemeliharaan & Jasa Telko": [0.46, 0.30, 0.14, 0.06, 0.04],
        "Penyusutan & Amortisasi":            [0.42, 0.38, 0.10, 0.06, 0.04],
        "Beban Karyawan":                     [0.36, 0.20, 0.18, 0.07, 0.19],
        "Beban Interkoneksi":                 [0.52, 0.18, 0.05, 0.24, 0.01],
        "Sewa Sirkuit & CPE":                 [0.24, 0.34, 0.32, 0.08, 0.02],
        "Umum, Adm & Pemasaran":              [0.45, 0.15, 0.18, 0.06, 0.16],
    }

    # Slight annual shift in segment weights to keep 2023-2025 realistic
    year_adjustments = {
        2023: [1.01, 0.98, 0.99, 1.01, 1.01],
        2024: [1.00, 1.00, 1.00, 1.00, 1.00],
        2025: [0.99, 1.02, 1.02, 0.99, 0.98],
    }

    records = []
    for item, yr_vals in cost_items_consolidated.items():
        base_weights = np.array(segment_weights[item])
        for yr, total_val in yr_vals.items():
            adj_weights = base_weights * np.array(year_adjustments[yr])
            adj_weights = adj_weights / adj_weights.sum()
            allocations = total_val * adj_weights
            for seg, val in zip(segments, allocations):
                records.append({
                    "Year": yr,
                    "Segment": seg,
                    "Cost_Item": item,
                    "Amount_Miliar": round(float(val), 2)
                })

    opex_df = pd.DataFrame(records)

    # Consolidated Revenue (Rp Miliar) anchored to 2025 OPEX-to-Revenue Ratio = 76.4%
    # 112,151 / 0.764 = 146,794.5 Miliar
    revenue_df = pd.DataFrame({
        "Year": [2023, 2024, 2025],
        "Revenue_Miliar": [149210.0, 147850.0, 146794.5],
        "Segment_Split": ["Consolidated", "Consolidated", "Consolidated"]
    })

    # Segment Revenue Shares (used for OPEX-to-Revenue ratio when filtering segments)
    seg_rev_weights = {
        "B2C": 0.48,
        "B2B Infra": 0.25,
        "B2B ICT": 0.15,
        "International": 0.08,
        "Strategic Holding/Lainnya": 0.04,
    }

    # Depreciation & Drop Cable Reclassification Projection Baseline (2023–2027)
    # 2025 includes +Rp1,352 Miliar impact from drop cable reclassification under 3-year baseline life
    depreciation_base_df = pd.DataFrame({
        "Year": [2023, 2024, 2025, 2026, 2027],
        "Type": ["Historical", "Historical", "Historical", "Projected", "Projected"],
        "Non_DropCable_Depr_Miliar": [31980.0, 33610.0, 35712.0, 36950.0, 38100.0],
        "DropCable_Base_Depr_Miliar": [530.0, 585.0, 1937.0, 2150.0, 2280.0],  # 2025 jump includes +1,352M impact
    })
    depreciation_base_df["Total_Baseline_Depr_Miliar"] = (
        depreciation_base_df["Non_DropCable_Depr_Miliar"]
        + depreciation_base_df["DropCable_Base_Depr_Miliar"]
    )

    return opex_df, revenue_df, seg_rev_weights, depreciation_base_df, segments


# ==============================================================================
# 3. HELPER FORMATTING & STYLING FUNCTIONS
# ==============================================================================
def fmt_triliun(miliar_val: float) -> str:
    """Format Rp Miliar into Rp Triliun (e.g., 112,151 -> Rp112.15T)."""
    return f"Rp{miliar_val / 1000:,.2f}T"


def fmt_miliar(miliar_val: float) -> str:
    """Format Rp Miliar with thousand separators (e.g., Rp112.151 M)."""
    return f"Rp{miliar_val:,.0f} M".replace(",", ".")


def render_kpi_card(title: str, value: str, delta_text: str, delta_type: str = "neutral"):
    """Render styled HTML KPI card."""
    delta_class = {
        "neg": "delta-neg",
        "pos": "delta-pos",
        "neutral": "delta-neutral"
    }.get(delta_type, "delta-neutral")

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta {delta_class}">{delta_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def highlight_yoy_growth(series: pd.Series):
    """
    Highlight YoY growth cells:
    - Red if growth > +10%
    - Yellow if growth > +5%
    - Green if negative (efficiency achieved)
    """
    styles = []
    for val in series:
        if pd.isna(val):
            styles.append("")
        elif val > 10.0:
            styles.append("background-color: #FEE2E2; color: #991B1B; font-weight: 700;")
        elif val > 5.0:
            styles.append("background-color: #FEF3C7; color: #92400E; font-weight: 700;")
        elif val < 0.0:
            styles.append("background-color: #D1FAE5; color: #065F46; font-weight: 700;")
        else:
            styles.append("background-color: #F3F4F6; color: #374151;")
    return styles


# ==============================================================================
# 4. LOAD DATA & SIDEBAR CONTROLS
# ==============================================================================
opex_df, revenue_df, seg_rev_weights, depr_proj_df, ALL_SEGMENTS = load_telkom_financial_data()

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align:center; padding: 0.5rem 0 1rem 0; border-bottom: 2px solid {TELKOM_RED};">
            <h2 style="margin:0; color:{TELKOM_RED}; font-weight:800; letter-spacing:1px;">TELKOM INDONESIA</h2>
            <p style="margin:0; font-size:0.8rem; color:{TELKOM_SLATE};">Financial & Asset Analytics</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 🔎 Filter Data")
    selected_year = st.selectbox(
        "Tahun Laporan (Reporting Year)",
        options=[2025, 2024, 2023],
        index=0,
        help="Pilih tahun laporan utama untuk analisis KPI dan komposisi OPEX."
    )

    selected_segments = st.multiselect(
        "Segmen Bisnis (Business Segments)",
        options=ALL_SEGMENTS,
        default=ALL_SEGMENTS,
        help="Filter metrik berdasarkan segmen bisnis PT Telkom Indonesia."
    )

    if not selected_segments:
        st.warning("Minimal satu segmen harus dipilih. Menampilkan semua segmen.")
        selected_segments = ALL_SEGMENTS

    st.markdown("---")
    st.markdown("### ⚙️ What-If Analysis Simulator")

    opex_efficiency_pct = st.slider(
        "Target Efisiensi OPEX (%)",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.5,
        help="Simulasikan target penghematan OPEX non-penyusutan (Operasi, CPE, Karyawan, dll)."
    )

    drop_cable_useful_life = st.slider(
        "Umur Manfaat Aset Drop Cable (Tahun)",
        min_value=3.0,
        max_value=7.0,
        value=3.0,
        step=0.5,
        help="Baseline kebijakan reklasifikasi 2025 = 3 tahun (dampak +Rp1.352 M). Perpanjangan umur manfaat menurunkan beban penyusutan tahunan."
    )

    st.markdown("---")
    st.caption(
        "**Sumber Konteks:** Laporan Keuangan Konsolidasian PT Telkom Indonesia (Persero) Tbk FY 2025 (Simulasi Manajemen)."
    )


# ==============================================================================
# 5. CORE COMPUTATIONS FOR SELECTED FILTERS
# ==============================================================================
filtered_opex = opex_df[opex_df["Segment"].isin(selected_segments)].copy()

# Aggregate by Year & Cost Item
by_year_item = (
    filtered_opex.groupby(["Year", "Cost_Item"], as_index=False)["Amount_Miliar"]
    .sum()
)

# Current year vs Prior year data
curr_year_df = by_year_item[by_year_item["Year"] == selected_year].copy()
prev_year = selected_year - 1
prev_year_df = by_year_item[by_year_item["Year"] == prev_year].copy()

total_opex_curr = curr_year_df["Amount_Miliar"].sum()
total_opex_prev = prev_year_df["Amount_Miliar"].sum() if not prev_year_df.empty else np.nan
opex_yoy_pct = ((total_opex_curr - total_opex_prev) / total_opex_prev * 100) if total_opex_prev else 0.0

# Apply What-If OPEX Efficiency (on controllable/non-depreciation OPEX for simulation readout)
non_depr_curr = curr_year_df[curr_year_df["Cost_Item"] != "Penyusutan & Amortisasi"]["Amount_Miliar"].sum()
simulated_savings_miliar = non_depr_curr * (opex_efficiency_pct / 100.0)
simulated_total_opex = total_opex_curr - simulated_savings_miliar

# Depreciation metric
depr_curr = curr_year_df.loc[
    curr_year_df["Cost_Item"] == "Penyusutan & Amortisasi", "Amount_Miliar"
].sum()
depr_prev = prev_year_df.loc[
    prev_year_df["Cost_Item"] == "Penyusutan & Amortisasi", "Amount_Miliar"
].sum() if not prev_year_df.empty else np.nan
depr_yoy_pct = ((depr_curr - depr_prev) / depr_prev * 100) if depr_prev else 0.0

# Revenue scaling for selected segments to compute accurate OPEX-to-Revenue Ratio
rev_base = revenue_df.loc[revenue_df["Year"] == selected_year, "Revenue_Miliar"].values[0]
selected_rev_share = sum(seg_rev_weights[s] for s in selected_segments)
adj_revenue = rev_base * selected_rev_share
opex_to_rev_ratio = (simulated_total_opex / adj_revenue * 100) if adj_revenue > 0 else 0.0

# Compute Cost Line YoY Growth table for Risk Count & Tab 4
if not prev_year_df.empty:
    yoy_comp_df = pd.merge(
        curr_year_df[["Cost_Item", "Amount_Miliar"]].rename(columns={"Amount_Miliar": f"FY_{selected_year}"}),
        prev_year_df[["Cost_Item", "Amount_Miliar"]].rename(columns={"Amount_Miliar": f"FY_{prev_year}"}),
        on="Cost_Item",
        how="left"
    )
    yoy_comp_df["Delta_Miliar"] = yoy_comp_df[f"FY_{selected_year}"] - yoy_comp_df[f"FY_{prev_year}"]
    yoy_comp_df["YoY_Pct"] = (yoy_comp_df["Delta_Miliar"] / yoy_comp_df[f"FY_{prev_year}"]) * 100
else:
    yoy_comp_df = curr_year_df[["Cost_Item", "Amount_Miliar"]].rename(columns={"Amount_Miliar": f"FY_{selected_year}"})
    yoy_comp_df[f"FY_{prev_year}"] = np.nan
    yoy_comp_df["Delta_Miliar"] = np.nan
    yoy_comp_df["YoY_Pct"] = 0.0

high_risk_count = int((yoy_comp_df["YoY_Pct"] > 5.0).sum())
critical_risk_count = int((yoy_comp_df["YoY_Pct"] > 10.0).sum())


# ==============================================================================
# 6. EXECUTIVE HEADER BANNER
# ==============================================================================
st.markdown(
    f"""
    <div class="telkom-banner">
        <h1>📡 PT Telkom Indonesia (Persero) Tbk — OPEX & Asset Depreciation Tracker</h1>
        <p>Executive Financial Performance Monitoring | Tahun Buku <b>{selected_year}</b> | Segmen Aktif: <b>{len(selected_segments)} dari {len(ALL_SEGMENTS)} Segmen</b></p>
    </div>
    """,
    unsafe_allow_html=True
)

if opex_efficiency_pct > 0 or drop_cable_useful_life > 3.0:
    st.info(
        f"**Mode Simulasi What-If Aktif:** Target Efisiensi OPEX Non-Penyusutan **-{opex_efficiency_pct:.1f}%** "
        f"(Potensi penghematan **{fmt_miliar(simulated_savings_miliar)}**) | "
        f"Umur Manfaat Drop Cable **{drop_cable_useful_life:.1f} tahun**."
    )


# ==============================================================================
# 7. MAIN DASHBOARD TABS
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Summary & KPI",
    "🍩 OPEX Breakdown & Segment",
    "📉 Asset Depreciation & Drop Cable Simulator",
    "🚨 Anomaly & Cost Efficiency Alerts"
])


# ------------------------------------------------------------------------------
# TAB 1: EXECUTIVE SUMMARY & KPI METRICS
# ------------------------------------------------------------------------------
with tab1:
    st.subheader(f"Ringkasan Kinerja Biaya & Rasio Efisiensi (FY {selected_year})")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        opex_display = fmt_triliun(simulated_total_opex)
        delta_lbl = (
            f"▲ +{opex_yoy_pct:.1f}% YoY (Baseline: {fmt_triliun(total_opex_curr)})"
            if opex_yoy_pct >= 0 else f"▼ {opex_yoy_pct:.1f}% YoY"
        )
        if opex_efficiency_pct > 0:
            delta_lbl = f"Simulasi: -{fmt_miliar(simulated_savings_miliar)} vs Baseline"
        render_kpi_card(
            "Total OPEX / Beban",
            opex_display,
            delta_lbl,
            delta_type="neg" if (opex_yoy_pct > 0 and opex_efficiency_pct == 0) else "pos"
        )

    with col2:
        depr_lbl = f"▲ +{depr_yoy_pct:.1f}% YoY ({fmt_miliar(depr_curr)})" if depr_yoy_pct >= 0 else f"▼ {depr_yoy_pct:.1f}% YoY"
        render_kpi_card(
            "Beban Penyusutan & Amortisasi",
            fmt_triliun(depr_curr),
            depr_lbl,
            delta_type="neg" if depr_yoy_pct > 5 else "neutral"
        )

    with col3:
        render_kpi_card(
            "OPEX-to-Revenue Ratio",
            f"{opex_to_rev_ratio:.1f}%",
            f"Pendapatan Terfilter: {fmt_triliun(adj_revenue)}",
            delta_type="neutral"
        )

    with col4:
        render_kpi_card(
            "High-Risk Cost Items",
            f"{high_risk_count} Pos Biaya",
            f"{critical_risk_count} Kritis (>+10% YoY) | {high_risk_count - critical_risk_count} Waspada (>+5%)",
            delta_type="neg" if high_risk_count > 0 else "pos"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # YoY Growth Waterfall Chart (Prev Year -> Selected Year)
    st.subheader(f"Jembatan Pergeseran Komponen OPEX (YoY Waterfall: {prev_year} → {selected_year})")

    if prev_year_df.empty:
        st.info("Data tahun pembanding (2022) tidak tersedia pada dataset historis. Pilih tahun 2024 atau 2025 untuk melihat Waterfall YoY.")
    else:
        wf_df = yoy_comp_df.sort_values(by="Delta_Miliar", ascending=False).copy()

        x_labels = [f"Total OPEX {prev_year}"] + wf_df["Cost_Item"].tolist() + [f"Total OPEX {selected_year}"]
        measures = ["absolute"] + ["relative"] * len(wf_df) + ["total"]
        y_values = [total_opex_prev] + wf_df["Delta_Miliar"].tolist() + [total_opex_curr]

        text_labels = [fmt_miliar(total_opex_prev)] + [
            f"{'+' if v >= 0 else ''}{v:,.0f} M".replace(",", ".") for v in wf_df["Delta_Miliar"]
        ] + [fmt_miliar(total_opex_curr)]

        fig_waterfall = go.Figure(go.Waterfall(
            name="OPEX Shift",
            orientation="v",
            measure=measures,
            x=x_labels,
            y=y_values,
            text=text_labels,
            textposition="outside",
            connector={"line": {"color": "#9CA3AF", "width": 1.5, "dash": "dot"}},
            increasing={"marker": {"color": TELKOM_RED}},       # Cost increase = Red
            decreasing={"marker": {"color": SUCCESS_GREEN}},    # Cost savings = Green
            totals={"marker": {"color": TELKOM_DARK_GREY}},
        ))

        fig_waterfall.update_layout(
            height=460,
            margin=dict(l=20, r=20, t=40, b=60),
            yaxis_title="Nilai Beban (Rp Miliar)",
            xaxis_tickangle=-18,
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font=dict(color=TELKOM_DARK_GREY),
            yaxis=dict(
                gridcolor="#E5E7EB",
                range=[min(total_opex_prev, total_opex_curr) * 0.85, max(total_opex_prev, total_opex_curr) * 1.08]
            )
        )
        st.plotly_chart(fig_waterfall, use_container_width=True)

        st.caption(
            "Catatan: Batang merah menunjukkan kenaikan beban (cost pressure), sedangkan batang hijau menunjukkan efisiensi biaya dibandingkan tahun sebelumnya."
        )


# ------------------------------------------------------------------------------
# TAB 2: OPEX BREAKDOWN & SEGMENT ANALYSIS
# ------------------------------------------------------------------------------
with tab2:
    st.subheader(f"Struktur Komposisi OPEX & Distribusi per Segmen Bisnis (FY {selected_year})")

    col_left, col_right = st.columns([1.05, 1.25])

    with col_left:
        st.markdown(f"**Komposisi Beban Operasional (FY {selected_year})**")
        donut_df = curr_year_df.sort_values(by="Amount_Miliar", ascending=False).copy()
        donut_df["Share_Pct"] = donut_df["Amount_Miliar"] / donut_df["Amount_Miliar"].sum() * 100

        telkom_palette = [
            TELKOM_DARK_GREY,
            TELKOM_RED,
            "#6B7280",
            "#9CA3AF",
            "#F87171",
            "#D1D5DB"
        ]

        fig_donut = go.Figure(data=[go.Pie(
            labels=donut_df["Cost_Item"],
            values=donut_df["Amount_Miliar"],
            hole=0.52,
            marker=dict(colors=telkom_palette, line=dict(color="#FFFFFF", width=2)),
            textinfo="percent",
            textposition="outside",
            hovertemplate="<b>%{label}</b><br>Nilai: Rp%{value:,.0f} M<br>Porsi: %{percent}<extra></extra>"
        )])

        fig_donut.update_layout(
            height=440,
            margin=dict(l=20, r=20, t=30, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5),
            annotations=[dict(
                text=f"Total<br><b>{fmt_triliun(total_opex_curr)}</b>",
                x=0.5, y=0.5, font_size=15, showarrow=False, font_color=TELKOM_DARK_GREY
            )],
            paper_bgcolor="#FFFFFF"
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_right:
        st.markdown(f"**Perbandingan OPEX per Segmen Bisnis (FY {selected_year})**")
        seg_breakdown = (
            filtered_opex[filtered_opex["Year"] == selected_year]
            .groupby(["Segment", "Cost_Item"], as_index=False)["Amount_Miliar"]
            .sum()
        )
        seg_totals = (
            seg_breakdown.groupby("Segment", as_index=False)["Amount_Miliar"]
            .sum()
            .sort_values("Amount_Miliar", ascending=False)
        )
        segment_order = seg_totals["Segment"].tolist()

        fig_seg_bar = px.bar(
            seg_breakdown,
            x="Segment",
            y="Amount_Miliar",
            color="Cost_Item",
            category_orders={"Segment": segment_order},
            color_discrete_sequence=telkom_palette,
            labels={"Amount_Miliar": "OPEX (Rp Miliar)", "Segment": "Segmen Bisnis", "Cost_Item": "Komponen Beban"},
        )

        # Add total labels on top of stacked bars
        for _, row in seg_totals.iterrows():
            fig_seg_bar.add_annotation(
                x=row["Segment"],
                y=row["Amount_Miliar"],
                text=fmt_triliun(row["Amount_Miliar"]),
                showarrow=False,
                yshift=10,
                font=dict(size=11, color=TELKOM_DARK_GREY, family="Arial Black")
            )

        fig_seg_bar.update_layout(
            height=440,
            barmode="stack",
            margin=dict(l=20, r=20, t=30, b=40),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            yaxis=dict(gridcolor="#E5E7EB", range=[0, seg_totals["Amount_Miliar"].max() * 1.15]),
            legend=dict(orientation="h", yanchor="bottom", y=-0.30, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_seg_bar, use_container_width=True)

    # Multi-Year Segment Trend Table
    with st.expander("Lihat Detail Tabel OPEX per Segmen (2023–2025)", expanded=False):
        pivot_seg = (
            filtered_opex.pivot_table(
                index="Segment", columns="Year", values="Amount_Miliar", aggfunc="sum"
            )
            .reset_index()
        )
        if 2024 in pivot_seg.columns and 2025 in pivot_seg.columns:
            pivot_seg["YoY 2025 (%)"] = (pivot_seg[2025] - pivot_seg[2024]) / pivot_seg[2024] * 100
        st.dataframe(
            pivot_seg.style.format({
                2023: "Rp{:,.0f} M",
                2024: "Rp{:,.0f} M",
                2025: "Rp{:,.0f} M",
                "YoY 2025 (%)": "{:+.2f}%"
            }),
            use_container_width=True,
            hide_index=True
        )


# ------------------------------------------------------------------------------
# TAB 3: ASSET DEPRECIATION & DROP CABLE SIMULATOR
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("Kurva Beban Penyusutan Historis & Proyeksi (2023–2027)")
    st.markdown(
        "Kenaikan penyusutan 2025 sebesar **+10,1% YoY (Rp37.649 miliar)** dipicu oleh ekspansi infrastruktur digital "
        "dan reklasifikasi kebijakan akuntansi aset *drop cable* dengan dampak penyusutan **+Rp1.352 miliar**."
    )

    # Scale depreciation simulation for selected segments
    seg_depr_share = (
        opex_df[(opex_df["Year"] == 2025) & (opex_df["Cost_Item"] == "Penyusutan & Amortisasi") & (opex_df["Segment"].isin(selected_segments))]["Amount_Miliar"].sum()
        / opex_df[(opex_df["Year"] == 2025) & (opex_df["Cost_Item"] == "Penyusutan & Amortisasi")]["Amount_Miliar"].sum()
    )

    sim_df = depr_proj_df.copy()
    sim_df["Non_DropCable_Adj"] = sim_df["Non_DropCable_Depr_Miliar"] * seg_depr_share
    sim_df["DropCable_Base_Adj"] = sim_df["DropCable_Base_Depr_Miliar"] * seg_depr_share
    sim_df["Total_Baseline_Adj"] = sim_df["Total_Baseline_Depr_Miliar"] * seg_depr_share

    # Recompute Drop Cable Depreciation from 2025 onwards using Straight-Line Useful Life Ratio (Baseline = 3.0 yrs)
    baseline_life = 3.0
    life_factor = baseline_life / drop_cable_useful_life

    sim_df["DropCable_Sim_Adj"] = np.where(
        sim_df["Year"] >= 2025,
        sim_df["DropCable_Base_Adj"] * life_factor,
        sim_df["DropCable_Base_Adj"]
    )
    sim_df["Total_Simulated_Adj"] = sim_df["Non_DropCable_Adj"] + sim_df["DropCable_Sim_Adj"]
    sim_df["Annual_Variance_Miliar"] = sim_df["Total_Simulated_Adj"] - sim_df["Total_Baseline_Adj"]

    # Interactive Simulator Control Mirror (synchronized info & quick KPI summary)
    c1, c2, c3 = st.columns(3)
    impact_2025 = sim_df.loc[sim_df["Year"] == 2025, "Annual_Variance_Miliar"].values[0]
    cum_savings_25_27 = sim_df.loc[sim_df["Year"] >= 2025, "Annual_Variance_Miliar"].sum()

    with c1:
        render_kpi_card(
            "Umur Manfaat Drop Cable (Simulasi)",
            f"{drop_cable_useful_life:.1f} Tahun",
            "Baseline Akuntansi 2025: 3.0 Tahun",
            delta_type="neutral"
        )
    with c2:
        render_kpi_card(
            "Dampak Penyusutan FY 2025",
            f"{'+' if impact_2025 > 0 else ''}{fmt_miliar(impact_2025)}",
            "Penghematan tahunan" if impact_2025 < 0 else "Sesuai baseline kebijakan 2025",
            delta_type="pos" if impact_2025 < 0 else "neutral"
        )
    with c3:
        render_kpi_card(
            "Akumulasi Penghematan (2025–2027)",
            fmt_miliar(abs(cum_savings_25_27)) if cum_savings_25_27 <= 0 else f"+{fmt_miliar(cum_savings_25_27)}",
            "Proyeksi efisiensi beban 3 tahun" if cum_savings_25_27 < 0 else "Ubah slider di sidebar untuk simulasi",
            delta_type="pos" if cum_savings_25_27 < 0 else "neutral"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Combined Bar + Line Chart: Baseline vs Simulated Depreciation Curve
    fig_depr = go.Figure()

    # Bar for Non-Drop Cable Infrastructure Depreciation
    fig_depr.add_trace(go.Bar(
        x=sim_df["Year"],
        y=sim_df["Non_DropCable_Adj"],
        name="Penyusutan Infrastruktur Inti (Non-Drop Cable)",
        marker_color="#D1D5DB",
        hovertemplate="Tahun %{x}<br>Infrastruktur Inti: Rp%{y:,.0f} M<extra></extra>"
    ))

    # Bar for Drop Cable Simulated Depreciation
    fig_depr.add_trace(go.Bar(
        x=sim_df["Year"],
        y=sim_df["DropCable_Sim_Adj"],
        name=f"Penyusutan Drop Cable ({drop_cable_useful_life:.1f} Thn)",
        marker_color="#FCA5A5",
        hovertemplate="Tahun %{x}<br>Drop Cable (Simulasi): Rp%{y:,.0f} M<extra></extra>"
    ))

    # Line for Baseline Total Depreciation
    fig_depr.add_trace(go.Scatter(
        x=sim_df["Year"],
        y=sim_df["Total_Baseline_Adj"],
        name="Total Penyusutan Baseline (Kebijakan 3 Thn)",
        mode="lines+markers+text",
        text=[fmt_triliun(v) for v in sim_df["Total_Baseline_Adj"]],
        textposition="top center",
        line=dict(color=TELKOM_RED, width=3, dash="dash"),
        marker=dict(size=9, color=TELKOM_RED)
    ))

    # Line for Simulated Total Depreciation
    fig_depr.add_trace(go.Scatter(
        x=sim_df["Year"],
        y=sim_df["Total_Simulated_Adj"],
        name=f"Total Penyusutan Simulasi ({drop_cable_useful_life:.1f} Thn)",
        mode="lines+markers",
        line=dict(color=TELKOM_DARK_GREY if drop_cable_useful_life == 3.0 else SUCCESS_GREEN, width=3.5),
        marker=dict(size=9)
    ))

    fig_depr.update_layout(
        barmode="stack",
        height=460,
        title="Simulasi Kurva Penyusutan 2023–2027: Dampak Perubahan Umur Manfaat Aset Drop Cable",
        xaxis=dict(tickmode="linear", dtick=1, title="Tahun"),
        yaxis=dict(title="Beban Penyusutan (Rp Miliar)", gridcolor="#E5E7EB"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=55, b=60)
    )
    st.plotly_chart(fig_depr, use_container_width=True)

    # Simulation Summary Table
    display_sim = sim_df[[
        "Year", "Type", "Total_Baseline_Adj", "Total_Simulated_Adj", "Annual_Variance_Miliar"
    ]].rename(columns={
        "Year": "Tahun",
        "Type": "Status",
        "Total_Baseline_Adj": "Baseline Penyusutan (Rp M)",
        "Total_Simulated_Adj": "Simulasi Penyusutan (Rp M)",
        "Annual_Variance_Miliar": "Selisih / Penghematan (Rp M)"
    })
    st.dataframe(
        display_sim.style.format({
            "Baseline Penyusutan (Rp M)": "{:,.0f}",
            "Simulasi Penyusutan (Rp M)": "{:,.0f}",
            "Selisih / Penghematan (Rp M)": "{:+,.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )


# ------------------------------------------------------------------------------
# TAB 4: ANOMALY & COST EFFICIENCY ALERT TABLE
# ------------------------------------------------------------------------------
with tab4:
    st.subheader(f"Deteksi Anomali Biaya & Efisiensi OPEX (FY {selected_year} vs {prev_year})")

    # Dedicated Executive Callouts
    col_alert1, col_alert2 = st.columns(2)

    with col_alert1:
        st.markdown(
            """
            <div class="callout-danger">
                <h4 style="margin:0 0 0.35rem 0; color:#991B1B;">🚨 CRITICAL ANOMALY: Sewa Sirkuit & CPE (+30,7% YoY)</h4>
                <p style="margin:0; font-size:0.9rem; color:#7F1D1D;">
                    Beban Sewa Sirkuit & CPE melonjak tajam dari <b>Rp3.423 miliar (2024)</b> menjadi <b>Rp4.474 miliar (2025)</b>.
                    Lonjakan ini memerlukan audit kontrak vendor CPE, optimasi utilisasi sirkuit B2B, dan renegosiasi SLA sewa.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_alert2:
        st.markdown(
            """
            <div class="callout-warning">
                <h4 style="margin:0 0 0.35rem 0; color:#92400E;">⚠️ HIGH WATCH: Depresiasi & Amortisasi (+10,1% YoY)</h4>
                <p style="margin:0; font-size:0.9rem; color:#78350F;">
                    Beban Penyusutan mencapai <b>Rp37.649 miliar (2025)</b> didorong ekspansi infrastruktur digital dan
                    dampak reklasifikasi kebijakan akuntansi <i>drop cable</i> sebesar <b>+Rp1.352 miliar</b>.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### Tabel Monitoring Pertumbuhan Pos Biaya (YoY Risk Matrix)")

    if prev_year_df.empty:
        st.info("Pilih tahun 2024 atau 2025 untuk menampilkan matriks pertumbuhan YoY.")
    else:
        alert_table = yoy_comp_df.copy()
        alert_table["Share_OPEX (%)"] = (alert_table[f"FY_{selected_year}"] / total_opex_curr) * 100

        def assign_status(yoy):
            if yoy > 10.0:
                return "🔴 Kritis (> +10%)"
            elif yoy > 5.0:
                return "🟡 Waspada (> +5%)"
            elif yoy < 0.0:
                return "🟢 Efisiensi Tercapai"
            else:
                return "⚪ Terkendali (0% - 5%)"

        alert_table["Status Risiko"] = alert_table["YoY_Pct"].apply(assign_status)
        alert_table = alert_table.sort_values(by="YoY_Pct", ascending=False)

        col_prev_name = f"FY {prev_year} (Rp M)"
        col_curr_name = f"FY {selected_year} (Rp M)"

        formatted_alert_df = alert_table.rename(columns={
            "Cost_Item": "Komponen Biaya",
            f"FY_{prev_year}": col_prev_name,
            f"FY_{selected_year}": col_curr_name,
            "Delta_Miliar": "Selisih YoY (Rp M)",
            "YoY_Pct": "Pertumbuhan YoY (%)",
            "Share_OPEX (%)": "Porsi thd OPEX (%)"
        })[[
            "Komponen Biaya", col_prev_name, col_curr_name,
            "Selisih YoY (Rp M)", "Pertumbuhan YoY (%)", "Porsi thd OPEX (%)", "Status Risiko"
        ]]

        styled_df = (
            formatted_alert_df.style
            .apply(highlight_yoy_growth, subset=["Pertumbuhan YoY (%)"])
            .format({
                col_prev_name: "{:,.0f}",
                col_curr_name: "{:,.0f}",
                "Selisih YoY (Rp M)": "{:+,.0f}",
                "Pertumbuhan YoY (%)": "{:+.2f}%",
                "Porsi thd OPEX (%)": "{:.1f}%"
            })
        )

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        st.markdown(
            """
            **Legenda Indikator Risiko:**
            - 🔴 **Merah (`> +10% YoY`)**: Eskalasi biaya tinggi, memerlukan intervensi manajemen segera (misal: *Sewa Sirkuit & CPE* dan *Penyusutan*).
            - 🟡 **Kuning (`+5% s.d. +10% YoY`)**: Tren kenaikan moderat-tinggi, perlu pemantauan ketat.
            - 🟢 **Hijau (`< 0% YoY`)**: Efisiensi biaya tercapai (misal: *Beban Karyawan -2,6%* dan *Umum/Adm/Pemasaran*).
            """
        )