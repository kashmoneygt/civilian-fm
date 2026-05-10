"""Streamlit 3-column comparison dashboard.

Run with: uv run streamlit run dashboard/app.py
"""
from __future__ import annotations

import streamlit as st

from dashboard import runners, store

st.set_page_config(page_title="civilian-fm", layout="wide")

st.title("civilian-fm — bare / stuffed / agentic comparison")

with st.sidebar:
    st.subheader("Models per column")
    bare_model = st.selectbox("Bare", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"], index=0)
    stuffed_model = st.selectbox("Stuffed", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"], index=0)
    agentic_model = st.selectbox("Agentic", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"], index=0)

query = st.text_area(
    "Query",
    "i have a liquor store in cobb county in acworth ga, it is based on S-corp where me and my wife are on payroll, how can i lower my tax burden",
    height=80,
)

if st.button("Run comparison", type="primary"):
    cols = st.columns(3)
    results = {}
    for col, name, model in zip(
        cols,
        ("bare", "stuffed", "agentic"),
        (bare_model, stuffed_model, agentic_model),
    ):
        with col:
            st.subheader(name)
            with st.spinner(f"Running {name}..."):
                r = runners.RUNNERS[name](query, model)
                store.log_run(query, r)
            st.caption(
                f"{r['model']} · {r['elapsed_s']}s · "
                f"{r['prompt_tokens']:,} prompt / {r['completion_tokens']:,} completion tokens"
            )
            st.markdown(r["content"])
            results[name] = r

st.divider()
st.subheader("Recent runs")
runs = store.all_runs()[:30]
if runs:
    st.dataframe(
        [
            {
                "id": r["id"],
                "when": r["created_at"],
                "runner": r["runner"],
                "model": r["model"],
                "tokens": (r["prompt_tokens"] or 0) + (r["completion_tokens"] or 0),
                "elapsed_s": r["elapsed_s"],
                "query": (r["query"] or "")[:80],
            }
            for r in runs
        ],
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("No runs yet.")
