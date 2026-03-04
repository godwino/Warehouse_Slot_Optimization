"""Streamlit dashboard for HVDC Grocery Warehouse Digital Twin."""

from __future__ import annotations

import math
import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

# Ensure local src imports work when app is launched from project root.
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.generate_data import generate_orders, generate_skus
from src.picking_simulation import build_travel_heatmap_data, simulate_picking
from src.slotting_engine import assign_prime_slotting, assign_random_slotting
from src.truck_simulation import simulate_truck_arrivals
from src.warehouse_layout import generate_layout


def _compute_layout_size(num_skus: int, levels: int = 4, default_aisles: int = 20) -> tuple[int, int]:
    """Compute a layout with enough slots to hold all SKUs."""
    bays_needed = math.ceil(num_skus / (default_aisles * levels))
    bays = max(20, bays_needed + 5)  # Add headroom for spare capacity.
    return default_aisles, bays


def _comparison_figure(random_metrics: dict, prime_metrics: dict):
    df = pd.DataFrame(
        [
            {
                "Strategy": "Random Slotting",
                "Total Distance (m)": random_metrics["total_travel_distance_m"],
                "Cases per Hour": random_metrics["cases_per_hour"],
            },
            {
                "Strategy": "Prime Slotting",
                "Total Distance (m)": prime_metrics["total_travel_distance_m"],
                "Cases per Hour": prime_metrics["cases_per_hour"],
            },
        ]
    )
    fig = px.bar(
        df,
        x="Strategy",
        y=["Total Distance (m)", "Cases per Hour"],
        barmode="group",
        title="Random vs Prime Slotting Comparison",
    )
    return fig


def _scenario_comparison_figure(baseline_metrics: dict, optimized_metrics: dict):
    df = pd.DataFrame(
        [
            {
                "Scenario": "Baseline",
                "Total Distance (m)": baseline_metrics["total_travel_distance_m"],
                "Cases per Hour": baseline_metrics["cases_per_hour"],
            },
            {
                "Scenario": "Optimized",
                "Total Distance (m)": optimized_metrics["total_travel_distance_m"],
                "Cases per Hour": optimized_metrics["cases_per_hour"],
            },
        ]
    )
    return px.bar(
        df,
        x="Scenario",
        y=["Total Distance (m)", "Cases per Hour"],
        barmode="group",
        title="Baseline vs Optimized Scenario",
    )


def _layout_figure(prime_slotting_df: pd.DataFrame):
    vis_df = prime_slotting_df.copy()
    fig = px.scatter(
        vis_df,
        x="x_m",
        y="y_m",
        color="velocity_class",
        hover_data=["sku_id", "location_id", "aisle", "bay", "level"],
        title="Warehouse Layout (Prime Slotting Positions)",
    )
    fig.update_traces(marker=dict(size=6, opacity=0.7))
    fig.update_layout(xaxis_title="Aisle X (m)", yaxis_title="Bay Depth Y (m)")
    return fig


def _heatmap_figure(heatmap_df: pd.DataFrame):
    if heatmap_df.empty:
        return px.imshow([[0]], title="Picker Travel Heatmap")

    pivot = heatmap_df.pivot(index="bay", columns="aisle", values="visit_count").fillna(0)
    fig = px.imshow(
        pivot,
        labels={"x": "Aisle", "y": "Bay", "color": "Visits"},
        title="Picker Travel Heatmap (Prime Slotting)",
        aspect="auto",
    )
    return fig


def run_simulation(num_skus: int, num_trucks: int, num_orders: int, seed: int):
    skus_df = generate_skus(num_skus=num_skus, seed=seed)
    orders_df = generate_orders(skus_df=skus_df, num_orders=num_orders, seed=seed)
    trucks_df = simulate_truck_arrivals(skus_df=skus_df, num_trucks=num_trucks, seed=seed)

    aisles, bays = _compute_layout_size(num_skus=num_skus, levels=4)
    layout_df = generate_layout(num_aisles=aisles, bays_per_aisle=bays, levels=4)

    random_slotting_df = assign_random_slotting(skus_df, layout_df, seed=seed)
    prime_slotting_df = assign_prime_slotting(skus_df, layout_df, seed=seed)

    random_metrics, random_picks_df = simulate_picking(orders_df, random_slotting_df)
    prime_metrics, prime_picks_df = simulate_picking(orders_df, prime_slotting_df)

    distance_saved = (
        random_metrics["total_travel_distance_m"] - prime_metrics["total_travel_distance_m"]
    )
    saved_pct = (
        (distance_saved / random_metrics["total_travel_distance_m"]) * 100.0
        if random_metrics["total_travel_distance_m"] > 0
        else 0.0
    )

    return {
        "skus_df": skus_df,
        "orders_df": orders_df,
        "trucks_df": trucks_df,
        "layout_df": layout_df,
        "random_slotting_df": random_slotting_df,
        "prime_slotting_df": prime_slotting_df,
        "random_metrics": random_metrics,
        "prime_metrics": prime_metrics,
        "random_picks_df": random_picks_df,
        "prime_picks_df": prime_picks_df,
        "distance_saved_m": round(distance_saved, 2),
        "distance_saved_pct": round(saved_pct, 2),
    }


def run_strategy_scenario(
    num_skus: int, num_trucks: int, num_orders: int, seed: int, strategy: str
) -> dict:
    """Run a single-strategy scenario for side-by-side comparison."""
    skus_df = generate_skus(num_skus=num_skus, seed=seed)
    orders_df = generate_orders(skus_df=skus_df, num_orders=num_orders, seed=seed)
    trucks_df = simulate_truck_arrivals(skus_df=skus_df, num_trucks=num_trucks, seed=seed)
    aisles, bays = _compute_layout_size(num_skus=num_skus, levels=4)
    layout_df = generate_layout(num_aisles=aisles, bays_per_aisle=bays, levels=4)

    if strategy.lower() == "prime":
        slotting_df = assign_prime_slotting(skus_df, layout_df, seed=seed)
    else:
        slotting_df = assign_random_slotting(skus_df, layout_df, seed=seed)

    metrics, picks_df = simulate_picking(orders_df, slotting_df)
    return {
        "strategy": strategy.title(),
        "metrics": metrics,
        "slotting_df": slotting_df,
        "picks_df": picks_df,
        "orders_df": orders_df,
        "trucks_df": trucks_df,
    }


def _render_downloads(results: dict):
    st.subheader("Download Simulation Outputs")
    st.download_button(
        "Download SKUs CSV",
        data=results["skus_df"].to_csv(index=False),
        file_name="skus.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download Orders CSV",
        data=results["orders_df"].to_csv(index=False),
        file_name="orders.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download Trucks CSV",
        data=results["trucks_df"].to_csv(index=False),
        file_name="trucks.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download Random Slotting CSV",
        data=results["random_slotting_df"].to_csv(index=False),
        file_name="random_slotting.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download Prime Slotting CSV",
        data=results["prime_slotting_df"].to_csv(index=False),
        file_name="prime_slotting.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download Random Picks CSV",
        data=results["random_picks_df"].to_csv(index=False),
        file_name="random_picks.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download Prime Picks CSV",
        data=results["prime_picks_df"].to_csv(index=False),
        file_name="prime_picks.csv",
        mime="text/csv",
    )


def main():
    st.set_page_config(page_title="HVDC Grocery Warehouse Digital Twin", layout="wide")
    st.title("HVDC Grocery Warehouse Digital Twin")
    st.caption("Prime slotting impact on picker travel distance")

    st.sidebar.header("Simulation Controls")
    num_skus = st.sidebar.slider("Number of SKUs", min_value=200, max_value=3000, value=1000, step=100)
    num_trucks = st.sidebar.slider("Number of Trucks", min_value=10, max_value=300, value=100, step=10)
    num_orders = st.sidebar.slider("Number of Orders", min_value=50, max_value=2000, value=1000, step=50)
    seed = st.sidebar.number_input("Random Seed", min_value=1, max_value=999999, value=42, step=1)

    st.sidebar.divider()
    st.sidebar.subheader("Scenario Comparison")
    baseline_seed = st.sidebar.number_input(
        "Baseline Seed", min_value=1, max_value=999999, value=101, step=1
    )
    optimized_seed = st.sidebar.number_input(
        "Optimized Seed", min_value=1, max_value=999999, value=202, step=1
    )
    baseline_orders = st.sidebar.slider(
        "Baseline Orders", min_value=50, max_value=2000, value=int(num_orders), step=50
    )
    optimized_orders = st.sidebar.slider(
        "Optimized Orders", min_value=50, max_value=2000, value=int(num_orders), step=50
    )

    run_clicked = st.button("Run Simulation", type="primary")
    run_compare_clicked = st.button("Run Scenario Comparison")

    tab_sim, tab_compare = st.tabs(["Simulation", "Scenario Comparison"])

    with tab_sim:
        if run_clicked:
            with st.spinner("Running digital twin simulation..."):
                st.session_state["sim_results"] = run_simulation(
                    num_skus=int(num_skus),
                    num_trucks=int(num_trucks),
                    num_orders=int(num_orders),
                    seed=int(seed),
                )

        if "sim_results" not in st.session_state:
            st.info("Set controls in the sidebar and click 'Run Simulation'.")
        else:
            results = st.session_state["sim_results"]
            random_metrics = results["random_metrics"]
            prime_metrics = results["prime_metrics"]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Prime Travel Distance (m)", f"{prime_metrics['total_travel_distance_m']:,.0f}")
            c2.metric("Cases Picked", f"{prime_metrics['cases_picked']:,}")
            c3.metric("Cases per Hour", f"{prime_metrics['cases_per_hour']:,.1f}")
            c4.metric(
                "Distance Saved vs Random",
                f"{results['distance_saved_m']:,.0f} m",
                f"{results['distance_saved_pct']:.1f}%",
            )

            st.subheader("Simulation Summary")
            st.write(
                {
                    "SKUs": len(results["skus_df"]),
                    "Orders": results["orders_df"]["order_id"].nunique(),
                    "Order lines": len(results["orders_df"]),
                    "Trucks": results["trucks_df"]["truck_id"].nunique(),
                }
            )

            st.plotly_chart(_layout_figure(results["prime_slotting_df"]), use_container_width=True)
            heatmap_df = build_travel_heatmap_data(results["prime_picks_df"])
            st.plotly_chart(_heatmap_figure(heatmap_df), use_container_width=True)
            st.plotly_chart(
                _comparison_figure(random_metrics, prime_metrics),
                use_container_width=True,
            )

            st.subheader("Slotting Strategy Metrics")
            metrics_table = pd.DataFrame(
                [
                    {"Strategy": "Random Slotting", **random_metrics},
                    {"Strategy": "Prime Slotting", **prime_metrics},
                ]
            )
            st.dataframe(metrics_table, use_container_width=True)
            _render_downloads(results)

    with tab_compare:
        if run_compare_clicked:
            with st.spinner("Running baseline and optimized scenarios..."):
                st.session_state["scenario_results"] = {
                    "baseline": run_strategy_scenario(
                        num_skus=int(num_skus),
                        num_trucks=int(num_trucks),
                        num_orders=int(baseline_orders),
                        seed=int(baseline_seed),
                        strategy="random",
                    ),
                    "optimized": run_strategy_scenario(
                        num_skus=int(num_skus),
                        num_trucks=int(num_trucks),
                        num_orders=int(optimized_orders),
                        seed=int(optimized_seed),
                        strategy="prime",
                    ),
                }

        if "scenario_results" not in st.session_state:
            st.info("Adjust baseline/optimized controls and click 'Run Scenario Comparison'.")
        else:
            baseline = st.session_state["scenario_results"]["baseline"]
            optimized = st.session_state["scenario_results"]["optimized"]
            baseline_metrics = baseline["metrics"]
            optimized_metrics = optimized["metrics"]
            distance_delta = (
                baseline_metrics["total_travel_distance_m"]
                - optimized_metrics["total_travel_distance_m"]
            )

            c1, c2, c3 = st.columns(3)
            c1.metric("Baseline Distance (m)", f"{baseline_metrics['total_travel_distance_m']:,.0f}")
            c2.metric("Optimized Distance (m)", f"{optimized_metrics['total_travel_distance_m']:,.0f}")
            c3.metric("Distance Improvement (m)", f"{distance_delta:,.0f}")

            left, right = st.columns(2)
            left.subheader("Baseline Metrics")
            left.dataframe(pd.DataFrame([baseline_metrics]), use_container_width=True)
            right.subheader("Optimized Metrics")
            right.dataframe(pd.DataFrame([optimized_metrics]), use_container_width=True)
            st.plotly_chart(
                _scenario_comparison_figure(baseline_metrics, optimized_metrics),
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
