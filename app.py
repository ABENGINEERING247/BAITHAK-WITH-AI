
import os
import uuid
import logging

import streamlit as st

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="BAITHAK WITH AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
You are Baithak, a helpful, friendly, and intelligent AI assistant.
Answer the user's actual question directly.
Use Markdown formatting when helpful.
Explain complex ideas step by step.
Be honest when you are uncertain.
Match the user's language where practical.
Write clean, well-formatted code when requested.
"""


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("baithak_ai")


# ============================================================
# CONFIGURATION AND SECRETS
# ============================================================

def get_secret(name, default=None):
    """Read configuration from Streamlit Secrets or environment."""
    try:
        value = st.secrets.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    except Exception:
        pass

    value = os.getenv(name)

    if value and value.strip():
        return value.strip()

    return default


API_KEY = get_secret("OPENAI_API_KEY")
MODEL = get_secret("OPENAI_MODEL", DEFAULT_MODEL)


# ============================================================
# OPENAI CLIENT
# ============================================================

@st.cache_resource(show_spinner=False)
def get_client(api_key):
    """Create an OpenAI client or return None."""
    if not api_key or OpenAI is None:
        return None

    try:
        return OpenAI(
            api_key=api_key,
            timeout=60.0,
            max_retries=1,
        )
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
        first_id: {
            "title": "New chat",
            "messages": [],
        }
    }

    st.session_state.active_conversation = first_id

if "active_conversation" not in st.session_state:
    st.session_state.active_conversation = next(
        iter(st.session_state.conversations)
    )

if (
    st.session_state.active_conversation
    not in st.session_state.conversations
):
    st.session_state.active_conversation = next(
        iter(st.session_state.conversations)
    )

if "notice" not in st.session_state:
    st.session_state.notice = ""

if "mode" not in st.session_state:
    st.session_state.mode = "Demo Mode"


# ============================================================
# CHAT MANAGEMENT
# ============================================================

def new_chat():
    chat_id = str(uuid.uuid4())

    st.session_state.conversations[chat_id] = {
        "title": "New chat",
        "messages": [],
    }

    st.session_state.active_conversation = chat_id
    st.session_state.notice = ""


def clear_current_chat():
    chat_id = st.session_state.active_conversation

    st.session_state.conversations[chat_id] = {
        "title": "New chat",
        "messages": [],
    }

    st.session_state.notice = ""


def delete_all_chats():
    chat_id = str(uuid.uuid4())

    st.session_state.conversations = {
        chat_id: {
            "title": "New chat",
            "messages": [],
        }
    }

    st.session_state.active_conversation = chat_id
    st.session_state.notice = ""


def update_chat_title(conversation, prompt):
    if conversation["title"] == "New chat":
        title = " ".join(prompt.split())

        if len(title) > 35:
            title = title[:35].rstrip() + "..."

        conversation["title"] = title


# ============================================================
# DEMO MODE FALLBACK
# ============================================================

def demo_reply(prompt):
    """Provide a local fallback without making an API request."""
    text = prompt.strip()
    lower = text.lower()

    if any(
        word in lower
        for word in [
            "hello",
            "hi",
            "hey",
            "salam",
            "assalam",
        ]
    ):
        return (
            "Hello! 👋 Welcome to **Baithak with AI**.\n\n"
            "How can I help you today?\n\n"
            "_Demo Mode is active. This is a sample response, "
            "not a live AI-generated answer._"
        )

    if any(
        word in lower
        for word in [
            "python",
            "code",
            "program",
            "programming",
            "debug",
        ]
    ):
        return (
            "I'd be happy to help with your programming task! 💻\n\n"
            "To get started:\n\n"
            "1. Describe what you want your program to do.\n"
            "2. Share your code, if available.\n"
            "3. Include the complete error message, if you have one.\n\n"
            "**Demo Mode is active**, so detailed live AI responses "
            "are unavailable. Configure `OPENAI_API_KEY` to enable "
            "the live assistant."
        )

    return (
        f"I received your message:\n\n> {text}\n\n"
        "**Demo Mode is active.** This local fallback does not "
        "provide a full AI-generated answer.\n\n"
        "To enable live responses, add `OPENAI_API_KEY` to "
        "Streamlit Secrets. The default model is `gpt-4o-mini`."
    )


# ============================================================
# AI RESPONSE GENERATION
# ============================================================

def generate_reply(messages):
    """
    Generate an answer with OpenAI.
    If configuration or the API request fails, use Demo Mode.
    """
    if client is None:
        st.session_state.mode = "Demo Mode"
        st.session_state.notice = (
            "Demo Mode · Configure OPENAI_API_KEY for live responses."
        )

        return demo_reply(messages[-1]["content"])

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                *messages,
            ],
        )

        answer = response.choices[0].message.content

        if not answer or not answer.strip():
            raise ValueError("The AI returned an empty response.")

        st.session_state.mode = "OpenAI"
        st.session_state.notice = f"Connected · {MODEL}"

        return answer.strip()

    except Exception:
        # Keep sensitive configuration and exception details
        # out of the user-facing chat.
        logger.exception("OpenAI request failed.")

        st.session_state.mode = "Demo Mode"
        st.session_state.notice = (
            "Demo Mode · The OpenAI request failed. "
            "Check your API key, model access, quota, and connection."
        )

        return (
            "I couldn't obtain a response from the live AI service, "
            "so I've switched to **Demo Mode**.\n\n"
            "Please check your OpenAI API key, model access, API "
            "billing or quota, and network connection. Then try again."
        )


def submit_prompt(prompt):
    """Save a user message and generate an assistant response."""
    prompt = prompt.strip()

    if not prompt:
        return

    conversation = st.session_state.conversations[
        st.session_state.active_conversation
    ]

    conversation["messages"].append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    update_chat_title(conversation, prompt)

    api_messages = [
        {
            "role": message["role"],
            "content": message["content"],
        }
        for message in conversation["messages"]
    ]

    answer = generate_reply(api_messages)

    conversation["messages"].append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


# ============================================================
# CHATGPT-STYLE DESIGN
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --main-bg: #ffffff;
        --sidebar-bg: #f9f9f9;
        --text: #242424;
        --muted: #777777;
        --line: #e5e5e5;
        --accent: #10a37f;
    }

    .stApp {
        background: var(--main-bg);
        color: var(--text);
    }

    header[data-testid="stHeader"] {
        background: rgba(255,255,255,.95);
    }

    [data-testid="stSidebar"] {
        background: var(--sidebar-bg);
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }

    [data-testid="stSidebar"] .stButton > button {
        text-align: left;
        border: 0;
        border-radius: 10px;
        background: transparent;
        color: #303030;
        padding: .65rem .8rem;
        font-weight: 500;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: #ececec;
        box-shadow: none;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #e9e9e9;
        color: #111111;
    }

    .main .block-container {
        max-width: 900px;
        padding-top: 1.2rem;
        padding-bottom: 7rem;
    }

    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        padding: .3rem 0 1.2rem;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 1.5rem;
    }

    .brand {
        font-size: 1.1rem;
        font-weight: 700;
        color: #202020;
    }

    .brand-mark {
        display: inline-flex;
        width: 28px;
        height: 28px;
        border-radius: 9px;
        align-items: center;
        justify-content: center;
        background: var(--accent);
        color: white;
        margin-right: 8px;
    }

    .status {
        font-size: .78rem;
        color: #707070;
        border: 1px solid #e5e5e5;
        border-radius: 999px;
        padding: 5px 10px;
        white-space: nowrap;
    }

    .welcome {
        text-align: center;
        padding: 8vh 0 2rem;
    }

    .welcome h1 {
        font-size: 2.1rem;
        font-weight: 650;
        letter-spacing: -1px;
        color: #242424;
        margin-bottom: .5rem;
    }

    .welcome p {
        color: #707070;
        font-size: 1rem;
    }

    div[data-testid="stChatMessage"] {
        border: 0;
        padding: .8rem .3rem;
        gap: .9rem;
    }

    [data-testid="stChatMessageContent"] {
        line-height: 1.7;
        font-size: 1rem;
    }

    [data-testid="stChatInput"] {
        border-radius: 24px !important;
        border: 1px solid #d9d9d9 !important;
        box-shadow: 0 5px 24px rgba(0,0,0,.06);
        background: white !important;
    }

    [data-testid="stChatInput"] textarea {
        padding-top: 13px !important;
    }

    .stButton > button {
        border-radius: 10px;
        transition: background .15s ease;
    }

    .footer {
        text-align: center;
        color: #999999;
        font-size: .75rem;
        padding: 1.2rem 0 .5rem;
    }

    @media (max-width: 700px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .welcome h1 {
            font-size: 1.7rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div style="font-size:1.2rem;font-weight:750;
                    padding:0 .5rem 1rem;">
            🤖 Baithak with AI
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "＋ New chat",
        use_container_width=True,
        type="primary",
    ):
        new_chat()
        st.rerun()

    st.markdown(
        """
        <div style="font-size:.78rem;color:#777;font-weight:650;
                    padding:.9rem .6rem .4rem;">
            YOUR CHATS
        </div>
        """,
        unsafe_allow_html=True,
    )

    chat_items = list(st.session_state.conversations.items())
    chat_items.reverse()

    for chat_id, chat in chat_items:
        prefix = (
            "▸ " if chat_id == st.session_state.active_conversation
            else "   "
        )

        label = prefix + chat["title"]

        if st.button(
            label[:42],
            key=f"select_{chat_id}",
            use_container_width=True,
            type=(
                "primary"
                if chat_id == st.session_state.active_conversation
                else "secondary"
            ),
        ):
            st.session_state.active_conversation = chat_id
            st.rerun()

    st.markdown(
        "<div style='height:1px;background:#e5e5e5;"
        "margin:1rem 0;'></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="font-size:.78rem;color:#777;font-weight:650;
                    padding:.2rem .6rem .5rem;">
            SETTINGS
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(f"Model: `{MODEL}`")

    # These messages use standard Streamlit calls without
    # potentially invalid icon arguments.
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
        <div style="margin-top:2rem;font-size:.76rem;
                    color:#999;line-height:1.6;">
            BAITHAK WITH AI<br>
            Designed by Certified Generative and Agentic AI
            Application Developer<br>
            <b>Engr. Bilal Mehmood</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN CHAT
# ============================================================

conversation = st.session_state.conversations[
    st.session_state.active_conversation
]

st.markdown(
    """
    <div class="topbar">
        <div class="brand">
            <span class="brand-mark">✳</span>
            Baithak <span style="font-weight:400;color:#777;">
                with AI
            </span>
        </div>
        <div class="status">Text assistant</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.notice:
    st.caption(st.session_state.notice)


# ============================================================
# WELCOME SCREEN AND SUGGESTIONS
# ============================================================

if not conversation["messages"]:
    st.markdown(
        """
        <div class="welcome">
            <h1>What can I help with?</h1>
            <p>Ask anything, explore an idea, or get something done.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    suggestions = [
        (
            "💡 Brainstorm ideas",
            "Help me brainstorm creative ideas for a project.",
        ),
        (
            "💻 Write or debug code",
            "Help me write a Python program and explain it step by step.",
        ),
        (
            "📝 Write something",
            "Help me write a clear, professional email.",
        ),
        (
            "📚 Learn a topic",
            "Teach me a difficult topic in simple words with examples.",
        ),
    ]

    columns = st.columns(2)

    for index, (label, suggested_prompt) in enumerate(suggestions):
        with columns[index % 2]:
            if st.button(
                label,
                key=f"suggest_{index}",
                use_container_width=True,
            ):
                submit_prompt(suggested_prompt)
                st.rerun()

else:
    for message in conversation["messages"]:
        avatar = "🧑" if message["role"] == "user" else "✳"

        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input("Message Baithak...")

if prompt and prompt.strip():
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt.strip())

    with st.chat_message("assistant", avatar="✳"):
        with st.spinner("Thinking..."):
            submit_prompt(prompt)

        # Read the newly saved assistant message.
        latest_answer = st.session_state.conversations[
            st.session_state.active_conversation
        ]["messages"][-1]["content"]

        st.markdown(latest_answer)

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        AI can make mistakes. Check important information.
        · BAITHAK WITH AI
    </div>
    """,
    unsafe_allow_html=True,
)
