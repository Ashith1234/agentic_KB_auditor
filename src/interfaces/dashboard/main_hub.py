import streamlit as st

def main():
    st.title("Download Hub")
    st.write("Login to download the plugin.")
    email = st.text_input("Email (optional)")
    if st.button("Download Plugin"):
        st.success("Plugin downloaded!")
        st.code("rag install .", language="bash")

if __name__ == "__main__":
    main()
