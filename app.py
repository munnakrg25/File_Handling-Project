"""
File Vault — A Streamlit UI for basic file CRUD operations.

Wraps create / read / update / delete file logic (originally a CLI script)
in a clean, single-page Streamlit app. All files live inside the local
`storage/` folder so the app can't accidentally touch anything outside it.

Run with:
    streamlit run app.py
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

import streamlit as st

# --------------------------------------------------------------------------
# Config & constants
# --------------------------------------------------------------------------
STORAGE_DIR = Path(__file__).parent / "storage"
STORAGE_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="File Vault",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp { background-color: #0e1117; }
        .file-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 10px;
        }
        .file-card:hover { border-color: #58a6ff; }
        .file-name { font-weight: 600; font-size: 1.02rem; color: #e6edf3; }
        .file-meta { color: #8b949e; font-size: 0.82rem; }
        div[data-testid="stMetric"] {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 10px 4px;
        }
        h1, h2, h3 { letter-spacing: -0.02em; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def safe_path(name: str) -> Path:
    """Resolve a user-supplied filename inside STORAGE_DIR, blocking traversal."""
    candidate = (STORAGE_DIR / name).resolve()
    if STORAGE_DIR.resolve() not in candidate.parents and candidate != STORAGE_DIR.resolve():
        raise ValueError("Invalid file name.")
    return candidate


def list_files():
    return sorted([p for p in STORAGE_DIR.iterdir() if p.is_file()], key=lambda p: p.name.lower())


def human_size(num_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.0f} {unit}" if unit == "B" else f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def toast(msg: str, icon: str = "✅"):
    st.session_state["_flash"] = (msg, icon)


# --------------------------------------------------------------------------
# Sidebar — navigation
# --------------------------------------------------------------------------
st.sidebar.title("🗂️ File Vault")
st.sidebar.caption("A simple file manager built with Streamlit")

page = st.sidebar.radio(
    "Operation",
    ["📁 Browse", "📝 Create", "📖 Read", "✏️ Update", "🗑️ Delete"],
    label_visibility="collapsed",
)

files = list_files()
st.sidebar.divider()
c1, c2 = st.sidebar.columns(2)
c1.metric("Files", len(files))
c2.metric("Total size", human_size(sum(f.stat().st_size for f in files)))
st.sidebar.caption(f"Storage folder: `{STORAGE_DIR.name}/`")

if "_flash" in st.session_state:
    msg, icon = st.session_state.pop("_flash")
    st.toast(msg, icon=icon)

# --------------------------------------------------------------------------
# Page: Browse
# --------------------------------------------------------------------------
if page == "📁 Browse":
    st.title("📁 Browse files")
    st.caption("Everything currently stored in the vault.")

    if not files:
        st.info("No files yet — head to **Create** to add your first one.")
    else:
        for f in files:
            stat = f.stat()
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%b %d, %Y · %H:%M")
            col1, col2, col3 = st.columns([5, 2, 2])
            with col1:
                st.markdown(
                    f"<div class='file-card'><span class='file-name'>📄 {f.name}</span><br>"
                    f"<span class='file-meta'>{human_size(stat.st_size)} · modified {modified}</span></div>",
                    unsafe_allow_html=True,
                )
            with col2:
                st.download_button(
                    "⬇️ Download", data=f.read_bytes(), file_name=f.name, key=f"dl_{f.name}"
                )
            with col3:
                if st.button("🗑️ Delete", key=f"del_{f.name}"):
                    f.unlink()
                    toast(f"Deleted {f.name}", "🗑️")
                    st.rerun()

# --------------------------------------------------------------------------
# Page: Create
# --------------------------------------------------------------------------
elif page == "📝 Create":
    st.title("📝 Create a new file")

    with st.form("create_form", clear_on_submit=True):
        name = st.text_input("File name", placeholder="notes.txt")
        data = st.text_area("File content", placeholder="Type what you want to save…", height=200)
        submitted = st.form_submit_button("Create file", type="primary", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Please enter a file name.")
        else:
            try:
                path = safe_path(name.strip())
                if path.exists():
                    st.warning(f"⚠️ **{name}** already exists. Pick a different name or use Update instead.")
                else:
                    path.write_text(data)
                    toast(f"Created {name}", "✅")
                    st.success(f"File **{name}** created successfully.")
            except Exception as err:
                st.error(f"Error: {err}")

# --------------------------------------------------------------------------
# Page: Read
# --------------------------------------------------------------------------
elif page == "📖 Read":
    st.title("📖 Read a file")

    if not files:
        st.info("No files yet — head to **Create** to add your first one.")
    else:
        choice = st.selectbox("Choose a file", [f.name for f in files])
        if choice:
            path = safe_path(choice)
            try:
                content = path.read_text()
                st.code(content or "(file is empty)", language=None)
                st.download_button("⬇️ Download this file", data=content, file_name=choice)
            except UnicodeDecodeError:
                st.warning("This file isn't plain text — can't preview it here.")
            except Exception as err:
                st.error(f"Error: {err}")

# --------------------------------------------------------------------------
# Page: Update
# --------------------------------------------------------------------------
elif page == "✏️ Update":
    st.title("✏️ Update a file")

    if not files:
        st.info("No files yet — head to **Create** to add your first one.")
    else:
        choice = st.selectbox("Choose a file", [f.name for f in files])
        action = st.radio("What do you want to do?", ["Rename", "Append text", "Overwrite content"], horizontal=True)
        path = safe_path(choice)

        if action == "Rename":
            new_name = st.text_input("New file name", value=choice)
            if st.button("Rename", type="primary"):
                try:
                    new_path = safe_path(new_name.strip())
                    if new_path.exists():
                        st.warning("A file with that name already exists.")
                    else:
                        path.rename(new_path)
                        toast("File renamed", "✏️")
                        st.success(f"Renamed **{choice}** → **{new_name}**")
                        st.rerun()
                except Exception as err:
                    st.error(f"Error: {err}")

        elif action == "Append text":
            extra = st.text_area("Text to append", height=150)
            if st.button("Append", type="primary"):
                try:
                    with open(path, "a") as fs:
                        fs.write("\n" + extra)
                    toast("Text appended", "➕")
                    st.success(f"Appended to **{choice}**")
                except Exception as err:
                    st.error(f"Error: {err}")

        elif action == "Overwrite content":
            current = path.read_text() if path.exists() else ""
            new_content = st.text_area("New content (replaces everything)", value=current, height=200)
            if st.button("Overwrite", type="primary"):
                try:
                    path.write_text(new_content)
                    toast("File overwritten", "♻️")
                    st.success(f"Overwrote **{choice}**")
                except Exception as err:
                    st.error(f"Error: {err}")

# --------------------------------------------------------------------------
# Page: Delete
# --------------------------------------------------------------------------
elif page == "🗑️ Delete":
    st.title("🗑️ Delete a file")

    if not files:
        st.info("No files yet — nothing to delete.")
    else:
        choice = st.selectbox("Choose a file to delete", [f.name for f in files])
        st.warning("This action can't be undone.")
        confirm = st.checkbox(f"Yes, I'm sure I want to delete **{choice}**")
        if st.button("Delete permanently", type="primary", disabled=not confirm):
            try:
                safe_path(choice).unlink()
                toast(f"Deleted {choice}", "🗑️")
                st.success(f"Deleted **{choice}**")
                st.rerun()
            except Exception as err:
                st.error(f"Error: {err}")