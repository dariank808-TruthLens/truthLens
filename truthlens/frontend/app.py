import streamlit as st

st.set_page_config(page_title="TruthLens", page_icon="🔍", layout="centered")

def ensure_page_state():
    if "page" not in st.session_state:
        st.session_state.page = "landing"

def get_page_from_state():
    ensure_page_state()
    return st.session_state.page

def go_to(page: str):
    ensure_page_state()
    st.session_state.page = page

def render_landing():
    st.title("Welcome to TruthLens")
    st.markdown(
        """
        **Mission:** Empower people with clear, reliable information by surfacing context,
        verifying claims, and making truth accessible.

        **Vision:** A world where accurate information is easy to find, understand, and share.
        """
    )
    st.button("Enter TruthLens", key="enter_btn", on_click=go_to, args=("app",))

def render_app():
    st.header("TruthLens — Application")
    st.write("This is the main TruthLens application placeholder. Replace with tools and UI.")
    st.button("← Back to Landing", key="back_btn", on_click=go_to, args=("landing",))

def main():
    page = get_page_from_state()
    if page == "landing":
        render_landing()
    else:
        render_app()

if __name__ == "__main__":
    main()