import streamlit as st

def render(score: float):
    st.metric(label="KB Health", value=f"{score}%", delta="-2%")
