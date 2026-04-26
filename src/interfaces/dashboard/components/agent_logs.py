import streamlit as st
import os

def render(log_file="data/logs/system.log"):
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = f.readlines()[-20:] # Show last 20 lines
        st.code("".join(logs), language="log")
    else:
        st.info("No logs available yet.")
