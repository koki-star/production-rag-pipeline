from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.pipeline import run_pipeline

st.set_page_config(page_title="Two-Stage RAG Pipeline", layout="wide")
st.title("Two-Stage RAG Pipeline")
st.caption("Query rewriting, bi-encoder search, cross-encoder reranking, and web fallback")

if "history" not in st.session_state:
    st.session_state.history = []

multi_turn = st.sidebar.checkbox("Multi-turn follow-ups", value=False)
if st.sidebar.button("Clear chat history"):
    st.session_state.history = []

query = st.text_input("Ask a question about the internal docs or a new topic")
run = st.button("Search", type="primary")

if run and query.strip():
    history = st.session_state.history if multi_turn else []
    with st.spinner("Running the pipeline..."):
        result = run_pipeline(query, history)
    if multi_turn:
        st.session_state.history.append(query)

    st.sidebar.subheader("Pipeline state")
    st.sidebar.write("Transformed query")
    st.sidebar.code(result.transformed_query or "(empty)")

    if result.route_taken == "INTERNAL_RAG":
        st.sidebar.success("INTERNAL_RAG (High Confidence)")
    else:
        st.sidebar.warning("WEB_FALLBACK (Low Confidence Triggered)")

    st.sidebar.write("Confidence meter")
    st.sidebar.progress(min(max(result.confidence_score, 0.0), 1.0))
    st.sidebar.write(f"Top cross-encoder score: {result.confidence_score:.3f}")
    st.sidebar.write("Threshold cutoff: 0.55")

    st.subheader("Answer")
    st.write(result.answer)
    st.write("Citations")
    for citation in result.citations:
        if citation.startswith("http://") or citation.startswith("https://"):
            st.markdown(f"- [{citation}]({citation})")
        else:
            st.markdown(f"- `{citation}`")

    with st.expander("Stage 1 bi-encoder top 20", expanded=False):
        rows = [
            {
                "rank": chunk.stage1_rank,
                "chunk_id": chunk.chunk_id,
                "score": round(chunk.score, 3),
                "preview": " ".join(chunk.content.split())[:140],
            }
            for chunk in result.stage1_candidates
        ]
        st.table(rows)

    with st.expander("Stage 2 cross-encoder top 5", expanded=True):
        rows = [
            {
                "new_rank": shift.stage2_rank,
                "old_rank": shift.stage1_rank,
                "shift": (
                    ""
                    if shift.stage1_rank is None or shift.stage2_rank is None
                    else shift.stage1_rank - shift.stage2_rank
                ),
                "chunk_id": shift.chunk_id,
                "score": next(
                    (
                        round(chunk.score, 3)
                        for chunk in result.stage2_candidates
                        if chunk.chunk_id == shift.chunk_id
                    ),
                    None,
                ),
            }
            for shift in result.rank_shifts
        ]
        st.table(rows)
elif run:
    st.info("Type a question first.")
