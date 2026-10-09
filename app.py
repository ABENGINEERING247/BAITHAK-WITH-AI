import os
import uuid
import logging
import html

import streamlit as st
import streamlit.components.v1 as components

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

DEFAULT_MODEL = "gpt-6-luna"
SYSTEM_PROMPT = """
You are Baithak, a helpful, friendly, clear AI assistant.
Answer the user's actual question directly. Use Markdown when useful.
Explain complex topics step by step, write complete code when requested,
and match the user's language where practical. Be honest when uncertain.
"""

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("baithak_ai")


# ============================================================
# SECRETS
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
# SESSION STATE
# ============================================================
if "conversations" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.conversations = {
        first_id: {"title": "New chat", "messages": []}
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
if "welcome_dismissed" not in st.session_state:
    st.session_state.welcome_dismissed = False


def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.conversations[chat_id] = {
        "title": "New chat", "messages": []
    }
    st.session_state.active_conversation = chat_id
    st.session_state.notice = ""


def clear_current_chat():
    chat_id = st.session_state.active_conversation
    st.session_state.conversations[chat_id] = {
        "title": "New chat", "messages": []
    }
    st.session_state.notice = ""


def delete_all_chats():
    chat_id = str(uuid.uuid4())
    st.session_state.conversations = {
        chat_id: {"title": "New chat", "messages": []}
    }
    st.session_state.active_conversation = chat_id
    st.session_state.notice = ""


def update_title(conversation, prompt):
    if conversation["title"] == "New chat":
        title = " ".join(prompt.split())
        conversation["title"] = title[:35].rstrip() + ("..." if len(title) > 35 else "")


def demo_reply(prompt):
    lower = prompt.lower()
    if any(word in lower for word in ("hello", "hi", "hey", "salam", "assalam")):
        return (
            "Hello! 👋 Welcome to **Baithak with AI**.\n\n"
            "How can I help you today?\n\n"
            "_Demo Mode is active; this is a sample response, not a live AI answer._"
        )
    if any(word in lower for word in ("python", "code", "program", "debug")):
        return (
            "I'd be happy to help with your coding task! 💻\n\n"
            "Please share your goal, your current code, and the complete error message.\n\n"
            "**Demo Mode is active**, so this is a limited sample response. "
            "Configure `OPENAI_API_KEY` to enable live AI responses."
        )
    return (
        f"I received your message:\n\n> {prompt}\n\n"
        "**Demo Mode is active.** This fallback cannot provide a full AI-generated answer. "
        "Configure `OPENAI_API_KEY` to enable the live assistant."
    )


def generate_reply(messages):
    if client is None:
        st.session_state.mode = "Demo Mode"
        st.session_state.notice = "Demo Mode · Add OPENAI_API_KEY in Streamlit Secrets for live AI."
        return demo_reply(messages[-1]["content"])

    try:
        # Responses API supports role-based input messages.
        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            input=messages,
        )
        answer = getattr(response, "output_text", None)
        if not answer or not answer.strip():
            raise ValueError("The model returned an empty response.")
        st.session_state.mode = "OpenAI"
        st.session_state.notice = f"Connected · {MODEL}"
        return answer.strip()
    except Exception:
        logger.exception("OpenAI response request failed.")
        st.session_state.mode = "Demo Mode"
        st.session_state.notice = (
            "Demo Mode · OpenAI request failed. Check model access, API key, quota, and connection."
        )
        return (
            "I couldn't get a response from the live AI service, so I've switched to **Demo Mode**.\n\n"
            f"The configured model is `{MODEL}`. Check whether this model ID is enabled for your API project, "
            "and verify your API key and billing/quota."
        )


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
    answer = generate_reply(api_messages)
    conversation["messages"].append({"role": "assistant", "content": answer})


# ============================================================
# CSS
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
        st.success("OpenAI response received")
    elif client is not None:
        st.info("OpenAI client configured")
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
    """
    <div class="topbar">
      <div class="brand"><span class="brand-mark">✳</span>Baithak <span style="font-weight:400;color:#777;">with AI</span></div>
      <div class="status">GPT Luna · Text assistant</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.notice:
    st.caption(st.session_state.notice)


# ============================================================
# ANIMATED ROBOT + WELCOME POPUP
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
    <span class="kicker">YOUR AI COMPANION</span>
    <h2>Welcome to Baithak with AI</h2>
    <p>Your ideas, questions, learning, and creativity have a place here. Start a conversation and let's make something useful together.</p>
    <div class="popup">
      <strong>👋 Hello everyone! I'm Baithak.</strong>
      <small>I'm ready to help you explore ideas, write, learn, and solve problems.</small>
    </div>
  </div>
</div>
</body>
</html>
"""
components.html(robot_html, height=300, scrolling=False)


# ============================================================
# CHAT AREA
# ============================================================
conversation = st.session_state.conversations[st.session_state.active_conversation]

if not conversation["messages"]:
    st.markdown(
        "<h3 style='text-align:center;margin-top:1.2rem;'>What can I help with?</h3>"
        "<p style='text-align:center;color:#777;'>Choose a suggestion or type your message below.</p>",
        unsafe_allow_html=True,
    )

    suggestions = [
        ("💡 Brainstorm ideas", "Help me brainstorm creative ideas for a project."),
        ("💻 Write or debug code", "Help me write a Python program and explain it step by step."),
        ("📝 Write something", "Help me write a clear, professional email."),
        ("📚 Learn a topic", "Teach me a difficult topic in simple words with examples."),
    ]
    cols = st.columns(2)
    for i, (label, suggested_prompt) in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(label, key=f"suggest_{i}", use_container_width=True):
                submit_prompt(suggested_prompt)
                st.rerun()
else:
    for message in conversation["messages"]:
        avatar = "🧑" if message["role"] == "user" else "✳"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

prompt = st.chat_input("Message Baithak...")
if prompt and prompt.strip():
    submit_prompt(prompt)
    st.rerun()


# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div class="footer">
      AI can make mistakes. Check important information.<br>
      BAITHAK WITH AI · Designed by Certified Generative and Agentic AI Application Developer · Engr. Bilal Mehmood
    </div>
    """,
    unsafe_allow_html=True,
)
