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

# 4-Tier Administrative System Prompts
SYSTEM_PROMPTS = {
    "Naib Qasid AI": """
You are Baithak Naib Qasid AI, the intake dispatcher and workflow initiator.
Your core responsibilities:
1. Formally accept the incoming request from the user.
2. Acknowledge the task brief, catalog attachments, and format an official Docket/Routing Slip.
3. Pass the docket down to the Clerk with clear instructions on what needs to be drafted.
""",
    "Clerk AI": """
You are Baithak Clerk AI, the drafting and clerical documentation specialist.
Your core responsibilities:
1. Review the docket sent by Naib Qasid.
2. Draft clear, formal, executive-ready emails, memos, notices, or markdown tables.
3. Prepare content cleanly so it can be exported to PDF, DOCX, TXT, or Excel.
4. Pass the prepared draft to the Superintendent for verification.
""",
    "Superintendent AI": """
You are Baithak Superintendent AI, the quality auditor and administrative verifier.
Your core responsibilities:
1. Audit the draft submitted by the Clerk for accuracy, tone, completeness, and structure.
2. Provide a clear verification audit note highlighting corrections or confirming readiness.
3. Forward the verified file with recommendations to the Section Officer for final executive sign-off.
""",
    "Section Officer AI": """
You are Baithak Section Officer AI, the final approving authority.
Your core responsibilities:
1. Review the entire file (Docket -> Clerk Draft -> Superintendent Audit).
2. Issue the final sanction/verdict: **SANCTIONED & APPROVED**, **APPROVED WITH CONDITIONS**, or **REJECTED**.
3. Authorize the immediate release and generation of downloadable files (PDF, Word, Excel, TXT).
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
    st.session_state.ai_role = "Full Multi-Agent Hierarchy (Naib Qasid -> Clerk -> Superintendent -> Section Officer)"


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
    return text.encode("utf-8")


def generate_pdf(text: str) -> bytes:
    if FPDF is None:
        raise RuntimeError("PDF generator library `fpdf2` is not installed.")
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
    if Document is None:
        raise RuntimeError("Word generator library `python-docx` is not installed.")
    doc = Document()
    doc.add_heading("Baithak Official File Export", level=1)
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
    if pd is None:
        raise RuntimeError("Pandas or openpyxl missing.")
    dfs = parse_markdown_tables(text)
    if not dfs:
        raise ValueError("No table found to export.")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        for idx, df in enumerate(dfs, start=1):
            df.to_excel(writer, sheet_name=f"Sheet_{idx}", index=False)
    return buffer.getvalue()


# ============================================================
# LLM ENGINE & 4-TIER HIERARCHY WORKFLOW
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
        logger.exception("API call failed.")
        return None


def demo_reply():
    return (
        "📨 **[1. Naib Qasid - Intake & Docket Creation]**\n"
        "• Request Received: Formal Request Dispatch\n"
        "• Status: Docket created and handed over to Clerk for drafting.\n\n"
        "---\n\n"
        "📝 **[2. Clerk AI - Draft Preparation]**\n\n"
        "**Subject:** Official Communication Brief\n\n"
        "Dear Authority,\n\n"
        "The file draft has been prepared as per guidelines:\n\n"
        "| Section | Detail | Status |\n"
        "| :--- | :--- | :--- |\n"
        "| File No. | BTH-2026-09 | Formulated |\n"
        "| Content | Requirements & Action Plan | Ready for Verification |\n\n"
        "---\n\n"
        "🔍 **[3. Superintendent AI - Audit & Verification]**\n"
        "• Audit Verdict: **VERIFIED**\n"
        "• Verification Note: Structure, table formatting, and clarity verified. Submitted to Section Officer.\n\n"
        "---\n\n"
        "🏛️ **[4. Section Officer AI - Executive Sanction & Sign-off]**\n"
        "• Final Verdict: **SANCTIONED & APPROVED FOR RELEASE**\n"
        "• Authorization: Granted. File is cleared for PDF, Word, Excel, and TXT export.\n\n"
        "_Demo Mode Active. Configure `OPENAI_API_KEY` for live AI generation._"
    )


def execute_hierarchy_workflow(messages):
    selected_role = st.session_state.ai_role

    if client is None:
        st.session_state.mode = "Demo Mode"
        st.session_state.notice = "Demo Mode · Add OPENAI_API_KEY in Streamlit Secrets."
        return demo_reply()

    try:
        if selected_role == "Full Multi-Agent Hierarchy (Naib Qasid -> Clerk -> Superintendent -> Section Officer)":
            # 1. Naib Qasid Accepts & Routes Brief
            nq_res = call_llm(messages, SYSTEM_PROMPTS["Naib Qasid AI"]) or "Request logged in official docket and forwarded to Clerk."
            
            # 2. Clerk Drafts Content
            clerk_input = messages + [{"role": "assistant", "content": f"Naib Qasid Docket: {nq_res}"}]
            clerk_res = call_llm(clerk_input, SYSTEM_PROMPTS["Clerk AI"]) or "Draft generated."

            # 3. Superintendent Audits
            supt_input = clerk_input + [{"role": "assistant", "content": clerk_res}]
            supt_res = call_llm(supt_input, SYSTEM_PROMPTS["Superintendent AI"]) or "Audit completed."

            # 4. Section Officer Approves
            so_input = supt_input + [{"role": "assistant", "content": supt_res}]
            so_res = call_llm(so_input, SYSTEM_PROMPTS["Section Officer AI"]) or "Sanctioned."

            combined_output = (
                f"📨 **[1. Naib Qasid - Intake & Routing Slip]**\n{nq_res}\n\n"
                f"---\n\n"
                f"📝 **[2. Clerk AI - File Draft]**\n\n{clerk_res}\n\n"
                f"---\n\n"
                f"🔍 **[3. Superintendent AI - Audit Note]**\n{supt_res}\n\n"
                f"---\n\n"
                f"🏛️ **[4. Section Officer AI - Executive Sanction]**\n{so_res}"
            )
            st.session_state.mode = "OpenAI"
            st.session_state.notice = f"Connected · {MODEL} · 4-Tier Hierarchy Executed"
            return combined_output
        else:
            system_prompt = SYSTEM_PROMPTS.get(selected_role, SYSTEM_PROMPTS["Clerk AI"])
            res = call_llm(messages, system_prompt)
            st.session_state.mode = "OpenAI"
            st.session_state.notice = f"Connected · {MODEL} · ({selected_role})"
            return res or demo_reply()

    except Exception:
        logger.exception("Hierarchy execution error.")
        st.session_state.mode = "Demo Mode"
        return demo_reply()


def extract_uploaded_text(uploaded_file):
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
                raise RuntimeError("PDF support missing.")
            reader = PdfReader(io.BytesIO(raw))
            pages = []
            for page_no, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or "").strip()
                if text:
                    pages.append(f"[Page {page_no}]\n{text}")
            return "\n\n".join(pages)
        if suffix == "docx":
            if Document is None:
                raise RuntimeError("Word support missing.")
            doc = Document(io.BytesIO(raw))
            parts = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
            for table_no, table in enumerate(doc.tables, start=1):
                parts.append(f"[Table {table_no}]")
                for row in table.rows:
                    parts.append(" | ".join(cell.text.replace("\n", " ").strip() for cell in row.cells))
            return "\n".join(parts).strip()
        raise ValueError("Unsupported file format.")
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
            "content": "📎 **Documents received by Naib Qasid for official processing:**\n\n" + "\n".join(f"- {name}" for name in names)
        })
        st.session_state.notice = f"Added {added} document(s)."


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
            "\n\nUse the following attached source file text.\n" + "".join(chunks)
        )
    answer = execute_hierarchy_workflow(api_messages)
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
        "<div style='font-size:.78rem;color:#777;font-weight:650;padding:.9rem .6rem .4rem;'>OFFICIAL HIERARCHY PIPELINE</div>",
        unsafe_allow_html=True,
    )
    st.session_state.ai_role = st.selectbox(
        "Select Workflow Level",
        options=[
            "Full Multi-Agent Hierarchy (Naib Qasid -> Clerk -> Superintendent -> Section Officer)",
            "Naib Qasid AI",
            "Clerk AI",
            "Superintendent AI",
            "Section Officer AI"
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
      <div class="status">Hierarchy: Naib Qasid ➔ Clerk ➔ Supt ➔ SO</div>
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
    <span class="kicker">4-TIER ADMINISTRATIVE PIPELINE</span>
    <h2>Baithak Agentic Workflow</h2>
    <p>Naib Qasid receives & routes requests ➔ Clerk drafts documents ➔ Superintendent verifies quality ➔ Section Officer grants executive approval.</p>
    <div class="popup">
      <strong>🏛️ Automated Administrative File Routing</strong>
      <small>Submit a request to execute the complete pipeline and download sanctioned files (PDF, DOCX, TXT, Excel).</small>
    </div>
  </div>
</div>
</body>
</html>
"""
components.html(robot_html, height=300, scrolling=False)


# ============================================================
# CHAT AREA & EXPORT TOOLBAR
# ============================================================
conversation = st.session_state.conversations[st.session_state.active_conversation]

if not conversation["messages"]:
    st.markdown(
        "<h3 style='text-align:center;margin-top:1.2rem;'>Submit a request to initiate official file routing</h3>",
        unsafe_allow_html=True,
    )
    suggestions = [
        ("✉️ Draft Official Procurement Memo", "Draft an official procurement memo for IT hardware supplies."),
        ("📊 Formulate Project Schedule Table", "Generate a detailed project schedule with deadlines and responsible leads."),
        ("📄 Process Administrative Notice", "Prepare a formal administrative notice regarding revised working hours."),
        ("📝 Executive Briefing Note", "Draft an executive briefing note based on attached document summary."),
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

            # Export toolbar for sanctioned outputs
            if message["role"] == "assistant":
                content = message["content"]
                st.markdown("---")
                st.caption("📥 **Export Sanctioned File:**")
                exp_col1, exp_col2, exp_col3, exp_col4 = st.columns(4)

                with exp_col1:
                    st.download_button(
                        label="📄 Download TXT",
                        data=generate_txt(content),
                        file_name=f"Official_File_{idx}.txt",
                        mime="text/plain",
                        key=f"dl_txt_{idx}",
                        use_container_width=True
                    )

                with exp_col2:
                    try:
                        docx_bytes = generate_docx(content)
                        st.download_button(
                            label="📝 Download DOCX",
                            data=docx_bytes,
                            file_name=f"Official_File_{idx}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"dl_docx_{idx}",
                            use_container_width=True
                        )
                    except Exception as err:
                        st.caption(f"DOCX error: {err}")

                with exp_col3:
                    try:
                        pdf_bytes = generate_pdf(content)
                        st.download_button(
                            label="📕 Download PDF",
                            data=pdf_bytes,
                            file_name=f"Official_File_{idx}.pdf",
                            mime="application/pdf",
                            key=f"dl_pdf_{idx}",
                            use_container_width=True
                        )
                    except Exception as err:
                        st.caption("Requires `fpdf2`")

                with exp_col4:
                    if "|" in content and "\n" in content:
                        try:
                            excel_bytes = generate_excel_from_tables(content)
                            st.download_button(
                                label="📊 Export Excel",
                                data=excel_bytes,
                                file_name=f"Official_Table_{idx}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"dl_xls_{idx}",
                                use_container_width=True
                            )
                        except Exception:
                            st.caption("No valid table found")


# ============================================================
# DOCUMENT ATTACHMENT & CHAT INPUT
# ============================================================
conversation.setdefault("documents", [])
with st.expander("📎 Attach reference documents for official file routing", expanded=bool(conversation.get("documents"))):
    st.caption("Supported formats: PDF, DOCX, TXT · Max 20 MB per file")
    uploaded_files = st.file_uploader(
        "Upload reference files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key=f"document_upload_{st.session_state.active_conversation}",
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
        st.markdown("**Attached Source Files**")
        for idx, doc in enumerate(conversation["documents"]):
            col_name, col_remove = st.columns([5, 1])
            with col_name:
                st.write(f"📄 {doc['name']}" + (" · truncated" if doc.get("truncated") else ""))
            with col_remove:
                if st.button("Remove", key=f"remove_doc_{st.session_state.active_conversation}_{idx}"):
                    conversation["documents"].pop(idx)
                    st.rerun()

prompt = st.chat_input("Submit request to Naib Qasid for processing...")
if prompt and prompt.strip():
    submit_prompt(prompt)
    st.rerun()


# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div class="footer">
      AI can make mistakes. Check important official information.<br>
      BAITHAK WITH AI · Designed by Certified Generative and Agentic AI Application Developer · Engr. Bilal Mehmood
    </div>
    """,
    unsafe_allow_html=True,
)
