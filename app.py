import os
import uuid
from datetime import datetime

import streamlit as st

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="BAITHAK WITH AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = """You are Baithak, a helpful, clear, friendly AI assistant. Answer the user's actual question directly. Use Markdown formatting when useful, explain complex ideas step by step, and be honest when you are unsure. Match the user's language where practical."""


def get_secret(name, default=None):
    try:
        value = st.secrets.get(name, None)
        if value is not None and str(value).strip():
            return str(value).strip()
    except Exception:
        pass
    value = os.getenv(name)
    return str(value).strip() if value and str(value).strip() else default


API_KEY = get_secret("OPENAI_API_KEY")
MODEL = get_secret("OPENAI_MODEL", DEFAULT_MODEL)


@st.cache_resource
def get_client(api_key):
    if not api_key or OpenAI is None:
        return None
    try:
        return OpenAI(api_key=api_key, timeout=60.0, max_retries=1)
    except Exception:
        return None


client = get_client(API_KEY)

# ============================================================
# SESSION STATE
# ============================================================
if "conversations" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.conversations = {first_id: {"title": "New chat", "messages": []}}
    st.session_state.active_conversation = first_id
if "active_conversation" not in st.session_state or st.session_state.active_conversation not in st.session_state.conversations:
    st.session_state.active_conversation = next(iter(st.session_state.conversations))
if "notice" not in st.session_state:
    st.session_state.notice = ""


def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.conversations[chat_id] = {"title": "New chat", "messages": []}
    st.session_state.active_conversation = chat_id
    st.session_state.notice = ""


def demo_reply(prompt):
    """Safe local fallback when the API is not configured or unavailable."""
    text = prompt.strip()
    lower = text.lower()
    if any(word in lower for word in ["hello", "hi", "salam", "assalam", "hey"]):
        return "Hello! 👋 Welcome to **Baithak with AI**. How can I help you today?\n\n*Demo Mode is active, so this is a sample response rather than a live AI answer.*"
    if any(word in lower for word in ["python", "code", "program"]):
        return ("I can help you plan or troubleshoot your code. In Demo Mode, I can only provide a limited sample response.\n\n"
                "1. Describe the goal of your program.\n2. Share the relevant code and full error message.\n3. Tell me what you expected to happen.\n\n"
                "Add a valid `OPENAI_API_KEY` in Streamlit Secrets to enable live AI responses.")
    return (f"I received your message:\n\n> {text}\n\n"
            "This app is currently using **Demo Mode**, so it cannot generate a full live AI answer. "
            "To enable ChatGPT-style responses, add your OpenAI API key in Streamlit Secrets as `OPENAI_API_KEY`. "
            "You can also set `OPENAI_MODEL` (default: `gpt-4o-mini`).")


def generate_reply(messages):
    if client is None:
        st.session_state.notice = "Demo Mode · Add OPENAI_API_KEY in Streamlit Secrets to enable live AI."
        return demo_reply(messages[-1]["content"])
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        )
        answer = response.choices[0].message.content
        st.session_state.notice = f"Connected · {MODEL}"
        return answer.strip() if answer else "I couldn't generate a response. Please try again."
    except Exception as exc:
        st.session_state.notice = "Demo Mode · OpenAI request failed; check your API key, model access, or quota."
        return ("I couldn't reach the live AI service, so I've switched to Demo Mode.\n\n"
                f"**Technical detail:** `{str(exc)[:500]}`\n\n"
                "Check `OPENAI_API_KEY`, your selected model, API billing/quota, and network access, then try again.")

# ============================================================
# CHATGPT-LIKE STYLING
# ============================================================
st.markdown("""
<style>
:root { --sidebar-bg: #f9f9f9; --main-bg: #ffffff; --text: #242424; --muted: #6b6b6b; --line: #e5e5e5; --accent: #10a37f; }
.stApp { background: var(--main-bg); color: var(--text); }
header[data-testid="stHeader"] { background: rgba(255,255,255,.92); }
[data-testid="stSidebar"] { background: var(--sidebar-bg); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
[data-testid="stSidebar"] .stButton > button { text-align: left; border: 0; border-radius: 10px; background: transparent; color: #303030; padding: .65rem .8rem; font-weight: 500; }
[data-testid="stSidebar"] .stButton > button:hover { background: #ececec; transform: none; box-shadow: none; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] { background: #e9e9e9; color: #111; }
.main .block-container { max-width: 900px; padding-top: 1.2rem; padding-bottom: 8rem; }
.topbar { display:flex; justify-content:space-between; align-items:center; padding: .2rem 0 1.2rem; border-bottom:1px solid #f0f0f0; margin-bottom:1.5rem; }
.brand { font-size:1.1rem; font-weight:700; letter-spacing:-.3px; color:#202020; }
.brand-mark { display:inline-flex; width:28px; height:28px; border-radius:9px; align-items:center; justify-content:center; background:#10a37f; color:white; margin-right:8px; }
.status { font-size:.78rem; color:#707070; border:1px solid #e5e5e5; border-radius:999px; padding:5px 10px; }
.welcome { text-align:center; padding: 9vh 0 2rem; }
.welcome h1 { font-size:2.1rem; font-weight:650; letter-spacing:-1px; color:#242424; margin-bottom:.5rem; }
.welcome p { color:#707070; font-size:1rem; }
div[data-testid="stChatMessage"] { border:0; padding: .8rem .3rem; gap: .9rem; }
[data-testid="stChatMessageContent"] { line-height:1.7; font-size:1rem; }
[data-testid="stChatInput"] { border-radius:24px !important; border:1px solid #d9d9d9 !important; box-shadow:0 5px 24px rgba(0,0,0,.06); background:white !important; }
[data-testid="stChatInput"] textarea { padding-top:13px !important; }
.stButton > button { border-radius:10px; transition:background .15s ease; }
.suggestion-wrap { margin-top:1rem; }
div[data-testid="stHorizontalBlock"] button { min-height:48px; }
.footer { text-align:center; color:#999; font-size:.75rem; padding:1.2rem 0 .5rem; }
@media (max-width: 700px) { .main .block-container { padding-left:1rem; padding-right:1rem; } .welcome h1 {font-size:1.7rem;} }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<div style="font-size:1.2rem;font-weight:750;padding:0 .5rem 1rem;">🤖 Baithak with AI</div>', unsafe_allow_html=True)
    if st.button("＋  New chat", use_container_width=True, type="primary"):
        new_chat()
        st.rerun()

    st.markdown("<div style='font-size:.78rem;color:#777;font-weight:650;padding:.9rem .6rem .4rem;'>YOUR CHATS</div>", unsafe_allow_html=True)
    chat_items = list(st.session_state.conversations.items())
    chat_items.reverse()
    for chat_id, chat in chat_items:
        label = ("▸  " if chat_id == st.session_state.active_conversation else "   ") + chat["title"]
        if st.button(label[:42], key=f"select_{chat_id}", use_container_width=True, type="primary" if chat_id == st.session_state.active_conversation else "secondary"):
            st.session_state.active_conversation = chat_id
            st.rerun()

    st.markdown("<div style='height:1px;background:#e5e5e5;margin:1rem 0;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.78rem;color:#777;font-weight:650;padding:.2rem .6rem .5rem;'>SETTINGS</div>", unsafe_allow_html=True)
    st.caption(f"Model: `{MODEL}`")
    if client:
        st.success("OpenAI connected", icon="✓")
    else:
        st.info("Demo Mode", icon="ℹ️")
    if st.button("Clear current chat", use_container_width=True):
        st.session_state.conversations[st.session_state.active_conversation]["messages"] = []
        st.session_state.conversations[st.session_state.active_conversation]["title"] = "New chat"
        st.session_state.notice = ""
        st.rerun()
    if st.button("Delete all chats", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.conversations = {new_id: {"title": "New chat", "messages": []}}
        st.session_state.active_conversation = new_id
        st.session_state.notice = ""
        st.rerun()
    st.markdown("<div style='position:relative;margin-top:2rem;font-size:.76rem;color:#999;line-height:1.5;'>BAITHAK WITH AI<br>Designed by Certified Generative and Agentic AI Application Developer<br><b>Engr. Bilal Mehmood</b></div>", unsafe_allow_html=True)

# ============================================================
# MAIN CHAT
# ============================================================
conversation = st.session_state.conversations[st.session_state.active_conversation]
st.markdown(
    '<div class="topbar"><div class="brand"><span class="brand-mark">✳</span>Baithak <span style="font-weight:400;color:#777;">with AI</span></div>'
    '<div class="status">Text assistant</div></div>',
    unsafe_allow_html=True,
)

if st.session_state.notice:
    st.caption(st.session_state.notice)

if not conversation["messages"]:
    st.markdown('<div class="welcome"><h1>What can I help with?</h1><p>Ask anything, explore an idea, or get something done.</p></div>', unsafe_allow_html=True)
    suggestions = [
        ("💡  Brainstorm ideas", "Help me brainstorm some creative ideas for a project."),
        ("💻  Write or debug code", "Help me write a Python program and explain it step by step."),
        ("📝  Write something", "Help me write a clear, professional email."),
        ("📚  Learn a topic", "Teach me a difficult topic in simple words with examples."),
    ]
    cols = st.columns(2)
    for i, (label, prompt) in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(label, key=f"suggest_{i}", use_container_width=True):
                conversation["messages"].append({"role": "user", "content": prompt})
                if conversation["title"] == "New chat":
                    conversation["title"] = prompt[:32] + ("…" if len(prompt) > 32 else "")
                api_messages = [{"role": m["role"], "content": m["content"]} for m in conversation["messages"]]
                answer = generate_reply(api_messages)
                conversation["messages"].append({"role": "assistant", "content": answer})
                st.rerun()
else:
    for message in conversation["messages"]:
        with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "✳"):
            st.markdown(message["content"])

prompt = st.chat_input("Message Baithak…")
if prompt and prompt.strip():
    prompt = prompt.strip()
    conversation["messages"].append({"role": "user", "content": prompt})
    if conversation["title"] == "New chat":
        conversation["title"] = prompt[:32] + ("…" if len(prompt) > 32 else "")
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="✳"):
        with st.spinner("Thinking…"):
            api_messages = [{"role": m["role"], "content": m["content"]} for m in conversation["messages"]]
            answer = generate_reply(api_messages)
        st.markdown(answer)
    conversation["messages"].append({"role": "assistant", "content": answer})
    st.rerun()

st.markdown('<div class="footer">AI can make mistakes. Check important information. · BAITHAK WITH AI</div>', unsafe_allow_html=True)
