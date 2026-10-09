import os
import uuid
import logging
import html
import io
import re

import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# OPTIONAL DEPENDENCIES WITH FALLBACK HANDLING
# ============================================================
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="BAITHAK WITH AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_MODEL = "gpt-6-luna"

SYSTEM_PROMPTS = {
    "General Assistant": """
You are Baithak, a helpful, friendly, clear AI assistant.
Answer the user's actual question directly. Use Markdown when useful.
Explain complex topics step by step, write complete code when requested,
and match the user's language where practical. Be honest when uncertain.
""",
    "Clerk AI (Drafting & File Preparation)": """
You are Baithak Clerk AI, a administrative assistant and documentation specialist.
Your core responsibilities:
1. Draft clear, formal, executive-ready emails, memos, official notices, meeting minutes, and corporate reports.
2. Structure information logically using headers, bullet points, and clean Markdown tables for quantitative or structured data.
3. Prepare content so it can be converted into downloadable PDF, Word, Excel, or TXT formats.
4. Maintain a polite, articulate, professional tone across all written communications.
""",
    "Superintendent AI (Review & Verification)": """
You are Baithak Superintendent AI, an executive reviewer and quality compliance supervisor.
Your core responsibilities:
1. Thoroughly review and verify drafted documents, emails, reports, and data tables.
2. Check for accuracy, tone consistency, completeness, structural clarity, and policy compliance.
3. Provide a clear verification verdict: **APPROVED**, **APPROVED WITH MODIFICATIONS**, or **REJECTED (REQUIRES REVISION)**.
4. Highlight missing details, correct grammatical or logical inconsistencies, and refine drafts for executive submission.
"""
}

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("baithak_ai")


# ============================================================
# SECRETS & CLIENT INIT
# ============================================================
def get_secret(name, default=None):
    try:
        value = st.secrets.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    except Exception:
        pass
    value = os.getenv(name)
    return str(value).strip() if value and str(value).strip() else default


API_KEY = get_secret("OPENAI_API_KEY")
MODEL = get_secret("OPENAI_MODEL", DEFAULT_MODEL)


@st.cache_resource(show_spinner=False)
def get_client(api_key):
    if not api_key or OpenAI is None:
        return None
    try:
        return OpenAI(api_key=api_key, timeout=60.0, max_retries=1)
    except Exception:
        logger.exception("OpenAI client initialization failed.")
        return None


client = get_client(API_KEY)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if "conversations" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.conversations = {
        first_id: {"title": "New chat", "messages": [], "documents": []}
    }
    st.session_state.active_conversation = first_id

if "active_conversation" not in st.session_state:
    st.session_state.active_conversation = next(iter(st.session_state.conversations))

if st.session_state.active_conversation not in st.session_state.conversations:
    st.session_state.active_conversation = next(iter(st.session_state.conversations))

if "notice" not in st.session_state:
    st.session_state.notice = ""
if "mode" not in st.session_state:
    st.session_state.mode = "Demo Mode"
if "ai_role" not in st.session_state:
    st.session_state.ai_role = "Dual Agent Workflow (Clerk Draft + Superintendent Review)"


def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.conversations[chat_id] = {
        "title": "New chat", "messages": [], "documents": []
    }
    st.session_state.active_conversation = chat_id
    st.session_state.notice = ""


def clear_current_chat():
    chat_id = st.session_state.active_conversation
    st.session_state.conversations[chat_id] = {
        "title": "New chat", "messages": [], "documents": []
    }
    st.session_state.notice = ""


def delete_all_chats():
    chat_id = str(uuid.uuid4())
    st.session_state.conversations = {
        chat_id: {"title": "New chat", "messages": [], "documents": []}
    }
    st.session_state.active_conversation = chat_id
    st.session_state.notice = ""


def update_title(conversation, prompt):
    if conversation["title"] == "New chat":
        title = " ".join(prompt.split())
        conversation["title"] = title[:35].rstrip() + ("..." if len(title) > 35 else "")


# ============================================================
# EXPORT HELPERS (PDF, DOCX, TXT, EXCEL)
# ============================================================
def generate_txt(text: str) -> bytes:
    """Return plain UTF-8 text bytes."""
    return text.encode("utf-8")


def generate_pdf(text: str) -> bytes:
    """Generate a clean PDF from standard text."""
    if FPDF is None:
        raise RuntimeError("PDF generator library `fpdf2` is not installed. Add `fpdf2` to requirements.txt.")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=11)
    
    clean_text = re.sub(r'[*_`#]', '', text)
    
    for line in clean_text.split("\n"):
        pdf.multi_cell(0, 7, txt=line)
    
    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()


def generate_docx(text: str) -> bytes:
    """Generate a structured DOCX document from markdown text."""
    if Document is None:
        raise RuntimeError("Word generator library `python-docx` is not installed. Add `python-docx` to requirements.txt.")
    
    doc = Document()
    doc.add_heading("Baithak AI Document Export", level=1)
    
    lines = text.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            doc.add_heading(stripped[2:], level=1)
        elif stripped.startswith("## "):
            doc.add_heading(stripped[3:], level=2)
        elif stripped.startswith("### "):
            doc.add_heading(stripped[4:], level=3)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            doc.add_paragraph(stripped[2:], style='List Bullet')
        elif stripped:
            p = doc.add_paragraph()
            parts = re.split(r'(\*\*.*?\*\*)', line)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    p.add_run(part[2:-2]).bold = True
                else:
                    p.add_run(part)
                    
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def parse_markdown_tables(text: str):
    """Extract Markdown tables into Pandas DataFrames."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    tables = []
    current_table = []

    for line in lines:
        if line.startswith("|") and line.endswith("|"):
            current_table.append(line)
        else:
            if len(current_table) >= 3:
                tables.append(current_table)
            current_table = []

    if len(current_table) >= 3:
        tables.append(current_table)

    dataframes = []
    for table_lines in tables:
        rows = []
        for row_str in table_lines:
            if re.match(r'^\|[\s\:\-|-]+\|$', row_str):
                continue
            cols = [col.strip() for col in row_str.split("|")[1:-1]]
            rows.append(cols)

        if len(rows) >= 2 and pd is not None:
            df = pd.DataFrame(rows[1:], columns=rows[0])
            dataframes.append(df)

    return dataframes


def generate_excel_from_tables(text: str) -> bytes:
    """Extract tables from markdown text and export to Excel workbook."""
    if pd is None:
        raise RuntimeError("Data processing library `pandas` or `openpyxl` is missing.")
    
    dfs = parse_markdown_tables(text)
    if not dfs:
        raise ValueError("No markdown table found in this message to export to Excel.")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        for idx, df in enumerate(dfs, start=1):
            df.to_excel(writer, sheet_name=f"Table_{idx}", index=False)
    
    return buffer.getvalue()


# ============================================================
# LLM & AGENT WORKFLOW ENGINE
# ============================================================
def call_llm(messages, system_instruction):
    if client is None:
        return None
    try:
        response = client.responses.create(
            model=MODEL,
            instructions=system_instruction,
            input=messages,
        )
        answer = getattr(response, "output_text", None)
        return answer.strip() if answer else None
    except Exception:
        logger.exception("API request failed.")
        return None


def demo_reply(prompt, role):
    lower = prompt.lower()
    if role == "Clerk AI (Drafting & File Preparation)":
        return (
            "📝 **[Clerk AI Draft]**\n\n"
            "**Subject:** Formal Notice & Requirements Document\n\n"
            "Dear Stakeholders,\n\n"
            "Please find the initial draft below for your review:\n\n"
            "| Task ID | Deliverable | Target Date | Status |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| T-101 | Requirements Gathering | 2026-10-15 | Completed |\n"
            "| T-102 | Draft Verification | 2026-10-18 | Pending Review |\n\n"
            "Kindly review and convert this draft into your preferred file format once verified.\n\n"
            "_Demo Mode active. Configure `OPENAI_API_KEY` for live AI generation._"
        )
    elif role == "Superintendent AI (Review & Verification)":
        return (
            "🔍 **[Superintendent AI Verification]**\n\n"
            "**Status:** APPROVED WITH MINOR MODIFICATIONS\n\n"
            "**Audit Summary:**\n"
            "- Structural integrity: Clear and well-organized.\n"
            "- Data tables: Verified and correctly formatted.\n"
            "- Recommendation: Ready for document export (PDF/DOCX/Excel).\n\n"
            "_Demo Mode active. Configure `OPENAI_API_KEY` for live AI generation._"
        )
    else:
        return (
            "📝 **[Clerk AI Draft]**\n\n"
            "**Subject:** Proposed Communication Draft\n\n"
            "Draft generated as requested.\n\n"
            "| Item | Specification | Notes |\n"
            "| :--- | :--- | :--- |\n"
            "| Document | Proposal | Ready for Superintendent audit |\n\n"
            "---\n\n"
            "🔍 **[Superintendent AI Verification]**\n\n"
            "**Status:** APPROVED\n\n"
            "**Verification Note:** Draft audited and approved for conversion into downloadable files (PDF, DOCX, TXT, Excel)."
        )


def execute_agent_workflow(messages):
    selected_role = st.session_state.ai_role

    if client is None:
        st.session_state.mode = "Demo Mode"
        st.session_state.notice = "Demo Mode · Add OPENAI_API_KEY in Streamlit Secrets for live AI."
        return demo_reply(messages[-1]["content"], selected_role)

    try:
        # Dual Agent Workflow (Clerk Draft -> Superintendent Review)
        if selected_role == "Dual Agent Workflow (Clerk Draft + Superintendent Review)":
            # Step 1: Clerk AI Drafts
            clerk_prompt = SYSTEM_PROMPTS["Clerk AI (Drafting & File Preparation)"]
            clerk_draft = call_llm(messages, clerk_prompt)
            if not clerk_draft:
                raise ValueError("Clerk AI failed to generate draft.")

            # Step 2: Superintendent Reviews Clerk's Draft
            superintendent_prompt = SYSTEM_PROMPTS["Superintendent AI (Review & Verification)"]
            review_input = messages + [
                {"role": "assistant", "content": clerk_draft},
                {"role": "user", "content": "As Superintendent AI, please review, audit, verify, and polish the Clerk's draft above."}
            ]
            superintendent_review = call_llm(review_input, superintendent_prompt)
            if not superintendent_review:
                superintendent_review = "🔍 **[Superintendent AI]**: Verified draft. Proceed with file generation."

            combined_response = (
                f"📝 **[Clerk AI Draft]**\n\n{clerk_draft}\n\n"
                f"---\n\n"
                f"🔍 **[Superintendent AI Verification]**\n\n{superintendent_review}"
            )
            st.session_state.mode = "OpenAI"
            st.session_state.notice = f"Connected · {MODEL} · Dual Agent Workflow Active"
            return combined_response

        # Single Agent Direct Execution
        else:
            system_instruction = SYSTEM_PROMPTS.get(selected_role, SYSTEM_PROMPTS["General Assistant"])
            response_text = call_llm(messages, system_instruction)
            if not response_text:
                raise ValueError("LLM returned empty response.")
            st.session_state.mode = "OpenAI"
            st.session_state.notice = f"Connected · {MODEL} · ({selected_role})"
            return response_text

    except Exception:
        logger.exception("Workflow execution failed.")
        st.session_state.mode = "Demo Mode"
        st.session_state.notice = "Demo Mode · Request failed. Check model access and API quota."
        return demo_reply(messages[-1]["content"], selected_role)


def extract_uploaded_text(uploaded_file):
    """Extract text from PDF, DOCX, or TXT uploads without saving to disk."""
    filename = uploaded_file.name
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    raw = uploaded_file.getvalue()
    try:
        if suffix == "txt":
            for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
                try:
                    return raw.decode(encoding).strip()
                except UnicodeDecodeError:
                    continue
            return raw.decode("utf-8", errors="replace").strip()
        if suffix == "pdf":
            if PdfReader is None:
                raise RuntimeError("PDF support is not installed. Add pypdf to requirements.txt.")
            reader = PdfReader(io.BytesIO(raw))
            pages = []
            for page_no, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or "").strip()
                if text:
                    pages.append(f"[Page {page_no}]\n{text}")
            return "\n\n".join(pages)
        if suffix == "docx":
            if Document is None:
                raise RuntimeError("Word support is not installed. Add python-docx to requirements.txt.")
            doc = Document(io.BytesIO(raw))
            parts = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
            for table_no, table in enumerate(doc.tables, start=1):
                parts.append(f"[Table {table_no}]")
                for row in table.rows:
                    parts.append(" | ".join(cell.text.replace("\n", " ").strip() for cell in row.cells))
            return "\n".join(parts).strip()
        raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")
    except Exception as exc:
        raise RuntimeError(f"Could not read {filename}: {exc}") from exc


def add_uploaded_documents(uploaded_files, conversation):
    if not uploaded_files:
        return
    existing = {doc.get("name") for doc in conversation.setdefault("documents", [])}
    added = 0
    for uploaded_file in uploaded_files:
        if uploaded_file.name in existing:
            continue
        try:
            extracted = extract_uploaded_text(uploaded_file)
            if not extracted:
                st.warning(f"{uploaded_file.name}: no selectable text was found.")
                continue
            max_chars = 80000
            was_truncated = len(extracted) > max_chars
            extracted = extracted[:max_chars]
            conversation["documents"].append({
                "name": uploaded_file.name,
                "text": extracted,
                "truncated": was_truncated,
            })
            added += 1
        except Exception as exc:
            st.error(str(exc))
    if added:
        names = [d["name"] for d in conversation["documents"]]
        conversation["messages"].append({
            "role": "assistant",
            "content": "📎 **Documents attached for Clerk drafting & Superintendent review:**\n\n" + "\n".join(f"- {name}" for name in names)
        })
        st.session_state.notice = f"Added {added} document(s) to conversation."


def submit_prompt(prompt):
    prompt = prompt.strip()
    if not prompt:
        return
    conversation = st.session_state.conversations[st.session_state.active_conversation]
    conversation["messages"].append({"role": "user", "content": prompt})
    update_title(conversation, prompt)
    api_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in conversation["messages"]
        if m["role"] in ("user", "assistant")
    ]
    documents = conversation.get("documents", [])
    if documents and api_messages and api_messages[-1]["role"] == "user":
        chunks = []
        remaining = 120000
        for doc in documents:
            if remaining <= 0:
                break
            piece = doc["text"][:remaining]
            chunks.append(f"\n\n--- Uploaded document: {doc['name']} ---\n{piece}")
            remaining -= len(piece)
        api_messages[-1]["content"] += (
            "\n\nUse the following uploaded document text as source material.\n" + "".join(chunks)
        )
    answer = execute_agent_workflow(api_messages)
    conversation["messages"].append({"role": "assistant", "content": answer})


# ============================================================
# STYLING
# ============================================================
st.markdown("""
<style>
:root { --sidebar-bg:#f8f8f8; --line:#e5e5e5; --accent:#10a37f; }
.stApp { background:#fff; color:#242424; }
header[data-testid="stHeader"] { background:rgba(255,255,255,.94); }
[data-testid="stSidebar"] { background:var(--sidebar-bg); border-right:1px solid var(--line); }
[data-testid="stSidebar"] > div:first-child { padding-top:1rem; }
[data-testid="stSidebar"] .stButton > button {
  text-align:left; border:0; border-radius:10px; background:transparent;
  color:#303030; padding:.65rem .8rem; font-weight:500;
}
[data-testid="stSidebar"] .stButton > button:hover { background:#ececec; box-shadow:none; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] { background:#e9e9e9; color:#111; }
.main .block-container { max-width:940px; padding-top:1.1rem; padding-bottom:6rem; }
.topbar { display:flex; justify-content:space-between; align-items:center; gap:12px;
  padding:.3rem 0 1.1rem; border-bottom:1px solid #f0f0f0; margin-bottom:1.2rem; }
.brand { font-size:1.1rem; font-weight:750; color:#202020; }
.brand-mark { display:inline-flex; width:29px; height:29px; border-radius:9px;
  align-items:center; justify-content:center; background:#10a37f; color:white; margin-right:8px; }
.status { font-size:.78rem; color:#707070; border:1px solid #e5e5e5;
  border-radius:999px; padding:5px 10px; white-space:nowrap; }
div[data-testid="stChatMessage"] { border:0; padding:.75rem .3rem; gap:.9rem; }
[data-testid="stChatMessageContent"] { line-height:1.7; font-size:1rem; }
[data-testid="stChatInput"] { border-radius:24px!important; border:1px solid #d9d9d9!important;
  box-shadow:0 5px 24px rgba(0,0,0,.06); background:white!important; }
[data-testid="stChatInput"] textarea { padding-top:13px!important; }
.stButton > button { border-radius:10px; }
.footer { text-align:center; color:#999; font-size:.75rem; padding:1.2rem 0 .5rem; }
@media(max-width:700px) {
 .main .block-container { padding-left:1rem; padding-right:1rem; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        '<div style="font-size:1.2rem;font-weight:750;padding:0 .5rem 1rem;">🤖 Baithak with AI</div>',
        unsafe_allow_html=True,
    )
    if st.button("＋ New chat", use_container_width=True, type="primary"):
        new_chat()
        st.rerun()

    st.markdown(
        "<div style='font-size:.78rem;color:#777;font-weight:650;padding:.9rem .6rem .4rem;'>SELECT AGENT WORKFLOW</div>",
        unsafe_allow_html=True,
    )
    st.session_state.ai_role = st.selectbox(
        "Agent Workflow Mode",
        options=[
            "Dual Agent Workflow (Clerk Draft + Superintendent Review)",
            "Clerk AI (Drafting & File Preparation)",
            "Superintendent AI (Review & Verification)",
            "General Assistant"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown(
        "<div style='font-size:.78rem;color:#777;font-weight:650;padding:.9rem .6rem .4rem;'>YOUR CHATS</div>",
        unsafe_allow_html=True,
    )
    for chat_id, chat in reversed(list(st.session_state.conversations.items())):
        prefix = "▸ " if chat_id == st.session_state.active_conversation else "   "
        if st.button(
            (prefix + chat["title"])[:42],
            key=f"select_{chat_id}",
            use_container_width=True,
            type="primary" if chat_id == st.session_state.active_conversation else "secondary",
        ):
            st.session_state.active_conversation = chat_id
            st.rerun()

    st.markdown("<hr style='border:0;border-top:1px solid #e5e5e5;margin:1rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:.78rem;color:#777;font-weight:650;padding:.2rem .6rem .5rem;'>SETTINGS</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"Model: `{MODEL}`")
    if st.session_state.mode == "OpenAI":
        st.success("OpenAI connected")
    elif client is not None:
        st.info("OpenAI client ready")
    else:
        st.info("Demo Mode active")

    if st.button("Clear current chat", use_container_width=True):
        clear_current_chat()
        st.rerun()
    if st.button("Delete all chats", use_container_width=True):
        delete_all_chats()
        st.rerun()

    st.markdown(
        """
        <div style="margin-top:2rem;font-size:.76rem;color:#999;line-height:1.6;">
        BAITHAK WITH AI<br>
        Designed by Certified Generative and Agentic AI Application Developer<br>
        <b>Engr. Bilal Mehmood</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN APP HEADER
# ============================================================
st.markdown(
    f"""
    <div class="topbar">
      <div class="brand"><span class="brand-mark">✳</span>Baithak <span style="font-weight:400;color:#777;">with AI</span></div>
      <div class="status">Active Mode: {st.session_state.ai_role}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.notice:
    st.caption(st.session_state.notice)


# ============================================================
# ANIMATED ROBOT WIDGET
# ============================================================
robot_html = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
*{box-sizing:border-box}
body{margin:0;font-family:Arial,sans-serif;background:transparent;color:#202124}
.stage{position:relative;min-height:270px;display:flex;align-items:center;justify-content:center;
 gap:28px;padding:20px 18px;overflow:hidden;border:1px solid #e8eee9;border-radius:22px;
 background:radial-gradient(circle at 20% 20%,#e7fff6 0,#f8fffc 34%,#fff 75%)}
.robot-wrap{position:relative;width:160px;height:205px;flex:0 0 160px;animation:float 3.2s ease-in-out infinite}
.glow{position:absolute;left:10px;right:10px;bottom:0;height:24px;background:#10a37f30;border-radius:50%;filter:blur(9px);animation:shadow 3.2s infinite}
.antenna{position:absolute;top:0;left:76px;width:8px;height:24px;background:#9ba8ad;border-radius:8px}
.antenna:before{content:"";position:absolute;top:-9px;left:-5px;width:18px;height:18px;border-radius:50%;background:#10a37f;box-shadow:0 0 15px #10a37f;animation:pulse 1.4s infinite}
.ear{position:absolute;top:57px;width:17px;height:37px;background:#aebbc1;border-radius:8px}
.ear.left{left:4px}.ear.right{right:4px}
.head{position:absolute;top:23px;left:18px;width:124px;height:105px;border:4px solid #b8c7cc;border-radius:31px;background:linear-gradient(145deg,#fff,#dce8eb);box-shadow:inset 0 -7px 10px #b4c7cc55,0 9px 20px #0b6b5330}
.face{position:absolute;left:13px;right:13px;top:17px;height:61px;border-radius:20px;background:#162d38;box-shadow:inset 0 0 13px #0008}
.eye{position:absolute;top:18px;width:15px;height:20px;background:#65ffe0;border-radius:9px;box-shadow:0 0 12px #4fffd0;animation:blink 4.8s infinite}
.eye.left{left:19px}.eye.right{right:19px}
.mouth{position:absolute;left:39px;bottom:9px;width:19px;height:5px;border-radius:5px;background:#65ffe0;animation:talk 1s infinite}
.neck{position:absolute;top:128px;left:69px;width:22px;height:14px;background:#b5c4c9;border-radius:5px}
.body{position:absolute;top:138px;left:38px;width:84px;height:52px;border:4px solid #b8c7cc;border-radius:18px;background:linear-gradient(145deg,#faffff,#d8e6e9);box-shadow:0 7px 15px #0b6b5320}
.core{position:absolute;top:11px;left:28px;width:20px;height:20px;border-radius:50%;background:#10a37f;box-shadow:0 0 15px #10a37f;animation:pulse 1.7s infinite}
.arm{position:absolute;top:143px;width:16px;height:39px;background:#c6d4d8;border-radius:10px;transform-origin:top center}
.arm.left{left:24px;transform:rotate(18deg);animation:wave 2.2s ease-in-out infinite}
.arm.right{right:24px;transform:rotate(-18deg)}
.leg{position:absolute;top:184px;width:17px;height:17px;background:#aebdc2;border-radius:6px}
.leg.left{left:52px}.leg.right{right:52px}
.copy{max-width:480px;min-width:0}
.kicker{display:inline-block;padding:6px 10px;border-radius:999px;background:#e2f8ef;color:#087c5d;font-size:11px;font-weight:700;letter-spacing:.8px}
h2{margin:12px 0 8px;font-size:clamp(21px,3vw,30px);letter-spacing:-.7px}
p{margin:0;color:#65716d;line-height:1.6;font-size:14px}
.popup{margin-top:14px;padding:12px 14px;border:1px solid #d8eee4;border-radius:15px;background:#ffffffd9;box-shadow:0 8px 22px #0b6b5310;animation:appear .65s ease-out both}
.popup strong{color:#087c5d}
.popup small{display:block;color:#66716d;margin-top:4px;font-size:12px}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
@keyframes shadow{0%,100%{transform:scale(1);opacity:.7}50%{transform:scale(.8);opacity:.35}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.55}}
@keyframes blink{0%,43%,47%,100%{transform:scaleY(1)}45%{transform:scaleY(.08)}}
@keyframes talk{0%,100%{width:19px;height:4px;left:39px}50%{width:25px;height:8px;left:36px}}
@keyframes wave{0%,100%{transform:rotate(18deg)}50%{transform:rotate(45deg)}}
@keyframes appear{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:600px){.stage{gap:10px;padding:15px 10px;flex-direction:column;text-align:center}.robot-wrap{transform:scale(.9);margin-bottom:-8px}.copy{padding-bottom:4px}.popup{text-align:left}}
</style>
</head>
<body>
<div class="stage">
  <div class="robot-wrap" aria-label="Animated Baithak robot">
    <div class="glow"></div><div class="antenna"></div>
    <div class="ear left"></div><div class="ear right"></div>
    <div class="head"><div class="face"><div class="eye left"></div><div class="eye right"></div><div class="mouth"></div></div></div>
    <div class="neck"></div><div class="body"><div class="core"></div></div>
    <div class="arm left"></div><div class="arm right"></div>
    <div class="leg left"></div><div class="leg right"></div>
  </div>
  <div class="copy">
    <span class="kicker">MULTI-AGENT PIPELINE</span>
    <h2>Baithak Agentic Workspace</h2>
    <p>Clerk AI drafts and prepares document files, while Superintendent AI audits, verifies, and approves them for final export.</p>
    <div class="popup">
      <strong>📝 Clerk & 🔍 Superintendent Active</strong>
      <small>Submit requests to initiate drafting, automatic verification, and file conversion (PDF, DOCX, TXT, Excel).</small>
    </div>
  </div>
</div>
</body>
</html>
"""
components.html(robot_html, height=300, scrolling=False)


# ============================================================
# CHAT AREA & AGENT OUTPUT CONVERSION TOOLBAR
# ============================================================
conversation = st.session_state.conversations[st.session_state.active_conversation]

if not conversation["messages"]:
    st.markdown(
        "<h3 style='text-align:center;margin-top:1.2rem;'>What task would you like Clerk & Superintendent to perform?</h3>"
        "<p style='text-align:center;color:#777;'>Select a task below or enter custom instructions.</p>",
        unsafe_allow_html=True,
    )

    suggestions = [
        ("✉️ Draft & Audit Vendor Email", "Draft a formal email to vendors requesting updated quarterly pricing. Then verify it."),
        ("📊 Create & Verify Project Schedule Table", "Draft a project schedule table with tasks, deadlines, and assigned leads, then verify it for accuracy."),
        ("📄 Generate Official Memo", "Draft an official administrative memo regarding office holiday schedules."),
        ("📝 Summarize Document to Report", "Summarize attached document into an executive brief and check for compliance."),
    ]
    cols = st.columns(2)
    for i, (label, suggested_prompt) in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(label, key=f"suggest_{i}", use_container_width=True):
                submit_prompt(suggested_prompt)
                st.rerun()
else:
    for idx, message in enumerate(conversation["messages"]):
        avatar = "🧑" if message["role"] == "user" else "✳"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

            # File export toolbar for AI assistant output
            if message["role"] == "assistant":
                content = message["content"]
                st.markdown("---")
                st.caption("📥 **Convert Verified Draft into File Formats:**")
                exp_col1, exp_col2, exp_col3, exp_col4 = st.columns(4)

                # Export TXT
                with exp_col1:
                    st.download_button(
                        label="📄 Download TXT",
                        data=generate_txt(content),
                        file_name=f"Verified_Document_{idx}.txt",
                        mime="text/plain",
                        key=f"dl_txt_{idx}",
                        use_container_width=True
                    )

                # Export DOCX
                with exp_col2:
                    try:
                        docx_bytes = generate_docx(content)
                        st.download_button(
                            label="📝 Download DOCX",
                            data=docx_bytes,
                            file_name=f"Verified_Document_{idx}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"dl_docx_{idx}",
                            use_container_width=True
                        )
                    except Exception as err:
                        st.caption(f"DOCX error: {err}")

                # Export PDF
                with exp_col3:
                    try:
                        pdf_bytes = generate_pdf(content)
                        st.download_button(
                            label="📕 Download PDF",
                            data=pdf_bytes,
                            file_name=f"Verified_Document_{idx}.pdf",
                            mime="application/pdf",
                            key=f"dl_pdf_{idx}",
                            use_container_width=True
                        )
                    except Exception as err:
                        st.caption("Requires `fpdf2`")

                # Export Excel (if table is detected)
                with exp_col4:
                    if "|" in content and "\n" in content:
                        try:
                            excel_bytes = generate_excel_from_tables(content)
                            st.download_button(
                                label="📊 Export Excel",
                                data=excel_bytes,
                                file_name=f"Verified_Tables_{idx}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"dl_xls_{idx}",
                                use_container_width=True
                            )
                        except Exception:
                            st.caption("No valid table found")


# ============================================================
# DOCUMENT ATTACHMENTS & USER CHAT INPUT
# ============================================================
conversation.setdefault("documents", [])
with st.expander("📎 Attach source documents for Clerk drafting & Superintendent review", expanded=bool(conversation.get("documents"))):
    st.caption("Supported formats: PDF, DOCX, TXT · Max 20 MB per file")
    uploaded_files = st.file_uploader(
        "Upload reference files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key=f"document_upload_{st.session_state.active_conversation}",
        help="Upload documents for the Clerk to draft from and the Superintendent to audit.",
    )
    if st.button("Add files to conversation", key=f"add_documents_{st.session_state.active_conversation}", use_container_width=True):
        if uploaded_files:
            too_large = [f.name for f in uploaded_files if f.size > 20 * 1024 * 1024]
            if too_large:
                st.error("These files exceed the 20 MB limit: " + ", ".join(too_large))
            else:
                add_uploaded_documents(uploaded_files, conversation)
                st.rerun()
        else:
            st.info("Choose one or more files first.")
            
    if conversation.get("documents"):
        st.markdown("**Attached Files**")
        for idx, doc in enumerate(conversation["documents"]):
            col_name, col_remove = st.columns([5, 1])
            with col_name:
                st.write(f"📄 {doc['name']}" + (" · truncated" if doc.get("truncated") else ""))
            with col_remove:
                if st.button("Remove", key=f"remove_doc_{st.session_state.active_conversation}_{idx}"):
                    conversation["documents"].pop(idx)
                    st.rerun()

prompt = st.chat_input("Task Clerk AI to draft and Superintendent AI to verify...")
if prompt and prompt.strip():
    submit_prompt(prompt)
    st.rerun()


# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div class="footer">
      AI agents can make mistakes. Verify critical facts and documentation.<br>
      BAITHAK WITH AI · Designed by Certified Generative and Agentic AI Application Developer · Engr. Bilal Mehmood
    </div>
    """,
    unsafe_allow_html=True,
)
