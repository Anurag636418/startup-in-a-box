import json
import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.workflow import save_results


st.set_page_config(
    page_title="Startup-in-a-Box",
    page_icon="SI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2e3147;
    }
    [data-testid="stMetric"] {
        background-color: #1a1d27;
        border: 1px solid #2e3147;
        border-radius: 8px;
        padding: 16px;
    }
    [data-testid="stMetricValue"] { color: #7c83fd; font-size: 1.4rem !important; }
    [data-testid="stMetricLabel"] { color: #8b92a5; }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1d27;
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: #8b92a5;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #7c83fd !important;
        color: white !important;
    }
    .stButton > button {
        background: #7c83fd;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        width: 100%;
    }
    .stDownloadButton > button {
        background: #2ecc71;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
    }
    .stTextArea textarea {
        background-color: #1a1d27;
        border: 1px solid #2e3147;
        color: #e0e4f0;
        border-radius: 8px;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid #2e3147;
        border-radius: 8px;
        overflow: hidden;
    }
    h1, h2, h3 { color: #e0e4f0 !important; }
    p, li { color: #b0b8cc; }
    .disclaimer {
        background-color: #1e1a2e;
        border-left: 4px solid #f39c12;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 12px 0;
        color: #b0b8cc;
        font-size: 0.85rem;
    }
    .agent-card {
        background-color: #1a1d27;
        border: 1px solid #2e3147;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #b0b8cc;
        font-size: 0.9rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


def format_inr(value: float | int | None) -> str:
    if value is None:
        return "INR 0"
    return f"INR {value:,.0f}"


with st.sidebar:
    st.markdown("## Startup-in-a-Box")
    st.markdown("---")

    st.markdown("### Agent workflow")
    st.markdown(
        """
    <div class='agent-card'><b>Market Analyst</b><br>Researches market, competitors, and risks</div>
    <div class='agent-card'><b>Product Manager</b><br>Defines features and value proposition</div>
    <div class='agent-card'><b>Financial Analyst</b><br>Searches industry finance benchmarks and builds projections</div>
    <div class='agent-card'><b>Pitch Creator</b><br>Assembles an investor-style pitch deck</div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### Settings")
    show_raw = st.checkbox("Show raw agent outputs", value=False)

    st.markdown("---")
    st.caption("Built with Groq, Python, and Streamlit")


st.markdown("# Startup-in-a-Box")
st.markdown("*Turn a startup idea into an investor-style pitch deck using AI agents.*")

st.markdown(
    """
<div class='disclaimer'>
<b>Financial disclaimer:</b> Projections are AI-generated estimates benchmarked against
available comparable-company data. They are for ideation only and should not be used for
investment decisions or fundraising without expert validation.
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")

col1, col2 = st.columns([4, 1])
with col1:
    idea = st.text_area(
        "Your startup idea",
        placeholder="Example: an app for renting farm equipment to small farmers in rural India",
        height=110,
        max_chars=4000,
    )
with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    run_btn = st.button("Generate Pitch", type="primary")


if run_btn:
    if not idea.strip():
        st.error("Please enter a startup idea first.")
    else:
        with st.status("Running AI agents...", expanded=True) as status:
            try:
                results = {}

                from agents.financial_analyst import run_financial_analyst
                from agents.market_analyst import run_market_analyst
                from agents.pitch_creator import run_pitch_creator
                from agents.product_manager import run_product_manager

                st.write("Market Analyst is researching...")
                results["market"] = run_market_analyst(idea)
                st.write("Market analysis complete")

                st.write("Product Manager is defining the product...")
                results["product"] = run_product_manager(results["market"])
                st.write("Product spec complete")

                st.write("Financial Analyst is building projections...")
                results["finance"] = run_financial_analyst(
                    results["market"],
                    results["product"],
                )
                st.write("Financial projections complete")

                st.write("Pitch Creator is assembling the deck...")
                results["pitch"] = run_pitch_creator(
                    results["market"],
                    results["product"],
                    results["finance"],
                )
                st.write("Pitch deck complete")

                output_path = save_results(results)
                st.session_state["results"] = results
                st.session_state["output_path"] = str(output_path)
                status.update(label="Pipeline complete", state="complete")

            except Exception as exc:
                status.update(label="Pipeline failed", state="error")
                st.error(f"Error: {exc}")


if "results" in st.session_state:
    results = st.session_state["results"]
    finance = results["finance"]

    st.markdown("---")
    st.markdown("## Results")

    if st.session_state.get("output_path"):
        st.caption(f"Saved outputs to {st.session_state['output_path']}")

    if "projections" in finance and "assumptions" in finance:
        projections = finance["projections"]
        assumptions = finance["assumptions"]
        year1 = projections[0]
        year5 = projections[4]

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Year 1 Revenue", format_inr(year1["revenue_inr"]))
        col2.metric(
            "Year 5 Revenue",
            format_inr(year5["revenue_inr"]),
            delta=f"+{((year5['revenue_inr'] / year1['revenue_inr']) - 1) * 100:.0f}% vs Y1",
        )
        col3.metric("Commission Rate", f"{assumptions['commission_rate_percent']}%")
        col4.metric("Upfront Investment", format_inr(finance.get("upfront_investment_inr", 0)))
        col5.metric(
            "Break-even",
            f"Year {finance['break_even_year']}" if finance.get("break_even_year") else "Beyond Y5",
        )

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Market Analysis",
            "Product Spec",
            "Financials",
            "Finance Benchmarks",
            "Pitch Deck",
        ]
    )

    with tab1:
        st.markdown("### Market Analysis")
        st.markdown(results["market"])
        if show_raw:
            st.code(results["market"], language="markdown")

    with tab2:
        st.markdown("### Product Specification")
        st.markdown(results["product"])
        if show_raw:
            st.code(results["product"], language="markdown")

    with tab3:
        st.markdown("### Financial Projections")
        st.markdown(
            """
        <div class='disclaimer'>
        These projections are directional AI-generated estimates. Treat them as a starting
        point for validation, not as financial advice.
        </div>
        """,
            unsafe_allow_html=True,
        )

        if "raw" in finance:
            st.warning("Financial data could not be parsed or validated.")
            st.text(finance["raw"])
        else:
            assumptions = finance["assumptions"]
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Transaction Value", format_inr(assumptions["avg_transaction_value_inr"]))
            col2.metric("Commission Rate", f"{assumptions['commission_rate_percent']}%")
            col3.metric("Growth Rate", f"{assumptions['growth_rate_percent']}%")

            if assumptions.get("notes"):
                st.caption(assumptions["notes"])

            if finance.get("financial_benchmark_summary"):
                st.markdown("#### Benchmark Basis")
                st.markdown(finance["financial_benchmark_summary"])

            rows = [
                {
                    "Year": f"Year {p['year']}",
                    "Transactions": f"{p['transactions']:,}",
                    "Revenue": format_inr(p["revenue_inr"]),
                    "Costs": format_inr(p["costs_inr"]),
                    "Profit": format_inr(p["profit_inr"]),
                    "Status": "Profit" if p["profit_inr"] > 0 else "Loss",
                }
                for p in finance["projections"]
            ]
            st.dataframe(rows, use_container_width=True, hide_index=True)

            break_even_year = finance.get("break_even_year")
            if break_even_year:
                st.success(f"Break-even achieved in Year {break_even_year}")
            else:
                st.warning("Break-even not achieved within 5 years")
                threshold = finance.get("breakeven_threshold")
                if threshold:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Year 5 Revenue", format_inr(threshold["year5_revenue"]))
                    col2.metric("Year 5 Costs", format_inr(threshold["year5_current_costs"]))
                    col3.metric("Cost Reduction Needed", format_inr(threshold["cost_reduction_needed"]))

    with tab4:
        st.markdown("### Finance Benchmarks")
        st.caption(
            "Fetched using Groq Compound web search. Public values are used when available; "
            "estimated ranges should be treated as directional."
        )
        if finance.get("comparable_data"):
            st.markdown(finance["comparable_data"])
        else:
            st.info("No benchmark data available for this sector.")

    with tab5:
        st.markdown("### Pitch Deck")
        st.caption("Marp Markdown format, ready to export.")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(results["pitch"])
        with col2:
            st.download_button(
                label="Download Pitch Deck",
                data=results["pitch"],
                file_name="pitch_deck.md",
                mime="text/markdown",
            )
            st.download_button(
                label="Download Financials",
                data=json.dumps(finance, indent=2),
                file_name="financials.json",
                mime="application/json",
            )

        if show_raw:
            st.code(results["pitch"], language="markdown")
