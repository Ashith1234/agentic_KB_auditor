import streamlit as st
from core.logger import logger

def render(article_id: str):
    if st.button(f"Undo Last Change for {article_id}"):
        logger.info(f"User requested rollback for {article_id}")
        st.success(f"Rollback initiated for {article_id}")
