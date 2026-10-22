import os
import sys
import sqlite3
import uuid
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from core.memory import ChatMemory
from core.pipeline import attach_document, handle
from modules.ocr import extract_text_from_image

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "chat_history.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    conn.execute("CREATE TABLE IF NOT EXISTS conversations (session_id TEXT PRIMARY KEY, title TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    return conn


def get_conversations():
    with db() as conn:
        return conn.execute("SELECT session_id, title, updated_at FROM conversations ORDER BY updated_at DESC LIMIT 50").fetchall()


def load_log(session_id):
    with db() as conn:
        return conn.execute("SELECT role, content FROM messages WHERE session_id=? ORDER BY id", (session_id,)).fetchall()


def save_message(session_id, role, content, title=None):
    with db() as conn:
        conn.execute("INSERT INTO messages(session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
        if title:
            conn.execute("INSERT INTO conversations(session_id,title) VALUES (?,?) ON CONFLICT(session_id) DO UPDATE SET title=excluded.title, updated_at=CURRENT_TIMESTAMP", (session_id, title[:70]))
        else:
            conn.execute("INSERT INTO conversations(session_id,title) VALUES (?,?) ON CONFLICT(session_id) DO UPDATE SET updated_at=CURRENT_TIMESTAMP", (session_id, "New conversation"))
        conn.commit()


st.set_page_config(page_title="Multimodal Chatbot", page_icon="🤖")
st.title("🤖 Multimodal AI Chatbot")
st.caption("Chat · Code · Summarize · Translate · Image OCR · Document reader")

# Feature selector: these modes guide the request while preserving the existing pipeline.
FEATURES = {
    "💬 Chat": "Answer the user clearly and helpfully.",
    "💻 Code": "Focus on programming. Provide correct code, explain where to place it, and include run commands when useful.",
    "📝 Summarize": "Summarize the user's provided content clearly, preserving the key points.",
    "🌐 Translate": "Translate the user's provided text. If no target language is specified, ask which language they want.",
    "🔎 Image OCR": "Extract and accurately reproduce visible text from the uploaded image. Do not guess unclear words.",
    "📄 Documents": "Answer using the uploaded document when available. Summarize or quote relevant sections as requested.",
    "🖼️ Image AI": "Analyze the uploaded image and answer questions about visible objects, scene, and context.",
    "📊 Data Analysis": "Analyze provided data, explain patterns, and show calculations or tables where useful.",
}
if "selected_feature" not in st.session_state:
    st.session_state.selected_feature = "💬 Chat"

with st.container(border=True):
    st.markdown("**Choose a feature**")
    feature_names = list(FEATURES.keys())
    feature_rows = [feature_names[:4], feature_names[4:]]
    for row in feature_rows:
        cols = st.columns(4)
        for col, feature in zip(cols, row):
            with col:
                if st.button(
                    feature,
                    key="feature_" + feature,
                    type="primary" if st.session_state.selected_feature == feature else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.selected_feature = feature
                    st.rerun()
    st.caption("Selected: " + st.session_state.selected_feature)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.memory = ChatMemory()
    st.session_state.log = []
    st.session_state.doc_key = None
    st.session_state.loaded_session = st.session_state.session_id

# Sidebar conversation history
with st.sidebar:
    st.subheader("Chat history")
    conversations = get_conversations()
    options = {f"{title} · {updated[:16]}": sid for sid, title, updated in conversations}
    labels = list(options.keys())
    selected_label = st.selectbox("Previous conversations", ["Current conversation"] + labels, key="history_picker")
    if selected_label != "Current conversation":
        selected_id = options[selected_label]
        if selected_id != st.session_state.session_id:
            st.session_state.session_id = selected_id
            st.session_state.log = load_log(selected_id)
            st.session_state.memory = ChatMemory()
            # Restore text context for subsequent turns.
            for role, content in st.session_state.log:
                if role in ("user", "assistant"):
                    st.session_state.memory.add(role, content)
            st.session_state.doc_key = None
            st.session_state.loaded_session = selected_id
            st.rerun()
    if st.button("＋ New conversation", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.memory = ChatMemory()
        st.session_state.log = []
        st.session_state.doc_key = None
        st.session_state.loaded_session = st.session_state.session_id
        st.rerun()

    uploaded = st.file_uploader("Image (optional)", type=["png", "jpg", "jpeg", "webp"])
    if uploaded:
        st.image(uploaded)
        if st.button("Extract text (OCR)", use_container_width=True):
            with st.spinner("Extracting text with local OCR..."):
                try:
                    st.session_state["ocr_result"] = extract_text_from_image(uploaded)
                except Exception as exc:
                    st.session_state["ocr_error"] = str(exc)
                    st.session_state.pop("ocr_result", None)
        if st.session_state.get("ocr_error"):
            st.error(st.session_state.pop("ocr_error"))
        if st.session_state.get("ocr_result") is not None:
            st.text_area("Extracted text (OCR)", st.session_state["ocr_result"], height=180)
            if st.session_state["ocr_result"]:
                st.download_button(
                    "Download OCR text",
                    data=st.session_state["ocr_result"],
                    file_name="extracted_text.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
    doc_file = st.file_uploader("Document (PDF / DOCX / TXT)", type=["pdf", "docx", "txt", "md"])
    if doc_file and st.session_state.doc_key != (doc_file.name, doc_file.size):
        with st.spinner("Reading document..."):
            try:
                info = attach_document(st.session_state.memory, doc_file.getvalue(), doc_file.name)
                st.session_state.doc_key = (doc_file.name, doc_file.size)
                notice = f"📄 Loaded {info['name']} ({info['pages']} pages). Ask me questions about it, or say summarize."
                st.session_state.log.append(("assistant", notice))
                save_message(st.session_state.session_id, "assistant", notice, title=f"Document: {doc_file.name}")
            except Exception as e:
                st.error(f"Could not read document: {e}")
    if st.session_state.memory.document:
        st.success(f"📄 Active: {st.session_state.memory.document.name}")
        if st.button("Remove document"):
            st.session_state.memory.document = None
            st.session_state.doc_key = None
            st.rerun()

for role, content in st.session_state.log:
    st.chat_message(role).markdown(content)

if prompt := st.chat_input("Ask, request code, summarize, translate, or question your document..."):
    st.chat_message("user").markdown(prompt)
    selected_feature = st.session_state.get("selected_feature", "💬 Chat")
    feature_instruction = FEATURES.get(selected_feature, "")
    routed_prompt = prompt if selected_feature == "💬 Chat" else (
        f"Selected mode: {selected_feature}. Instruction: {feature_instruction}\n\nUser request: {prompt}"
    )
    with st.spinner("Thinking..."):
        try:
            res = handle(routed_prompt, st.session_state.memory, uploaded.getvalue() if uploaded else None)
            answer = f"*Mode: {res['task']}*\n\n{res['answer']}"
            if res.get("pages_used"):
                answer += f"\n\n*Pages used: {', '.join(map(str, res['pages_used']))}*"
        except Exception as e:
            res, answer = {}, f"**Error:** {e}\n\nCheck that Ollama is running and the configured model is installed."
    st.chat_message("assistant").markdown(answer)
    if res.get("ocr_text") is not None:
        with st.expander("Extracted text (OCR) - check for mistakes"):
            st.text(res["ocr_text"] or "No text detected. Check OCR installation and image quality.")
    st.session_state.log += [("user", prompt), ("assistant", answer)]
    title = prompt if len(st.session_state.log) <= 2 else None
    save_message(st.session_state.session_id, "user", prompt, title=title)
    save_message(st.session_state.session_id, "assistant", answer)
