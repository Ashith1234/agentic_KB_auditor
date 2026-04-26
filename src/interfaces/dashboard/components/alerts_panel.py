import streamlit as st

def render(signals: list):
    if not signals:
        st.success("No active issues found.")
        return
    for signal in signals:
        st.warning(f"{signal.signal_type.upper()}: {signal.description}")
