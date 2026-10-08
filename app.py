import os
import base64
import streamlit as st
from openai import OpenAI


# ============================================================
# BAITHAK WITH AI
# OpenAI Powered Talking Robot
# ============================================================

st.set_page_config(
    page_title="BAITHAK WITH AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SETTINGS
# ============================================================

DEFAULT_MODEL = "gpt-6-luna"
TRANSCRIBE_MODEL = "gpt-4o-mini-transcribe"
TTS_MODEL = "gpt-4o-mini-tts"

SYSTEM_PROMPT = """
You are BAITHAK WITH AI, a friendly intelligent talking AI assistant.

You are designed like a friendly robot sitting in a virtual baithak.

Personality:
- Friendly
- Intelligent
- Helpful
- Natural
- Professional when appropriate
- Warm and conversational

Language:
- Understand English
- Understand Urdu
- Understand Roman Urdu
- Reply in the language used by the user whenever possible.

Keep normal answers concise and conversational.
Give detailed answers when the user asks for details.

Never claim that you performed an action in the physical world
unless the application actually performed that action.
"""


# ============================================================
# API KEY
# ============================================================

def get_api_key():
    """
    Get OpenAI API key from Streamlit Secrets first,
    then environment variable.
    """

    try:
        key = st.secrets.get("OPENAI_API_KEY")

        if key:
            return str(key).strip()

    except Exception:
        pass

    key = os.getenv("OPENAI_API_KEY")

    if key:
        return key.strip()

    return ""


OPENAI_API_KEY = get_api_key()


# ============================================================
# OPENAI CLIENT
# ============================================================

client = None

if OPENAI_API_KEY:

    try:
        client = OpenAI(
            api_key=OPENAI_API_KEY
        )
    except Exception as e:
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


if "status" not in st.session_state:

    st.session_state.status = "READY"


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&display=swap'
);

* {
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: 'Orbitron', sans-serif;
}

.stApp {

    background:
        radial-gradient(
            circle at 50% 15%,
            rgba(0, 200, 255, 0.16),
            transparent 28%
        ),
        radial-gradient(
            circle at 15% 85%,
            rgba(0, 255, 170, 0.08),
            transparent 30%
        ),
        #030712;

    color: white;
}


/* =========================================================
   TITLE
   ========================================================= */

.baithak-title {

    text-align: center;

    font-size: clamp(32px, 5vw, 62px);

    font-weight: 800;

    letter-spacing: 5px;

    color: #00eaff;

    text-shadow:
        0 0 10px #00eaff,
        0 0 25px #00eaff,
        0 0 50px rgba(0,234,255,.5);

    margin-top: 10px;

}


.baithak-subtitle {

    text-align: center;

    color: #8ddff0;

    font-size: 14px;

    letter-spacing: 3px;

    margin-bottom: 25px;

}


/* =========================================================
   ROBOT AREA
   ========================================================= */

.robot-container {

    min-height: 480px;

    display: flex;

    justify-content: center;

    align-items: center;

    position: relative;

}


.robot-glow {

    position: absolute;

    width: 310px;

    height: 310px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(0,225,255,.25),
            rgba(0,225,255,.03) 55%,
            transparent 70%
        );

    animation: glowPulse 2.5s infinite;

}


@keyframes glowPulse {

    0%, 100% {

        transform: scale(.9);

        opacity: .6;

    }

    50% {

        transform: scale(1.12);

        opacity: 1;

    }

}


/* =========================================================
   ROBOT
   ========================================================= */

.robot {

    width: 260px;

    height: 370px;

    position: relative;

    animation: floatRobot 3s ease-in-out infinite;

    z-index: 2;

}


@keyframes floatRobot {

    0%,100% {

        transform: translateY(0);

    }

    50% {

        transform: translateY(-18px);

    }

}


/* =========================================================
   ANTENNA
   ========================================================= */

.antenna {

    position: absolute;

    top: -55px;

    left: 126px;

    width: 7px;

    height: 55px;

    background: #b9f7ff;

    box-shadow: 0 0 15px #00eaff;

}


.antenna-light {

    position: absolute;

    top: -78px;

    left: 116px;

    width: 28px;

    height: 28px;

    border-radius: 50%;

    background: #00ffae;

    box-shadow:
        0 0 10px #00ffae,
        0 0 35px #00ffae;

    animation: antennaPulse 1s infinite;

}


@keyframes antennaPulse {

    0%,100% {

        transform: scale(.75);

    }

    50% {

        transform: scale(1.2);

    }

}


/* =========================================================
   HEAD
   ========================================================= */

.robot-head {

    position: absolute;

    top: 0;

    left: 25px;

    width: 210px;

    height: 165px;

    border-radius: 45px;

    background:
        linear-gradient(
            145deg,
            #eaf8ff,
            #7890a6
        );

    border: 5px solid #a5f4ff;

    box-shadow:
        0 0 15px #00eaff,
        0 0 45px rgba(0,234,255,.7),
        inset 0 0 25px rgba(255,255,255,.4);

}


/* =========================================================
   FACE SCREEN
   ========================================================= */

.face-screen {

    position: absolute;

    top: 36px;

    left: 30px;

    width: 150px;

    height: 90px;

    background: #020a13;

    border-radius: 28px;

    border: 3px solid #00eaff;

    box-shadow:
        inset 0 0 25px #00eaff,
        0 0 15px rgba(0,234,255,.5);

}


/* =========================================================
   EYES
   ========================================================= */

.eye {

    position: absolute;

    top: 20px;

    width: 28px;

    height: 38px;

    border-radius: 50%;

    background: #00f6ff;

    box-shadow:
        0 0 10px #00f6ff,
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

    0%, 90%, 100% {

        transform: scaleY(1);

    }

    94% {

        transform: scaleY(.08);

    }

}


/* =========================================================
   MOUTH
   ========================================================= */

.mouth {

    position: absolute;

    left: 58px;

    bottom: 12px;

    width: 35px;

    height: 8px;

    border-radius: 20px;

    background: #00f6ff;

    box-shadow: 0 0 15px #00f6ff;

    animation: talking 1s infinite;

}


@keyframes talking {

    0%,100% {

        height: 7px;

        width: 35px;

    }

    50% {

        height: 24px;

        width: 29px;

    }

}


/* =========================================================
   BODY
   ========================================================= */

.robot-body {

    position: absolute;

    top: 175px;

    left: 58px;

    width: 145px;

    height: 130px;

    border-radius: 30px;

    background:
        linear-gradient(
            145deg,
            #e6f5ff,
            #61758b
        );

    border: 5px solid #a5f4ff;

    box-shadow:
        0 0 20px #00eaff,
        inset 0 0 20px rgba(255,255,255,.3);

}


/* =========================================================
   CHEST
   ========================================================= */

.chest {

    position: absolute;

    top: 30px;

    left: 28px;

    width: 84px;

    height: 62px;

    border-radius: 16px;

    background: #020a13;

    border: 3px solid #00eaff;

    box-shadow: inset 0 0 20px #00eaff;

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
        0 0 10px #00ffae,
        0 0 25px #00ffae;

    animation: corePulse 1.2s infinite;

}


@keyframes corePulse {

    0%,100% {

        transform: scale(.75);

    }

    50% {

        transform: scale(1.2);

    }

}


/* =========================================================
   ARMS
   ========================================================= */

.arm {

    position: absolute;

    top: 185px;

    width: 38px;

    height: 110px;

    border-radius: 25px;

    background:
        linear-gradient(
            #b5cadb,
            #52667a
        );

    border: 4px solid #a5f4ff;

    box-shadow: 0 0 15px #00eaff;

}


.arm-left {

    left: 13px;

    transform: rotate(12deg);

}


.arm-right {

    right: 13px;

    transform: rotate(-12deg);

}


/* =========================================================
   STATUS
   ========================================================= */

.robot-status {

    text-align: center;

    margin-top: -15px;

}


.status-pill {

    display: inline-block;

    padding: 10px 24px;

    border: 1px solid #00eaff;

    border-radius: 30px;

    color: #00eaff;

    background: rgba(0,234,255,.08);

    box-shadow: 0 0 20px rgba(0,234,255,.25);

}


/* =========================================================
   CARDS
   ========================================================= */

.baithak-card {

    background: rgba(8,20,38,.78);

    border: 1px solid rgba(0,234,255,.25);

    border-radius: 18px;

    padding: 18px;

    margin-bottom: 15px;

}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button {

    width: 100%;

    min-height: 45px;

    border-radius: 12px;

    border: 1px solid #00eaff;

    background: rgba(0,234,255,.08);

    color: #00eaff;

    font-weight: 700;

}


.stButton > button:hover {

    background: rgba(0,234,255,.22);

    box-shadow: 0 0 18px rgba(0,234,255,.6);

}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {

    text-align: center;

    color: #668397;

    font-size: 12px;

    margin-top: 30px;

    padding: 20px;

}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# FUNCTIONS
# ============================================================

def get_ai_response(user_text):

    """
    Send conversation to OpenAI Responses API.
    """

    if client is None:

        return (
            "I cannot connect to OpenAI right now. "
            "Please check your OPENAI_API_KEY in Streamlit Secrets."
        )

    # Add user message
    st.session_state.conversation.append(
        {
            "role": "user",
            "content": user_text,
        }
    )

    # Keep conversation from becoming excessively large
    recent_messages = st.session_state.conversation[-20:]

    try:

        response = client.responses.create(
            model=DEFAULT_MODEL,
            instructions=SYSTEM_PROMPT,
            input=recent_messages,
        )

        answer = response.output_text

        if not answer:

            answer = "Sorry, I could not generate a response."

        st.session_state.conversation.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        st.session_state.last_answer = answer

        return answer

    except Exception as e:

        # Remove failed user message if API call failed
        if st.session_state.conversation:
            if st.session_state.conversation[-1]["role"] == "user":
                st.session_state.conversation.pop()

        return (
            "⚠️ OpenAI connection error.\n\n"
            f"{str(e)}"
        )


def transcribe_audio(audio_file):

    """
    Convert microphone recording to text.
    """

    if client is None:

        return None, (
            "OpenAI API key is missing or invalid."
        )

    try:

        audio_file.seek(0)

        result = client.audio.transcriptions.create(
            model=TRANSCRIBE_MODEL,
            file=audio_file,
        )

        text = getattr(result, "text", "")

        if not text:

            return None, "I could not understand the recording."

        return text.strip(), None

    except Exception as e:

        return None, str(e)


def generate_voice(text):

    """
    Generate AI speech.
    """

    if client is None:

        return None, "OpenAI API is not connected."

    try:

        response = client.audio.speech.create(
            model=TTS_MODEL,
            voice="alloy",
            input=text,
        )

        audio_bytes = response.read()

        return audio_bytes, None

    except Exception as e:

        return None, str(e)


def audio_html(audio_bytes, autoplay=False):

    """
    Create browser audio player.
    """

    if not audio_bytes:
        return ""

    encoded = base64.b64encode(
        audio_bytes
    ).decode("utf-8")

    auto = "autoplay" if autoplay else ""

    html = f"""
    <audio controls {auto} style="width:100%;">
        <source
            src="data:audio/mp3;base64,{encoded}"
            type="audio/mp3"
        >
    </audio>
    """

    return html


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="baithak-title">🤖 BAITHAK WITH AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="baithak-subtitle">'
    'YOUR INTELLIGENT TALKING AI COMPANION'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ⚙️ BAITHAK SETTINGS")

    if client:

        st.success("🟢 OPENAI CONNECTED")

    else:

        st.error("🔴 OPENAI NOT CONNECTED")

    st.markdown("---")

    st.markdown("### 🧠 AI MODEL")

    st.code(DEFAULT_MODEL)

    st.markdown("### 🎙️ VOICE MODE")

    voice_enabled = st.toggle(
        "Enable AI Voice",
        value=True,
    )

    st.markdown("---")

    if st.button(
        "🗑️ CLEAR CONVERSATION"
    ):

        st.session_state.conversation = []

        st.session_state.last_answer = ""

        st.session_state.last_audio = None

        st.rerun()

    st.markdown("---")

    st.markdown(
        """
### 🔐 API KEY

Store your OpenAI key in:

`.streamlit/secrets.toml`

Never put the real key inside `app.py`.

### 🎙️ VOICE

Microphone recording is handled
by Streamlit's native audio input.

### 🤖 BAITHAK

OpenAI handles:

**Speech → AI → Voice**
"""
    )


# ============================================================
# MAIN COLUMNS
# ============================================================

robot_column, chat_column = st.columns(
    [1, 1.25],
    gap="large",
)


# ============================================================
# ROBOT
# ============================================================

with robot_column:

    st.markdown(
        """
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
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="robot-status">

    <span class="status-pill">
        🟢 BAITHAK IS READY
    </span>

</div>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# CHAT
# ============================================================

with chat_column:

    st.markdown(
        "## 💬 Conversation"
    )

    if not st.session_state.conversation:

        st.info(
            "👋 Assalam-o-Alaikum! "
            "I am BAITHAK WITH AI. "
            "Type a message or use the microphone below."
        )

    else:

        for message in st.session_state.conversation:

            role = message.get("role")

            content = message.get("content", "")

            if role == "user":

                with st.chat_message(
                    "user",
                    avatar="👤",
                ):

                    st.write(content)

            elif role == "assistant":

                with st.chat_message(
                    "assistant",
                    avatar="🤖",
                ):

                    st.write(content)


# ============================================================
# TEXT CHAT
# ============================================================

st.markdown("---")

text_input = st.chat_input(
    "💬 Talk to BAITHAK by typing..."
)


if text_input:

    with st.spinner(
        "🤖 BAITHAK is thinking..."
    ):

        answer = get_ai_response(
            text_input
        )

    st.rerun()


# ============================================================
# MICROPHONE
# ============================================================

st.markdown(
    "## 🎙️ Talk to BAITHAK"
)

st.caption(
    "Click the microphone button, speak, then press "
    "'Process Voice'."
)


audio_input = st.audio_input(
    "🎙️ Record your message"
)


if audio_input is not None:

    st.audio(
        audio_input,
        format="audio/wav",
    )

    st.markdown("---")

    if st.button(
        "🧠 PROCESS VOICE",
        type="primary",
    ):

        # ----------------------------------------------------
        # STEP 1: TRANSCRIPTION
        # ----------------------------------------------------

        with st.spinner(
            "🎙️ BAITHAK is listening..."
        ):

            spoken_text, error = transcribe_audio(
                audio_input
            )

        if error:

            st.error(
                f"❌ Voice recognition failed: {error}"
            )

        else:

            st.success(
                f"🎙️ You said: {spoken_text}"
            )

            # ------------------------------------------------
            # STEP 2: AI
            # ------------------------------------------------

            with st.spinner(
                "🧠 BAITHAK is thinking..."
            ):

                answer = get_ai_response(
                    spoken_text
                )

            # ------------------------------------------------
            # STEP 3: DISPLAY RESPONSE
            # ------------------------------------------------

            st.markdown(
                "### 🤖 BAITHAK"
            )

            st.write(answer)

            # ------------------------------------------------
            # STEP 4: TEXT TO SPEECH
            # ------------------------------------------------

            if voice_enabled:

                with st.spinner(
                    "🔊 BAITHAK is speaking..."
                ):

                    audio_bytes, error = generate_voice(
                        answer
                    )

                if error:

                    st.warning(
                        f"🔊 Voice generation failed: {error}"
                    )

                elif audio_bytes:

                    st.session_state.last_audio = (
                        audio_bytes
                    )

                    st.markdown(
                        "### 🔊 BAITHAK VOICE"
                    )

                    st.markdown(
                        audio_html(
                            audio_bytes,
                            autoplay=True,
                        ),
                        unsafe_allow_html=True,
                    )


# ============================================================
# LAST RESPONSE AUDIO
# ============================================================

if (
    st.session_state.last_audio
    and not audio_input
):

    st.markdown("---")

    st.markdown(
        "### 🔊 LAST AI RESPONSE"
    )

    st.markdown(
        audio_html(
            st.session_state.last_audio
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">

    BAITHAK WITH AI

    <br><br>

    🤖 AI ROBOT • 🎙️ VOICE INPUT • 🧠 OPENAI • 🔊 AI VOICE

    <br><br>

    Intelligent Conversation • Voice Interaction • AI Assistant

</div>
""",
    unsafe_allow_html=True,
)
