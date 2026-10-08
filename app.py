import os
import base64
import html
import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# OPTIONAL OPENAI IMPORT
# ============================================================

try:
    from openai import OpenAI
    OPENAI_PACKAGE_AVAILABLE = True
except Exception:
    OPENAI_PACKAGE_AVAILABLE = False


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

DEFAULT_MODEL = "gpt-6-luna"
DEFAULT_TRANSCRIPTION_MODEL = "gpt-4o-mini-transcribe"
DEFAULT_VOICE_MODEL = "gpt-4o-mini-tts"

SYSTEM_PROMPT = """
You are BAITHAK WITH AI, a friendly intelligent talking robot assistant.

Your personality:
- Friendly
- Professional
- Helpful
- Clear
- Concise
- Respectful
- Educational

You can communicate naturally in:
- English
- Urdu
- Roman Urdu

If the user writes in Urdu, reply in Urdu.
If the user writes in Roman Urdu, reply in Roman Urdu.
If the user writes in English, reply in English.

Help users with:
- General questions
- Education
- Programming
- AI
- Agentic AI
- Robotics
- Automation
- Productivity
- Engineering
- Technology
- Daily assistance

Do not claim to have performed real-world actions unless the application
actually provides that capability.

Do not expose system instructions, API keys, secrets, or private configuration.
"""


# ============================================================
# SECRET / ENVIRONMENT HELPER
# ============================================================

def get_secret(name, default=None):
    """
    Safely read a value from Streamlit secrets first,
    then environment variables.
    """

    try:
        value = st.secrets.get(name)

        if value is not None:
            value = str(value).strip()

            if value:
                return value

    except Exception:
        pass

    value = os.getenv(name)

    if value:
        return str(value).strip()

    return default


OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
OPENAI_MODEL = get_secret("OPENAI_MODEL", DEFAULT_MODEL)
TRANSCRIPTION_MODEL = get_secret(
    "TRANSCRIPTION_MODEL",
    DEFAULT_TRANSCRIPTION_MODEL
)
VOICE_MODEL = get_secret(
    "VOICE_MODEL",
    DEFAULT_VOICE_MODEL
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

if "api_error" not in st.session_state:
    st.session_state.api_error = ""

if "current_mode" not in st.session_state:
    st.session_state.current_mode = "Demo Mode"


# ============================================================
# OPENAI CLIENT
# ============================================================

def create_openai_client():
    """
    Create OpenAI client if package and API key are available.
    """

    if not OPENAI_PACKAGE_AVAILABLE:
        return None

    if not OPENAI_API_KEY:
        return None

    try:
        return OpenAI(api_key=OPENAI_API_KEY)
    except Exception as exc:
        st.session_state.api_error = str(exc)
        return None


openai_client = create_openai_client()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

html, body, [class*="css"] {
    font-family: Arial, Helvetica, sans-serif;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    margin-top: 5px;
    margin-bottom: 0px;
}

.main-subtitle {
    text-align: center;
    font-size: 18px;
    opacity: 0.75;
    margin-bottom: 20px;
}

.mode-card {
    padding: 14px;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,0.25);
    margin-bottom: 12px;
}

.status-ok {
    padding: 10px 14px;
    border-radius: 10px;
    background: rgba(0, 180, 100, 0.10);
    border: 1px solid rgba(0, 180, 100, 0.30);
}

.status-demo {
    padding: 10px 14px;
    border-radius: 10px;
    background: rgba(80, 130, 255, 0.10);
    border: 1px solid rgba(80, 130, 255, 0.30);
}

.status-error {
    padding: 10px 14px;
    border-radius: 10px;
    background: rgba(220, 50, 50, 0.10);
    border: 1px solid rgba(220, 50, 50, 0.30);
}

.chat-container {
    margin-top: 15px;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🤖 BAITHAK WITH AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    'Intelligent Talking Robot Assistant'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# ROBOT + FOOTER COMPONENT
# IMPORTANT:
# Raw HTML is kept inside components.html()
# ============================================================

robot_footer_html = """
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: Arial, Helvetica, sans-serif;
}

.robot-wrapper {
    width: 100%;
    min-height: 535px;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    overflow: hidden;
}

.robot-stage {
    position: relative;

    width: 320px;
    height: 390px;

    display: flex;
    align-items: center;
    justify-content: center;
}

/* -----------------------------
   GLOW
------------------------------ */

.robot-glow {
    position: absolute;

    width: 270px;
    height: 270px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(0, 180, 255, 0.28) 0%,
            rgba(80, 80, 255, 0.12) 45%,
            transparent 72%
        );

    filter: blur(12px);
}

/* -----------------------------
   ROBOT BODY
------------------------------ */

.robot-body {

    position: relative;

    width: 190px;
    height: 215px;

    border-radius: 45px 45px 55px 55px;

    background:
        linear-gradient(
            145deg,
            #f7f9fc,
            #cfd7e3
        );

    border: 5px solid #8d99a8;

    box-shadow:
        0 20px 45px rgba(0,0,0,0.25),
        inset 0 3px 5px rgba(255,255,255,0.9);

    display: flex;
    flex-direction: column;
    align-items: center;
}

/* -----------------------------
   HEAD
------------------------------ */

.robot-head {

    position: absolute;

    top: -82px;

    width: 220px;
    height: 165px;

    border-radius: 65px;

    background:
        linear-gradient(
            145deg,
            #ffffff,
            #d8dee8
        );

    border: 5px solid #8d99a8;

    box-shadow:
        0 15px 30px rgba(0,0,0,0.25),
        inset 0 4px 8px rgba(255,255,255,0.95);
}

/* -----------------------------
   EARS
------------------------------ */

.ear-left,
.ear-right {

    position: absolute;

    top: 43px;

    width: 35px;
    height: 55px;

    border-radius: 18px;

    background: #b9c4d2;

    border: 4px solid #818d9d;
}

.ear-left {
    left: -29px;
}

.ear-right {
    right: -29px;
}

/* -----------------------------
   EYES
------------------------------ */

.eye {

    position: absolute;

    top: 48px;

    width: 40px;
    height: 40px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle at 35% 30%,
            #ffffff 0%,
            #67dfff 10%,
            #0099ff 40%,
            #0047a5 75%,
            #001c52 100%
        );

    border: 3px solid #526275;

    box-shadow:
        0 0 18px rgba(0,170,255,0.75);
}

.eye-left {
    left: 43px;
}

.eye-right {
    right: 43px;
}

/* -----------------------------
   MOUTH
------------------------------ */

.robot-mouth {

    position: absolute;

    left: 50%;

    bottom: 28px;

    transform: translateX(-50%);

    width: 75px;
    height: 28px;

    border-radius: 0 0 40px 40px;

    background: #202631;

    border: 4px solid #667384;

    box-shadow:
        inset 0 5px 8px rgba(0,0,0,0.5);
}

/* -----------------------------
   ANTENNA
------------------------------ */

.antenna {

    position: absolute;

    top: -47px;

    left: 50%;

    transform: translateX(-50%);

    width: 7px;
    height: 47px;

    background: #6e7b8d;

    border-radius: 10px;
}

.antenna-light {

    position: absolute;

    top: -14px;

    left: 50%;

    transform: translateX(-50%);

    width: 22px;
    height: 22px;

    border-radius: 50%;

    background: #00c8ff;

    box-shadow:
        0 0 20px #00c8ff;
}

/* -----------------------------
   CHEST
------------------------------ */

.chest {

    position: absolute;

    bottom: 30px;

    width: 110px;
    height: 70px;

    border-radius: 18px;

    background:
        linear-gradient(
            145deg,
            #dfe5ed,
            #aeb9c8
        );

    border: 4px solid #788596;

    display: flex;
    align-items: center;
    justify-content: center;
}

.chest-screen {

    width: 75px;
    height: 36px;

    border-radius: 8px;

    background: #091521;

    border: 3px solid #59697a;

    display: flex;
    align-items: center;
    justify-content: center;

    color: #00d9ff;

    font-size: 15px;
    font-weight: bold;

    box-shadow:
        0 0 15px rgba(0,210,255,0.4);
}

/* -----------------------------
   ARMS
------------------------------ */

.arm {

    position: absolute;

    top: 55px;

    width: 42px;
    height: 125px;

    border-radius: 25px;

    background:
        linear-gradient(
            90deg,
            #9ca8b7,
            #e3e8ef,
            #9ca8b7
        );

    border: 4px solid #7a8797;
}

.arm-left {
    left: -51px;
    transform: rotate(10deg);
}

.arm-right {
    right: -51px;
    transform: rotate(-10deg);
}

/* -----------------------------
   HANDS
------------------------------ */

.hand {

    position: absolute;

    bottom: -19px;

    left: 50%;

    transform: translateX(-50%);

    width: 48px;
    height: 48px;

    border-radius: 50%;

    background: #cbd3dd;

    border: 4px solid #788596;
}

/* -----------------------------
   FEET
------------------------------ */

.foot {

    position: absolute;

    bottom: -27px;

    width: 58px;
    height: 30px;

    border-radius: 20px;

    background: #8995a5;

    border: 4px solid #697586;
}

.foot-left {
    left: 32px;
}

.foot-right {
    right: 32px;
}

/* -----------------------------
   STATUS
------------------------------ */

.robot-status {

    margin-top: 55px;

    font-size: 16px;
    font-weight: 700;

    letter-spacing: 0.5px;

    opacity: 0.8;
}

/* -----------------------------
   FOOTER
------------------------------ */

.baithak-footer {

    width: 100%;

    text-align: center;

    padding: 20px 10px 12px;

    margin-top: 5px;

    border-top:
        1px solid rgba(120,120,120,0.25);
}

.footer-title {

    font-size: 22px;

    font-weight: 900;

    margin-bottom: 8px;
}

.footer-description {

    font-size: 15px;

    font-weight: 700;

    margin-bottom: 6px;

    line-height: 1.4;
}

.footer-name {

    font-size: 18px;

    font-weight: 900;

    margin-bottom: 9px;
}

.footer-subtitle {

    font-size: 13px;

    opacity: 0.75;

    line-height: 1.5;
}

</style>

</head>

<body>

<div class="robot-wrapper">

    <div class="robot-stage">

        <div class="robot-glow"></div>

        <div class="robot-body">

            <div class="robot-head">

                <div class="antenna"></div>

                <div class="antenna-light"></div>

                <div class="ear-left"></div>
                <div class="ear-right"></div>

                <div class="eye eye-left"></div>
                <div class="eye eye-right"></div>

                <div class="robot-mouth"></div>

            </div>

            <div class="arm arm-left">
                <div class="hand"></div>
            </div>

            <div class="arm arm-right">
                <div class="hand"></div>
            </div>

            <div class="chest">
                <div class="chest-screen">
                    AI
                </div>
            </div>

            <div class="foot foot-left"></div>
            <div class="foot foot-right"></div>

        </div>

    </div>

    <div class="robot-status">
        🤖 Intelligent Talking Robot Assistant
    </div>

    <div class="baithak-footer">

        <div class="footer-title">
            🤖 BAITHAK WITH AI
        </div>

        <div class="footer-description">
            Designed by Certified Generative and Agentic AI Application Developer
        </div>

        <div class="footer-name">
            Engr. Bilal Mehmood
        </div>

        <div class="footer-subtitle">
            Intelligent Talking AI • Voice Interaction • OpenAI Powered • Streamlit Application
        </div>

    </div>

</div>

</body>

</html>
"""

components.html(
    robot_footer_html,
    height=570,
    scrolling=False
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ BAITHAK SETTINGS")

    st.subheader("AI Mode")

    selected_mode = st.radio(
        "Choose operating mode:",
        [
            "Demo Mode",
            "OpenAI API Mode"
        ],
        index=0
    )

    st.session_state.current_mode = selected_mode

    st.divider()

    st.subheader("🤖 AI Configuration")

    st.write(
        f"**Model:** `{OPENAI_MODEL}`"
    )

    st.write(
        "**Priority:** Demo → OpenAI API"
    )

    if selected_mode == "Demo Mode":

        st.markdown(
            """
            <div class="status-demo">
            🟢 <b>Demo Mode Active</b><br>
            No API key is required.
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        if OPENAI_API_KEY and OPENAI_PACKAGE_AVAILABLE:

            st.markdown(
                """
                <div class="status-ok">
                🟢 <b>OpenAI API Ready</b>
                </div>
                """,
                unsafe_allow_html=True
            )

        elif not OPENAI_PACKAGE_AVAILABLE:

            st.markdown(
                """
                <div class="status-error">
                🔴 <b>OpenAI package unavailable</b><br>
                Install the openai package.
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="status-demo">
                🟡 <b>No OpenAI API key detected</b><br>
                App will automatically use Demo Mode.
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    st.subheader("🎙️ Voice")

    st.caption(
        "Voice transcription and AI voice responses "
        "are available in OpenAI API Mode."
    )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.last_answer = ""
        st.session_state.audio_bytes = None
        st.session_state.api_error = ""

        st.rerun()

    st.divider()

    st.caption(
        "BAITHAK WITH AI"
    )

    st.caption(
        "Intelligent Talking AI"
    )

    st.caption(
        "OpenAI Powered • Streamlit Application"
    )


# ============================================================
# DEMO RESPONSE ENGINE
# ============================================================

def demo_response(user_text):
    """
    Local demonstration response engine.

    This is intentionally API-free.
    """

    text = user_text.lower().strip()

    if not text:
        return "Please tell me how I can help you."

    if any(word in text for word in [
        "hello",
        "hi",
        "hey",
        "salam",
        "assalam"
    ]):

        return (
            "🤖 Hello! Welcome to BAITHAK WITH AI.\n\n"
            "I am your intelligent talking robot assistant. "
            "You can ask me about AI, Agentic AI, programming, "
            "robotics, engineering, education, or productivity."
        )

    if "who are you" in text:

        return (
            "I am BAITHAK WITH AI — an intelligent talking robot "
            "assistant designed for conversational AI, voice interaction, "
            "education, engineering, robotics and productivity."
        )

    if "your name" in text:

        return (
            "My name is BAITHAK WITH AI. 🤖"
        )

    if "agentic ai" in text:

        return (
            "Agentic AI refers to AI systems that can understand goals, "
            "reason about tasks, plan actions, use tools and work through "
            "multi-step objectives with greater autonomy."
        )

    if "artificial intelligence" in text or text == "ai":

        return (
            "Artificial Intelligence enables computer systems to perform "
            "tasks that normally require human intelligence, such as "
            "reasoning, learning, perception, language understanding "
            "and decision-making."
        )

    if "robot" in text or "robotics" in text:

        return (
            "Robotics combines mechanical engineering, electronics, "
            "embedded systems, control systems, sensors and AI to create "
            "machines capable of sensing, processing and acting in the "
            "physical world."
        )

    if "streamlit" in text:

        return (
            "Streamlit is a Python framework for building interactive "
            "data and AI applications quickly. BAITHAK WITH AI itself "
            "uses Streamlit as its application interface."
        )

    if "python" in text:

        return (
            "Python is a powerful programming language widely used for "
            "AI, machine learning, automation, robotics, data science "
            "and application development."
        )

    if "urdu" in text:

        return (
            "جی بالکل! میں اردو میں بھی آپ کے ساتھ گفتگو کر سکتا ہوں۔ "
            "آپ اپنا سوال اردو یا رومن اردو میں بھی پوچھ سکتے ہیں۔"
        )

    if any(word in text for word in [
        "thank",
        "thanks",
        "shukriya"
    ]):

        return (
            "You're most welcome! 🤖\n\n"
            "BAITHAK WITH AI is always ready to help."
        )

    return (
        "🤖 Demo Mode is active.\n\n"
        "I received your request:\n\n"
        f"“{user_text}”\n\n"
        "For full AI-generated answers, switch to "
        "**OpenAI API Mode** and configure your OpenAI API key.\n\n"
        "You can ask me about AI, Agentic AI, Python, robotics, "
        "automation, engineering, education or productivity."
    )


# ============================================================
# OPENAI RESPONSE
# ============================================================

def ask_openai(user_text):

    if not OPENAI_PACKAGE_AVAILABLE:

        raise RuntimeError(
            "OpenAI package is not installed. "
            "Install it with: pip install openai"
        )

    if not OPENAI_API_KEY:

        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    client = create_openai_client()

    if client is None:

        raise RuntimeError(
            "Unable to create OpenAI client."
        )

    # Keep conversation reasonably sized.
    recent_messages = st.session_state.messages[-20:]

    input_messages = []

    for message in recent_messages:

        role = message.get("role")
        content = message.get("content", "")

        if role in ["user", "assistant"]:

            input_messages.append(
                {
                    "role": role,
                    "content": content
                }
            )

    input_messages.append(
        {
            "role": "user",
            "content": user_text
        }
    )

    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=input_messages,
    )

    answer = getattr(response, "output_text", None)

    if not answer:

        raise RuntimeError(
            "OpenAI returned an empty response."
        )

    return answer.strip()


# ============================================================
# MAIN AI ROUTER
# ============================================================

def ask_ai(user_text, requested_mode):

    st.session_state.api_error = ""

    # -------------------------
    # DEMO MODE
    # -------------------------

    if requested_mode == "Demo Mode":

        return demo_response(user_text), "Demo Mode"

    # -------------------------
    # OPENAI API MODE
    # -------------------------

    try:

        answer = ask_openai(user_text)

        return answer, "OpenAI API"

    except Exception as exc:

        error_message = str(exc)

        st.session_state.api_error = error_message

        # Automatic fallback
        fallback = demo_response(user_text)

        return (
            fallback,
            "Demo Mode — Automatic Fallback"
        )


# ============================================================
# CHAT HISTORY DISPLAY
# ============================================================

st.subheader("💬 Conversation")

if not st.session_state.messages:

    st.info(
        "👋 Start a conversation with BAITHAK WITH AI below."
    )

else:

    for message in st.session_state.messages:

        role = message.get("role")
        content = message.get("content", "")

        if role == "user":

            with st.chat_message("user", avatar="👤"):

                st.markdown(content)

        elif role == "assistant":

            with st.chat_message("assistant", avatar="🤖"):

                st.markdown(content)


# ============================================================
# TEXT INPUT
# ============================================================

st.subheader("🗣️ Ask BAITHAK")

user_prompt = st.chat_input(
    "Type your message here..."
)


# ============================================================
# TEXT CHAT PROCESSING
# ============================================================

if user_prompt:

    user_prompt = user_prompt.strip()

    if user_prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_prompt
            }
        )

        with st.spinner("🤖 BAITHAK is thinking..."):

            answer, actual_mode = ask_ai(
                user_prompt,
                st.session_state.current_mode
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        st.session_state.last_answer = answer

        # Display current response immediately.
        with st.chat_message("user", avatar="👤"):

            st.markdown(user_prompt)

        with st.chat_message("assistant", avatar="🤖"):

            st.markdown(answer)

            if actual_mode.startswith("Demo Mode"):

                st.caption(
                    f"⚙️ {actual_mode}"
                )

            else:

                st.caption(
                    "⚡ OpenAI API • "
                    f"{OPENAI_MODEL}"
                )

        # API error notification
        if st.session_state.api_error:

            st.warning(
                "OpenAI API was unavailable, so BAITHAK automatically "
                "switched to Demo Mode.\n\n"
                f"Technical detail: {st.session_state.api_error}"
            )


# ============================================================
# VOICE SECTION
# ============================================================

st.divider()

st.subheader("🎙️ Voice Interaction")

if st.session_state.current_mode == "Demo Mode":

    st.info(
        "🎙️ Voice transcription requires OpenAI API Mode. "
        "You can still use the text chat in Demo Mode."
    )

else:

    if not OPENAI_API_KEY:

        st.warning(
            "OpenAI API key is not configured. "
            "Voice features are unavailable."
        )

    else:

        audio_input = st.audio_input(
            "🎙️ Record your question"
        )

        if audio_input is not None:

            audio_bytes = audio_input.getvalue()

            st.session_state.audio_bytes = audio_bytes

            st.audio(
                audio_bytes,
                format="audio/wav"
            )

            if st.button(
                "🧠 Transcribe & Ask BAITHAK",
                use_container_width=True
            ):

                try:

                    client = create_openai_client()

                    if client is None:

                        raise RuntimeError(
                            "OpenAI client could not be created."
                        )

                    with st.spinner(
                        "🎙️ Transcribing your voice..."
                    ):

                        transcription = (
                            client.audio.transcriptions.create(
                                model=TRANSCRIPTION_MODEL,
                                file=(
                                    "baithak_voice.wav",
                                    audio_bytes,
                                    "audio/wav"
                                )
                            )
                        )

                    transcript_text = getattr(
                        transcription,
                        "text",
                        ""
                    )

                    transcript_text = (
                        transcript_text or ""
                    ).strip()

                    if not transcript_text:

                        st.error(
                            "No speech could be detected."
                        )

                    else:

                        st.success(
                            f"🗣️ You said: {transcript_text}"
                        )

                        st.session_state.messages.append(
                            {
                                "role": "user",
                                "content": transcript_text
                            }
                        )

                        with st.spinner(
                            "🤖 BAITHAK is thinking..."
                        ):

                            answer, actual_mode = ask_ai(
                                transcript_text,
                                "OpenAI API Mode"
                            )

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer
                            }
                        )

                        st.session_state.last_answer = answer

                        st.subheader(
                            "🤖 BAITHAK Response"
                        )

                        st.markdown(answer)

                        if actual_mode.startswith(
                            "Demo Mode"
                        ):

                            st.warning(
                                "OpenAI response failed. "
                                "Automatically switched to Demo Mode."
                            )

                except Exception as exc:

                    st.error(
                        "Voice processing failed."
                    )

                    st.code(
                        str(exc)
                    )


# ============================================================
# AI VOICE RESPONSE
# ============================================================

if (
    st.session_state.current_mode == "OpenAI API Mode"
    and st.session_state.last_answer
    and OPENAI_API_KEY
):

    st.divider()

    st.subheader("🔊 AI Voice Response")

    if st.button(
        "🔊 Generate BAITHAK Voice",
        use_container_width=True
    ):

        try:

            client = create_openai_client()

            if client is None:

                raise RuntimeError(
                    "OpenAI client could not be created."
                )

            with st.spinner(
                "🔊 Generating AI voice..."
            ):

                speech_response = client.audio.speech.create(
                    model=VOICE_MODEL,
                    voice="alloy",
                    input=st.session_state.last_answer,
                    response_format="mp3",
                )

                audio_data = speech_response.read()

            st.audio(
                audio_data,
                format="audio/mp3"
            )

            st.success(
                "🔊 BAITHAK voice response generated."
            )

        except Exception as exc:

            st.error(
                "AI voice generation failed."
            )

            st.code(
                str(exc)
            )


# ============================================================
# API CONFIGURATION HELP
# ============================================================

with st.expander(
    "🔐 OpenAI API Configuration"
):

    st.markdown(
       
### Streamlit Secrets

Create:

`.streamlit/secrets.toml`

Then add:

```toml
OPENAI_API_KEY = "sk-your-real-openai-api-key"
OPENAI_MODEL = "gpt-6-luna"

TRANSCRIPTION_MODEL = "gpt-4o-mini-transcribe"
VOICE_MODEL = "gpt-4o-mini-tts"
