# app.py
"""
Breast Service Demand Forecasting & DES Simulation Tool – RDUH
(HSMA 6036)

Integrated app:
- Forecast 2WW referrals
- DES simulation for pathway waits
- Capacity planning search
"""

from __future__ import annotations
import json
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from config.geography import geography_defaults
from config.scenarios import scenario_presets
from docs.user_guide import get_user_guide
from forecast.demand_model import DemandParams
from forecast.forecast_engine import make_forecast_series
from simulation.des_model import SimInputs, ServiceTimes, PathwayProbs, ResourcesConfig
from simulation.monte_carlo import run_mc
from simulation.capacity_planning import safe_capacity_search

# -----------------------------
# Helper functions
# -----------------------------
def _quick_help_toggle(tab_name: str, default: bool = False) -> bool:
    return st.checkbox(
        "Show quick help for this tab",
        value=default,
        key=f"quick_help_{tab_name}",
    )

def _render_quick_help(section_title: str, section_text: str):
    with st.expander(f"Quick help – {section_title}", expanded=True):
        st.markdown(section_text)

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Breast Service Forecasting & DES – RDUH (HSMA 6036)",
    layout="wide",
)
st.title("Breast Service Demand Forecasting & DES – RDUH (HSMA 6036)")

from PIL import Image
nhs_logo = Image.open("nhs_logo.jpeg")
st.image(nhs_logo, width=200)  # Logo at top

# -----------------------------
# Sidebar: presets
# -----------------------------
geos = geography_defaults()
scens = scenario_presets()

st.sidebar.header("1) Geography & Scenario")
geo = st.sidebar.selectbox("Geography", list(geos.keys()), index=list(geos.keys()).index("Exeter"))
scn = st.sidebar.selectbox("Scenario", list(scens.keys()), index=list(scens.keys()).index("Baseline"))

geo_defaults = geos[geo]
scn_defaults = scens[scn]

with st.sidebar.expander("2) Optional Forecast Overrides"):
    baseline_daily = st.number_input("Baseline Daily Referrals (R₀)", min_value=1, max_value=200,
                                     value=int(geo_defaults["baseline_referrals"]))
    growth_pct = st.number_input("Population Growth %/yr", 0.0, 10.0,
                                 float(geo_defaults["growth"] + scn_defaults["growth_delta"]))
    housing_pct = st.number_input("Additional Housing Impact %/yr", 0.0, 20.0,
                                  float(geo_defaults["housing"] + scn_defaults["housing_delta"]))
    ref_infl_pct = st.number_input("Referral Inflation %/yr", 0.0, 10.0,
                                   float(scn_defaults["referral_inflation"]))

with st.sidebar.expander("3) Age Distribution"):
    age_u40 = st.slider("Under 40", 0.0, 1.0, float(geo_defaults["age"]["u40"]))
    age_40_49 = st.slider("40–49", 0.0, 1.0, float(geo_defaults["age"]["a40_49"]))
    age_50_plus = st.slider("50+", 0.0, 1.0, float(geo_defaults["age"]["a50_plus"]))

# Normalise age proportions
total_age = age_u40 + age_40_49 + age_50_plus
if total_age > 0:
    age_u40 /= total_age
    age_40_49 /= total_age
    age_50_plus /= total_age

# Build demand parameters
demand_params = DemandParams(
    baseline_daily=float(baseline_daily),
    growth=float(growth_pct),
    housing=float(housing_pct),
    referral_inflation=float(ref_infl_pct),
    age_u40=float(age_u40),
    age_40_49=float(age_40_49),
    age_50_plus=float(age_50_plus),
)

st.sidebar.markdown("---")
st.sidebar.markdown("🛈 See full guide in the **Documentation** tab.")

# -----------------------------
# Tabs
# -----------------------------
tab_forecast, tab_sim, tab_capacity, tab_docs = st.tabs(
    ["Activity Forecasting", "Simulation (DES)", "Capacity Planning", "Documentation"]
)

# -----------------------------
# Tab 1: Forecasting
# -----------------------------
with tab_forecast:
    st.subheader("20-Year Activity Projection")

    if _quick_help_toggle("forecast"):
        _render_quick_help(
            "Activity Forecasting",
            "- Project future daily & annual referrals\n"
            "- Includes population + housing growth, referral inflation, age weighting\n"
            "- Provides low/high uncertainty scenarios"
        )

    years = st.slider("Projection horizon (years)", 5, 30, 20)
    
    with st.expander("Scenario adjustments (optional)"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            g_low = st.number_input("Δ Growth (low) ppts", -2.0, 0.0, -0.3, 0.1)
        with col2:
            g_high = st.number_input("Δ Growth (high) ppts", 0.0, 2.0, 0.3, 0.1)
        with col3:
            r_low = st.number_input("Δ Referral Infl. (low) ppts", -2.0, 0.0, -0.2, 0.1)
        with col4:
            r_high = st.number_input("Δ Referral Infl. (high) ppts", 0.0, 2.0, 0.2, 0.1)

    df_f = make_forecast_series(
        demand_params,
        years=years,
        growth_low_delta=g_low,
        growth_high_delta=g_high,
        ref_low_delta=r_low,
        ref_high_delta=r_high,
    )

    # Annual projection chart
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_f["Year"], y=df_f["Annual_Central"], mode="lines+markers", name="Annual (base)"))
    fig1.add_trace(go.Scatter(x=df_f["Year"], y=df_f["Annual_High"], mode="lines", name="Annual (high)", line=dict(dash="dash")))
    fig1.add_trace(go.Scatter(x=df_f["Year"], y=df_f["Annual_Low"], mode="lines", name="Annual (low)", line=dict(dash="dash")))
    fig1.update_layout(title="Projected Annual Referrals (with uncertainty)",
                       xaxis_title="Year from baseline",
                       yaxis_title="Referrals / year")
    st.plotly_chart(fig1, use_container_width=True)

    # YoY % change chart
    fig2 = px.bar(df_f, x="Year", y="YoY_%", title="Year-on-Year % Change")
    st.plotly_chart(fig2, use_container_width=True)

    # CSV download
    st.download_button("Download forecast CSV",
                       data=df_f.to_csv(index=False).encode("utf-8"),
                       file_name="forecast.csv",
                       mime="text/csv")

# -----------------------------
# Tab 2: Simulation (DES)
# -----------------------------
with tab_sim:
    st.subheader("Discrete Event Simulation (2WW Pathway)")
    st.markdown("Default parameters reflect baseline demand. Expand to adjust advanced options.")

    # Always-visible basic settings
    sim_days = st.number_input("Simulation horizon (days)", 30, 3650, 180, 30)
    sim_year = st.slider("Simulation year (from forecast)", 0, 20, 5)
    warmup_days = st.number_input("Warm-up (days)", 0, 365, 0, 7)

    # Advanced options hidden in expander
    with st.expander("Advanced Simulation Options"):
        mc_runs = st.number_input("Monte Carlo runs", 1, 100, 20, 1)
        consult_mean = st.number_input("Consult mean (min)", 5, 60, 30, 1)
        imaging_mean = st.number_input("Imaging mean (min)", 5, 60, 20, 1)
        biopsy_mean = st.number_input("Biopsy mean (min)", 5, 90, 30, 1)
        consult_cap = st.number_input("Consult capacity", 1, 40, 2, 1)
        imaging_cap = st.number_input("Imaging capacity", 0, 40, 1, 1)
        biopsy_cap = st.number_input("Biopsy capacity", 0, 40, 1, 1)
        imaging_prob = st.slider("Prob imaging after consult", 0.0, 1.0, 0.35, 0.01)
        biopsy_prob = st.slider("Prob biopsy given imaging", 0.0, 1.0, 0.15, 0.01)

    # Build simulation inputs using either default or advanced values
    service_times = ServiceTimes(
        clinic_mean_mins=consult_mean,
        imaging_mean_mins=imaging_mean,
        biopsy_mean_mins=biopsy_mean,
    )
    pathway = PathwayProbs(
        imaging_prob=imaging_prob,
        biopsy_prob=biopsy_prob,
    )
    resources = ResourcesConfig(
        clinic_rooms=consult_cap,
        imaging_slots=imaging_cap,
        biopsy_slots=biopsy_cap,
    )

    sim_inputs = SimInputs(
        daily_referrals=demand_params.daily_demand_at_year(sim_year),
        service_times=service_times,
        pathway_probs=pathway,
        resources=resources,
        sim_days=sim_days,
        warm_up=warmup_days,
    )

    # Run simulation
    if st.button("Run Monte Carlo simulation"):
        with st.spinner("Running simulation..."):
            summary = run_mc(sim_inputs, n_runs=mc_runs)

            # Extract metrics
            mean_wait_days = round(summary["mean_wait"]["mean"], 2)
            p95_wait_days = round(summary["p95_wait"]["mean"], 2)
            mean_wait_hours = mean_wait_days * 24
            p95_wait_hours = p95_wait_days * 24

            # Display metrics
            st.markdown("### Mean Wait Metrics")
            col1, col2 = st.columns(2)
            col1.metric("Mean wait (days)", round(mean_wait_days, 2))
            col2.metric("95th percentile wait (days)", round(p95_wait_days, 2))

            # Display capacities chosen for simulation
            # df_caps = pd.DataFrame({
            #     "Service": ["Clinic", "Imaging", "Biopsy"],
            #     "Capacity": [consult_cap, imaging_cap, biopsy_cap]
            # })

            # fig_caps = px.bar(
            #     df_caps,
            #     x="Service",
            #     y="Capacity",
            #     text="Capacity",
            #     title="Capacity Chosen for Simulation",
            #     color="Service"
            # )
            # fig_caps.update_traces(texttemplate="%{text}", textposition="outside")
            # st.plotly_chart(fig_caps, use_container_width=True)

            # Round wait metrics for display
            mean_wait_days = round(mean_wait_days, 2)
            p95_wait_days = round(p95_wait_days, 2)

            # Build combined dataframe

        # ---- Capacities Only ----
            df_caps = pd.DataFrame({
                "Service": ["Clinic", "Imaging", "Biopsy"],
                "Capacity": [consult_cap, imaging_cap, biopsy_cap]
            })

            fig_caps = px.bar(
                df_caps,
                x="Service",
                y="Capacity",
                text="Capacity",
                title="Simulation: Capacity Chosen for Simulation",
                color="Service",
            )
            fig_caps.update_traces(texttemplate="%{text}", textposition="outside")
            st.plotly_chart(fig_caps, use_container_width=True)

            # ---- Wait Metrics Only ----
            df_waits = pd.DataFrame({
                "Metric": ["Mean Wait", "95th Percentile Wait"],
                "Days": [mean_wait_days, p95_wait_days]
            })

            fig_waits = px.bar(
                df_waits,
                x="Metric",
                y="Days",
                text="Days",
                color="Metric",
                title="Simulation: Achieved Wait Times",
                color_discrete_sequence=["#EF553B", "#FF97FF"]
            )
            fig_waits.update_traces(texttemplate="%{text}", textposition="outside")
            # Optional traffic-light style feedback
            target_wait = st.number_input("Target mean wait for alert (days)", 0.0, 60.0, 14.0)
            # Optional: Add horizontal line for target wait
            fig_waits.add_hline(
                y=target_wait,
                line_dash="dash",
                line_color="green",
                annotation_text="Target Wait",
                annotation_position="top right"
            )

            st.plotly_chart(fig_waits, use_container_width=True)

            # # -----------------------------
            # # Build Sankey diagram
            # # -----------------------------
            # labels = ["Referral", "Clinic", "Imaging", "Biopsy", "Diagnosis", "Delayed"]
            # flow = summary.get("flow", {})  # safely get the flow dict or empty if missing
            # flows = summary.get("flows", {})  # <- note "flows" plural
            # values = [
            #     flows.get("referral_to_clinic", 0),
            #     flows.get("clinic_to_imaging", 0),
            #     flows.get("clinic_to_delayed", 0),
            #     flows.get("imaging_to_biopsy", 0),
            #     flows.get("imaging_to_diagnosis", 0),
            #     flows.get("biopsy_to_diagnosis", 0),
            # ]

            # source = [0, 1, 1, 2, 2, 3]
            # target = [1, 2, 5, 3, 4, 4]

            # fig_sankey = go.Figure(data=[go.Sankey(
            #     node=dict(
            #         pad=15,
            #         thickness=20,
            #         line=dict(color="black", width=0.5),
            #         label=labels,
            #         color=["green","green","green","orange","green","red"]
            #     ),
            #     link=dict(
            #         source=source,
            #         target=target,
            #         value=values,
            #         color=["green","green","red","orange","green","orange"]
            #     )
            # )])
            # fig_sankey.update_layout(
            #     title_text="Breast Diagnostic Pathway & Bottlenecks",
            #     font_size=12
            # )
            # st.plotly_chart(fig_sankey, use_container_width=True)
            # st.write(summary)


            # df_combined = pd.DataFrame({
            #     "Service/Metric": ["Clinic", "Imaging", "Biopsy", "Mean wait", "95th percentile"],
            #     "Value": [consult_cap, imaging_cap, biopsy_cap, mean_wait_days, p95_wait_days],
            #     "Type": ["Capacity", "Capacity", "Capacity", "Wait (days)", "Wait (days)"]
            # })

            # fig_combined = px.bar(
            #     df_combined,
            #     x="Service/Metric",
            #     y="Value",
            #     color="Type",
            #     barmode="group",
            #     text="Value",
            #     title="Simulation Inputs & Key Wait Metrics",
            #     color_discrete_map={"Capacity": "#636EFA", "Wait (days)": "#EF553B"}
            # )
            # fig_combined.update_traces(texttemplate="%{text}", textposition="outside")
            # st.plotly_chart(fig_combined, use_container_width=True)

            st.markdown("### In hours")
            col3, col4 = st.columns(2)
            col3.metric("Mean wait (hours)", round(mean_wait_hours, 1))
            col4.metric("95th percentile wait (hours)", round(p95_wait_hours, 1))

            # Optional traffic-light style feedback
           #target_wait = st.number_input("Target mean wait for alert (days)", 0.0, 60.0, 14.0)
            
            if mean_wait_days <= target_wait:
                st.success(f"Mean wait is within target ✔ ({round(target_wait - mean_wait_days, 2)} days below target)")
            else:
                st.error(f"Mean wait exceeds target ✖ ({round(mean_wait_days - target_wait, 2)} days above target)")

            # # Optional bar chart
            # st.markdown("### Wait Time Distribution")
            # import plotly.express as px
            # import pandas as pd

            # df_waits = pd.DataFrame({
            #     "Metric": ["Mean wait", "95th percentile"],
            #     "Days": [mean_wait_days, p95_wait_days]
            # })
            # fig = px.bar(df_waits, x="Metric", y="Days", text="Days")
            # st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Tab 3: Capacity Planning
# -----------------------------
with tab_capacity:
    st.subheader("Capacity Planning")
    st.markdown("Searches for minimum resources required to meet the target mean waiting time.")
    target_wait = st.number_input("Target mean wait (days)", 0.0, 60.0, 14.0)
    max_iterations = st.number_input("Max search iterations", 1, 50, 20, 1)

    if st.button("Run capacity search"):

        with st.spinner("Searching capacity..."):

            baseline_resources = resources

            result = safe_capacity_search(
                base_inputs=sim_inputs,
                base_resources=resources,
                target_wait_days=target_wait,
                max_iterations=max_iterations,
                step_size=1,
                runs=mc_runs
            )

        # ---- Extract results safely ----
        required = result["required_resources"]
        achieved_wait = result["achieved_wait"]

        # ---- Capacity Increase ----
        delta_clinic = required.clinic_rooms - baseline_resources.clinic_rooms
        delta_imaging = required.imaging_slots - baseline_resources.imaging_slots
        delta_biopsy = required.biopsy_slots - baseline_resources.biopsy_slots

        st.markdown("### Capacity Increase Required")

        col1, col2, col3 = st.columns(3)
        col1.metric("Clinic Increase", delta_clinic)
        col2.metric("Imaging Increase", delta_imaging)
        col3.metric("Biopsy Increase", delta_biopsy)

        st.markdown("---")

        # ---- Final Recommended Capacity ----
        st.markdown("## Capacity Recommendation")

        col1, col2, col3 = st.columns(3)
        col1.metric("Clinic Rooms Required", required.clinic_rooms)
        col2.metric("Imaging Slots Required", required.imaging_slots)
        col3.metric("Biopsy Slots Required", required.biopsy_slots)

        st.markdown("---")

        # ---- Achieved Performance ----
        st.metric("Achieved Mean Wait (days)", round(achieved_wait, 2))

        gap = target_wait - achieved_wait

        if achieved_wait <= target_wait:
            st.success(f"Target achieved ✔ ({round(gap,2)} days below target)")
        else:
            st.error(f"Target NOT achieved ✖ ({round(abs(gap),2)} days above target)")

        if "warning" in result:
            st.warning(result["warning"])

# -----------------------------
# Tab 4: Documentation
# -----------------------------
with tab_docs:
    st.subheader("Documentation & Guidance")
    st.markdown(get_user_guide())
    st.download_button(
        "Download user guide (markdown)",
        data=get_user_guide().encode("utf-8"),
        file_name="RDUH_Breast_Service_Tool_User_Guide.md",
        mime="text/markdown",
    )






