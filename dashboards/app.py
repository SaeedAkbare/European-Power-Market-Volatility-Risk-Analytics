"""Local five-page research dashboard. Run from repository root."""
from pathlib import Path

import pandas as pd
import streamlit as st

from power_risk.portfolio.risk import daily_scenarios, risk_summary, scenario_pnl

st.set_page_config(page_title="German Power Market Risk", layout="wide")
st.title("European Power Market Volatility & Risk Analytics")
st.caption("DE-LU • €0 public-data workflow • Source: Bundesnetzagentur | SMARD.de")
page = st.sidebar.radio("Research page", ["Market Overview", "Volatility Monitor", "Fundamental Drivers",
                                         "Probabilistic Forecasting", "Portfolio Risk"])
st.sidebar.caption("Historical analysis, exploratory forecasts and hypothetical scenarios are labelled separately.")


@st.cache_data
def parquet(path, modified):
    return pd.read_parquet(path)


def load(path):
    if not Path(path).exists():
        st.info(f"Output not generated yet: {path}. Run the documented pipeline commands.")
        st.stop()
    return parquet(path, Path(path).stat().st_mtime_ns)


if page == "Market Overview":
    st.subheader("Actual market observations — historical")
    frame = load("reports/volatility_metrics.parquet")
    st.metric("Hourly-equivalent average price", f"€{frame.price_eur_mwh.mean():.2f}/MWh")
    st.line_chart(frame.price_eur_mwh.resample("D").mean(), y_label="EUR/MWh (UTC daily mean)")
    st.dataframe(frame.groupby("season").price_eur_mwh.agg(["count", "mean", "std"]))
    st.image("reports/price_distribution.png")
    st.caption("Post-transition prices are complete hourly averages. Native negative durations appear in the event report.")
elif page == "Volatility Monitor":
    st.subheader("Historical volatility and extreme events")
    frame = load("reports/volatility_metrics.parquet")
    st.line_chart(frame[["rolling_std_7d", "bollinger_upper", "bollinger_lower"]].resample("D").last())
    st.image("reports/volatility_heatmap.png")
    if Path("reports/negative_price_events.csv").exists():
        st.dataframe(pd.read_csv("reports/negative_price_events.csv"))
    if Path("reports/regime_transitions.csv").exists():
        st.caption("Lagged volatility states; cutpoints fixed using 2023 calibration.")
        st.dataframe(pd.read_csv("reports/regime_transitions.csv", index_col=0))
elif page == "Fundamental Drivers":
    st.subheader("Retrospective associations — ENTSO-E integration pending")
    st.info("No validated fundamental observations are bundled. A free ENTSO-E token and category-specific validation are required. No driver findings are inferred from prices alone.")
    st.dataframe(pd.read_csv("reports/data_availability_report.csv"))
elif page == "Probabilistic Forecasting":
    st.subheader("Exploratory historical forecasts")
    st.warning("Source publication/revision history is unverified. This backtest is not an executable trading strategy.")
    frame = load("reports/price_risk_forecasts.parquet")
    model = st.selectbox("Model", sorted(frame.model.unique()))
    selection = frame.loc[frame.model.eq(model)].tail(24 * 14)
    st.line_chart(selection[["actual", "q10", "q50", "q90"]])
    st.line_chart(selection[["p_negative", "p_spike"]])
    st.dataframe(pd.read_csv("reports/model_comparison.csv"))
    st.dataframe(pd.read_csv("reports/probability_calibration.csv"))
else:
    st.subheader("Hypothetical portfolio scenarios")
    side = st.selectbox("Position", ["purchase", "generation"])
    exposure = st.number_input("Flat exposure (MW)", min_value=0., value=1.)
    reference = st.number_input("Contract/reference price (EUR/MWh)", value=100.)
    confidence = st.slider("VaR / ES confidence", .90, .99, .95)
    st.caption("Historical sampler: complete, nonoverlapping 24-hour UTC blocks; daily exposure shape is flat.")
    hourly = load("data/processed/prices_hourly.parquet")
    scenarios = daily_scenarios(hourly, exposure, reference, side)
    st.dataframe(pd.DataFrame([risk_summary(scenarios.pnl_eur, confidence)]))
    st.bar_chart(scenarios.set_index("scenario_start").pnl_eur)
    st.markdown("Custom interval scenario: CSV columns `price_eur_mwh`, `exposure_mw`, `duration_hours`. Supports hourly or quarter-hourly exposure and an arbitrary horizon.")
    uploaded = st.file_uploader("Upload hypothetical exposure/price scenario", type="csv")
    if uploaded is not None:
        try:
            custom = pd.read_csv(uploaded)
            custom["pnl_eur"] = scenario_pnl(custom.price_eur_mwh, custom.exposure_mw, custom.duration_hours, reference, side)
            st.metric("Scenario P&L", f"€{custom.pnl_eur.sum():,.2f}")
            st.dataframe(custom)
        except (ValueError, AttributeError, KeyError) as exc:
            st.error(f"Invalid input: {exc}")
    st.caption("Purchase P&L=(reference−spot)×MW×hours; generation reverses the sign. Loss=−P&L. Historical representativeness is an assumption; no optimal hedge is implied.")
