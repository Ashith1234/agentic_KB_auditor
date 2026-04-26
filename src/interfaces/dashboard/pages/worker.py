import streamlit as st

def main():
    st.title("Worker Dashboard")
    query = st.text_input("Query Input")
    if query:
        st.write("Real LLM Response: ...")
        st.write("Source Docs: ...")
        st.write("Confidence Score: 0.85")
        
        st.write("Feedback UI:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Like"):
                st.success("Feedback recorded!")
        with col2:
            if st.button("👎 Dislike"):
                reason = st.selectbox("Reason", ["OUTDATED", "WRONG", "IRRELEVANT", "VERSION_MISMATCH"])
                if st.button("Submit Dislike"):
                    st.warning(f"Feedback submitted: {reason}")

if __name__ == "__main__":
    main()
