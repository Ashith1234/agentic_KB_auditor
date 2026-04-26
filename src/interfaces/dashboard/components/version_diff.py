import streamlit as st
import difflib

def render(old_text: str, new_text: str):
    diff = difflib.ndiff(old_text.splitlines(), new_text.splitlines())
    diff_text = "\n".join(diff)
    st.code(diff_text, language="diff")
