import os
import base64

import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI


# ============================================================
# BAITHAK WITH AI
# Intelligent Talking Robot Assistant
# DEMO MODE + OPENAI GPT-6 LUNA API MODE
# ============================================================


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
You are BAITHAK WITH AI.

You are a friendly, intelligent and conversational AI robot
assistant sitting with the user in a virtual baithak.

Personality:
- Friendly
- Intelligent
- Helpful
- Respectful
- Professional
- Warm
- Conversational

Languages:
- English
- Urdu
- Roman Urdu

Language behavior:
- If the user speaks English, answer in English.
- If the user speaks Urdu, answer naturally in Urdu.
- If the user uses Roman Urdu, answer naturally in Roman Urdu.
- Do not unnecessarily change the user's language.

Response behavior:
- Keep ordinary answers concise.
- Give detailed answers when requested.
- Be technically accurate.
- Never claim that a real-world action was completed
  unless the application actually performed it.
"""


# ============================================================
# SECRET LOADER
# ============================================================

def get_secret(name, default=""):

    try:

        value = st.secrets.get(name)

        if value:

            return str(value).strip()

    except Exception:

        pass

    return os.getenv(
        name,
        default
    )


# ============================================================
# OPENAI SETTINGS
# ============================================================

OPENAI_API_KEY = get_secret(
    "OPENAI_API_KEY"
)

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


if "last_audio" not in st.session_state:

    st.session_state.last_audio = None


if "mode" not in st.session_state:

    st.session_state.mode = "Demo Mode"


if "api_error" not in st.session_state:

    st.session_state.api_error = ""


# ============================================================
# GLOBAL CSS
# IMPORTANT:
# Only normal Streamlit CSS here.
# Robot + footer HTML are rendered separately.
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

    font-family:
        'Orbitron',
        sans-serif;

}


.stApp {

    background:

        radial-gradient(
            circle at 50% 10%,
            rgba(0,220,255,.16),
            transparent 30%
        ),

        radial-gradient(
            circle at 10% 90%,
            rgba(0,255,160,.08),
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

    font-size:
        clamp(32px, 5vw, 60px);

    font-weight: 800;

    letter-spacing: 5px;

    color: #00eaff;

    text-shadow:

        0 0 10px #00eaff,

        0 0 25px #00eaff,

        0 0 55px
        rgba(0,234,255,.55);

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

    background:
        rgba(7,18,35,.75);

    border:
        1px solid
        rgba(0,234,255,.25);

    border-radius: 20px;

    padding: 18px;

}


/* ==========================================================
   MODE BADGE
   ========================================================== */

.mode-demo {

    padding: 10px;

    border-radius: 12px;

    border:
        1px solid
        rgba(255,193,7,.5);

    background:
        rgba(255,193,7,.08);

}


.mode-api {

    padding: 10px;

    border-radius: 12px;

    border:
        1px solid
        rgba(0,255,174,.5);

    background:
        rgba(0,255,174,.08);

}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# DEMO AI
# ============================================================

def demo_response(user_text):

    text = user_text.lower().strip()


    # --------------------------------------------------------
    # GREETING
    # --------------------------------------------------------

    if any(
        word in text
        for word in [
            "hello",
            "hi",
            "salam",
            "assalam",
            "aoa"
        ]
    ):

        return (
            "وعلیکم السلام! 🤖\n\n"
            "میں BAITHAK WITH AI ہوں۔ "
            "آپ مجھ سے English، Urdu یا Roman Urdu "
            "میں بات کر سکتے ہیں۔\n\n"
            "How can I help you today?"
        )


    # --------------------------------------------------------
    # IDENTITY
    # --------------------------------------------------------

    if (
        "who are you" in text
        or "tum kon" in text
        or "aap kon" in text
        or "آپ کون" in text
    ):

        return (
            "میں BAITHAK WITH AI ہوں — ایک intelligent "
            "talking AI companion۔ 🤖\n\n"
            "میں English، Urdu اور Roman Urdu میں "
            "آپ کے ساتھ conversational انداز میں بات کر سکتا ہوں۔"
        )


    # --------------------------------------------------------
    # DEMO MODE
    # --------------------------------------------------------

    if (
        "demo" in text
        or "api" in text
        or "mode" in text
    ):

        return (
            "آپ اس وقت BAITHAK WITH AI کے Demo Mode میں ہیں۔\n\n"
            "Demo Mode API key کے بغیر بھی کام کرتا ہے۔ "
            "اگر OpenAI API Mode استعمال کرنا ہو تو "
            "OPENAI_API_KEY کو Streamlit Secrets میں add کریں۔"
        )


    # --------------------------------------------------------
    # PYTHON
    # --------------------------------------------------------

    if "python" in text:

        return (
            "Python ایک high-level programming language ہے "
            "جو AI، Machine Learning، Automation، Data Science "
            "اور Web Development میں بہت استعمال ہوتی ہے۔ 🐍"
        )


    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    if (
        "artificial intelligence" in text
        or text == "ai"
        or "what is ai" in text
    ):

        return (
            "Artificial Intelligence یعنی AI ایسی technology ہے "
            "جس کے ذریعے computer systems انسانی intelligence "
            "سے متعلق tasks perform کر سکتے ہیں، جیسے reasoning، "
            "language understanding، vision اور decision making۔"
        )


    # --------------------------------------------------------
    # ROBOT
    # --------------------------------------------------------

    if "robot" in text:

        return (
            "Robot ایک programmable machine ہے جو sensors، "
            "controllers، software اور actuators استعمال کر کے "
            "physical world میں actions perform کر سکتا ہے۔ 🤖"
        )


    # --------------------------------------------------------
    # URDU
    # --------------------------------------------------------

    if (
        "کیا حال" in text
        or "آپ کیسے" in text
        or "تم کیسے" in text
    ):

        return (
            "الحمدللہ، میں بالکل ٹھیک ہوں! 🤖\n\n"
            "آپ بتائیں، میں BAITHAK میں آپ کی کیا مدد کر سکتا ہوں؟"
        )


    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    return (
        "🤖 Demo Mode:\n\n"
        f"آپ نے پوچھا: {user_text}\n\n"
        "میں Demo Mode میں اس request کا simulated جواب دے رہا ہوں۔ "
        "زیادہ intelligent اور detailed جواب کے لیے OpenAI API Mode "
        "اور GPT-6 Luna استعمال کریں۔"
    )


# ============================================================
# AI REQUEST
# ============================================================

def ask_ai(user_text):

    # --------------------------------------------------------
    # DEMO MODE
    # --------------------------------------------------------

    if st.session_state.mode == "Demo Mode":

        answer = demo_response(
            user_text
        )

        st.session_state.conversation.append(
            {
                "role": "user",
                "content": user_text
            }
        )

        st.session_state.conversation.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer


    # --------------------------------------------------------
    # API MODE
    # --------------------------------------------------------

    if client is None:

        st.session_state.mode = "Demo Mode"

        answer = demo_response(
            user_text
        )

        answer = (
            "⚠️ OpenAI API available نہیں ہے۔ "
            "Automatically Demo Mode پر switch کر دیا گیا ہے.\n\n"
            + answer
        )

        st.session_state.conversation.append(
            {
                "role": "user",
                "content": user_text
            }
        )

        st.session_state.conversation.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer


    # --------------------------------------------------------
    # STORE USER MESSAGE
    # --------------------------------------------------------

    st.session_state.conversation.append(
        {
            "role": "user",
            "content": user_text
        }
    )


    history = (
        st.session_state.conversation[-20:]
    )


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


        st.session_state.api_error = ""

        return answer


    except Exception as error:

        # Remove failed user request

        if st.session_state.conversation:

            if (
                st.session_state.conversation[-1]["role"]
                == "user"
            ):

                st.session_state.conversation.pop()


        # Automatic fallback

        st.session_state.mode = "Demo Mode"

        st.session_state.api_error = str(
            error
        )


        demo_answer = demo_response(
            user_text
        )


        final_answer = (
            "⚠️ OpenAI API request failed.\n\n"
            "🔄 BAITHAK automatically switched "
            "to Demo Mode.\n\n"
            f"{demo_answer}"
        )


        st.session_state.conversation.append(
            {
                "role": "user",
                "content": user_text
            }
        )


        st.session_state.conversation.append(
            {
                "role": "assistant",
                "content": final_answer
            }
        )


        return final_answer


# ============================================================
# SPEECH TO TEXT
# ============================================================

def transcribe_audio(audio_file):

    if (
        client is None
        or st.session_state.mode != "API Mode"
    ):

        return None, (
            "Voice transcription requires "
            "OpenAI API Mode."
        )


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

            return None, (
                "No speech was detected."
            )


        return text.strip(), None


    except Exception as error:

        return None, str(error)


# ============================================================
# TEXT TO SPEECH
# ============================================================

def create_voice(text):

    if (
        client is None
        or st.session_state.mode != "API Mode"
    ):

        return None, (
            "AI Voice requires OpenAI API Mode."
        )


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
    <audio
        controls
        autoplay
        style="width:100%;"
    >

        <source
            src="data:audio/mp3;base64,{encoded}"
            type="audio/mp3"
        >

    </audio>
    """


# ============================================================
# ROBOT + FOOTER COMPONENT
# IMPORTANT:
# ALL RAW HTML IS INSIDE components.html()
# Therefore Streamlit will not display <div> as text.
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

    min-height: 100%;

    background: transparent;

    overflow: hidden;

    color: white;

    font-family: Arial, sans-serif;
}


/* ==========================================================
   ROBOT CONTAINER
   ========================================================== */

.robot-container {

    position: relative;

    width: 100%;

    height: 485px;

    display: flex;

    justify-content: center;

    align-items: center;
}


/* ==========================================================
   GLOW
   ========================================================== */

.robot-glow {

    position: absolute;

    width: 330px;

    height: 330px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(0,225,255,.28),
            rgba(0,225,255,.08) 50%,
            transparent 72%
        );

    animation:
        glowPulse 2.5s ease-in-out infinite;

    z-index: 1;
}


@keyframes glowPulse {

    0%,
    100% {

        transform: scale(.90);

        opacity: .55;
    }

    50% {

        transform: scale(1.12);

        opacity: 1;
    }
}


/* ==========================================================
   ROBOT
   ========================================================== */

.robot {

    position: relative;

    width: 270px;

    height: 380px;

    z-index: 5;

    animation:
        robotFloat 3s ease-in-out infinite;
}


@keyframes robotFloat {

    0%,
    100% {

        transform:
            translateY(0);
    }

    50% {

        transform:
            translateY(-17px);
    }
}


/* ==========================================================
   ANTENNA
   ========================================================== */

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

    animation:
        antennaPulse 1.2s infinite;
}


@keyframes antennaPulse {

    0%,
    100% {

        transform:
            scale(.75);
    }

    50% {

        transform:
            scale(1.2);
    }
}


/* ==========================================================
   HEAD
   ========================================================== */

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

        0 0 45px
        rgba(0,234,255,.7),

        inset 0 0 25px
        rgba(255,255,255,.45);
}


/* ==========================================================
   FACE
   ========================================================== */

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

        0 0 15px
        rgba(0,234,255,.5);
}


/* ==========================================================
   EYES
   ========================================================== */

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

    animation:
        blink 4s infinite;
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

        transform:
            scaleY(1);
    }

    94% {

        transform:
            scaleY(.08);
    }
}


/* ==========================================================
   MOUTH
   ========================================================== */

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

    animation:
        robotTalk .9s infinite;
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


/* ==========================================================
   BODY
   ========================================================== */

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

        inset 0 0 20px
        rgba(255,255,255,.3);
}


/* ==========================================================
   CHEST
   ========================================================== */

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

    animation:
        corePulse 1.2s infinite;
}


@keyframes corePulse {

    0%,
    100% {

        transform:
            scale(.75);
    }

    50% {

        transform:
            scale(1.2);
    }
}


/* ==========================================================
   ARMS
   ========================================================== */

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

    transform:
        rotate(12deg);
}


.arm-right {

    right: 16px;

    transform:
        rotate(-12deg);
}


/* ==========================================================
   STATUS
   ========================================================== */

.robot-status {

    text-align: center;

    margin-top: -5px;
}


.status-pill {

    display: inline-block;

    padding: 10px 25px;

    border-radius: 30px;

    color: #00eaff;

    border:
        1px solid #00eaff;

    background:
        rgba(0,234,255,.08);

    box-shadow:
        0 0 20px
        rgba(0,234,255,.25);

    font-size: 14px;

    letter-spacing: 1px;
}


/* ==========================================================
   FOOTER
   ========================================================== */

.baithak-footer {

    margin-top: 35px;

    padding: 28px 15px;

    text-align: center;

    border-top:
        1px solid
        rgba(0,234,255,.25);

    background:
        linear-gradient(
            180deg,
            rgba(0,234,255,.02),
            rgba(0,234,255,.08)
        );
}


.footer-title {

    font-size: 17px;

    font-weight: 700;

    letter-spacing: 2px;

    color: #00eaff;

    text-shadow:
        0 0 10px
        rgba(0,234,255,.6);
}


.footer-name {

    margin-top: 10px;

    font-size: 18px;

    font-weight: 800;

    line-height: 1.6;

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

    letter-spacing: 1px;
}

</style>

</head>


<body>


<!-- ========================================================
     ROBOT
     ======================================================== -->

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


<!-- ========================================================
     FOOTER
     ======================================================== -->

<div class="baithak-footer">

    <div class="footer-title">

        🤖 BAITHAK WITH AI

    </div>


    <div class="footer-name">

        Designed by Certified Generative and Agentic AI
        Application Developer

        <br>

        Engr. Bilal Mehmood

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


</body>

</html>
"""


    components.html(
        robot_html,
        height=760,
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
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## ⚙️ BAITHAK SETTINGS"
    )


    # --------------------------------------------------------
    # MODE SELECTOR
    # --------------------------------------------------------

    mode = st.radio(
        "Select Operating Mode",
        [
            "Demo Mode",
            "API Mode"
        ],
        index=(
            0
            if st.session_state.mode == "Demo Mode"
            else 1
        )
    )


    st.session_state.mode = mode


    # --------------------------------------------------------
    # MODE STATUS
    # --------------------------------------------------------

    st.markdown("---")

    if mode == "Demo Mode":

        st.info(
            "🟡 DEMO MODE\n\n"
            "No API key required."
        )

    else:

        if client:

            st.success(
                "🟢 OPENAI API MODE"
            )

        else:

            st.warning(
                "🟠 API MODE SELECTED\n\n"
                "OPENAI_API_KEY is not configured."
            )


    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown(
        "### 🧠 AI MODEL"
    )

    if mode == "API Mode":

        st.code(
            OPENAI_MODEL
        )

    else:

        st.code(
            "BAITHAK DEMO ENGINE"
        )


    # --------------------------------------------------------
    # VOICE
    # --------------------------------------------------------

    st.markdown(
        "### 🎙️ VOICE"
    )

    voice_enabled = st.toggle(
        "Enable AI Voice",
        value=True
    )


    # --------------------------------------------------------
    # API INFO
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown(
        "### 🔐 API SECURITY"
    )

    st.info(
        "OPENAI_API_KEY is loaded from "
        "Streamlit Secrets or environment variables."
    )


    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    st.markdown("---")

    if st.button(
        "🗑️ CLEAR CONVERSATION",
        use_container_width=True
    ):

        st.session_state.conversation = []

        st.session_state.last_audio = None

        st.session_state.api_error = ""

        st.rerun()


# ============================================================
# MAIN COLUMNS
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


    # --------------------------------------------------------
    # CURRENT MODE
    # --------------------------------------------------------

    if st.session_state.mode == "Demo Mode":

        st.warning(
            "🟡 BAITHAK is running in DEMO MODE"
        )

    else:

        st.success(
            "🟢 BAITHAK is running with "
            f"{OPENAI_MODEL}"
        )


    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    if not st.session_state.conversation:

        st.info(
            "👋 Assalam-o-Alaikum!\n\n"
            "I am BAITHAK WITH AI.\n\n"
            "You can type a message or use the microphone."
        )

    else:

        for message in (
            st.session_state.conversation
        ):

            role = message["role"]

            content = message["content"]


            if role == "user":

                with st.chat_message(
                    "user",
                    avatar="👤"
                ):

                    st.write(
                        content
                    )


            elif role == "assistant":

                with st.chat_message(
                    "assistant",
                    avatar="🤖"
                ):

                    st.write(
                        content
                    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# TEXT CHAT
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
# VOICE SECTION
# ============================================================

st.markdown("---")


st.markdown(
    "## 🎙️ TALK TO BAITHAK"
)


st.caption(
    "Record your voice, process it with OpenAI, "
    "and receive an AI response."
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


        # ----------------------------------------------------
        # DEMO MODE VOICE
        # ----------------------------------------------------

        if st.session_state.mode == "Demo Mode":

            st.info(
                "🎙️ Voice transcription requires "
                "API Mode with OpenAI."
            )


        else:

            # ------------------------------------------------
            # TRANSCRIPTION
            # ------------------------------------------------

            with st.spinner(
                "🎙️ BAITHAK is listening..."
            ):

                spoken_text, error = (
                    transcribe_audio(
                        audio_input
                    )
                )


            if error:

                st.error(
                    "❌ Speech recognition failed:\n\n"
                    + error
                )


            else:

                st.success(
                    "🎙️ You said:"
                )


                st.write(
                    spoken_text
                )


                # --------------------------------------------
                # AI
                # --------------------------------------------

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


                # --------------------------------------------
                # VOICE
                # --------------------------------------------

                if voice_enabled:

                    with st.spinner(
                        "🔊 BAITHAK is speaking..."
                    ):

                        audio_bytes, error = (
                            create_voice(
                                answer
                            )
                        )


                    if error:

                        st.warning(
                            "🔊 Voice generation failed:\n\n"
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
# LAST AUDIO
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

