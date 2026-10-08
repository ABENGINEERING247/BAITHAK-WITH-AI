import os
import tempfile
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components


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

APP_NAME = "BAITHAK WITH AI"

DEFAULT_MODEL = "gpt-4o-mini"
TRANSCRIPTION_MODEL = "gpt-4o-mini-transcribe"
TTS_MODEL = "gpt-4o-mini-tts"
TTS_VOICE = "alloy"

SYSTEM_PROMPT = """
You are BAITHAK WITH AI, a helpful, friendly and professional
AI assistant.

Answer clearly and practically.

Keep responses concise unless the user asks for detail.

Use simple language where possible.

For technical questions, provide accurate step-by-step guidance.

Do not invent facts.

If you are uncertain, clearly say that you are uncertain.

You can help with:

- Artificial Intelligence
- Generative AI
- Agentic AI
- Python
- Programming
- Streamlit
- Google AI Studio
- Automation
- Robotics
- Education
- Productivity
- Technology
"""


# ============================================================
# SECRET HELPER
# ============================================================

def get_secret(name, default=None):

    try:

        value = st.secrets.get(name)

        if value:
            return value

    except Exception:
        pass

    return os.getenv(
        name,
        default,
    )


OPENAI_API_KEY = get_secret(
    "OPENAI_API_KEY"
)

OPENAI_MODEL = get_secret(
    "OPENAI_MODEL",
    DEFAULT_MODEL,
)


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
# APPLICATION CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       APPLICATION BACKGROUND
       ======================================================== */

    .stApp {

        background:
            radial-gradient(
                circle at 15% 10%,
                rgba(255,255,255,0.95),
                transparent 25%
            ),

            radial-gradient(
                circle at 90% 15%,
                rgba(95,220,255,0.30),
                transparent 30%
            ),

            linear-gradient(
                135deg,
                #effcff 0%,
                #ddf7ff 40%,
                #c9efff 70%,
                #b9eaff 100%
            );

        color: #063b55;
    }


    .block-container {

        max-width: 1250px;

        padding-top: 1.5rem;

        padding-bottom: 2rem;
    }


    /* ========================================================
       STREAMLIT HEADINGS
       ======================================================== */

    h1 {

        color:
            #034e6d !important;

        font-weight:
            900 !important;

        letter-spacing:
            1px;
    }


    h2,
    h3 {

        color:
            #075477 !important;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #e5faff 0%,
                #d0f2ff 50%,
                #bceaff 100%
            );

        border-right:
            1px solid
            rgba(0,110,160,0.15);
    }


    [data-testid="stSidebar"] * {

        color:
            #063b55;
    }


    /* ========================================================
       GLASS CARDS
       ======================================================== */

    .glass-card {

        padding:
            22px;

        margin-top:
            18px;

        border-radius:
            22px;

        background:
            rgba(255,255,255,0.68);

        border:
            1px solid
            rgba(0,130,180,0.14);

        box-shadow:
            0 12px 35px
            rgba(0,100,150,0.10);

        backdrop-filter:
            blur(14px);
    }


    .card-title {

        color:
            #005477;

        font-size:
            22px;

        font-weight:
            850;

        margin-bottom:
            8px;
    }


    /* ========================================================
       CHAT
       ======================================================== */

    [data-testid="stChatMessage"] {

        background:
            rgba(255,255,255,0.58);

        border-radius:
            18px;

        border:
            1px solid
            rgba(0,120,170,0.10);

        margin-bottom:
            10px;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {

        border-radius:
            14px;

        border:
            1px solid
            rgba(0,110,160,0.20);

        font-weight:
            750;

        background:
            linear-gradient(
                135deg,
                #ffffff,
                #dff7ff
            );

        color:
            #005477;

        box-shadow:
            0 5px 15px
            rgba(0,100,150,0.10);

        transition:
            all 0.2s ease;
    }


    .stButton > button:hover {

        border-color:
            #00a9df;

        color:
            #004765;

        transform:
            translateY(-1px);

        box-shadow:
            0 8px 20px
            rgba(0,130,180,0.18);
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {

        margin-top:
            40px;

        padding:
            22px;

        text-align:
            center;

        color:
            #075477;

        font-size:
            14px;

        border-top:
            1px solid
            rgba(0,100,150,0.15);
    }


    .footer strong {

        color:
            #004d70;
    }


    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 700px) {

        .block-container {

            padding-left:
                0.8rem;

            padding-right:
                0.8rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ANIMATED ROBOT
# ============================================================

def show_animated_robot():

    robot_html = """
    <!DOCTYPE html>

    <html>

    <head>

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <style>

    html,
    body {

        margin: 0;
        padding: 0;

        width: 100%;
        height: 100%;

        overflow: hidden;

        background: transparent;
    }


    .robot-wrapper {

        width: 100%;

        height: 550px;

        display: flex;

        justify-content: center;

        align-items: center;

        position: relative;
    }


    .robot {

        width: 390px;

        height: 510px;

        position: relative;

        animation:
            floatRobot 3.5s
            ease-in-out
            infinite;
    }


    /* ======================================================
       FLOOR GLOW
       ====================================================== */

    .glow {

        position: absolute;

        width: 290px;

        height: 90px;

        left: 50%;

        bottom: 25px;

        transform:
            translateX(-50%);

        border-radius:
            50%;

        background:
            rgba(0,210,255,0.25);

        filter:
            blur(25px);

        animation:
            glowPulse 2.5s
            ease-in-out
            infinite;
    }


    /* ======================================================
       ANTENNA
       ====================================================== */

    .antenna {

        position: absolute;

        width: 9px;

        height: 58px;

        left: 50%;

        top: 0;

        transform:
            translateX(-50%);

        border-radius:
            10px;

        background:
            linear-gradient(
                to bottom,
                #07577a,
                #0abce8
            );
    }


    .antenna-light {

        position: absolute;

        width: 28px;

        height: 28px;

        left: 50%;

        top: -10px;

        transform:
            translateX(-50%);

        border-radius:
            50%;

        background:
            white;

        box-shadow:
            0 0 8px white,
            0 0 18px #00eaff,
            0 0 35px #00eaff;

        animation:
            antennaPulse 1.2s
            infinite;
    }


    /* ======================================================
       EARS
       ====================================================== */

    .ear {

        position: absolute;

        top: 108px;

        width: 42px;

        height: 75px;

        border-radius:
            22px;

        background:
            linear-gradient(
                145deg,
                #effcff,
                #86d9f2
            );

        border:
            6px solid #086d98;

        box-shadow:
            0 8px 18px
            rgba(0,80,120,0.20);
    }


    .ear.left {

        left: 35px;
    }


    .ear.right {

        right: 35px;
    }


    /* ======================================================
       HEAD
       ====================================================== */

    .head {

        position: absolute;

        width: 245px;

        height: 175px;

        left: 50%;

        top: 55px;

        transform:
            translateX(-50%);

        border-radius:
            55px;

        background:
            linear-gradient(
                145deg,
                #ffffff,
                #c7f2ff
            );

        border:
            7px solid #086d98;

        box-shadow:
            0 18px 40px
            rgba(0,80,120,0.28),

            inset 0 0 30px
            rgba(255,255,255,0.9);
    }


    /* ======================================================
       EYES
       ====================================================== */

    .eye {

        position: absolute;

        width: 42px;

        height: 50px;

        top: 54px;

        border-radius:
            50%;

        background:
            radial-gradient(
                circle at 35% 25%,
                #ffffff 0 8%,
                #00eaff 12%,
                #0084a9 48%,
                #003e58 75%
            );

        box-shadow:
            0 0 12px #00eaff,
            0 0 28px
            rgba(0,230,255,0.80);

        animation:
            blink 5s infinite;
    }


    .eye.left {

        left: 48px;
    }


    .eye.right {

        right: 48px;
    }


    /* ======================================================
       EYE SCANNER
       ====================================================== */

    .scan-line {

        position: absolute;

        left: 12px;

        right: 12px;

        top: 50%;

        height: 3px;

        background:
            #ffffff;

        box-shadow:
            0 0 8px #00ffff;

        animation:
            scan 1.7s
            ease-in-out
            infinite;
    }


    /* ======================================================
       MOUTH
       ====================================================== */

    .mouth {

        position: absolute;

        left: 50%;

        bottom: 27px;

        width: 75px;

        height: 16px;

        transform:
            translateX(-50%);

        border-radius:
            20px;

        background:
            #064b67;

        box-shadow:
            0 0 12px
            rgba(0,220,255,0.75);

        animation:
            talk 1.1s
            ease-in-out
            infinite;
    }


    /* ======================================================
       BODY
       ====================================================== */

    .body {

        position: absolute;

        width: 205px;

        height: 160px;

        left: 50%;

        bottom: 45px;

        transform:
            translateX(-50%);

        border-radius:
            45px 45px 32px 32px;

        background:
            linear-gradient(
                145deg,
                #ffffff,
                #a9e5f7
            );

        border:
            7px solid #086d98;

        box-shadow:
            0 18px 40px
            rgba(0,80,120,0.28),

            inset 0 0 25px
            rgba(255,255,255,0.9);
    }


    /* ======================================================
       CHEST PANEL
       ====================================================== */

    .chest {

        position: absolute;

        width: 105px;

        height: 58px;

        left: 50%;

        top: 38px;

        transform:
            translateX(-50%);

        border-radius:
            17px;

        background:
            #063e57;

        border:
            3px solid #00bde9;

        box-shadow:
            inset 0 0 18px
            rgba(0,230,255,0.25),

            0 5px 12px
            rgba(0,50,80,0.20);
    }


    .dot {

        position: absolute;

        width: 12px;

        height: 12px;

        top: 20px;

        border-radius:
            50%;

        background:
            #00eaff;

        box-shadow:
            0 0 8px #00eaff,
            0 0 18px #00eaff;

        animation:
            dotPulse 1s
            infinite alternate;
    }


    .dot.one {

        left: 20px;
    }


    .dot.two {

        left: 46px;

        animation-delay:
            .2s;
    }


    .dot.three {

        right: 20px;

        animation-delay:
            .4s;
    }


    /* ======================================================
       ARMS
       ====================================================== */

    .arm {

        position: absolute;

        width: 43px;

        height: 135px;

        top: 285px;

        border-radius:
            25px;

        background:
            linear-gradient(
                145deg,
                #f3fdff,
                #8bd8f1
            );

        border:
            6px solid #086d98;

        box-shadow:
            0 10px 20px
            rgba(0,80,120,0.22);
    }


    .arm.left {

        left: 45px;

        transform:
            rotate(20deg);

        animation:
            leftArm 2.2s
            ease-in-out
            infinite;
    }


    .arm.right {

        right: 45px;

        transform:
            rotate(-20deg);

        animation:
            rightArm 2.2s
            ease-in-out
            infinite;
    }


    /* ======================================================
       HANDS
       ====================================================== */

    .hand {

        position: absolute;

        width: 55px;

        height: 55px;

        border-radius:
            50%;

        background:
            linear-gradient(
                145deg,
                #ffffff,
                #91dcf3
            );

        border:
            5px solid #086d98;
    }


    .hand.left {

        left: 31px;

        top: 400px;
    }


    .hand.right {

        right: 31px;

        top: 400px;
    }


    /* ======================================================
       ANIMATIONS
       ====================================================== */

    @keyframes floatRobot {

        0%,
        100% {
            transform:
                translateY(0);
        }

        50% {
            transform:
                translateY(-16px);
        }
    }


    @keyframes blink {

        0%,
        92%,
        100% {
            transform:
                scaleY(1);
        }

        95% {
            transform:
                scaleY(0.08);
        }
    }


    @keyframes talk {

        0%,
        100% {
            height:
                14px;
        }

        50% {
            height:
                30px;
        }
    }


    @keyframes antennaPulse {

        0%,
        100% {
            transform:
                translateX(-50%)
                scale(1);

            opacity:
                1;
        }

        50% {
            transform:
                translateX(-50%)
                scale(1.35);

            opacity:
                0.65;
        }
    }


    @keyframes dotPulse {

        from {
            transform:
                scale(0.7);

            opacity:
                0.5;
        }

        to {
            transform:
                scale(1.25);

            opacity:
                1;
        }
    }


    @keyframes scan {

        0%,
        100% {
            top:
                25%;

            opacity:
                0.5;
        }

        50% {
            top:
                70%;

            opacity:
                1;
        }
    }


    @keyframes leftArm {

        0%,
        100% {
            transform:
                rotate(20deg);
        }

        50% {
            transform:
                rotate(5deg);
        }
    }


    @keyframes rightArm {

        0%,
        100% {
            transform:
                rotate(-20deg);
        }

        50% {
            transform:
                rotate(-5deg);
        }
    }


    @keyframes glowPulse {

        0%,
        100% {
            opacity:
                0.35;

            transform:
                translateX(-50%)
                scaleX(0.85);
        }

        50% {
            opacity:
                0.70;

            transform:
                translateX(-50%)
                scaleX(1.05);
        }
    }

    </style>

    </head>

    <body>

        <div class="robot-wrapper">

            <div class="robot">

                <div class="glow"></div>

                <div class="antenna"></div>

                <div class="antenna-light"></div>

                <div class="ear left"></div>

                <div class="ear right"></div>

                <div class="head">

                    <div class="eye left">
                        <div class="scan-line"></div>
                    </div>

                    <div class="eye right">
                        <div class="scan-line"></div>
                    </div>

                    <div class="mouth"></div>

                </div>

                <div class="arm left"></div>

                <div class="arm right"></div>

                <div class="body">

                    <div class="chest">

                        <div class="dot one"></div>

                        <div class="dot two"></div>

                        <div class="dot three"></div>

                    </div>

                </div>

                <div class="hand left"></div>

                <div class="hand right"></div>

            </div>

        </div>

    </body>

    </html>
    """

    components.html(
        robot_html,
        height=560,
        scrolling=False,
    )


# ============================================================
# OPENAI CLIENT
# ============================================================

def create_openai_client():

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


# ============================================================
# ERROR DETECTION
# ============================================================

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

    return any(
        keyword in text
        for keyword in keywords
    )


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

    return any(
        keyword in text
        for keyword in keywords
    )


def is_model_error(error_text):

    text = str(error_text).lower()

    keywords = [
        "model_not_found",
        "model not found",
        "does not exist",
        "do not have access",
        "no access",
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# ============================================================
# OPENAI ERROR DISPLAY
# ============================================================

def show_openai_error(error):

    error_text = str(error)

    st.session_state.mode = "Demo Mode"

    st.session_state.last_error = error_text


    if is_quota_error(error_text):

        st.warning(
            "⚠️ OpenAI API credits are unavailable "
            "or exhausted."
        )

        st.info(
            "BAITHAK WITH AI has automatically "
            "switched to Demo Mode."
        )


    elif is_auth_error(error_text):

        st.warning(
            "⚠️ Your OpenAI API credential "
            "could not be verified."
        )

        st.info(
            "Please check OPENAI_API_KEY "
            "in Streamlit Secrets."
        )


    elif is_model_error(error_text):

        st.warning(
            "⚠️ The selected OpenAI model "
            "is unavailable."
        )

        st.info(
            "BAITHAK WITH AI has switched "
            "to Demo Mode."
        )


    else:

        st.warning(
            "⚠️ OpenAI service is temporarily "
            "unavailable."
        )

        st.info(
            "BAITHAK WITH AI has switched "
            "to Demo Mode."
        )


# ============================================================
# DEMO MODE
# ============================================================

def demo_response(prompt):

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
            "I am ready to help you with AI, "
            "programming, robotics, technology "
            "and learning."
        )


    if (
        "who are you" in text
        or "what are you" in text
    ):

        return (
            "I am BAITHAK WITH AI 🤖, an AI "
            "assistant designed to communicate "
            "with users through text and voice."
        )


    if (
        "artificial intelligence" in text
        or text == "ai"
    ):

        return (
            "Artificial Intelligence is the field "
            "of creating computer systems capable "
            "of performing tasks that normally "
            "require human intelligence."
        )


    if "python" in text:

        return (
            "Python is a high-level programming "
            "language widely used for AI, automation, "
            "data science, robotics and web "
            "applications."
        )


    if (
        "robot" in text
        or "robotics" in text
    ):

        return (
            "Robotics combines mechanical engineering, "
            "electronics, sensors, control systems "
            "and software to create intelligent machines."
        )


    if (
        "study" in text
        or "learn" in text
    ):

        return (
            "A practical learning strategy is:\n\n"
            "1. Define your goal.\n"
            "2. Learn the fundamentals.\n"
            "3. Practice with small projects.\n"
            "4. Build a real-world project.\n"
            "5. Review and improve regularly."
        )


    if "career" in text:

        return (
            "For a technology career, focus on "
            "fundamentals, practical projects, "
            "communication skills and a strong "
            "portfolio."
        )


    return (
        "🤖 Demo Mode is active.\n\n"
        "I can help with AI, Python, robotics, "
        "technology, education and productivity.\n\n"
        "For full AI-powered responses, add "
        "OPENAI_API_KEY to Streamlit Secrets."
    )


# ============================================================
# OPENAI TEXT RESPONSE
# ============================================================

def ask_openai(prompt):

    client = create_openai_client()

    if client is None:

        raise RuntimeError(
            "OpenAI API key is not configured."
        )


    conversation = []


    for message in st.session_state.messages[-12:]:

        role = message.get("role")

        if role not in [
            "user",
            "assistant",
        ]:
            continue


        conversation.append(
            {
                "role": role,
                "content": message.get(
                    "content",
                    "",
                ),
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


    answer = getattr(
        response,
        "output_text",
        None,
    )


    if not answer:

        raise RuntimeError(
            "OpenAI returned an empty response."
        )


    return answer.strip()


# ============================================================
# SPEECH TO TEXT
# ============================================================

def transcribe_audio(audio_file):

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


    mime_type = getattr(
        audio_file,
        "type",
        "audio/wav",
    )


    extension = ".wav"


    if "webm" in mime_type:

        extension = ".webm"

    elif "ogg" in mime_type:

        extension = ".ogg"

    elif "mp4" in mime_type:

        extension = ".mp4"

    elif "mpeg" in mime_type:

        extension = ".mp3"


    temp_path = None


    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_file:

            temp_file.write(
                audio_bytes
            )

            temp_path = (
                temp_file.name
            )


        with open(
            temp_path,
            "rb",
        ) as audio:

            result = (
                client.audio.transcriptions.create(
                    model=TRANSCRIPTION_MODEL,
                    file=audio,
                )
            )


        transcript = getattr(
            result,
            "text",
            "",
        )


        return transcript.strip()


    finally:

        if temp_path:

            try:

                os.remove(
                    temp_path
                )

            except Exception:

                pass


# ============================================================
# TEXT TO SPEECH
# ============================================================

def generate_speech(text):

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
# PROPER STREAMLIT HEADER
# ============================================================

st.title(
    "🤖 BAITHAK WITH AI"
)

st.subheader(
    "Your Intelligent Voice & Text AI Assistant"
)

st.caption(
    "Speak naturally, type your question, "
    "and interact with your AI assistant."
)


# ============================================================
# ROBOT
# ============================================================

show_animated_robot()


# ============================================================
# APPLICATION FLOW
# ============================================================

st.info(
    "🎤 Speech → 🧠 OpenAI → 💬 AI Response → 🔊 Voice"
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "🤖 BAITHAK WITH AI"
    )


    st.subheader(
        "⚙️ AI Configuration"
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
            if (
                st.session_state.mode
                == "OpenAI API Mode"
                and OPENAI_API_KEY
            )
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

            st.session_state.mode = (
                "OpenAI API Mode"
            )

        else:

            st.warning(
                "⚠️ Add OPENAI_API_KEY "
                "in Streamlit Secrets."
            )

            st.session_state.mode = (
                "Demo Mode"
            )


    else:

        st.session_state.mode = (
            "Demo Mode"
        )

        st.info(
            "🟡 Demo Mode active"
        )


    st.divider()


    st.subheader(
        "📋 Current Status"
    )


    if (
        st.session_state.mode
        == "OpenAI API Mode"
    ):

        st.success(
            "🧠 OpenAI API Mode"
        )

    else:

        st.info(
            "🤖 Demo Mode"
        )


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


    st.subheader(
        "🎤 Voice Pipeline"
    )


    st.markdown(
        """
        **Speech**

        ↓

        **OpenAI Transcription**

        ↓

        **AI Response**

        ↓

        **OpenAI Text-to-Speech**

        ↓

        🔊 **Voice**
        """
    )


# ============================================================
# MODE STATUS
# ============================================================

if (
    st.session_state.mode
    == "OpenAI API Mode"
):

    st.success(
        f"🧠 OpenAI API Mode Active • "
        f"{OPENAI_MODEL}"
    )

else:

    st.info(
        "🤖 Demo Mode Active — "
        "Add your OpenAI credentials "
        "to enable full AI."
    )


# ============================================================
# VOICE ASSISTANT
# ============================================================

st.header(
    "🎤 Voice Assistant"
)

st.write(
    "Record your question using your microphone. "
    "BAITHAK WITH AI will convert your speech "
    "into text and generate an AI response."
)


audio_input = st.audio_input(
    "🎤 Record your question"
)


# ============================================================
# VOICE PROCESSING
# ============================================================

if audio_input is not None:

    st.audio(
        audio_input,
        format=(
            audio_input.type
            if audio_input.type
            else "audio/wav"
        ),
    )


    if st.button(
        "🧠 Convert Speech to AI Response",
        use_container_width=True,
    ):

        if not OPENAI_API_KEY:

            st.warning(
                "⚠️ Kindly add your OpenAI API "
                "credentials in Streamlit Secrets."
            )

            st.info(
                "Speech-to-text requires "
                "OpenAI API access."
            )

        else:

            with st.spinner(
                "🎤 Converting speech to text..."
            ):

                try:

                    transcript = (
                        transcribe_audio(
                            audio_input
                        )
                    )


                    if not transcript:

                        st.warning(
                            "⚠️ No speech was detected."
                        )

                    else:

                        st.success(
                            f"📝 You said: "
                            f"{transcript}"
                        )


                        st.session_state.messages.append(
                            {
                                "role": "user",
                                "content": transcript,
                            }
                        )


                        try:

                            answer = ask_openai(
                                transcript
                            )

                        except Exception as error:

                            show_openai_error(
                                error
                            )

                            answer = demo_response(
                                transcript
                            )


                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                            }
                        )


                        st.session_state.last_answer = (
                            answer
                        )

                        st.session_state.voice_audio = (
                            None
                        )


                        st.rerun()


                except Exception as error:

                    show_openai_error(
                        error
                    )


# ============================================================
# CONVERSATION
# ============================================================

if st.session_state.messages:

    st.header(
        "💬 Conversation"
    )


    for message in st.session_state.messages:

        role = message.get(
            "role"
        )

        content = message.get(
            "content",
            "",
        )


        if role == "user":

            with st.chat_message(
                "user",
                avatar="👤",
            ):

                st.markdown(
                    content
                )


        elif role == "assistant":

            with st.chat_message(
                "assistant",
                avatar="🤖",
            ):

                st.markdown(
                    content
                )


# ============================================================
# TEXT CHAT
# ============================================================

st.header(
    "💬 Text Chat"
)


prompt = st.chat_input(
    "Type your message here..."
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


        if (
            st.session_state.mode
            == "OpenAI API Mode"
        ):

            with st.spinner(
                "🧠 BAITHAK WITH AI is thinking..."
            ):

                try:

                    answer = ask_openai(
                        prompt
                    )

                except Exception as error:

                    show_openai_error(
                        error
                    )

                    answer = demo_response(
                        prompt
                    )

        else:

            answer = demo_response(
                prompt
            )


        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )


        st.session_state.last_answer = (
            answer
        )

        st.session_state.voice_audio = (
            None
        )


        st.rerun()


# ============================================================
# TEXT TO SPEECH
# ============================================================

if st.session_state.last_answer:

    st.header(
        "🔊 AI Voice Response"
    )


    st.write(
        "Convert the latest AI response "
        "into natural speech using "
        "OpenAI Text-to-Speech."
    )


    if st.button(
        "🔊 Speak Latest AI Response",
        use_container_width=True,
    ):

        if not OPENAI_API_KEY:

            st.warning(
                "⚠️ Kindly add your OpenAI API "
                "credentials in Streamlit Secrets."
            )

        else:

            with st.spinner(
                "🔊 Generating AI voice..."
            ):

                try:

                    voice_data = (
                        generate_speech(
                            st.session_state.last_answer
                        )
                    )


                    st.session_state.voice_audio = (
                        voice_data
                    )


                except Exception as error:

                    show_openai_error(
                        error
                    )


    if st.session_state.voice_audio:

        st.audio(
            st.session_state.voice_audio,
            format="audio/mp3",
        )


        st.download_button(

            label="⬇️ Download AI Voice",

            data=(
                st.session_state.voice_audio
            ),

            file_name=(
                "baithak_ai_response.mp3"
            ),

            mime="audio/mpeg",

            use_container_width=True,
        )


# ============================================================
# FOOTER
# ============================================================

current_year = datetime.now().year


st.divider()


st.caption(
    f"BAITHAK WITH AI • OpenAI Powered • {current_year}"
)


st.markdown(
    "**Designed by Certified Generative and "
    "Agentic AI Application Developer — "
    "Engr. Bilal Mehmood**"
)
