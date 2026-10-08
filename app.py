
import os
import base64
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI


# ============================================================
# BAITHAK WITH AI
# Intelligent Talking Robot Assistant
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
DEFAULT_TRANSCRIPTION_MODEL = "gpt-4o-mini-transcribe"
DEFAULT_VOICE_MODEL = "gpt-4o-mini-tts"

SYSTEM_PROMPT = """
You are BAITHAK WITH AI.

You are a friendly, intelligent and conversational AI robot
assistant sitting with the user in a virtual baithak.

Personality:
- Friendly
- Intelligent
- Helpful
- Respectful
- Professional
- Conversational
- Warm

Languages:
- English
- Urdu
- Roman Urdu

If the user speaks Urdu, answer naturally in Urdu or Roman Urdu.
If the user speaks English, answer in English.

Keep ordinary answers concise.
Provide detailed answers when requested.

Never claim that you performed a real-world action unless the
application actually performed it.
"""


# ============================================================
# SECRET / ENVIRONMENT VARIABLE
# ============================================================

def get_secret(name, default=""):
    try:
        value = st.secrets.get(name)

        if value:
            return str(value).strip()

    except Exception:
        pass

    return os.getenv(name, default)


OPENAI_API_KEY = get_secret("OPENAI_API_KEY")

OPENAI_MODEL = get_secret(
    "OPENAI_MODEL",
    DEFAULT_MODEL
)

TRANSCRIPTION_MODEL = get_secret(
    "TRANSCRIPTION_MODEL",
    DEFAULT_TRANSCRIPTION_MODEL
)

VOICE_MODEL = get_secret(
    "VOICE_MODEL",
    DEFAULT_VOICE_MODEL
)


# ============================================================
# OPENAI CLIENT
# ============================================================

client = None

if OPENAI_API_KEY:

    try:
        client = OpenAI(
            api_key=OPENAI_API_KEY
        )

    except Exception:
        client = None


# ============================================================
# SESSION STATE
# ============================================================

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

if "api_error" not in st.session_state:
    st.session_state.api_error = ""


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>

@import url(
    'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&display=swap'
);

html,
body,
[class*="css"] {
    font-family: 'Orbitron', sans-serif;
}

.stApp {

    background:
        radial-gradient(
            circle at 50% 10%,
            rgba(0, 220, 255, 0.16),
            transparent 30%
        ),

        radial-gradient(
            circle at 10% 90%,
            rgba(0, 255, 160, 0.08),
            transparent 30%
        ),

        #030712;

    color: white;
}


/* ==========================================================
   TITLE
   ========================================================== */

.baithak-title {

    text-align: center;

    font-size: clamp(32px, 5vw, 60px);

    font-weight: 800;

    letter-spacing: 5px;

    color: #00eaff;

    text-shadow:
        0 0 10px #00eaff,
        0 0 25px #00eaff,
        0 0 55px rgba(0,234,255,.55);

    margin-top: 5px;
}


.baithak-subtitle {

    text-align: center;

    font-size: 14px;

    letter-spacing: 3px;

    color: #9beafa;

    margin-bottom: 25px;
}


/* ==========================================================
   CHAT PANEL
   ========================================================== */

.chat-panel {

    background: rgba(7,18,35,.75);

    border: 1px solid rgba(0,234,255,.25);

    border-radius: 20px;

    padding: 18px;

}


/* ==========================================================
   FOOTER
   ========================================================== */

.baithak-footer {

    margin-top: 45px;

    padding: 28px 15px;

    text-align: center;

    border-top: 1px solid rgba(0,234,255,.25);

    background:
        linear-gradient(
            180deg,
            rgba(0,234,255,.02),
            rgba(0,234,255,.08)
        );
}


.footer-title {

    font-size: 16px;

    font-weight: 700;

    letter-spacing: 2px;

    color: #00eaff;

    text-shadow:
        0 0 10px rgba(0,234,255,.6);
}


.footer-name {

    margin-top: 10px;

    font-size: 18px;

    font-weight: 800;

    color: white;
}


.footer-line {

    margin-top: 12px;

    font-size: 12px;

    color: #7fa0b3;

    letter-spacing: 1px;
}


.footer-tech {

    margin-top: 15px;

    color: #00ffae;

    font-size: 12px;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# FUNCTIONS
# ============================================================

def ask_ai(user_text):

    if client is None:

        return (
            "⚠️ OpenAI is not connected.\n\n"
            "Please add OPENAI_API_KEY to Streamlit Secrets."
        )

    user_message = {
        "role": "user",
        "content": user_text
    }

    st.session_state.conversation.append(
        user_message
    )

    history = st.session_state.conversation[-20:]

    try:

        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=history,
        )

        answer = response.output_text

        if not answer:
            answer = (
                "Sorry, I could not generate a response."
            )

        st.session_state.conversation.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        st.session_state.last_answer = answer

        return answer

    except Exception as error:

        if st.session_state.conversation:

            if (
                st.session_state.conversation[-1]["role"]
                == "user"
            ):
                st.session_state.conversation.pop()

        st.session_state.api_error = str(error)

        return (
            "⚠️ OpenAI request failed.\n\n"
            f"{error}"
        )


# ============================================================
# SPEECH TO TEXT
# ============================================================

def transcribe_audio(audio_file):

    if client is None:
        return None, "OpenAI is not connected."

    try:

        audio_file.seek(0)

        result = client.audio.transcriptions.create(
            model=TRANSCRIPTION_MODEL,
            file=audio_file,
        )

        text = getattr(
            result,
            "text",
            ""
        )

        if not text:
            return None, "No speech was detected."

        return text.strip(), None

    except Exception as error:

        return None, str(error)


# ============================================================
# TEXT TO SPEECH
# ============================================================

def create_voice(text):

    if client is None:
        return None, "OpenAI is not connected."

    try:

        speech = client.audio.speech.create(
            model=VOICE_MODEL,
            voice="alloy",
            input=text,
            response_format="mp3",
        )

        audio_bytes = speech.read()

        return audio_bytes, None

    except Exception as error:

        return None, str(error)


# ============================================================
# AUDIO PLAYER
# ============================================================

def make_audio_player(audio_bytes):

    encoded = base64.b64encode(
        audio_bytes
    ).decode("utf-8")

    return f"""
    <audio controls autoplay style="width:100%;">
        <source
            src="data:audio/mp3;base64,{encoded}"
            type="audio/mp3"
        >
    </audio>
    """


# ============================================================
# ROBOT HTML
# ============================================================

def render_robot():

    robot_html = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<style>

* {
    box-sizing: border-box;
}

html,
body {

    margin: 0;
    padding: 0;

    width: 100%;
    height: 100%;

    background: transparent;

    overflow: hidden;
}


/* ============================================================
   ROBOT STAGE
   ============================================================ */

.robot-container {

    position: relative;

    width: 100%;

    height: 490px;

    display: flex;

    justify-content: center;

    align-items: center;

}


/* ============================================================
   GLOW
   ============================================================ */

.robot-glow {

    position: absolute;

    width: 330px;

    height: 330px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(0,225,255,0.28),
            rgba(0,225,255,0.08) 50%,
            transparent 72%
        );

    animation: glowPulse 2.5s ease-in-out infinite;

    z-index: 1;
}


@keyframes glowPulse {

    0%,
    100% {

        transform: scale(0.90);

        opacity: 0.55;
    }

    50% {

        transform: scale(1.12);

        opacity: 1;
    }
}


/* ============================================================
   ROBOT
   ============================================================ */

.robot {

    position: relative;

    width: 270px;

    height: 380px;

    z-index: 5;

    animation: robotFloat 3s ease-in-out infinite;
}


@keyframes robotFloat {

    0%,
    100% {

        transform: translateY(0px);
    }

    50% {

        transform: translateY(-17px);
    }
}


/* ============================================================
   ANTENNA
   ============================================================ */

.antenna {

    position: absolute;

    top: -52px;

    left: 131px;

    width: 7px;

    height: 52px;

    background: #bdf8ff;

    border-radius: 5px;

    box-shadow:
        0 0 15px #00eaff;
}


.antenna-light {

    position: absolute;

    top: -77px;

    left: 120px;

    width: 28px;

    height: 28px;

    border-radius: 50%;

    background: #00ffae;

    box-shadow:
        0 0 10px #00ffae,
        0 0 30px #00ffae;

    animation: antennaPulse 1.2s infinite;
}


@keyframes antennaPulse {

    0%,
    100% {

        transform: scale(0.75);
    }

    50% {

        transform: scale(1.2);
    }
}


/* ============================================================
   HEAD
   ============================================================ */

.robot-head {

    position: absolute;

    top: 0;

    left: 30px;

    width: 215px;

    height: 165px;

    border-radius: 45px;

    background:
        linear-gradient(
            145deg,
            #eefaff,
            #72869b
        );

    border: 5px solid #a5f4ff;

    box-shadow:
        0 0 18px #00eaff,
        0 0 45px rgba(0,234,255,.7),
        inset 0 0 25px rgba(255,255,255,.45);
}


/* ============================================================
   FACE SCREEN
   ============================================================ */

.face-screen {

    position: absolute;

    left: 30px;

    top: 35px;

    width: 150px;

    height: 90px;

    border-radius: 27px;

    background: #020a13;

    border: 3px solid #00eaff;

    box-shadow:
        inset 0 0 25px #00eaff,
        0 0 15px rgba(0,234,255,.5);
}


/* ============================================================
   EYES
   ============================================================ */

.eye {

    position: absolute;

    top: 18px;

    width: 28px;

    height: 38px;

    border-radius: 50%;

    background: #00f6ff;

    box-shadow:
        0 0 12px #00f6ff,
        0 0 25px #00f6ff;

    animation: blink 4s infinite;
}


.eye-left {

    left: 28px;
}


.eye-right {

    right: 28px;
}


@keyframes blink {

    0%,
    90%,
    100% {

        transform: scaleY(1);
    }

    94% {

        transform: scaleY(0.08);
    }
}


/* ============================================================
   MOUTH
   ============================================================ */

.mouth {

    position: absolute;

    left: 58px;

    bottom: 10px;

    width: 34px;

    height: 8px;

    border-radius: 20px;

    background: #00f6ff;

    box-shadow:
        0 0 14px #00f6ff;

    animation: robotTalk 0.9s infinite;
}


@keyframes robotTalk {

    0%,
    100% {

        height: 7px;

        width: 34px;
    }

    50% {

        height: 22px;

        width: 28px;
    }
}


/* ============================================================
   BODY
   ============================================================ */

.robot-body {

    position: absolute;

    top: 175px;

    left: 62px;

    width: 145px;

    height: 130px;

    border-radius: 30px;

    background:
        linear-gradient(
            145deg,
            #e8f7ff,
            #61758b
        );

    border: 5px solid #a5f4ff;

    box-shadow:
        0 0 20px #00eaff,
        inset 0 0 20px rgba(255,255,255,.3);
}


/* ============================================================
   CHEST
   ============================================================ */

.chest {

    position: absolute;

    top: 29px;

    left: 28px;

    width: 84px;

    height: 62px;

    border-radius: 15px;

    background: #020a13;

    border: 3px solid #00eaff;

    box-shadow:
        inset 0 0 20px #00eaff;
}


.chest-core {

    position: absolute;

    left: 31px;

    top: 18px;

    width: 18px;

    height: 18px;

    border-radius: 50%;

    background: #00ffae;

    box-shadow:
        0 0 12px #00ffae,
        0 0 28px #00ffae;

    animation: corePulse 1.2s infinite;
}


@keyframes corePulse {

    0%,
    100% {

        transform: scale(0.75);
    }

    50% {

        transform: scale(1.2);
    }
}


/* ============================================================
   ARMS
   ============================================================ */

.arm {

    position: absolute;

    top: 180px;

    width: 38px;

    height: 110px;

    border-radius: 25px;

    background:
        linear-gradient(
            #b5cadb,
            #52667a
        );

    border: 4px solid #a5f4ff;

    box-shadow:
        0 0 15px #00eaff;
}


.arm-left {

    left: 16px;

    transform: rotate(12deg);
}


.arm-right {

    right: 16px;

    transform: rotate(-12deg);
}


/* ============================================================
   STATUS
   ============================================================ */

.robot-status {

    text-align: center;

    margin-top: -5px;

    font-family: Arial, sans-serif;
}


.status-pill {

    display: inline-block;

    padding: 10px 25px;

    border-radius: 30px;

    color: #00eaff;

    border: 1px solid #00eaff;

    background: rgba(0,234,255,.08);

    box-shadow:
        0 0 20px rgba(0,234,255,.25);

    font-size: 14px;

    letter-spacing: 1px;
}

</style>

</head>


<body>

<div class="robot-container">

    <div class="robot-glow"></div>

    <div class="robot">

        <div class="antenna"></div>

        <div class="antenna-light"></div>

        <div class="robot-head">

            <div class="face-screen">

                <div class="eye eye-left"></div>

                <div class="eye eye-right"></div>

                <div class="mouth"></div>

            </div>

        </div>


        <div class="robot-body">

            <div class="chest">

                <div class="chest-core"></div>

            </div>

        </div>


        <div class="arm arm-left"></div>

        <div class="arm arm-right"></div>

    </div>

</div>


<div class="robot-status">

    <span class="status-pill">
        🟢 BAITHAK IS READY
    </span>

</div>


</body>

</html>
"""

    components.html(
        robot_html,
        height=570,
        scrolling=False
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="baithak-title">
        🤖 BAITHAK WITH AI
    </div>

    <div class="baithak-subtitle">
        YOUR INTELLIGENT TALKING AI COMPANION
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ⚙️ BAITHAK SETTINGS")

    if client:

        st.success(
            "🟢 OPENAI CONNECTED"
        )

    else:

        st.error(
            "🔴 OPENAI NOT CONNECTED"
        )

    st.markdown("---")

    st.markdown("### 🧠 AI MODEL")

    st.code(
        OPENAI_MODEL
    )

    st.markdown("### 🎙️ VOICE")

    voice_enabled = st.toggle(
        "Enable AI Voice",
        value=True
    )

    st.markdown("---")

    st.markdown("### 🔐 API SECURITY")

    st.info(
        "API key is loaded securely from Streamlit Secrets."
    )

    st.markdown("---")

    if st.button(
        "🗑️ CLEAR CONVERSATION",
        use_container_width=True
    ):

        st.session_state.conversation = []

        st.session_state.last_answer = ""

        st.session_state.last_audio = None

        st.session_state.api_error = ""

        st.rerun()


# ============================================================
# MAIN AREA
# ============================================================

robot_column, chat_column = st.columns(
    [1, 1.15],
    gap="large"
)


# ============================================================
# ROBOT
# ============================================================

with robot_column:

    render_robot()


# ============================================================
# CHAT
# ============================================================

with chat_column:

    st.markdown(
        '<div class="chat-panel">',
        unsafe_allow_html=True
    )

    st.markdown(
        "## 💬 BAITHAK CONVERSATION"
    )

    if not st.session_state.conversation:

        st.info(
            "👋 Assalam-o-Alaikum!\n\n"
            "I am BAITHAK WITH AI.\n\n"
            "Type a message or use the microphone."
        )

    else:

        for message in st.session_state.conversation:

            role = message["role"]

            content = message["content"]

            if role == "user":

                with st.chat_message(
                    "user",
                    avatar="👤"
                ):

                    st.write(content)

            elif role == "assistant":

                with st.chat_message(
                    "assistant",
                    avatar="🤖"
                ):

                    st.write(content)

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# TEXT INPUT
# ============================================================

text_message = st.chat_input(
    "💬 Type your message to BAITHAK..."
)


if text_message:

    with st.spinner(
        "🤖 BAITHAK is thinking..."
    ):

        ask_ai(
            text_message
        )

    st.rerun()


# ============================================================
# VOICE INPUT
# ============================================================

st.markdown("---")

st.markdown(
    "## 🎙️ TALK TO BAITHAK"
)

st.caption(
    "Press the microphone button, speak naturally, "
    "then process your recording."
)


audio_input = st.audio_input(
    "🎙️ Record your voice"
)


if audio_input is not None:

    st.audio(
        audio_input,
        format="audio/wav"
    )

    if st.button(
        "🧠 PROCESS VOICE",
        type="primary",
        use_container_width=True
    ):

        # ====================================================
        # SPEECH TO TEXT
        # ====================================================

        with st.spinner(
            "🎙️ BAITHAK is listening..."
        ):

            spoken_text, error = transcribe_audio(
                audio_input
            )

        if error:

            st.error(
                "❌ Speech recognition failed: "
                + error
            )

        else:

            st.success(
                "🎙️ You said:"
            )

            st.write(
                spoken_text
            )


            # =================================================
            # AI RESPONSE
            # =================================================

            with st.spinner(
                "🧠 BAITHAK is thinking..."
            ):

                answer = ask_ai(
                    spoken_text
                )

            st.markdown(
                "### 🤖 BAITHAK"
            )

            st.write(
                answer
            )


            # =================================================
            # TEXT TO SPEECH
            # =================================================

            if voice_enabled:

                with st.spinner(
                    "🔊 BAITHAK is speaking..."
                ):

                    audio_bytes, error = create_voice(
                        answer
                    )

                if error:

                    st.warning(
                        "🔊 Voice generation failed: "
                        + error
                    )

                elif audio_bytes:

                    st.session_state.last_audio = (
                        audio_bytes
                    )

                    st.markdown(
                        "### 🔊 BAITHAK VOICE"
                    )

                    st.markdown(
                        make_audio_player(
                            audio_bytes
                        ),
                        unsafe_allow_html=True
                    )


# ============================================================
# LAST RESPONSE
# ============================================================

if (
    st.session_state.last_audio
    and audio_input is None
):

    st.markdown("---")

    st.markdown(
        "### 🔊 LAST AI RESPONSE"
    )

    st.markdown(
        make_audio_player(
            st.session_state.last_audio
        ),
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="baithak-footer">

        <div class="footer-title">
            🤖 BAITHAK WITH AI
        </div>

        <div class="footer-name">

            Designed by Certified Generative and Agentic AI
            Application Developer

            <br>

            <strong>Engr. Bilal Mehmood</strong>

        </div>

        <div class="footer-line">

            Intelligent Talking AI • Voice Interaction •
            OpenAI Powered • Streamlit Application

        </div>

        <div class="footer-tech">

            🧠 AI &nbsp; • &nbsp;
            🎙️ SPEECH &nbsp; • &nbsp;
            🔊 VOICE &nbsp; • &nbsp;
            🤖 ROBOTICS

        </div>

    </div>
    """,
    unsafe_allow_html=True
)

