# 🗂️ File Vault — Streamlit File Manager

A clean, single-page **Streamlit** UI for basic file operations — create, read, update (rename / append / overwrite), and delete — built on top of a simple Python `Path`/`os` file-handling script.

## ✨ Features

- 📁 **Browse** — see every file in the vault with size, last-modified time, and one-click download
- 📝 **Create** — write new files with custom content
- 📖 **Read** — preview any file's contents in the browser
- ✏️ **Update** — rename, append to, or overwrite a file
- 🗑️ **Delete** — remove a file with a confirmation step
- All files are sandboxed inside a local `storage/` folder

## 🚀 Getting started

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/file-vault.git
cd file-vault

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

## 🧱 Tech stack

- [Streamlit](https://streamlit.io/) for the UI
- Python's built-in `pathlib` / `os` for file operations — no external file-handling libraries

## 📸 Screenshots

*(Add a screenshot or GIF of the app here before posting to GitHub/LinkedIn!)*

## 📄 License

MIT
