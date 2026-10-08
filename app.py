
import os
import tempfile
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
You are BAITHAK WITH AI, a helpful, intelligent and friendly
AI assistant.

You can communicate in English, Urdu, Roman Urdu and other
languages when appropriate.

Give clear, practical and accurate answers.

For technical questions, provide step-by-step guidance.

Be concise when a short answer is sufficient.
"""


# ============================================================
# SECRET MANAGEMENT
# ============================================================

def get_secret(name, default=""):
    try:
        value = st.secrets.get(name, default)

        if value:
            return str(value).strip()

    except Exception:
        pass

    return os.getenv(name, default).strip()


OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
OPENAI_MODEL = get_secret(
    "OPENAI_MODEL",
    DEFAULT_MODEL
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


# ============================================================
# DEMO RESPONSE
# ============================================================

def demo_response(prompt):

    text = prompt.lower().strip()

    if any(word in text for word in [
        "hello",
        "hi",
        "salam",
        "assalam"
    ]):
        return (
            "Assalam-o-Alaikum! 👋\n\n"
            "Welcome to BAITHAK WITH AI. "
            "How can I help you today?"
        )

    if any(word in text for word in [
        "ai",
        "artificial intelligence",
        "agentic ai"
    ]):
        return (
            "Artificial Intelligence enables machines to perform "
            "tasks that normally require human intelligence.\n\n"
            "Agentic AI can reason, plan, use tools and work "
            "toward defined objectives."
        )

    if any(word in text for word in [
        "python",
        "programming",
        "coding"
    ]):
        return (
            "Python is widely used for AI, automation, data science, "
            "robotics and application development.\n\n"
            "Tell me what you want to build and I can guide you."
        )

    if any(word in text for word in [
        "robot",
        "robotics",
        "arduino",
        "raspberry pi",
        "jetson"
    ]):
        return (
            "Robotics combines mechanical systems, electronics, "
            "embedded systems, sensors, actuators and software.\n\n"
            "Arduino, Raspberry Pi and Jetson platforms can be "
            "used to create practical robotics systems."
        )

    if any(word in text for word in [
        "study",
        "education",
        "learning",
        "course"
    ]):
        return (
            "A practical learning strategy is:\n\n"
            "1. Define the objective\n"
            "2. Learn the fundamentals\n"
            "3. Practice\n"
            "4. Build a project\n"
            "5. Review and improve\n\n"
            "Tell me your subject and I can create a study plan."
        )

    return (
        "BAITHAK WITH AI is currently running in Demo Mode.\n\n"
        "Configure your OPENAI_API_KEY in Streamlit Secrets "
        "to enable full OpenAI capabilities."
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
# ERROR CLASSIFICATION
# ============================================================

def classify_openai_error(error):

    text = str(error).lower()

    status_code = getattr(
        error,
        "status_code",
        None
    )

    error_code = str(
        getattr(error, "code", "")
        or ""
    ).lower()

    if (
        "insufficient_quota" in text
        or "credit_balance_exhausted" in text
        or "no credits remaining" in text
        or "quota" in text
        or error_code in [
            "insufficient_quota",
            "credit_balance_exhausted"
        ]
    ):
        return "quota"

    if (
        "invalid_api_key" in text
        or "incorrect api key" in text
        or "authentication" in text
        or status_code == 401
        or "401" in text
    ):
        return "invalid_key"

    if (
        "model_not_found" in text
        or "does not exist" in text
        or "do not have access" in text
    ):
        return "model"

    if (
        "rate_limit" in text
        or "rate limit" in text
    ):
        return "rate_limit"

    if status_code == 429:

        if "quota" in text:
            return "quota"

        return "rate_limit"

    return "api_error"


# ============================================================
# FRIENDLY ERROR HANDLING
# ============================================================

def show_openai_error(error_type):

    if error_type == "missing_key":

        message = (
            "⚠️ Kindly Use Your API Credentials "
            "in Streamlit Secrets!"
        )

        st.toast(
            message,
            icon="⚠️"
        )

        st.warning(message)

        st.info(
            "Add OPENAI_API_KEY to your Streamlit Secrets."
        )

    elif error_type == "quota":

        message = (
            "⚠️ Kindly Use Your API Credentials "
            "in Streamlit Secrets!"
        )

        st.toast(
            message,
            icon="⚠️"
        )

        st.warning(message)

        st.info(
            "OpenAI API credits are exhausted or unavailable. "
            "BAITHAK WITH AI has automatically switched "
            "to Demo Mode."
        )

    elif error_type == "invalid_key":

        st.toast(
            "⚠️ Please check your OpenAI API credentials.",
            icon="⚠️"
        )

        st.warning(
            "OpenAI authentication failed. "
            "Please check OPENAI_API_KEY in Streamlit Secrets."
        )

    elif error_type == "model":

        st.toast(
            "⚠️ OpenAI model is unavailable.",
            icon="⚠️"
        )

        st.warning(
            "The configured OpenAI model is unavailable "
            "for this account."
        )

    elif error_type == "rate_limit":

        st.toast(
            "⏳ OpenAI rate limit reached.",
            icon="⏳"
        )

        st.info(
            "Please wait a moment and try again. "
            "Demo Mode is being used temporarily."
        )

    else:

        st.toast(
            "⚠️ OpenAI API is temporarily unavailable.",
            icon="⚠️"
        )

        st.info(
            "BAITHAK WITH AI has switched to Demo Mode."
        )


# ============================================================
# OPENAI CHAT
# ============================================================

def ask_openai(user_prompt):

    client = create_openai_client()

    if client is None:
        return None, "missing_key"

    try:

        conversation = []

        for message in st.session_state.messages[-12:]:

            if message["role"] in [
                "user",
                "assistant"
            ]:

                conversation.append({
                    "role": message["role"],
                    "content": message["content"]
                })

        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=conversation,
        )

        answer = getattr(
            response,
            "output_text",
            ""
        )

        if not answer:
            return None, "api_error"

        return answer.strip(), None

    except Exception as error:

        return None, classify_openai_error(error)


# ============================================================
# OPENAI SPEECH TO TEXT
# ============================================================

def transcribe_audio(audio_file):

    client = create_openai_client()

    if client is None:
        return None, "missing_key"

    temporary_file = None

    try:

        audio_bytes = audio_file.getvalue()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_file:

            temp_file.write(audio_bytes)
            temporary_file = temp_file.name

        with open(
            temporary_file,
            "rb"
        ) as audio:

            result = client.audio.transcriptions.create(
                model=TRANSCRIPTION_MODEL,
                file=audio,
            )

        transcript = getattr(
            result,
            "text",
            ""
        )

        if not transcript:
            return None, "api_error"

        return transcript.strip(), None

    except Exception as error:

        return None, classify_openai_error(error)

    finally:

        if temporary_file:

            try:
                os.remove(temporary_file)
            except Exception:
                pass


# ============================================================
# OPENAI TEXT TO SPEECH
# ============================================================

def generate_speech(text):

    client = create_openai_client()

    if client is None:
        return None, "missing_key"

    try:

        response = client.audio.speech.create(
            model=TTS_MODEL,
            voice=TTS_VOICE,
            input=text[:4000],
        )

        audio_data = response.read()

        if not audio_data:
            return None, "api_error"

        return audio_data, None

    except Exception as error:

        return None, classify_openai_error(error)


# ============================================================
# SKY BLUE UI
# ============================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL SKY BLUE THEME
       ===================================================== */

    .stApp {

        background:
            linear-gradient(
                135deg,
                #eaf9ff 0%,
                #d9f3ff 35%,
                #c4edff 70%,
                #b3e7ff 100%
            );

        color: #06324a;

    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #d8f5ff 0%,
                #bceaff 100%
            );

        border-right:
            2px solid rgba(0, 153, 204, 0.20);

    }


    /* =====================================================
       MAIN TITLE
       ===================================================== */

    .main-title {

        text-align: center;

        font-size:
            clamp(2.2rem, 5vw, 4rem);

        font-weight: 900;

        letter-spacing: 2px;

        color: #005b82;

        text-shadow:
            0 3px 12px
            rgba(0, 126, 170, 0.20);

        margin-top: 5px;

        margin-bottom: 0;

    }


    .subtitle {

        text-align: center;

        font-size: 1.10rem;

        font-weight: 600;

        color: #176b8d;

        margin-top: 4px;

        margin-bottom: 25px;

    }


    /* =====================================================
       ROBOT HERO
       ===================================================== */

    .robot-box {

        position: relative;

        overflow: hidden;

        border-radius: 32px;

        padding: 35px 20px 30px;

        text-align: center;

        background:
            linear-gradient(
                135deg,
                #62d5ff 0%,
                #36bff0 45%,
                #159bd0 100%
            );

        color: white;

        border:
            2px solid
            rgba(255,255,255,0.65);

        box-shadow:
            0 18px 45px
            rgba(0, 126, 170, 0.25);

        margin-bottom: 25px;

    }


    /* Animated light circles */

    .robot-box::before {

        content: "";

        position: absolute;

        width: 220px;
        height: 220px;

        border-radius: 50%;

        background:
            rgba(255,255,255,0.15);

        top: -100px;
        left: -70px;

        animation:
            bubbleMove 7s infinite ease-in-out;

    }


    .robot-box::after {

        content: "";

        position: absolute;

        width: 180px;
        height: 180px;

        border-radius: 50%;

        background:
            rgba(255,255,255,0.12);

        right: -60px;
        bottom: -90px;

        animation:
            bubbleMove2 6s infinite ease-in-out;

    }


    @keyframes bubbleMove {

        0%, 100% {
            transform: translate(0, 0);
        }

        50% {
            transform: translate(80px, 40px);
        }

    }


    @keyframes bubbleMove2 {

        0%, 100% {
            transform: translate(0, 0);
        }

        50% {
            transform: translate(-50px, -30px);
        }

    }


    /* =====================================================
       ANIMATED ROBOT
       ===================================================== */

    .robot-stage {

        position: relative;

        display: inline-block;

        width: 180px;

        height: 190px;

        z-index: 5;

        animation:
            robotFloat 3s ease-in-out infinite;

    }


    .robot-head {

        position: absolute;

        width: 125px;

        height: 105px;

        left: 27px;

        top: 15px;

        border-radius: 35px;

        background:
            linear-gradient(
                145deg,
                #ffffff,
                #dcefff
            );

        border:
            5px solid #087da8;

        box-shadow:
            inset 0 -8px 15px
            rgba(0, 100, 140, 0.12),

            0 10px 30px
            rgba(0, 77, 110, 0.30);

    }


    .robot-eye {

        position: absolute;

        width: 22px;
        height: 30px;

        top: 37px;

        border-radius: 50%;

        background:
            #00bfff;

        box-shadow:
            0 0 12px #00eaff,
            0 0 25px #00d9ff;

        animation:
            eyeBlink 4s infinite;

    }


    .robot-eye.left {

        left: 28px;

    }


    .robot-eye.right {

        right: 28px;

    }


    .robot-mouth {

        position: absolute;

        width: 48px;

        height: 18px;

        left: 34px;

        bottom: 17px;

        border-bottom:
            5px solid #087da8;

        border-radius:
            0 0 30px 30px;

    }


    .robot-ear {

        position: absolute;

        width: 18px;
        height: 42px;

        top: 46px;

        border-radius: 10px;

        background: #079aca;

        border: 3px solid #087da8;

    }


    .robot-ear.left {

        left: 8px;

    }


    .robot-ear.right {

        right: 8px;

    }


    .robot-antenna {

        position: absolute;

        width: 6px;

        height: 30px;

        background: #087da8;

        left: 88px;

        top: -13px;

        border-radius: 5px;

    }


    .robot-light {

        position: absolute;

        width: 15px;
        height: 15px;

        left: 83px;

        top: -25px;

        border-radius: 50%;

        background: #ffffff;

        box-shadow:
            0 0 10px #ffffff,
            0 0 25px #00eaff;

        animation:
            lightPulse 1.2s infinite;

    }


    .robot-body {

        position: absolute;

        width: 105px;

        height: 65px;

        left: 37px;

        top: 116px;

        border-radius: 28px 28px 20px 20px;

        background:
            linear-gradient(
                145deg,
                #f7fdff,
                #c9eaff
            );

        border:
            5px solid #087da8;

        box-shadow:
            0 10px 25px
            rgba(0, 77, 110, 0.25);

    }


    .robot-panel {

        position: absolute;

        width: 45px;

        height: 25px;

        left: 25px;

        top: 15px;

        border-radius: 8px;

        background: #0b9dcc;

        border: 2px solid #066986;

    }


    .robot-dot {

        display: inline-block;

        width: 7px;

        height: 7px;

        margin: 7px 2px;

        border-radius: 50%;

        background: #8ff5ff;

        animation:
            dotPulse 1s infinite alternate;

    }


    .robot-arm {

        position: absolute;

        width: 16px;

        height: 55px;

        top: 121px;

        border-radius: 10px;

        background: #d9f2ff;

        border: 4px solid #087da8;

    }


    .robot-arm.left {

        left: 18px;

        transform:
            rotate(20deg);

        animation:
            leftArm 2.5s infinite ease-in-out;

    }


    .robot-arm.right {

        right: 18px;

        transform:
            rotate(-20deg);

        animation:
            rightArm 2.5s infinite ease-in-out;

    }


    @keyframes robotFloat {

        0%, 100% {
            transform: translateY(0px);
        }

        50% {
            transform: translateY(-15px);
        }

    }


    @keyframes eyeBlink {

        0%, 44%, 48%, 100% {
            transform: scaleY(1);
        }

        46% {
            transform: scaleY(0.12);
        }

    }


    @keyframes lightPulse {

        0%, 100% {
            opacity: 0.5;
            transform: scale(0.8);
        }

        50% {
            opacity: 1;
            transform: scale(1.2);
        }

    }


    @keyframes dotPulse {

        from {
            opacity: 0.3;
        }

        to {
            opacity: 1;
        }

    }


    @keyframes leftArm {

        0%, 100% {
            transform: rotate(20deg);
        }

        50% {
            transform: rotate(5deg);
        }

    }


    @keyframes rightArm {

        0%, 100% {
            transform: rotate(-20deg);
        }

        50% {
            transform: rotate(-5deg);
        }

    }


    /* =====================================================
       HERO TEXT
       ===================================================== */

    .hero-heading {

        position: relative;

        z-index: 10;

        font-size: 2rem;

        font-weight: 900;

        margin-top: 10px;

        text-shadow:
            0 2px 5px
            rgba(0, 70, 100, 0.20);

    }


    .hero-text {

        position: relative;

        z-index: 10;

        font-size: 1.05rem;

        font-weight: 600;

        margin: 6px;

    }


    .flow-text {

        position: relative;

        z-index: 10;

        display: inline-block;

        padding: 10px 18px;

        border-radius: 50px;

        background:
            rgba(255,255,255,0.18);

        border:
            1px solid
            rgba(255,255,255,0.45);

        font-weight: 800;

        margin-top: 10px;

    }


    /* =====================================================
       VOICE SECTION
       ===================================================== */

    .voice-card {

        padding: 18px;

        border-radius: 20px;

        background:
            rgba(255,255,255,0.65);

        border:
            1px solid
            rgba(0, 130, 180, 0.18);

        box-shadow:
            0 8px 25px
            rgba(0, 120, 170, 0.10);

        margin-bottom: 18px;

    }


    .voice-title {

        text-align: center;

        font-size: 1.5rem;

        font-weight: 900;

        color: #005b82;

    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {

        border-radius: 14px !important;

        font-weight: 700 !important;

        border:
            1px solid
            rgba(0, 126, 170, 0.25) !important;

    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {

        text-align: center;

        color: #075b7c;

        padding: 35px 5px 15px;

        font-size: 0.92rem;

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
    '<div class="subtitle">'
    'OpenAI-Powered Intelligent Voice & Chat Assistant'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ BAITHAK SETTINGS")

    st.session_state.mode = st.radio(
        "AI Mode",
        [
            "Demo Mode",
            "OpenAI API Mode"
        ],
        index=(
            1
            if st.session_state.mode
            == "OpenAI API Mode"
            else 0
        )
    )

    st.divider()

    st.subheader("🔐 OpenAI Status")

    if OPENAI_API_KEY:

        st.success(
            "OpenAI API Key Detected"
        )

    else:

        st.warning(
            "OpenAI API Key Not Found"
        )

    st.caption(
        "Only OpenAI is used for AI, "
        "speech-to-text and text-to-speech."
    )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.last_answer = ""
        st.session_state.voice_audio = None

        st.rerun()


# ============================================================
# ANIMATED ROBOT HERO
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
    unsafe_allow_html=True
)


# ============================================================
# MICROPHONE
# ============================================================

st.markdown(
    """
    <div class="voice-card">

        <div class="voice-title">
            🎤 TALK TO BAITHAK
        </div>

    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Press the microphone button, record your question, "
    "then convert your speech using OpenAI."
)

audio_input = st.audio_input(
    "🎤 Record your question"
)


if audio_input is not None:

    st.audio(
        audio_input
    )

    if st.button(
        "🧠 Convert Speech to Text",
        type="primary",
        use_container_width=True
    ):

        if not OPENAI_API_KEY:

            show_openai_error(
                "missing_key"
            )

        else:

            with st.spinner(
                "🎤 OpenAI is converting your speech..."
            ):

                transcript, error_type = (
                    transcribe_audio(
                        audio_input
                    )
                )

            if error_type:

                show_openai_error(
                    error_type
                )

            elif transcript:

                st.success(
                    "✅ Speech converted successfully."
                )

                st.markdown(
                    "**📝 You said:**"
                )

                st.info(
                    transcript
                )

                st.session_state.messages.append({
                    "role": "user",
                    "content": transcript
                })

                # --------------------------------------------
                # AI RESPONSE
                # --------------------------------------------

                if (
                    st.session_state.mode
                    == "OpenAI API Mode"
                ):

                    with st.spinner(
                        "🤖 BAITHAK WITH AI is thinking..."
                    ):

                        answer, error_type = (
                            ask_openai(
                                transcript
                            )
                        )

                    if error_type:

                        show_openai_error(
                            error_type
                        )

                        st.session_state.mode = (
                            "Demo Mode"
                        )

                        answer = demo_response(
                            transcript
                        )

                else:

                    answer = demo_response(
                        transcript
                    )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                st.session_state.last_answer = answer

                st.rerun()


# ============================================================
# TEXT CHAT
# ============================================================

user_prompt = st.chat_input(
    "💬 Type your message here..."
)


if user_prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": user_prompt
    })

    if (
        st.session_state.mode
        == "OpenAI API Mode"
    ):

        with st.spinner(
            "🤖 BAITHAK WITH AI is thinking..."
        ):

            answer, error_type = (
                ask_openai(
                    user_prompt
                )
            )

        if error_type:

            show_openai_error(
                error_type
            )

            st.session_state.mode = (
                "Demo Mode"
            )

            answer = demo_response(
                user_prompt
            )

    else:

        answer = demo_response(
            user_prompt
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.session_state.last_answer = answer

    st.rerun()


# ============================================================
# CONVERSATION
# ============================================================

if st.session_state.messages:

    st.divider()

    st.subheader(
        "💬 Conversation"
    )

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


# ============================================================
# OPENAI TEXT TO SPEECH
# ============================================================

if st.session_state.last_answer:

    st.divider()

    st.subheader(
        "🔊 AI VOICE RESPONSE"
    )

    if st.button(
        "🔊 Speak Response with OpenAI",
        type="primary",
        use_container_width=True
    ):

        if not OPENAI_API_KEY:

            show_openai_error(
                "missing_key"
            )

        else:

            with st.spinner(
                "🔊 OpenAI is generating voice..."
            ):

                audio_data, error_type = (
                    generate_speech(
                        st.session_state.last_answer
                    )
                )

            if error_type:

                show_openai_error(
                    error_type
                )

            elif audio_data:

                st.session_state.voice_audio = (
                    audio_data
                )

                st.success(
                    "✅ OpenAI voice generated successfully."
                )

    if st.session_state.voice_audio:

        st.audio(
            st.session_state.voice_audio,
            format="audio/mp3"
        )

        st.download_button(
            "⬇️ Download AI Voice",
            data=st.session_state.voice_audio,
            file_name="baithak_ai_voice.mp3",
            mime="audio/mpeg",
            use_container_width=True
        )


# ============================================================
# STREAMLIT SECRETS
# ============================================================

with st.expander(
    "🔐 OPENAI STREAMLIT SECRETS"
):

    st.markdown(
        """
        ### Use only OpenAI credentials

        Go to:

        **Streamlit → App → Settings → Secrets**

        Add:
        """
    )

    st.code(
        'OPENAI_API_KEY = "your-openai-api-key"\n'
        'OPENAI_MODEL = "gpt-4o-mini"',
        language="toml"
    )

    st.success(
        "Google API is completely removed. "
        "Only OpenAI is used."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        <strong>
            Designed by Certified Generative and Agentic
            AI Application Developer
        </strong>

        <br>

        Engr. Bilal Mehmood

    </div>
    """,
    unsafe_allow_html=True
)

