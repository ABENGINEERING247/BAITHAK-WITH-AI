import os
import base64
import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# OPTIONAL OPENAI IMPORT
# ============================================================

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


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TRANSCRIPTION_MODEL = "gpt-4o-mini-transcribe"
DEFAULT_TTS_MODEL = "gpt-4o-mini-tts"
DEFAULT_TTS_VOICE = "alloy"


# ============================================================
# GET SETTINGS FROM STREAMLIT SECRETS / ENVIRONMENT
# ============================================================

def get_secret(name, default=None):
    """Read a value from Streamlit Secrets first, then environment."""
    try:
        if name in st.secrets:
            value = st.secrets[name]
            if value is not None and str(value).strip():
                return str(value).strip()
    except Exception:
        pass

    value = os.getenv(name)
    if value is not None and str(value).strip():
        return str(value).strip()

    return default


OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
OPENAI_MODEL = get_secret("OPENAI_MODEL", DEFAULT_MODEL)
TRANSCRIPTION_MODEL = get_secret(
    "TRANSCRIPTION_MODEL",
    DEFAULT_TRANSCRIPTION_MODEL
)
TTS_MODEL = get_secret("TTS_MODEL", DEFAULT_TTS_MODEL)
TTS_VOICE = get_secret("TTS_VOICE", DEFAULT_TTS_VOICE)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

if "voice_audio" not in st.session_state:
    st.session_state.voice_audio = None

if "last_error" not in st.session_state:
    st.session_state.last_error = ""

if "trial_popup_shown" not in st.session_state:
    st.session_state.trial_popup_shown = False

if "trial_accepted" not in st.session_state:
    st.session_state.trial_accepted = False


# ============================================================
# OPENAI CLIENT
# ============================================================

@st.cache_resource
def get_openai_client(api_key):
    if not api_key:
        return None

    if OpenAI is None:
        return None

    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None


client = get_openai_client(OPENAI_API_KEY)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       MAIN APP
    -------------------------------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at 15% 10%,
                rgba(0, 190, 230, 0.12),
                transparent 30%
            ),
            radial-gradient(
                circle at 85% 15%,
                rgba(0, 120, 180, 0.10),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #f7fdff 0%,
                #eefaff 45%,
                #ffffff 100%
            );
    }


    /* --------------------------------------------------------
       SIDEBAR
    -------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #e8f9ff 0%,
                #f7fdff 100%
            );
        border-right: 1px solid rgba(0, 160, 200, 0.15);
    }


    /* --------------------------------------------------------
       BUTTONS
    -------------------------------------------------------- */

    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(0, 150, 190, 0.25);
        font-weight: 700;
        transition: all 0.25s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow:
            0 8px 25px rgba(0, 160, 200, 0.18);
    }


    /* --------------------------------------------------------
       CHAT MESSAGE
    -------------------------------------------------------- */

    div[data-testid="stChatMessage"] {
        border-radius: 18px;
        border: 1px solid rgba(0, 150, 190, 0.10);
        box-shadow:
            0 5px 20px rgba(0, 80, 110, 0.05);
        margin-bottom: 12px;
    }


    /* --------------------------------------------------------
       INFO CARD
    -------------------------------------------------------- */

    .info-card {
        padding: 18px;
        border-radius: 18px;
        background: rgba(255,255,255,0.72);
        border: 1px solid rgba(0, 170, 210, 0.16);
        box-shadow: 0 8px 30px rgba(0,80,110,0.06);
        margin-bottom: 18px;
    }

    .info-card-title {
        font-size: 17px;
        font-weight: 800;
        color: #034e6d;
        margin-bottom: 8px;
    }

    .info-card-text {
        color: #42636e;
        line-height: 1.55;
        font-size: 14px;
    }


    /* --------------------------------------------------------
       STATUS
    -------------------------------------------------------- */

    .status-online {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 13px;
        border-radius: 30px;
        background: rgba(0, 180, 120, 0.10);
        color: #087f5b;
        font-size: 13px;
        font-weight: 800;
    }

    .status-demo {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 13px;
        border-radius: 30px;
        background: rgba(255, 170, 0, 0.12);
        color: #9b6500;
        font-size: 13px;
        font-weight: 800;
    }


    /* --------------------------------------------------------
       FOOTER
    -------------------------------------------------------- */

    .footer {
        text-align: center;
        color: #6a858e;
        font-size: 12px;
        padding: 30px 0 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TRIAL POPUP
# ============================================================

def show_trial_popup():

    popup_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: Arial, Helvetica, sans-serif;
        }

        .overlay {
            position: fixed;
            inset: 0;

            display: flex;
            align-items: center;
            justify-content: center;

            background:
                radial-gradient(
                    circle at center,
                    rgba(0, 200, 255, 0.18),
                    transparent 45%
                ),
                rgba(2, 25, 40, 0.82);

            backdrop-filter: blur(10px);

            z-index: 999999;
        }

        .popup {
            width: min(560px, 90vw);

            padding: 40px 36px;

            text-align: center;

            border-radius: 28px;

            background:
                linear-gradient(
                    145deg,
                    #ffffff,
                    #eafaff
                );

            border:
                1px solid rgba(0, 180, 220, 0.35);

            box-shadow:
                0 30px 100px rgba(0,0,0,0.40),
                0 0 50px rgba(0,200,255,0.20);

            animation:
                popupIn 0.7s cubic-bezier(.2,.8,.2,1);
        }

        @keyframes popupIn {
            from {
                opacity: 0;
                transform:
                    translateY(35px)
                    scale(0.78);
            }

            to {
                opacity: 1;
                transform:
                    translateY(0)
                    scale(1);
            }
        }

        .robot {
            font-size: 76px;

            display: inline-block;

            animation:
                floatRobot 2.2s ease-in-out infinite;

            filter:
                drop-shadow(
                    0 10px 20px
                    rgba(0,160,210,0.25)
                );
        }

        @keyframes floatRobot {

            0%,100% {
                transform:
                    translateY(0)
                    rotate(0deg);
            }

            50% {
                transform:
                    translateY(-12px)
                    rotate(2deg);
            }
        }

        .badge {
            display: inline-block;

            margin-top: 12px;

            padding:
                8px 18px;

            border-radius: 30px;

            background:
                linear-gradient(
                    135deg,
                    #007da3,
                    #00b9dc
                );

            color: white;

            font-size: 13px;
            font-weight: 900;

            letter-spacing: 1.5px;

            box-shadow:
                0 8px 22px
                rgba(0,160,200,0.30);
        }

        h1 {
            margin:
                16px 0 8px;

            color: #034e6d;

            font-size: 34px;
            font-weight: 900;
        }

        .subtitle {
            color: #42636e;

            font-size: 17px;

            line-height: 1.6;

            margin-bottom: 18px;
        }

        .notice {
            padding: 14px 18px;

            margin:
                18px 0 25px;

            text-align: left;

            border-radius: 14px;

            background:
                rgba(0,160,200,0.08);

            border-left:
                4px solid #00a8cc;

            color: #365964;

            font-size: 14px;

            line-height: 1.5;
        }

        .continue {
            display: inline-block;

            padding:
                13px 28px;

            border-radius: 30px;

            background:
                linear-gradient(
                    135deg,
                    #006f91,
                    #00b8dc
                );

            color: white;

            font-size: 16px;
            font-weight: 800;

            box-shadow:
                0 10px 25px
                rgba(0,150,190,0.30);
        }

        .small {
            margin-top: 16px;

            color: #79929a;

            font-size: 12px;
        }

    </style>
    </head>

    <body>

        <div class="overlay">

            <div class="popup">

                <div class="robot">
                    🤖
                </div>

                <div class="badge">
                    TRIAL VERSION
                </div>

                <h1>
                    BAITHAK WITH AI
                </h1>

                <div class="subtitle">
                    Welcome to your intelligent
                    voice & text AI assistant.
                </div>

                <div class="notice">
                    🧪 <b>Trial / Testing Phase</b><br>
                    This application is currently being
                    evaluated and improved. Some features
                    may be experimental or subject to change.
                </div>

                <div class="continue">
                    ✨ Continue to Baithak
                </div>

                <div class="small">
                    Powered by AI • Voice • Text • Automation
                </div>

            </div>

        </div>

    </body>
    </html>
    """

    components.html(
        popup_html,
        height=720,
        scrolling=False
    )


# ============================================================
# SHOW TRIAL POPUP
# ============================================================

# The popup is shown when the Streamlit session starts.
# A Continue button is displayed below the popup by Streamlit
# so the user can enter the application.

if not st.session_state.trial_accepted:

    show_trial_popup()

    popup_col1, popup_col2, popup_col3 = st.columns([2, 2, 2])

    with popup_col2:

        if st.button(
            "🚀 Continue to Baithak",
            use_container_width=True,
            type="primary"
        ):
            st.session_state.trial_accepted = True
            st.rerun()

    st.stop()


# ============================================================
# ANIMATED ROBOT
# ============================================================

def show_animated_robot():

    robot_html = """
    <!DOCTYPE html>
    <html>
    <head>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: transparent;
            overflow: hidden;
        }

        .scene {
            height: 500px;

            display: flex;

            justify-content: center;

            align-items: center;

            position: relative;

            font-family: Arial, sans-serif;
        }


        /* ----------------------------------------------------
           FLOOR GLOW
        ---------------------------------------------------- */

        .floor {
            position: absolute;

            bottom: 35px;

            width: 330px;
            height: 35px;

            border-radius: 50%;

            background:
                radial-gradient(
                    ellipse,
                    rgba(0,180,230,0.38),
                    rgba(0,180,230,0.04),
                    transparent 70%
                );

            filter: blur(4px);

            animation:
                floorPulse 2.5s ease-in-out infinite;
        }

        @keyframes floorPulse {

            0%,100% {
                transform: scaleX(0.85);
                opacity: 0.55;
            }

            50% {
                transform: scaleX(1.08);
                opacity: 1;
            }
        }


        /* ----------------------------------------------------
           ROBOT
        ---------------------------------------------------- */

        .robot {

            position: relative;

            width: 220px;

            animation:
                robotFloat 3s ease-in-out infinite;
        }

        @keyframes robotFloat {

            0%,100% {
                transform:
                    translateY(0);
            }

            50% {
                transform:
                    translateY(-14px);
            }
        }


        /* ----------------------------------------------------
           ANTENNA
        ---------------------------------------------------- */

        .antenna {

            width: 5px;
            height: 42px;

            background:
                linear-gradient(
                    180deg,
                    #5eeaff,
                    #0788ae
                );

            position: absolute;

            top: -45px;

            left: 50%;

            transform:
                translateX(-50%);

            border-radius: 5px;
        }

        .antenna-ball {

            width: 17px;
            height: 17px;

            border-radius: 50%;

            background: #00d9ff;

            position: absolute;

            top: -12px;

            left: 50%;

            transform:
                translateX(-50%);

            box-shadow:
                0 0 15px #00d9ff,
                0 0 30px rgba(0,217,255,0.6);

            animation:
                antennaPulse 1.4s ease-in-out infinite;
        }

        @keyframes antennaPulse {

            0%,100% {
                transform:
                    translateX(-50%)
                    scale(0.85);

                opacity: 0.7;
            }

            50% {
                transform:
                    translateX(-50%)
                    scale(1.2);

                opacity: 1;
            }
        }


        /* ----------------------------------------------------
           HEAD
        ---------------------------------------------------- */

        .head {

            width: 220px;
            height: 155px;

            position: relative;

            border-radius: 48px;

            background:
                linear-gradient(
                    145deg,
                    #f8fdff,
                    #ccecf5
                );

            border:
                5px solid #087e9e;

            box-shadow:
                inset 0 0 20px
                rgba(255,255,255,0.8),

                0 15px 35px
                rgba(0,120,160,0.25);
        }


        /* ----------------------------------------------------
           EARS
        ---------------------------------------------------- */

        .ear {
            position: absolute;

            top: 52px;

            width: 22px;
            height: 52px;

            background:
                linear-gradient(
                    180deg,
                    #bdebf5,
                    #5fc8df
                );

            border:
                3px solid #087e9e;

            border-radius: 10px;
        }

        .ear.left {
            left: -27px;
        }

        .ear.right {
            right: -27px;
        }


        /* ----------------------------------------------------
           FACE SCREEN
        ---------------------------------------------------- */

        .face {

            position: absolute;

            left: 15px;
            right: 15px;

            top: 20px;
            bottom: 20px;

            border-radius: 32px;

            background:
                linear-gradient(
                    145deg,
                    #063b51,
                    #021f2c
                );

            border:
                3px solid #1ba8c8;

            box-shadow:
                inset 0 0 30px
                rgba(0,220,255,0.10);
        }


        /* ----------------------------------------------------
           EYES
        ---------------------------------------------------- */

        .eyes {

            display: flex;

            justify-content: center;

            gap: 52px;

            margin-top: 34px;
        }

        .eye {

            width: 26px;
            height: 34px;

            border-radius: 50%;

            background:
                radial-gradient(
                    circle at 50% 40%,
                    white 0 10%,
                    #00eaff 25%,
                    #009dcc 60%,
                    #00647e 100%
                );

            box-shadow:
                0 0 12px #00eaff;

            animation:
                blink 4.5s infinite;
        }

        @keyframes blink {

            0%,44%,48%,100% {
                transform:
                    scaleY(1);
            }

            46% {
                transform:
                    scaleY(0.08);
            }
        }


        /* ----------------------------------------------------
           SCAN LINE
        ---------------------------------------------------- */

        .scan {

            position: absolute;

            left: 15px;
            right: 15px;

            top: 20px;

            height: 2px;

            background:
                rgba(0,240,255,0.55);

            box-shadow:
                0 0 8px #00eaff;

            animation:
                scan 2.8s linear infinite;
        }

        @keyframes scan {

            0% {
                top: 20px;
                opacity: 0;
            }

            10% {
                opacity: 1;
            }

            90% {
                opacity: 1;
            }

            100% {
                top: 120px;
                opacity: 0;
            }
        }


        /* ----------------------------------------------------
           MOUTH
        ---------------------------------------------------- */

        .mouth {

            width: 72px;
            height: 25px;

            position: absolute;

            left: 50%;

            transform:
                translateX(-50%);

            bottom: 22px;

            border-radius: 0 0 35px 35px;

            border-bottom:
                5px solid #00eaff;

            box-shadow:
                0 5px 15px
                rgba(0,230,255,0.35);

            animation:
                talk 1.1s ease-in-out infinite;
        }

        @keyframes talk {

            0%,100% {
                height: 12px;
            }

            50% {
                height: 30px;
            }
        }


        /* ----------------------------------------------------
           BODY
        ---------------------------------------------------- */

        .body {

            width: 165px;
            height: 160px;

            margin:
                -2px auto 0;

            position: relative;

            border-radius:
                35px 35px 45px 45px;

            background:
                linear-gradient(
                    145deg,
                    #f3fbff,
                    #b9e6f1
                );

            border:
                5px solid #087e9e;

            box-shadow:
                0 18px 30px
                rgba(0,100,140,0.20);
        }


        /* ----------------------------------------------------
           CHEST
        ---------------------------------------------------- */

        .chest {

            position: absolute;

            width: 72px;
            height: 72px;

            top: 28px;
            left: 50%;

            transform:
                translateX(-50%);

            border-radius: 50%;

            background:
                radial-gradient(
                    circle,
                    #052d3d,
                    #021b27
                );

            border:
                3px solid #00a7c7;

            box-shadow:
                0 0 20px
                rgba(0,220,255,0.20);
        }

        .core {

            position: absolute;

            width: 25px;
            height: 25px;

            top: 50%;
            left: 50%;

            transform:
                translate(-50%, -50%);

            border-radius: 50%;

            background:
                #00eaff;

            box-shadow:
                0 0 15px #00eaff,
                0 0 35px rgba(0,230,255,0.55);

            animation:
                corePulse 1.2s infinite;
        }

        @keyframes corePulse {

            0%,100% {
                transform:
                    translate(-50%, -50%)
                    scale(0.8);

                opacity: 0.65;
            }

            50% {
                transform:
                    translate(-50%, -50%)
                    scale(1.2);

                opacity: 1;
            }
        }


        /* ----------------------------------------------------
           ARMS
        ---------------------------------------------------- */

        .arm {

            width: 35px;
            height: 105px;

            position: absolute;

            top: 28px;

            border-radius: 22px;

            background:
                linear-gradient(
                    180deg,
                    #e5f8fc,
                    #82d4e5
                );

            border:
                4px solid #087e9e;
        }

        .arm.left {

            left: -40px;

            transform:
                rotate(16deg);

            transform-origin:
                top center;

            animation:
                leftArm 2.5s ease-in-out infinite;
        }

        .arm.right {

            right: -40px;

            transform:
                rotate(-16deg);

            transform-origin:
                top center;

            animation:
                rightArm 2.5s ease-in-out infinite;
        }

        @keyframes leftArm {

            0%,100% {
                transform:
                    rotate(16deg);
            }

            50% {
                transform:
                    rotate(28deg);
            }
        }

        @keyframes rightArm {

            0%,100% {
                transform:
                    rotate(-16deg);
            }

            50% {
                transform:
                    rotate(-28deg);
            }
        }


        /* ----------------------------------------------------
           STATUS LIGHTS
        ---------------------------------------------------- */

        .lights {

            position: absolute;

            bottom: 25px;

            left: 50%;

            transform:
                translateX(-50%);

            display: flex;

            gap: 8px;
        }

        .light {

            width: 8px;
            height: 8px;

            border-radius: 50%;

            background:
                #00eaff;

            box-shadow:
                0 0 10px #00eaff;

            animation:
                lightBlink 1.5s infinite;
        }

        .light:nth-child(2) {
            animation-delay: .2s;
        }

        .light:nth-child(3) {
            animation-delay: .4s;
        }

        @keyframes lightBlink {

            0%,100% {
                opacity: 0.3;
            }

            50% {
                opacity: 1;
            }
        }

    </style>

    </head>

    <body>

        <div class="scene">

            <div class="floor"></div>

            <div class="robot">

                <div class="antenna">
                    <div class="antenna-ball"></div>
                </div>

                <div class="head">

                    <div class="ear left"></div>
                    <div class="ear right"></div>

                    <div class="face">

                        <div class="scan"></div>

                        <div class="eyes">
                            <div class="eye"></div>
                            <div class="eye"></div>
                        </div>

                        <div class="mouth"></div>

                    </div>

                </div>

                <div class="body">

                    <div class="arm left"></div>
                    <div class="arm right"></div>

                    <div class="chest">
                        <div class="core"></div>
                    </div>

                    <div class="lights">
                        <div class="light"></div>
                        <div class="light"></div>
                        <div class="light"></div>
                    </div>

                </div>

            </div>

        </div>

    </body>
    </html>
    """

    components.html(
        robot_html,
        height=510,
        scrolling=False
    )


# ============================================================
# DEMO RESPONSE
# ============================================================

def demo_response(question):

    question_lower = question.lower().strip()

    if any(word in question_lower for word in ["hello", "hi", "salam", "assalam"]):
        return (
            "Hello! 👋 Welcome to Baithak With AI. "
            "I am currently running in Trial/Demo Mode. "
            "You can ask me questions, and I will try my best to help."
        )

    if "your name" in question_lower:
        return (
            "My name is Baithak With AI. 🤖 "
            "I am your intelligent voice and text assistant."
        )

    if "python" in question_lower:
        return (
            "Python is a beginner-friendly programming language "
            "widely used for AI, data science, automation, web apps, "
            "and smart systems."
        )

    if "streamlit" in question_lower:
        return (
            "Streamlit is a Python framework that makes it easy "
            "to build interactive data and AI web applications."
        )

    if "ai" in question_lower:
        return (
            "Artificial Intelligence enables computer systems to "
            "perform tasks that normally require human intelligence, "
            "such as understanding language, recognizing patterns, "
            "and making predictions."
        )

    return (
        "I am currently operating in Trial/Demo Mode. 🤖\n\n"
        "Please configure your OPENAI_API_KEY in Streamlit Secrets "
        "to enable full AI-powered responses."
    )


# ============================================================
# TEXT AI RESPONSE
# ============================================================

def generate_ai_response(question):

    if not question or not question.strip():
        return "Please enter a question."

    if client is None:

        return demo_response(question)

    try:

        recent_messages = st.session_state.messages[-12:]

        conversation = []

        for item in recent_messages:

            conversation.append(
                {
                    "role": item["role"],
                    "content": item["content"]
                }
            )

        conversation.append(
            {
                "role": "user",
                "content": question
            }
        )

        response = client.responses.create(
            model=OPENAI_MODEL,

            instructions=(
                "You are Baithak With AI, a friendly, intelligent "
                "and professional AI assistant. "
                "Answer clearly and naturally. "
                "Use simple language when appropriate. "
                "You may respond in English, Urdu, or Roman Urdu "
                "according to the user's language. "
                "Do not claim to be a human. "
                "Keep answers useful and reasonably concise."
            ),

            input=conversation
        )

        answer = response.output_text

        if not answer:
            return "I could not generate a response. Please try again."

        return answer

    except Exception as e:

        st.session_state.last_error = str(e)

        return (
            "⚠️ I encountered an AI service error.\n\n"
            "Please check your OpenAI API key, model configuration, "
            "API credits, and internet connection."
        )


# ============================================================
# SPEECH TO TEXT
# ============================================================

def transcribe_audio(audio_file):

    if audio_file is None:
        return ""

    if client is None:

        return (
            "Voice transcription requires an OpenAI API key. "
            "Please configure OPENAI_API_KEY in Streamlit Secrets."
        )

    try:

        audio_bytes = audio_file.getvalue()

        with open(
            "temporary_voice_input.wav",
            "wb"
        ) as f:

            f.write(audio_bytes)

        with open(
            "temporary_voice_input.wav",
            "rb"
        ) as audio:

            transcription = client.audio.transcriptions.create(
                model=TRANSCRIPTION_MODEL,
                file=audio
            )

        text = getattr(
            transcription,
            "text",
            ""
        )

        return text.strip()

    except Exception as e:

        st.session_state.last_error = str(e)

        return ""


# ============================================================
# TEXT TO SPEECH
# ============================================================

def generate_speech(text):

    if not text:
        return None

    if client is None:
        return None

    try:

        speech_response = client.audio.speech.create(
            model=TTS_MODEL,
            voice=TTS_VOICE,
            input=text
        )

        audio_bytes = speech_response.read()

        return audio_bytes

    except Exception as e:

        st.session_state.last_error = str(e)

        return None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Baithak Settings")

    st.divider()

    st.subheader("AI Mode")

    if client:

        st.success(
            "🟢 OpenAI Connected"
        )

    else:

        st.warning(
            "🟡 Trial / Demo Mode"
        )

    st.caption(
        f"Model: `{OPENAI_MODEL}`"
    )

    st.divider()

    st.subheader("🎙️ Voice")

    voice_enabled = st.toggle(
        "Enable AI Voice Response",
        value=True
    )

    st.divider()

    st.subheader("🧹 Conversation")

    if st.button(
        "Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.last_answer = ""
        st.session_state.voice_audio = None

        st.rerun()

    st.divider()

    st.subheader("ℹ️ About")

    st.write(
        """
        **BAITHAK WITH AI** is an AI-powered
        voice and text assistant.

        You can:

        🎤 Speak through your microphone

        💬 Type questions

        🤖 Get AI responses

        🔊 Listen to AI responses

        🧪 Test the application in Trial Mode
        """
    )

    st.divider()

    st.caption(
        "BAITHAK WITH AI • Trial Edition"
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.title("🤖 BAITHAK WITH AI")

st.subheader(
    "Your Intelligent Voice & Text AI Assistant"
)

st.caption(
    "Speak naturally, type your question, and interact with your AI assistant."
)


# ============================================================
# STATUS
# ============================================================

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:

    if client:

        st.markdown(
            '<div class="status-online">'
            '🟢 AI ONLINE'
            '</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<div class="status-demo">'
            '🧪 TRIAL MODE'
            '</div>',
            unsafe_allow_html=True
        )


with status_col2:

    st.markdown(
        '<div class="status-online">'
        '🎤 VOICE READY'
        '</div>',
        unsafe_allow_html=True
    )


with status_col3:

    st.markdown(
        '<div class="status-online">'
        '💬 CHAT READY'
        '</div>',
        unsafe_allow_html=True
    )


st.divider()


# ============================================================
# ROBOT SECTION
# ============================================================

robot_col, intro_col = st.columns(
    [1.1, 1],
    gap="large"
)

with robot_col:

    show_animated_robot()


with intro_col:

    st.header("Welcome to Baithak 👋")

    st.write(
        """
        Baithak With AI is your intelligent digital
        conversation partner.

        You can communicate with Baithak using
        **text or your microphone**.
        """
    )

    st.info(
        "🎤 Use the microphone below to speak with Baithak."
    )

    st.info(
        "💬 Or type your question in the chat box."
    )

    if client:

        st.success(
            "OpenAI AI services are connected."
        )

    else:

        st.warning(
            "Trial Mode is active. Configure "
            "`OPENAI_API_KEY` in Streamlit Secrets "
            "for full AI functionality."
        )


st.divider()


# ============================================================
# VOICE INPUT
# ============================================================

st.header("🎤 Talk to Baithak")

st.write(
    "Click the microphone, speak naturally, and submit your voice message."
)

audio_input = st.audio_input(
    "Record your voice"
)


if audio_input is not None:

    st.session_state.voice_audio = audio_input

    st.audio(
        audio_input
    )

    voice_col1, voice_col2 = st.columns(
        [1, 1]
    )

    with voice_col1:

        if st.button(
            "🎙️ Process Voice",
            use_container_width=True,
            type="primary"
        ):

            with st.spinner(
                "Listening and converting your voice..."
            ):

                transcript = transcribe_audio(
                    audio_input
                )

            if transcript:

                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": transcript
                    }
                )

                with st.spinner(
                    "Baithak is thinking..."
                ):

                    answer = generate_ai_response(
                        transcript
                    )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

                st.session_state.last_answer = answer

                if voice_enabled and client:

                    with st.spinner(
                        "Generating voice response..."
                    ):

                        audio_bytes = generate_speech(
                            answer
                        )

                    st.session_state.voice_audio = audio_bytes

                st.rerun()

    with voice_col2:

        if st.button(
            "🗑️ Remove Voice",
            use_container_width=True
        ):

            st.session_state.voice_audio = None

            st.rerun()


# ============================================================
# LAST AI VOICE RESPONSE
# ============================================================

if (
    st.session_state.voice_audio
    and isinstance(
        st.session_state.voice_audio,
        bytes
    )
):

    st.subheader(
        "🔊 Baithak's Voice Response"
    )

    st.audio(
        st.session_state.voice_audio,
        format="audio/mp3"
    )


st.divider()


# ============================================================
# CHAT
# ============================================================

st.header("💬 Chat with Baithak")


if not st.session_state.messages:

    st.info(
        "👋 Start a conversation by typing a message below "
        "or use the microphone above."
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    role = message["role"]

    content = message["content"]

    if role == "user":

        with st.chat_message(
            "user",
            avatar="👤"
        ):

            st.markdown(content)

    else:

        with st.chat_message(
            "assistant",
            avatar="🤖"
        ):

            st.markdown(content)


# ============================================================
# CHAT INPUT
# ============================================================

user_prompt = st.chat_input(
    "Type your message to Baithak..."
)


if user_prompt:

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )

    # Display immediately
    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.markdown(user_prompt)

    # Generate answer
    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        with st.spinner(
            "Baithak is thinking..."
        ):

            answer = generate_ai_response(
                user_prompt
            )

        st.markdown(answer)

    # Save answer
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    st.session_state.last_answer = answer

    # Generate voice
    if voice_enabled and client:

        with st.spinner(
            "Preparing voice response..."
        ):

            audio_bytes = generate_speech(
                answer
            )

        if audio_bytes:

            st.session_state.voice_audio = audio_bytes

            st.audio(
                audio_bytes,
                format="audio/mp3"
            )

    st.rerun()


# ============================================================
# ERROR INFORMATION
# ============================================================

if st.session_state.last_error:

    with st.expander(
        "⚠️ Technical Information"
    ):

        st.code(
            st.session_state.last_error
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">

        🤖 <b>BAITHAK WITH AI</b><br>

        Intelligent Voice & Text AI Assistant<br>

        🧪 Trial Edition • Powered by AI

    </div>
    """,
    unsafe_allow_html=True
)
