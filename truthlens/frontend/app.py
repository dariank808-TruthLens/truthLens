import streamlit as st
import time

st.set_page_config(page_title="TruthLens", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")

def ensure_page_state():
    if "page" not in st.session_state:
        st.session_state.page = "landing"
    # initialize settings and upload state
    if "fact_check" not in st.session_state:
        st.session_state.fact_check = False
    if "logical_fallacy_check" not in st.session_state:
        st.session_state.logical_fallacy_check = False
    if "ai_generation_check" not in st.session_state:
        st.session_state.ai_generation_check = False
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "results_ready" not in st.session_state:
        st.session_state.results_ready = False


def _file_icon(name: str) -> str:
    """Return a small emoji icon based on file extension."""
    ext = (name.split('.')[-1].lower() if '.' in name else '')
    return {
        'pdf': '📄',
        'txt': '📄',
        'md': '📝',
        'doc': '📄',
        'docx': '📄',
        'png': '🖼️',
        'jpg': '🖼️',
        'jpeg': '🖼️',
        'csv': '📊',
        'json': '🧾',
    }.get(ext, '📁')

def get_page_from_state():
    ensure_page_state()
    return st.session_state.page

def go_to(page: str):
    ensure_page_state()
    st.session_state.page = page


def reset_and_return_to_app():
    # clear upload and processing state and reset settings to defaults
    st.session_state.uploaded_files = []
    # clear file input if present
    if "file_input" in st.session_state:
        del st.session_state["file_input"]
    st.session_state.processing = False
    st.session_state.results_ready = False
    st.session_state.fact_check = False
    st.session_state.logical_fallacy_check = False
    st.session_state.ai_generation_check = False
    go_to("app")

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
    st.markdown("# 🔎 TruthLens")
    st.subheader("Quickly surface factual evidence, fallacies, and AI-generation signals")

    # Sidebar: settings (with help text)
    st.sidebar.header("Settings")
    st.sidebar.write("Select which checks to run on uploaded content:")
    fact = st.sidebar.checkbox("Fact check", value=st.session_state.fact_check, key="fact_check", help="Find supporting and opposing sources for claims.")
    fallacy = st.sidebar.checkbox("Logical fallacy check", value=st.session_state.logical_fallacy_check, key="logical_fallacy_check", help="Detect common logical fallacies in statements.")
    ai_gen = st.sidebar.checkbox("AI generation check", value=st.session_state.ai_generation_check, key="ai_generation_check", help="Heuristic checks for AI-generated text (placeholder).")

    # Main area: file drop and upload
    st.subheader("Upload files")
    st.write("Drag and drop files below, then click Upload to send them for analysis.")
    uploaded = st.file_uploader("Drop files here", accept_multiple_files=True, key="file_input")

    # Do not auto-navigate on file selection; user should click Upload to proceed

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Upload", key="upload_btn"):
            files = st.session_state.get("file_input")
            if not files:
                st.warning("No files selected to upload.")
                st.session_state.uploaded_files = []
            else:
                st.session_state.uploaded_files = files
                # simulate processing backend: show progress bar then mark results ready
                st.session_state.processing = True
                st.session_state.results_ready = False
                progress = st.progress(0)
                for p in range(0, 101, 10):
                    progress.progress(p)
                    time.sleep(0.08)
                st.session_state.processing = False
                st.session_state.results_ready = True
                st.success(f"Analysis complete for {len(files)} file(s). Click 'Get Results' to view them.")
    with col2:
        if st.session_state.uploaded_files:
            st.markdown("**Uploaded files:**")
            for f in st.session_state.uploaded_files:
                st.markdown(f"{_file_icon(f.name)}  **{f.name}**  — {round(getattr(f, 'size', 0)/1024,1) if hasattr(f, 'size') else ''} KB")
        else:
            st.info("No uploaded files yet.")

    # Get Results button: only active after processing completes
    st.markdown("---")
    if st.session_state.get("results_ready"):
        st.info("Results are ready — click the button to view detailed analysis.")
        st.button("Get Results", key="get_results", on_click=go_to, args=("results",))
    else:
        if st.session_state.get("processing"):
            st.info("Analysis in progress — please wait...")
        else:
            st.info("Click Upload to start analysis. 'Get Results' will appear when ready.")

    # show active settings summary
    st.markdown("---")
    st.write("**Active checks:**",
             f"Fact check: {st.session_state.fact_check}",
             f"| Logical fallacy: {st.session_state.logical_fallacy_check}",
             f"| AI generation: {st.session_state.ai_generation_check}")

    st.button("← Back to Landing", key="back_btn", on_click=go_to, args=("landing",))
    


def render_results():
    st.header("Results — TruthLens Analysis")

    # show settings in the sidebar on the results page as well
    st.sidebar.header("Settings")
    st.sidebar.write("Choose which checks to run on uploaded content:")
    st.sidebar.checkbox("Fact check", value=st.session_state.fact_check, key="fact_check")
    st.sidebar.checkbox("Logical fallacy check", value=st.session_state.logical_fallacy_check, key="logical_fallacy_check")
    st.sidebar.checkbox("AI generation check", value=st.session_state.ai_generation_check, key="ai_generation_check")

    # show which checks were active when upload occurred
    st.subheader("Active checks for this run")
    st.write(
        f"Fact check: {st.session_state.fact_check}",
        f"| Logical fallacy check: {st.session_state.logical_fallacy_check}",
        f"| AI generation check: {st.session_state.ai_generation_check}",
    )

    files = st.session_state.get("uploaded_files", [])
    if not files:
        st.info("No files uploaded — return to the app and upload files first.")
        if st.button("← Back to App", key="results_back"):
            go_to("app")
        return

    for idx, f in enumerate(files, start=1):
        st.markdown(f"### File {idx}: {f.name}")

        # Logical fallacies section (shown only if enabled)
        if st.session_state.get("logical_fallacy_check", False):
            st.subheader("Logical Fallacies")
            with st.expander("View detected logical fallacies", expanded=False):
                st.write("No fallacies detected in this placeholder analysis.")
                st.write("Example:")
                st.write("- Name: Strawman")
                st.write("  - Statement: 'They want to ban all books' — excerpt where fallacy appears")

        # Fact checks section (shown only if enabled)
        if st.session_state.get("fact_check", False):
            st.subheader("Fact Checks")
            with st.expander("View fact-check results", expanded=True):
                st.write("Statements checked and linked sources:")
                st.markdown("**Statement:** The city reduced crime by 40% last year")
                with st.expander("Sources (for / against)"):
                    st.markdown("- For: [Local Police Report](https://example.com/for)")
                    st.markdown("- Against: [Independent Analysis](https://example.com/against)")

        # AI generation check (shown only if enabled)
        if st.session_state.get("ai_generation_check", False):
            st.subheader("AI Generation Check")
            with st.expander("AI detection explanation", expanded=False):
                st.write(
                    "Placeholder explanation: heuristics indicate low likelihood of AI generation. "
                    "A physics-based backend will provide detailed rationale later."
                )

        # If no checks enabled, inform the user
        if not any([
            st.session_state.get("logical_fallacy_check", False),
            st.session_state.get("fact_check", False),
            st.session_state.get("ai_generation_check", False),
        ]):
            st.info("No checks selected in Settings — return to the app to enable checks.")

        st.markdown("---")

    st.button("← Back to App (clear)", key="results_back_bottom", on_click=reset_and_return_to_app)

def main():
    page = get_page_from_state()
    if page == "landing":
        render_landing()
    elif page == "app":
        render_app()
    elif page == "results":
        render_results()
    else:
        render_app()

if __name__ == "__main__":
    main()