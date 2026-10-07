```python
import os
import base64
import html
import tempfile
from pathlib import Path

import streamlit as st

# ============================================================
# OPTIONAL OPENAI IMPORT
# ============================================================

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Baithak With AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(0, 170, 255, 0.12), transparent 30%),
        radial-gradient(circle at 85% 20%, rgba(140, 70, 255, 0.12), transparent 30%),
        linear-gradient(135deg, #07111f 0%, #0b1220 50%, #10182b 100%);
    color: white;
}

/* Hide Streamlit branding */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

/* Main title */
.baithak-title {
    text-align: center;
    font-size: 3.1rem;
    font-weight: 800;
    margin-top: 10px;
    margin-bottom: 0;
    letter-spacing: -2px;
}

.baithak-title span {
    background: linear-gradient(90deg, #00d4ff, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.baithak-subtitle {
    text-align: center;
    color: #aab7ca;
    font-size: 1rem;
    margin-bottom: 20px;
}

/* Robot area */
.robot-stage {
    width: 100%;
    min-height: 430px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}

/* Robot */
.robot {
    position: relative;
    width: 230px;
    height: 300px;
    animation: floatRobot 3.2s ease-in-out infinite;
}

@keyframes floatRobot {
    0%, 100% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-15px);
    }
}

/* Glow */
.robot-glow {
    position: absolute;
    width: 260px;
    height: 260px;
    border-radius: 50%;
    left: -15px;
    top: 20px;
    background: radial-gradient(
        circle,
        rgba(0, 212, 255, 0.22),
        rgba(139, 92, 246, 0.10),
        transparent 70%
    );
    filter: blur(10px);
    animation: pulseGlow 2s infinite;
}

@keyframes pulseGlow {
    0%, 100% {
        transform: scale(0.95);
        opacity: 0.6;
    }
    50% {
        transform: scale(1.1);
        opacity: 1;
    }
}

/* Robot antenna */
.antenna {
    position: absolute;
    width: 6px;
    height: 35px;
    background: #5ee7ff;
    left: 112px;
    top: -25px;
    border-radius: 10px;
}

.antenna-dot {
    position: absolute;
    width: 15px;
    height: 15px;
    border-radius: 50%;
    background: #00d9ff;
    box-shadow: 0 0 25px #00d9ff;
    left: -4px;
    top: -10px;
    animation: antennaBlink 1.2s infinite;
}

@keyframes antennaBlink {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}

/* Robot head */
.robot-head {
    position: absolute;
    width: 190px;
    height: 145px;
    left: 20px;
    top: 15px;
    border-radius: 42px;
    background:
        linear-gradient(145deg, #dbeafe, #8da8c5);
    border: 5px solid #51677e;
    box-shadow:
        inset 0 0 20px rgba(255,255,255,0.5),
        0 15px 45px rgba(0,0,0,0.35);
}

/* Face screen */
.robot-face {
    position: absolute;
    width: 155px;
    height: 92px;
    left: 13px;
    top: 20px;
    border-radius: 28px;
    background: #07111c;
    border: 3px solid #1c3a52;
    overflow: hidden;
    box-shadow: inset 0 0 25px rgba(0,212,255,0.1);
}

/* Eyes */
.eye {
    position: absolute;
    width: 29px;
    height: 40px;
    border-radius: 50%;
    background: #4deaff;
    box-shadow: 0 0 20px rgba(77,234,255,0.8);
    top: 22px;
    animation: blink 4s infinite;
}

.eye-left {
    left: 30px;
}

.eye-right {
    right: 30px;
}

@keyframes blink {
    0%, 45%, 48%, 100% {
        transform: scaleY(1);
    }
    46%, 47% {
        transform: scaleY(0.08);
    }
}

/* Mouth */
.robot-mouth {
    position: absolute;
    width: 48px;
    height: 12px;
    border-radius: 20px;
    border: 3px solid #4deaff;
    left: 51px;
    bottom: 12px;
    animation: mouthTalk 1s infinite;
}

@keyframes mouthTalk {
    0%, 100% {
        height: 8px;
    }
    50% {
        height: 22px;
    }
}

/* Robot body */
.robot-body {
    position: absolute;
    width: 150px;
    height: 115px;
    left: 40px;
    top: 165px;
    border-radius: 40px 40px 25px 25px;
    background: linear-gradient(145deg, #dbeafe, #829ab3);
    border: 5px solid #51677e;
    box-shadow: 0 15px 35px rgba(0,0,0,0.3);
}

/* Chest */
.chest {
    position: absolute;
    width: 75px;
    height: 48px;
    left: 32px;
    top: 25px;
    border-radius: 15px;
    background: #07111c;
    border: 3px solid #27465e;
}

.chest-light {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #00d9ff;
    box-shadow: 0 0 20px #00d9ff;
    margin: 15px auto;
    animation: chestPulse 1s infinite;
}

@keyframes chestPulse {
    0%,100% {
        transform: scale(0.8);
    }
    50% {
        transform: scale(1.3);
    }
}

/* Arms */
.arm {
    position: absolute;
    width: 30px;
    height: 90px;
    background: linear-gradient(145deg, #dbeafe, #829ab3);
    border: 4px solid #51677e;
    border-radius: 20px;
    top: 175px;
}

.arm-left {
    left: 4px;
    transform: rotate(12deg);
}

.arm-right {
    right: 4px;
    transform: rotate(-12deg);
}

/* Robot status */
.robot-status {
    text-align: center;
    margin-top: 12px;
    font-size: 0.9rem;
    color: #6ee7ff;
    letter-spacing: 1px;
}

/* Chat container */
.chat-box {
    background: rgba(12, 22, 39, 0.82);
    border: 1px solid rgba(130, 160, 200, 0.15);
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
    backdrop-filter: blur(15px);
}

/* User message */
.user-message {
    background: linear-gradient(135deg, #2563eb, #4f46e5);
    border-radius: 18px 18px 4px 18px;
    padding: 13px 16px;
    margin: 10px 0;
    margin-left: 15%;
}

/* AI message */
.ai-message {
    background: rgba(31, 45, 65, 0.9);
    border: 1px solid rgba(120,150,190,0.12);
    border-radius: 18px 18px 18px 4px;
    padding: 13px 16px;
    margin: 10px 0;
    margin-right: 15%;
}

/* Cards */
.info-card {
    background: rgba(16, 28, 48, 0.75);
    border: 1px solid rgba(130,160,200,0.15);
    border-radius: 18px;
    padding: 18px;
    height: 100%;
}

.info-card h4 {
    margin-top: 0;
    color: #6ee7ff;
}

.info-card p {
    color: #b5c2d4;
}

/* Buttons */
.stButton > button {
    border-radius: 12px;
    border: 1px solid rgba(120,180,255,0.25);
    background: rgba(20,40,65,0.85);
    color: white;
    font-weight: 600;
    min-height: 45px;
}

.stButton > button:hover {
    border-color: #00d9ff;
    color: #00d9ff;
}

/* Text input */
.stTextInput input,
.stTextArea textarea {
    background: rgba(8,17,30,0.9) !important;
    color: white !important;
    border: 1px solid rgba(120,160,200,0.25) !important;
    border-radius: 14px !important;
}

/* Audio */
audio {
    width: 100%;
    margin-top: 8px;
}

/* Footer */
.baithak-footer {
    text-align: center;
    color: #718096;
    font-size: 0.8rem;
    margin-top: 35px;
    padding-bottom: 20px;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_audio" not in st.session_state:
    st.session_state.last_audio = None


# ============================================================
# OPENAI CLIENT
# ============================================================

def get_api_key():
    """
    Reads OPENAI_API_KEY from Streamlit Secrets first,
    then environment variables.
    """

    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

    return os.getenv("OPENAI_API_KEY")


def get_openai_client():
    if OpenAI is None:
        return None

    api_key = get_api_key()

    if not api_key:
        return None

    return OpenAI(api_key=api_key)


client = get_openai_client()


# ============================================================
# ROBOT
# ============================================================

def render_robot():
    st.markdown(
        """
        <div class="robot-stage">

            <div class="robot">

                <div class="robot-glow"></div>

                <div class="antenna">
                    <div class="antenna-dot"></div>
                </div>

                <div class="robot-head">

                    <div class="robot-face">

                        <div class="eye eye-left"></div>
                        <div class="eye eye-right"></div>

                        <div class="robot-mouth"></div>

                    </div>

                </div>

                <div class="arm arm-left"></div>
                <div class="arm arm-right"></div>

                <div class="robot-body">

                    <div class="chest">
                        <div class="chest-light"></div>
                    </div>

                </div>

            </div>

        </div>

        <div class="robot-status">
            ● BAITHAK AI ONLINE
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# AI RESPONSE
# ============================================================

def ask_ai(user_message):

    if client is None:
        return (
            "OpenAI API is not configured. "
            "Please add OPENAI_API_KEY to Streamlit Secrets."
        )

    conversation = [
        {
            "role": "system",
            "content": """
You are Baithak AI, a friendly Pakistani AI conversational assistant.

Your personality:
- Friendly
- Helpful
- Respectful
- Natural
- Conversational
- Concise when possible

You can communicate in:
- English
- Urdu
- Roman Urdu

If the user asks in Urdu or Roman Urdu, reply naturally in the same language.

The user may speak to you through a microphone, so make your responses natural for text-to-speech.

Do not claim to be human.
Do not invent information.
""",
        }
    ]

    for message in st.session_state.messages:
        conversation.append(
            {
                "role": message["role"],
                "content": message["content"],
            }
        )

    conversation.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    try:

        response = client.chat.completions.create(
            model="gpt-5.6",
            messages=conversation,
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"AI Error: {str(e)}"


# ============================================================
# TEXT TO SPEECH
# ============================================================

def generate_speech(text):

    if client is None:
        return None

    try:

        speech_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        )

        speech_path = speech_file.name
        speech_file.close()

        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text,
        ) as response:

            response.stream_to_file(speech_path)

        with open(speech_path, "rb") as audio:

            audio_bytes = audio.read()

        try:
            os.remove(speech_path)
        except Exception:
            pass

        return audio_bytes

    except Exception:
        return None


# ============================================================
# SPEECH TO TEXT
# ============================================================

def transcribe_audio(audio_file):

    if client is None:
        return None

    try:

        suffix = Path(audio_file.name).suffix or ".wav"

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:

            tmp.write(audio_file.getbuffer())
            temp_path = tmp.name

        with open(temp_path, "rb") as audio:

            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio,
            )

        try:
            os.remove(temp_path)
        except Exception:
            pass

        return transcript.text

    except Exception as e:

        st.error(f"Microphone transcription error: {e}")

        return None


# ============================================================
# PROCESS USER MESSAGE
# ============================================================

def process_message(user_text):

    if not user_text:
        return

    user_text = user_text.strip()

    if not user_text:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_text,
        }
    )

    with st.spinner("🤖 Baithak AI is thinking..."):

        answer = ask_ai(user_text)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    with st.spinner("🔊 Preparing voice response..."):

        audio = generate_speech(answer)

    st.session_state.last_audio = audio


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="baithak-title">
        <span>BAITHAK WITH AI</span>
    </div>

    <div class="baithak-subtitle">
        Your AI Conversation Partner • Talk • Listen • Chat
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# API STATUS
# ============================================================

if client is None:

    st.warning(
        "⚠️ OpenAI API is not configured. "
        "Add OPENAI_API_KEY in Streamlit Secrets."
    )

else:

    st.success("🟢 OpenAI connection ready")


# ============================================================
# MAIN LAYOUT
# ============================================================

left, right = st.columns([1, 1.15], gap="large")


# ============================================================
# LEFT — ROBOT
# ============================================================

with left:

    render_robot()

    st.markdown(
        """
        <div class="info-card">

            <h4>🤖 Meet Baithak AI</h4>

            <p>
            Baithak is an AI-powered talking assistant.
            Speak through your microphone or type a message,
            and Baithak will understand you and respond.
            </p>

            <p>
            🎙️ Voice Input<br>
            🧠 OpenAI Intelligence<br>
            🔊 AI Voice Response<br>
            🤖 Animated Robot<br>
            🌐 English • Urdu • Roman Urdu
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# RIGHT — CHAT
# ============================================================

with right:

    st.markdown(
        '<div class="chat-box">',
        unsafe_allow_html=True
    )

    st.markdown("### 💬 Baithak Conversation")

    # Display messages
    for message in st.session_state.messages:

        content = html.escape(message["content"])

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="user-message">
                    <strong>👤 You</strong><br>
                    {content}
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                f"""
                <div class="ai-message">
                    <strong>🤖 Baithak AI</strong><br>
                    {content}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # ========================================================
    # MICROPHONE
    # ========================================================

    st.markdown("### 🎙️ Talk to Baithak")

    audio_input = st.audio_input(
        "Press the microphone button and speak"
    )

    if audio_input is not None:

        if st.button(
            "🎙️ Send Voice Message",
            use_container_width=True
        ):

            with st.spinner("🎧 Listening and understanding..."):

                spoken_text = transcribe_audio(audio_input)

            if spoken_text:

                st.info(f"🎙️ You said: {spoken_text}")

                process_message(spoken_text)

                st.rerun()

    # ========================================================
    # TEXT INPUT
    # ========================================================

    st.markdown("### ⌨️ Or Type Your Message")

    with st.form("chat_form", clear_on_submit=True):

        user_text = st.text_input(
            "Message Baithak AI",
            placeholder="Type here... e.g. Hello Baithak, how are you?"
        )

        send = st.form_submit_button(
            "🚀 Send Message",
            use_container_width=True
        )

        if send and user_text:

            process_message(user_text)

            st.rerun()

    # ========================================================
    # AUDIO RESPONSE
    # ========================================================

    if st.session_state.last_audio:

        st.markdown("### 🔊 Baithak Voice")

        st.audio(
            st.session_state.last_audio,
            format="audio/mp3"
        )

    # ========================================================
    # CONTROLS
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🧹 Clear Chat",
            use_container_width=True
        ):

            st.session_state.messages = []
            st.session_state.last_audio = None
            st.rerun()

    with col2:

        if st.button(
            "🔊 Repeat Last Voice",
            use_container_width=True
        ):

            if st.session_state.messages:

                last_ai = None

                for msg in reversed(
                    st.session_state.messages
                ):

                    if msg["role"] == "assistant":

                        last_ai = msg["content"]
                        break

                if last_ai:

                    with st.spinner("Generating voice..."):

                        st.session_state.last_audio = (
                            generate_speech(last_ai)
                        )

                    st.rerun()


# ============================================================
# FEATURES
# ============================================================

st.write("")

st.markdown("## ✨ Baithak Features")

c1, c2, c3 = st.columns(3)

with c1:

    st.markdown(
        """
        <div class="info-card">

        <h4>🎙️ Voice Conversation</h4>

        <p>
        Speak naturally using your device microphone.
        Baithak converts your speech into text and
        sends it to the AI.
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:

    st.markdown(
        """
        <div class="info-card">

        <h4>🧠 OpenAI Brain</h4>

        <p>
        Baithak uses OpenAI models for natural,
        intelligent conversations and multilingual
        responses.
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:

    st.markdown(
        """
        <div class="info-card">

        <h4>🔊 Talking Robot</h4>

        <p>
        AI answers can be converted into speech,
        while the animated robot provides a visual
        AI companion.
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="baithak-footer">

        BAITHAK WITH AI © 2026<br>
        Powered by Streamlit + OpenAI

    </div>
    """,
    unsafe_allow_html=True,
)
```
