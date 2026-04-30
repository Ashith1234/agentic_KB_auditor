import streamlit as st
import sys, os
sys.path.append(os.path.abspath("src"))

def main():
    st.title("📥 RAG Auditor — Download Hub")
    st.caption("Install the self-correcting KB auditor into your project in 60 seconds.")
    st.markdown("---")

    # ── Login ─────────────────────────────────────────────────────
    st.markdown("### 👤 Get Started")
    col_name, col_email = st.columns(2)
    name  = col_name.text_input("Your Name",  placeholder="Jane Smith")
    email = col_email.text_input("Work Email", placeholder="jane@company.com")

    if st.button("🚀 Generate My Install Command", type="primary", disabled=not (name and email)):
        st.session_state["logged_in"] = True
        st.session_state["user_name"] = name
        st.session_state["user_email"] = email

    if st.session_state.get("logged_in"):
        user = st.session_state.get("user_name", "User")
        st.success(f"Welcome, {user}! Here is your personalised install command:")

        st.markdown("#### Step 1 — Clone & Install")
        st.code("git clone https://github.com/your-org/rag-auditor && cd rag-auditor\npip install -r requirements.txt", language="bash")

        st.markdown("#### Step 2 — Run Installer (auto-detects your project)")
        st.code("python src/installer/installer.py install /path/to/your/project", language="bash")

        st.markdown("#### Step 3 — Launch Dashboard")
        st.code("streamlit run src/interfaces/dashboard/streamlit_app.py --server.port 8502", language="bash")

        st.markdown("#### Step 4 — Run First Audit")
        st.code("python src/plugin/cli.py audit", language="bash")

        st.markdown("---")
        st.markdown("### 📌 What happens after install")
        st.markdown("""
- ✅ Your chatbot's `/chat` endpoint is intercepted
- ✅ Every query is logged to the Audit Dashboard
- ✅ Workers review responses and submit feedback  
- ✅ Managers approve KB changes via the Manager Dashboard
- ✅ Agents self-correct based on feedback automatically
        """)

        st.markdown("---")
        st.info(f"📧 A confirmation with docs has been sent to **{st.session_state.get('user_email')}** _(simulated)_")

if __name__ == "__main__":
    main()

