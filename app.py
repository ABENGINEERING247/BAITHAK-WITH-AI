```python
import os
import tempfile
from datetime import datetime

import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="BAITHAK WITH AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MODEL = "gpt-4o-mini"
TRANSCRIPTION_MODEL = "gpt-4o-mini-transcribe"
TTS_MODEL = "gpt-4o-mini-tts"
TTS_VOICE = "alloy"

SYSTEM_PROMPT = """
You are BAITHAK WITH AI, a helpful, friendly and professional AI assistant.

Answer clearly and practically.
Keep responses concise unless the user asks for detail.
Use simple language where possible.
For technical questions, provide accurate step-by-step guidance.
Do not invent facts.
"""


# ============================================================
# SECRET / ENVIRONMENT HELPERS
# ============================================================

def get_secret(name, default=None):
    """
    Safely read a value from Streamlit Secrets first,
    then environment variables.
    """

    try:
        value = st.secrets.get(name)

        if value:
            return value

    except Exception:
        pass

    return os.getenv(name, default)


OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
OPENAI_MODEL = get_secret("OPENAI_MODEL", DEFAULT_MODEL)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

if "voice_audio" not in st.session_state:
    st.session_state.voice_audio = None

if "mode" not in st.session_state:
    st.session_state.mode = "Demo Mode"

if "last_error" not in st.session_state:
    st.session_state.last_error = ""


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(255,255,255,0.95),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(150,225,255,0.55),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #effbff 0%,
                #dff6ff 35%,
                #c9efff 70%,
                #b8e9ff 100%
            );
        color: #063b55;
    }

    /* Main container */

    .block-container {
        max-width: 1250px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* Sidebar */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #dff7ff 0%,
                #c8efff 50%,
                #b8e8ff 100%
            );
        border-right: 1px solid rgba(0,110,160,0.15);
    }

    [data-testid="stSidebar"] * {
        color: #063b55;
    }

    /* ========================================================
       HERO
       ======================================================== */

    .robot-box {
        position: relative;
        overflow: hidden;

        margin: 10px 0 28px 0;
        padding: 30px 20px 38px 20px;

        text-align: center;

        border-radius: 32px;

        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(255,255,255,0.55),
                transparent 25%
            ),
            radial-gradient(
                circle at 85% 75%,
                rgba(255,255,255,0.30),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #72dcff,
                #39c4f2,
                #159bd0
            );

        box-shadow:
            0 25px 60px rgba(0,100,150,0.25),
            inset 0 1px 0 rgba(255,255,255,0.75);

        border: 1px solid rgba(255,255,255,0.55);
    }

    .robot-box::before,
    .robot-box::after {
        content: "";
        position: absolute;
        border-radius: 50%;
        background: rgba(255,255,255,0.18);
        pointer-events: none;
    }

    .robot-box::before {
        width: 180px;
        height: 180px;
        left: -60px;
        top: -70px;
        animation: bubbleMove 7s ease-in-out infinite;
    }

    .robot-box::after {
        width: 140px;
        height: 140px;
        right: -40px;
        bottom: -50px;
        animation: bubbleMove2 8s ease-in-out infinite;
    }

    /* ========================================================
       ROBOT STAGE
       ======================================================== */

    .robot-stage {
        position: relative;

        width: 280px;
        height: 315px;

        margin: 0 auto 8px auto;

        animation: robotFloat 3.2s ease-in-out infinite;

        z-index: 2;
    }

    /* ========================================================
       ANTENNA
       ======================================================== */

    .robot-antenna {
        position: absolute;

        left: 50%;
        top: 3px;

        width: 7px;
        height: 55px;

        transform: translateX(-50%);

        background: #086d98;

        border-radius: 10px;

        box-shadow:
            0 0 8px rgba(0,220,255,0.8);
    }

    .robot-light {
        position: absolute;

        left: 50%;
        top: -5px;

        width: 23px;
        height: 23px;

        transform: translateX(-50%);

        border-radius: 50%;

        background: #ffffff;

        box-shadow:
            0 0 8px #ffffff,
            0 0 18px #00eaff,
            0 0 32px #00eaff;

        animation: lightPulse 1.5s infinite;
    }

    /* ========================================================
       ROBOT EARS
       ======================================================== */

    .robot-ear {
        position: absolute;

        top: 102px;

        width: 28px;
        height: 58px;

        border-radius: 16px;

        background:
            linear-gradient(
                145deg,
                #e9fbff,
                #83d5ef
            );

        border: 4px solid #086d98;

        box-shadow:
            0 5px 12px rgba(0,80,120,0.20);
    }

    .robot-ear.left {
        left: 34px;
    }

    .robot-ear.right {
        right: 34px;
    }

    /* ========================================================
       ROBOT HEAD
       ======================================================== */

    .robot-head {
        position: absolute;

        left: 50%;
        top: 62px;

        width: 165px;
        height: 118px;

        transform: translateX(-50%);

        border-radius: 38px;

        background:
            linear-gradient(
                145deg,
                #ffffff,
                #c6f0ff
            );

        border: 5px solid #086d98;

        box-shadow:
            0 16px 28px rgba(0,80,120,0.24),
            inset 0 0 20px rgba(255,255,255,0.9);
    }

    /* ========================================================
       ROBOT EYES
       ======================================================== */

    .robot-eye {
        position: absolute;

        top: 39px;

        width: 25px;
        height: 31px;

        border-radius: 50%;

        background:
            radial-gradient(
                circle at 40% 30%,
                #ffffff 0 8%,
                #00eaff 10%,
                #005577 70%
            );

        box-shadow:
            0 0 10px #00eaff,
            0 0 22px rgba(0,230,255,0.75);

        animation: eyeBlink 4s infinite;
    }

    .robot-eye.left {
        left: 37px;
    }

    .robot-eye.right {
        right: 37px;
    }

    /* ========================================================
       ROBOT MOUTH
       ======================================================== */

    .robot-mouth {
        position: absolute;

        left: 50%;
        bottom: 19px;

        width: 48px;
        height: 11px;

        transform: translateX(-50%);

        border-radius: 10px;

        background: #07506e;

        box-shadow:
            0 0 10px rgba(0,220,255,0.7);
    }

    /* ========================================================
       ROBOT BODY
       ======================================================== */

    .robot-body {
        position: absolute;

        left: 50%;
        bottom: 3px;

        width: 145px;
        height: 105px;

        transform: translateX(-50%);

        border-radius: 32px 32px 24px 24px;

        background:
            linear-gradient(
                145deg,
                #ffffff,
                #aee5f8
            );

        border: 5px solid #086d98;

        box-shadow:
            0 15px 30px rgba(0,80,120,0.24),
            inset 0 0 18px rgba(255,255,255,0.9);
    }

    /* ========================================================
       ROBOT PANEL
       ======================================================== */

    .robot-panel {
        position: absolute;

        left: 50%;
        top: 31px;

        transform: translateX(-50%);

        display: flex;
        align-items: center;
        gap: 10px;

        padding: 12px 17px;

        border-radius: 15px;

        background: #063d57;

        box-shadow:
            inset 0 0 15px rgba(0,230,255,0.25),
            0 5px 10px rgba(0,50,80,0.2);
    }

    .robot-dot {
        display: block;

        width: 12px;
        height: 12px;

        border-radius: 50%;

        background: #00eaff;

        box-shadow:
            0 0 8px #00eaff,
            0 0 15px #00eaff;

        animation: dotPulse 1.2s infinite alternate;
    }

    .robot-dot:nth-child(2) {
        animation-delay: 0.2s;
    }

    .robot-dot:nth-child(3) {
        animation-delay: 0.4s;
    }

    /* ========================================================
       ROBOT ARMS
       ======================================================== */

    .robot-arm {
        position: absolute;

        top: 196px;

        width: 28px;
        height: 92px;

        border-radius: 18px;

        background:
            linear-gradient(
                145deg,
                #e8fbff,
                #8dd7ef
            );

        border: 4px solid #086d98;

        box-shadow:
            0 7px 15px rgba(0,80,120,0.20);
    }

    .robot-arm.left {
        left: 29px;
        transform: rotate(18deg);

        animation: leftArm 2s ease-in-out infinite;
    }

    .robot-arm.right {
        right: 29px;
        transform: rotate(-18deg);

        animation: rightArm 2s ease-in-out infinite;
    }

    /* ========================================================
       HERO TEXT
       ======================================================== */

    .hero-heading {
        position: relative;
        z-index: 3;

        margin-top: 5px;

        color: #004c6c;

        font-size: 44px;
        font-weight: 900;

        letter-spacing: 2px;

        text-shadow:
            0 2px 4px rgba(255,255,255,0.75);
    }

    .hero-text {
        position: relative;
        z-index: 3;

        margin-top: 8px;

        color: #063b55;

        font-size: 20px;
        font-weight: 650;
    }

    .flow-text {
        position: relative;
        z-index: 3;

        display: inline-block;

        margin-top: 16px;
        padding: 11px 22px;

        color: #ffffff;

        font-size: 18px;
        font-weight: 800;

        border-radius: 30px;

        background: rgba(0,60,90,0.28);

        border: 1px solid rgba(255,255,255,0.30);

        box-shadow:
            0 8px 20px rgba(0,50,80,0.16);
    }

    /* ========================================================
       CARDS
       ======================================================== */

    .voice-card {
        padding: 20px;

        margin-top: 20px;

        border-radius: 22px;

        background: rgba(255,255,255,0.68);

        border: 1px solid rgba(0,130,180,0.15);

        box-shadow:
            0 10px 30px rgba(0,100,150,0.10);

        backdrop-filter: blur(12px);
    }

    .voice-title {
        color: #005477;

        font-size: 22px;
        font-weight: 850;

        margin-bottom: 8px;
    }

    /* ========================================================
       CHAT
       ======================================================== */

    [data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.52);
        border-radius: 18px;
        border: 1px solid rgba(0,120,170,0.10);
        margin-bottom: 10px;
    }

    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        border-radius: 14px;

        border: 1px solid rgba(0,110,160,0.20);

        font-weight: 750;

        background:
            linear-gradient(
                135deg,
                #ffffff,
                #dff7ff
            );

        color: #005477;

        box-shadow:
            0 5px 15px rgba(0,100,150,0.10);
    }

    .stButton > button:hover {
        border-color: #00a9df;

        color: #004765;

        transform: translateY(-1px);

        box-shadow:
            0 8px 20px rgba(0,130,180,0.18);
    }

    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        margin-top: 35px;
        padding: 20px;

        text-align: center;

        color: #075477;

        font-size: 14px;

        border-top: 1px solid rgba(0,100,150,0.15);
    }

    .footer strong {
        color: #004d70;
    }

    /* ========================================================
       ANIMATIONS
       ======================================================== */

    @keyframes robotFloat {
        0%,
        100% {
            transform: translateY(0px);
        }

        50% {
            transform: translateY(-12px);
        }
    }

    @keyframes eyeBlink {
        0%,
        91%,
        100% {
            transform: scaleY(1);
        }

        94% {
            transform: scaleY(0.12);
        }
    }

    @keyframes lightPulse {
        0%,
        100% {
            transform: translateX(-50%) scale(1);
            opacity: 1;
        }

        50% {
            transform: translateX(-50%) scale(1.35);
            opacity: 0.65;
        }
    }

    @keyframes dotPulse {
        from {
            transform: scale(0.78);
            opacity: 0.55;
        }

        to {
            transform: scale(1.18);
            opacity: 1;
        }
    }

    @keyframes leftArm {
        0%,
        100% {
            transform: rotate(18deg);
        }

        50% {
            transform: rotate(5deg);
        }
    }

    @keyframes rightArm {
        0%,
        100% {
            transform: rotate(-18deg);
        }

        50% {
            transform: rotate(-5deg);
        }
    }

    @keyframes bubbleMove {
        0%,
        100% {
            transform: translate(0, 0);
        }

        50% {
            transform: translate(35px, 25px);
        }
    }

    @keyframes bubbleMove2 {
        0%,
        100% {
            transform: translate(0, 0);
        }

        50% {
            transform: translate(-30px, -25px);
        }
    }

    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 700px) {

        .robot-box {
            padding: 22px 10px 30px;
        }

        .robot-stage {
            transform: scale(0.82);
            transform-origin: center top;
            margin-bottom: -35px;
        }

        .hero-heading {
            font-size: 30px;
            letter-spacing: 1px;
        }

        .hero-text {
            font-size: 16px;
        }

        .flow-text {
            font-size: 14px;
            padding: 9px 15px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# OPENAI HELPERS
# ============================================================

def create_openai_client():
    """
    Create an OpenAI client only when a key exists.
    """

    if not OPENAI_API_KEY:
        return None

    try:
        from openai import OpenAI

        return OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=60.0,
            max_retries=0,
        )

    except Exception:
        return None


def is_quota_error(error_text):
    text = str(error_text).lower()

    keywords = [
        "insufficient_quota",
        "credit_balance_exhausted",
        "credit balance",
        "quota",
        "no credits remaining",
        "billing",
        "exceeded your current quota",
        "429",
    ]

    return any(keyword in text for keyword in keywords)


def is_auth_error(error_text):
    text = str(error_text).lower()

    keywords = [
        "invalid api key",
        "incorrect api key",
        "authentication",
        "unauthorized",
        "401",
        "api key",
    ]

    return any(keyword in text for keyword in keywords)


def is_model_error(error_text):
    text = str(error_text).lower()

    keywords = [
        "model_not_found",
        "model not found",
        "does not exist",
        "do not have access",
        "no access",
    ]

    return any(keyword in text for keyword in keywords)


def show_openai_error(error):
    """
    Show friendly messages without exposing raw API errors.
    """

    error_text = str(error)

    st.session_state.mode = "Demo Mode"
    st.session_state.last_error = error_text

    if is_quota_error(error_text):

        st.warning(
            "⚠️ Kindly Use Your API Credentials in Streamlit Secrets!"
        )

        st.info(
            "OpenAI API credits are unavailable or exhausted. "
            "BAITHAK WITH AI has automatically switched to Demo Mode."
        )

    elif is_auth_error(error_text):

        st.warning(
            "⚠️ Kindly Use Your API Credentials in Streamlit Secrets!"
        )

        st.info(
            "Your OpenAI API credential could not be verified. "
            "The application has switched to Demo Mode."
        )

    elif is_model_error(error_text):

        st.warning(
            "⚠️ The selected OpenAI model is unavailable "
            "for this API account."
        )

        st.info(
            "BAITHAK WITH AI has automatically switched to Demo Mode."
        )

    else:

        st.warning(
            "⚠️ OpenAI service is temporarily unavailable."
        )

        st.info(
            "BAITHAK WITH AI has automatically switched to Demo Mode."
        )


# ============================================================
# DEMO MODE
# ============================================================

def demo_response(prompt):
    """
    Local response engine used when OpenAI is unavailable.
    """

    text = prompt.lower().strip()

    if any(
        word in text
        for word in [
            "hello",
            "hi",
            "salam",
            "assalam",
            "hey",
        ]
    ):
        return (
            "Wa Alaikum Assalam! 👋\n\n"
            "Welcome to BAITHAK WITH AI. "
            "I am ready to help you with learning, "
            "technology, productivity, robotics and AI."
        )

    if "who are you" in text or "what are you" in text:
        return (
            "I am BAITHAK WITH AI 🤖, an AI assistant designed "
            "to understand your questions through text or voice."
        )

    if "artificial intelligence" in text or text == "ai":
        return (
            "Artificial Intelligence (AI) is the field of building "
            "systems that can perform tasks that normally require "
            "human intelligence, such as understanding language, "
            "recognizing images, learning patterns and making decisions."
        )

    if "python" in text:
        return (
            "Python is a high-level programming language widely used "
            "for AI, machine learning, automation, data science, "
            "robotics and web applications."
        )

    if "robot" in text or "robotics" in text:
        return (
            "Robotics combines mechanical engineering, electronics, "
            "control systems, embedded systems and software to build "
            "machines capable of sensing, deciding and acting."
        )

    if "study" in text or "learn" in text:
        return (
            "A practical learning strategy is:\n\n"
            "1. Define the goal.\n"
            "2. Learn the fundamentals.\n"
            "3. Practice with small projects.\n"
            "4. Build one real-world project.\n"
            "5. Review and improve regularly."
        )

    if "career" in text:
        return (
            "For a technology career, focus on strong fundamentals, "
            "practical projects, communication skills and a portfolio "
            "that demonstrates what you can actually build."
        )

    return (
        "🤖 Demo Mode is active.\n\n"
        "I can help with AI, programming, robotics, "
        "learning, productivity and general technology questions.\n\n"
        "For full AI-powered answers, add your OpenAI API "
        "credentials in Streamlit Secrets."
    )


# ============================================================
# OPENAI TEXT GENERATION
# ============================================================

def ask_openai(prompt):
    """
    Ask OpenAI using the Responses API.
    """

    client = create_openai_client()

    if client is None:
        raise RuntimeError("OpenAI API key is not configured.")

    conversation = []

    for message in st.session_state.messages[-12:]:

        role = message.get("role")

        if role not in ["user", "assistant"]:
            continue

        conversation.append(
            {
                "role": role,
                "content": message.get("content", ""),
            }
        )

    conversation.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=conversation,
    )

    answer = getattr(response, "output_text", None)

    if not answer:
        raise RuntimeError("OpenAI returned an empty response.")

    return answer.strip()


# ============================================================
# SPEECH TO TEXT
# ============================================================

def transcribe_audio(audio_file):
    """
    Convert microphone recording into text using OpenAI.
    """

    client = create_openai_client()

    if client is None:
        raise RuntimeError(
            "OpenAI API key is not configured."
        )

    audio_bytes = audio_file.getvalue()

    if not audio_bytes:
        raise RuntimeError(
            "The microphone recording is empty."
        )

    suffix = ".wav"

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            temp_file.write(audio_bytes)

            temp_path = temp_file.name

        try:

            with open(temp_path, "rb") as audio:

                result = client.audio.transcriptions.create(
                    model=TRANSCRIPTION_MODEL,
                    file=audio,
                )

            transcript = getattr(
                result,
                "text",
                "",
            )

            return transcript.strip()

        finally:

            try:
                os.remove(temp_path)
            except Exception:
                pass

    except Exception:
        raise


# ============================================================
# TEXT TO SPEECH
# ============================================================

def generate_speech(text):
    """
    Generate voice using OpenAI TTS.
    """

    client = create_openai_client()

    if client is None:
        raise RuntimeError(
            "OpenAI API key is not configured."
        )

    response = client.audio.speech.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=text[:4000],
    )

    return response.read()


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="robot-box">

        <div class="robot-stage">

            <div class="robot-antenna"></div>
            <div class="robot-light"></div>

            <div class="robot-ear left"></div>
            <div class="robot-ear right"></div>

            <div class="robot-head">

                <div class="robot-eye left"></div>
                <div class="robot-eye right"></div>

                <div class="robot-mouth"></div>

            </div>

            <div class="robot-arm left"></div>
            <div class="robot-arm right"></div>

            <div class="robot-body">

                <div class="robot-panel">

                    <span class="robot-dot"></span>
                    <span class="robot-dot"></span>
                    <span class="robot-dot"></span>

                </div>

            </div>

        </div>

        <div class="hero-heading">
            BAITHAK WITH AI
        </div>

        <div class="hero-text">
            Speak naturally or type your question.
        </div>

        <div class="flow-text">
            🎤 Speech
            &nbsp;→&nbsp;
            🧠 OpenAI
            &nbsp;→&nbsp;
            🔊 Voice
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🤖 BAITHAK WITH AI")

    st.markdown(
        "### ⚙️ AI Configuration"
    )

    mode_options = [
        "Demo Mode",
        "OpenAI API Mode",
    ]

    selected_mode = st.radio(
        "Operating Mode",
        mode_options,
        index=(
            1
            if st.session_state.mode == "OpenAI API Mode"
            and OPENAI_API_KEY
            else 0
        ),
    )

    if selected_mode == "OpenAI API Mode":

        if OPENAI_API_KEY:

            st.success(
                "🟢 OpenAI API Key detected"
            )

            st.caption(
                f"Model: {OPENAI_MODEL}"
            )

            st.session_state.mode = "OpenAI API Mode"

        else:

            st.warning(
                "⚠️ Kindly Use Your API Credentials "
                "in Streamlit Secrets!"
            )

            st.session_state.mode = "Demo Mode"

    else:

        st.session_state.mode = "Demo Mode"

        st.info(
            "🟡 Demo Mode active"
        )

    st.divider()

    st.markdown("### 📋 Current Status")

    if st.session_state.mode == "OpenAI API Mode":
        st.success("🧠 OpenAI API Mode")
    else:
        st.info("🤖 Demo Mode")

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []
        st.session_state.last_answer = ""
        st.session_state.voice_audio = None

        st.rerun()

    st.divider()

    st.markdown(
        """
        **🎤 Voice Pipeline**

        Speech  
        ↓  
        OpenAI Transcription  
        ↓  
        AI Response  
        ↓  
        OpenAI Text-to-Speech  
        ↓  
        🔊 Voice
        """
    )

    st.divider()

    st.caption(
        "OpenAI is the only external AI provider "
        "used by this application."
    )


# ============================================================
# MODE INFORMATION
# ============================================================

if st.session_state.mode == "OpenAI API Mode":

    st.success(
        f"🧠 OpenAI API Mode Active • {OPENAI_MODEL}"
    )

else:

    st.info(
        "🤖 Demo Mode Active — "
        "Add your OpenAI credentials to enable full AI."
    )


# ============================================================
# VOICE INPUT
# ============================================================

st.markdown(
    '<div class="voice-card">',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="voice-title">🎤 Voice Assistant</div>',
    unsafe_allow_html=True,
)

st.write(
    "Record your question and BAITHAK WITH AI will "
    "convert your speech into text."
)

audio_input = st.audio_input(
    "🎤 Record your question"
)

st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# PROCESS VOICE
# ============================================================

if audio_input is not None:

    st.audio(
        audio_input,
        format="audio/wav",
    )

    if st.button(
        "🧠 Convert Speech to Text",
        use_container_width=True,
    ):

        if not OPENAI_API_KEY:

            st.warning(
                "⚠️ Kindly Use Your API Credentials in "
                "Streamlit Secrets!"
            )

            st.session_state.mode = "Demo Mode"

            st.info(
                "Speech-to-text requires OpenAI API access. "
                "Please add OPENAI_API_KEY in Streamlit Secrets."
            )

        else:

            with st.spinner(
                "🎤 Converting speech to text..."
            ):

                try:

                    transcript = transcribe_audio(
                        audio_input
                    )

                    if not transcript:

                        st.warning(
                            "⚠️ No speech was detected."
                        )

                    else:

                        st.success(
                            f"📝 You said: {transcript}"
                        )

                        st.session_state.messages.append(
                            {
                                "role": "user",
                                "content": transcript,
                            }
                        )

                        if st.session_state.mode == "OpenAI API Mode":

                            try:

                                answer = ask_openai(
                                    transcript
                                )

                            except Exception as error:

                                show_openai_error(error)

                                answer = demo_response(
                                    transcript
                                )

                        else:

                            answer = demo_response(
                                transcript
                            )

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                            }
                        )

                        st.session_state.last_answer = answer

                        st.rerun()

                except Exception as error:

                    show_openai_error(error)


# ============================================================
# CHAT HISTORY
# ============================================================

if st.session_state.messages:

    st.markdown("## 💬 Conversation")

    for message in st.session_state.messages:

        role = message.get("role")
        content = message.get("content", "")

        if role == "user":

            with st.chat_message(
                "user",
                avatar="👤",
            ):

                st.markdown(content)

        elif role == "assistant":

            with st.chat_message(
                "assistant",
                avatar="🤖",
            ):

                st.markdown(content)


# ============================================================
# TEXT CHAT
# ============================================================

prompt = st.chat_input(
    "💬 Type your message here..."
)

if prompt:

    prompt = prompt.strip()

    if prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        if st.session_state.mode == "OpenAI API Mode":

            with st.spinner(
                "🧠 BAITHAK WITH AI is thinking..."
            ):

                try:

                    answer = ask_openai(prompt)

                except Exception as error:

                    show_openai_error(error)

                    answer = demo_response(prompt)

        else:

            answer = demo_response(prompt)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        st.session_state.last_answer = answer

        st.rerun()


# ============================================================
# TEXT TO SPEECH
# ============================================================

if st.session_state.last_answer:

    st.markdown(
        '<div class="voice-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="voice-title">🔊 AI Voice Response</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Listen to the latest AI response using "
        "OpenAI Text-to-Speech."
    )

    if st.button(
        "🔊 Speak Response with OpenAI",
        use_container_width=True,
    ):

        if not OPENAI_API_KEY:

            st.warning(
                "⚠️ Kindly Use Your API Credentials in "
                "Streamlit Secrets!"
            )

        else:

            with st.spinner(
                "🔊 Generating AI voice..."
            ):

                try:

                    voice_data = generate_speech(
                        st.session_state.last_answer
                    )

                    st.session_state.voice_audio = voice_data

                except Exception as error:

                    show_openai_error(error)

    if st.session_state.voice_audio:

        st.audio(
            st.session_state.voice_audio,
            format="audio/mp3",
        )

        st.download_button(
            label="⬇️ Download AI Voice",
            data=st.session_state.voice_audio,
            file_name="baithak_ai_response.mp3",
            mime="audio/mpeg",
            use_container_width=True,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

current_year = datetime.now().year

st.markdown(
    f"""
    <div class="footer">

        <strong>
            Designed by Certified Generative and Agentic
            AI Application Developer
        </strong>

        <br>

        Engr. Bilal Mehmood

        <br><br>

        <span>
            BAITHAK WITH AI • OpenAI Powered • {current_year}
        </span>

    </div>
    """,
    unsafe_allow_html=True,
)
```
