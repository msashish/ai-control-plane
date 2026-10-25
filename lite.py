""" streamlit interface for llm-router """

import streamlit as st
from router.app import route, get_recommended_model

st.set_page_config(page_title="LLM Router", page_icon="🤖", layout="wide")
st.title("LLM Router")
st.caption("Select the appropriate model based on the prompt and questions.")

input_column, summary_column = st.columns([2,3], gap="small")

with input_column:
    st.subheader("Your prompt")
    with st.form("classify_prompt"):
        user_prompt = st.text_area(
            "Enter your prompt here",
            key="user_prompt",
             height=220,
             placeholder="Example: What is the capital of France?",
             )
        submitted = st.form_submit_button("Classify Prompt", type="primary")

    if submitted:
        st.session_state.pop("classification",None)
        prompt = user_prompt.strip()
        if not prompt:
            st.warning("Enter a prompt before classifying.")
        else:
            try:
                with st.spinner("Classifying with Laya... First run will take time..."):
                    summary = route(prompt)
                    recommended_model = get_recommended_model(summary["model_tier"])
                    flagged = summary["unsafe"] == "yes"
            except (OSError, RuntimeError, ValueError, KeyError, TypeError) as e:
                st.error(f"An error occurred while processing the prompt: {e}")
                st.exception(e)
            else:
                st.session_state["classification"] = {
                    "prompt": prompt,
                    "summary": summary,
                    "recommended_model": recommended_model,
                    "flagged": flagged
                }
with summary_column:
    st.subheader("Laya Signals")
    classification = st.session_state.get("classification")
    if classification is None:
        st.info("Enter a prompt to see the results.")
    else:
        summary = classification["summary"]
        if classification["flagged"]:
            st.warning("⚠️ Poetntial unsafe content. Please review the content before proceeding.")
        else:
            st.success("✅ No safety issues flagged.")
        st.caption(f"Results for last submitted prompt:")
        st.text(classification["prompt"])

        fields = [
            ("reasoning", "Reasoning"),
            ("model_tier", "Model type"),
            ("rag", "Requires RAG ?"),
            ("unsafe", "Unsafe ?"),
        ]
        cards = st.columns(len(fields), gap="small")
        for index, (key, title) in enumerate(fields):
            with cards[index].container(border=True):
                st.caption(title)
                st.markdown(f"**{summary[key].replace('_', ' ').capitalize()}**")
        st.caption(
            "Unsafe includes harmful requests and prompt injection.."
            "This is an estimate, not a guarantee"
        )

        with st.container(border=True):
            st.markdown(f"Recommended LLM: **{classification['recommended_model']}**")
            st.caption(
                f"Model Tier: {summary['model_tier'].replace('_', ' ').capitalize()}. "
                "Recommendation only. No LLM called"
            )
            if classification["flagged"]:
                st.caption(
                    "⚠️ This prompt is flagged as unsafe. Please review the content before proceeding."
                )
    with st.expander("View compact JSON"):
        if classification is not None:
            st.json(classification["summary"])
        else:
            st.caption("No classification data available yet.")
