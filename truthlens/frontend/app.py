import streamlit as st
import time
import httpx

st.set_page_config(page_title="TruthLens", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")

# Backend API URL (override via env or Streamlit config)
BACKEND_URL = "http://localhost:8000"

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
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None


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
    st.session_state.uploaded_files = []
    st.session_state.analysis_result = None
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
    st.write("Drag and drop text-based files (TXT, PDF, DOCX, MD, HTML), then click Upload for analysis.")
    uploaded = st.file_uploader(
        "Drop files here",
        accept_multiple_files=True,
        type=["txt", "md", "pdf", "docx", "doc", "html", "htm"],
        key="file_input",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Upload", key="upload_btn"):
            files = st.session_state.get("file_input")
            if not files:
                st.warning("No files selected to upload.")
                st.session_state.uploaded_files = []
                st.session_state.analysis_result = None
            else:
                st.session_state.uploaded_files = files
                st.session_state.processing = True
                st.session_state.results_ready = False
                st.session_state.analysis_result = None
                progress = st.progress(0)
                try:
                    with httpx.Client(timeout=60.0) as client:
                        files_data = [("files", (f.name, f.getvalue(), f.type or "application/octet-stream")) for f in files]
                        data = {
                            "fact_check": st.session_state.fact_check,
                            "logical_fallacy_check": st.session_state.logical_fallacy_check,
                            "ai_generation_check": st.session_state.ai_generation_check,
                        }
                        resp = client.post(
                            f"{BACKEND_URL}/api/analyze",
                            files=files_data,
                            data=data,
                        )
                    progress.progress(100)
                    if resp.status_code == 200:
                        st.session_state.analysis_result = resp.json()
                        st.session_state.results_ready = True
                        st.success(f"Analysis complete for {len(files)} file(s). Click 'Get Results' to view them.")
                    else:
                        err = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                        st.error(err.get("error", f"Backend error: {resp.status_code}"))
                except httpx.ConnectError:
                    st.error("Could not reach backend. Is FastAPI running on port 8000?")
                except Exception as e:
                    st.error(f"Upload failed: {e}")
                finally:
                    st.session_state.processing = False
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

    st.sidebar.header("Settings")
    st.sidebar.checkbox("Fact check", value=st.session_state.fact_check, key="fact_check")
    st.sidebar.checkbox("Logical fallacy check", value=st.session_state.logical_fallacy_check, key="logical_fallacy_check")
    st.sidebar.checkbox("AI generation check", value=st.session_state.ai_generation_check, key="ai_generation_check")

    analysis = st.session_state.get("analysis_result")
    files = st.session_state.get("uploaded_files", [])

    if not files and not analysis:
        st.info("No files uploaded — return to the app and upload files first.")
        if st.button("← Back to App", key="results_back"):
            go_to("app")
        return

    # Overall credibility score
    if analysis and "breakdown" in analysis:
        b = analysis["breakdown"]
        score = b.get("overall_credibility_score")
        if score is not None:
            pct = int(round(score * 100))
            st.metric("Truth percentage", f"{pct}%", help="Overall credibility from fact-check and fallacy analysis")

    # File summary
    if analysis and "files" in analysis:
        for fr in analysis["files"]:
            name = fr.get("name", "?")
            if fr.get("skipped"):
                st.caption(f"{name} — skipped: {fr.get('reason', 'unknown')}")
            else:
                st.caption(f"{name} — {fr.get('chars', 0)} chars extracted")

    # Logical fallacies
    if st.session_state.get("logical_fallacy_check") and analysis:
        fallacies = analysis.get("fallacies", [])
        st.subheader("Logical Fallacies")
        with st.expander(f"View detected logical fallacies ({len(fallacies)} found)", expanded=bool(fallacies)):
            if not fallacies:
                st.write("No fallacies detected in the uploaded content.")
            else:
                for f in fallacies:
                    st.markdown(f"**{f.get('name', '?')}** (severity: {f.get('severity', 0):.2f})")
                    st.write(f"Statement: \"{f.get('statement', '')}\"")
                    if f.get("context_excerpt"):
                        st.caption(f"Context: {f['context_excerpt'][:150]}...")
                    st.markdown("---")

    # Fact checks
    if st.session_state.get("fact_check") and analysis:
        fact_checks = analysis.get("fact_checks", [])
        st.subheader("Fact Checks")
        with st.expander(f"View fact-check results ({len(fact_checks)} claims)", expanded=bool(fact_checks)):
            if not fact_checks:
                st.write("No factual claims extracted for checking.")
            else:
                for fc in fact_checks:
                    score = fc.get("score", 0.5)
                    stmt = fc.get("statement", "")
                    st.markdown(f"**Statement:** {stmt[:300] + ('...' if len(stmt) > 300 else '')}")
                    st.write(f"Confidence: {int(score * 100)}%")
                    if fc.get("note"):
                        st.caption(fc["note"])
                    for s in fc.get("sources_for", [])[:3]:
                        st.markdown(f"- For: [{s.get('title', 'Link')}]({s.get('url', '#')})")
                    for s in fc.get("sources_against", [])[:3]:
                        st.markdown(f"- Against: [{s.get('title', 'Link')}]({s.get('url', '#')})")
                    st.markdown("---")

    # AI generation (placeholder)
    if st.session_state.get("ai_generation_check") and analysis:
        ai = analysis.get("ai_check", {})
        st.subheader("AI Generation Check")
        with st.expander("AI detection", expanded=False):
            st.write(ai.get("explanation", "Not available for text-only analysis."))

    if not any([st.session_state.get("logical_fallacy_check"), st.session_state.get("fact_check"), st.session_state.get("ai_generation_check")]):
        st.info("No checks were selected. Return to the app to enable fact-check or logical fallacy check.")

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