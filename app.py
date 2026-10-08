
import os
import base64
import requests
import streamlit as st
import streamlit.components.v1 as components

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
GOOGLE_TTS_URL = (
    "https://texttospeech.googleapis.com/v1/text:synthesize"
)

SYSTEM_PROMPT = """
You are BAITHAK WITH AI, a helpful and friendly AI assistant.
Answer clearly, politely, and practically.
Respond in the language used by the user where possible.
"""

# ============================================================
# SECRETS
# ============================================================

def get_setting(name, default=""):
    try:
        value = st.secrets.get(name, default)
        if value:
            return str(value).strip()
    except Exception:
        pass

    return os.getenv(name, default).strip()


OPENAI_API_KEY = get_setting("OPENAI_API_KEY")
OPENAI_MODEL = get_setting("OPENAI_MODEL", DEFAULT_MODEL)
GOOGLE_TTS_API_KEY = get_setting("GOOGLE_TTS_API_KEY")

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

if "speech_audio" not in st.session_state:
    st.session_state.speech_audio = None

if "current_mode" not in st.session_state:
    st.session_state.current_mode = "Demo Mode"

if "api_notice" not in st.session_state:
    st.session_state.api_notice = None

# ============================================================
# DEMO MODE
# ============================================================

def demo_response(prompt):
    """Return a useful response without calling an external API."""
    prompt_lower = prompt.lower()

    if any(word in prompt_lower for word in
           ["hello", "hi", "salam", "assalam"]):
        return (
            "Assalam-o-Alaikum! Welcome to BAITHAK WITH AI. "
            "How can I help you today?"
        )

    if any(word in prompt_lower for word in
           ["python", "coding", "programming", "code"]):
        return (
            "Python is a beginner-friendly programming language. "
            "You can use it for automation, AI, data analysis, "
            "robotics, and web applications. Tell me the specific "
            "task and I can guide you with an example."
        )

    if any(word in prompt_lower for word in
           ["ai", "artificial intelligence", "agentic"]):
        return (
            "Artificial Intelligence enables computer systems to "
            "perform tasks such as understanding language, reasoning, "
            "and recognizing patterns. Agentic AI systems can also "
            "plan tasks and use tools to work toward a goal."
        )

    if any(word in prompt_lower for word in
           ["robot", "robotics", "arduino", "raspberry pi"]):
        return (
            "For a robotics project, start by defining the task, "
            "choosing a controller such as Arduino or Raspberry Pi, "
            "selecting suitable sensors and actuators, and testing "
            "the system safely. Share your project requirements "
            "for a more specific plan."
        )

    if any(word in prompt_lower for word in
           ["study", "learn", "education", "course"]):
        return (
            "A practical learning plan includes a clear objective, "
            "short study sessions, hands-on exercises, revision, "
            "and a small project. Tell me your subject and skill "
            "level to build a suitable plan."
        )

    if any(word in prompt_lower for word in
           ["business", "career", "job", "professional"]):
        return (
            "Start by defining your professional goal, identifying "
            "the skills required, building practical projects, and "
            "documenting your achievements. I can help you create "
            "a more detailed plan when you share your objective."
        )

    return (
        "I am currently running in Demo Mode, so I cannot provide "
        "a full live AI-generated answer. Your application is still "
        "working. Add valid API credentials and check API billing "
        "to enable OpenAI responses. You can also ask about AI, "
        "Python, robotics, learning, and productivity."
    )

# ============================================================
# OPENAI API
# ============================================================

def get_openai_answer(prompt):
    """
    Returns (answer, error_type).
    A missing key or exhausted API credits never crashes the app.
    """
    if not OPENAI_API_KEY:
        return None, "missing_key"

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=45.0,
            max_retries=0,
        )

        conversation = []
        for message in st.session_state.messages[-12:]:
            if message["role"] in ("user", "assistant"):
                conversation.append({
                    "role": message["role"],
                    "content": message["content"],
                })

        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=conversation,
        )

        answer = getattr(response, "output_text", "")
        if not answer:
            return None, "empty_response"

        return answer, None

    except Exception as error:
        error_text = str(error).lower()
        error_code = str(
            getattr(error, "code", "") or ""
        ).lower()
        status_code = getattr(error, "status_code", None)

        # Insufficient quota / exhausted credits
        if (
            "insufficient_quota" in error_text
            or "credit_balance_exhausted" in error_text
            or "no credits remaining" in error_text
            or error_code in (
                "insufficient_quota",
                "credit_balance_exhausted",
            )
        ):
            return None, "quota"

        # Rate limit: distinguish ordinary rate limits from quota.
        if status_code == 429 or "429" in error_text:
            if (
                "rate_limit_exceeded" in error_text
                or "rate limit" in error_text
            ):
                return None, "rate_limit"
            return None, "quota"

        if (
            "authentication" in error_text
            or "invalid_api_key" in error_text
            or "401" in error_text
        ):
            return None, "invalid_key"

        if (
            "model_not_found" in error_text
            or "does not exist" in error_text
            or "do not have access" in error_text
        ):
            return None, "model"

        return None, "api_error"

# ============================================================
# FRIENDLY API NOTIFICATIONS
# ============================================================

def show_api_notice(error_type):
    if error_type == "missing_key":
        message = (
            "⚠️ Kindly Use Your API Credentials in Streamlit Secrets!"
        )
        st.toast(message, icon="⚠️")
        st.warning(message)

    elif error_type == "quota":
        message = (
            "⚠️ Kindly Use Your API Credentials in Streamlit Secrets!"
        )
        st.toast(message, icon="⚠️")
        st.warning(
            message
            + "\n\nOpenAI API credits are exhausted or unavailable. "
              "Please check your API billing and credits. "
              "Switching to Demo Mode."
        )

    elif error_type == "rate_limit":
        st.toast(
            "OpenAI is receiving too many requests. Please try again.",
            icon="⏳",
        )
        st.info(
            "The API rate limit was reached. Please wait and try "
            "again. A Demo Mode response is shown for now."
        )

    elif error_type == "invalid_key":
        message = (
            "⚠️ Kindly Use Your API Credentials in Streamlit Secrets!"
        )
        st.toast(message, icon="⚠️")
        st.warning(
            message
            + "\n\nPlease verify that OPENAI_API_KEY is correct."
        )

    elif error_type == "model":
        st.toast(
            "Please check your OPENAI_MODEL setting.",
            icon="⚠️",
        )
        st.warning(
            "The configured model may be unavailable to your account. "
            "Check OPENAI_MODEL in Streamlit Secrets."
        )

    else:
        st.toast(
            "API unavailable. Switching to Demo Mode.",
            icon="⚠️",
        )
        st.info(
            "The API request could not be completed. "
            "Please check your credentials, model, and connection."
        )

# ============================================================
# GOOGLE TEXT-TO-SPEECH
# ============================================================

def google_text_to_speech(text, language="en-US"):
    if not GOOGLE_TTS_API_KEY:
        return None, (
            "Google TTS key is missing. Add GOOGLE_TTS_API_KEY "
            "to Streamlit Secrets."
        )

    voice_names = {
        "en-US": "en-US-Neural2-D",
        "ur-IN": "ur-IN-Standard-A",
    }

    payload = {
        "input": {"text": text[:4500]},
        "voice": {
            "languageCode": language,
            "name": voice_names.get(language, "en-US-Neural2-D"),
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": 0.95,
            "pitch": 0.0,
        },
    }

    try:
        response = requests.post(
            GOOGLE_TTS_URL,
            params={"key": GOOGLE_TTS_API_KEY},
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            return None, (
                "Google TTS could not generate speech. "
                "Check the API key, billing, enabled API, and voice."
            )

        audio_content = response.json().get("audioContent")
        if not audio_content:
            return None, "Google TTS returned no audio."

        return base64.b64decode(audio_content), None

    except requests.RequestException:
        return None, "Could not connect to Google Text-to-Speech."

# ============================================================
# PAGE STYLING
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: clamp(2rem, 5vw, 3.2rem);
        font-weight: 800;
        letter-spacing: 1px;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        font-size: 1.05rem;
        opacity: 0.8;
        margin-top: 5px;
        margin-bottom: 20px;
    }
    .robot-box {
        border-radius: 22px;
        padding: 16px;
        text-align: center;
        background: linear-gradient(135deg, #10213b, #173e61);
        color: white;
        margin-bottom: 15px;
    }
    .robot {
        font-size: 95px;
        display: inline-block;
        animation: floatRobot 2.4s ease-in-out infinite;
    }
    @keyframes floatRobot {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-12px); }
    }
    .footer {
        text-align: center;
        opacity: 0.8;
        padding: 20px 5px 8px 5px;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">🤖 BAITHAK WITH AI</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Your Intelligent AI Conversation Partner</div>',
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("⚙️ Settings")

    selected_mode = st.radio(
        "Select AI Mode",
        ["Demo Mode", "OpenAI API Mode"],
        index=(
            1 if st.session_state.current_mode == "OpenAI API Mode"
            else 0
        ),
    )

    st.session_state.current_mode = selected_mode

    st.caption(
        "Demo Mode works without API credits. OpenAI API Mode "
        "requires a valid key, model access, and available credits."
    )

    st.divider()
    st.subheader("🔊 Speech Settings")

    speech_language = st.selectbox(
        "Google TTS voice",
        ["English (US)", "Urdu (India)"],
    )

    language_code = (
        "ur-IN" if speech_language == "Urdu (India)" else "en-US"
    )

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_answer = ""
        st.session_state.speech_audio = None
        st.session_state.api_notice = None
        st.rerun()

    st.divider()
    st.caption("API credentials are read from Streamlit Secrets.")

# ============================================================
# ROBOT DISPLAY
# ============================================================

st.markdown(
    """
    <div class="robot-box">
        <div class="robot">🤖</div>
        <h3>Welcome to BAITHAK WITH AI</h3>
        <p>Ask a question, explore an idea, or start a conversation.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================================
# CHAT INPUT AND AUTOMATIC DEMO FALLBACK
# ============================================================

user_prompt = st.chat_input("Type your message here...")

if user_prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": user_prompt,
    })

    with st.chat_message("user"):
        st.markdown(user_prompt)

    answer = None

    if st.session_state.current_mode == "OpenAI API Mode":
        with st.spinner("BAITHAK WITH AI is thinking..."):
            answer, error_type = get_openai_answer(user_prompt)

        if error_type:
            show_api_notice(error_type)
            st.session_state.current_mode = "Demo Mode"
            answer = demo_response(user_prompt)

    else:
        answer = demo_response(user_prompt)

    st.session_state.last_answer = answer
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.rerun()

# ============================================================
# SPEECH OUTPUT
# ============================================================

last_answer = st.session_state.last_answer

if last_answer:
    st.divider()
    st.subheader("🔊 Listen to the Response")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎙️ Generate Google Speech", use_container_width=True):
            with st.spinner("Generating speech..."):
                audio_bytes, speech_error = google_text_to_speech(
                    last_answer,
                    language=language_code,
                )

            if audio_bytes:
                st.session_state.speech_audio = audio_bytes
                st.success("Google speech generated successfully.")
            else:
                st.session_state.speech_audio = None
                st.warning(
                    speech_error
                    + " You can use the browser speech button instead."
                )

    with col2:
        if st.button("🗣️ Browser Speech", use_container_width=True):
            safe_text = (
                last_answer.replace("\\", "\\\\")
                .replace("'", "\\'")
                .replace("\n", " ")
            )
            browser_language = (
                "ur-PK" if language_code == "ur-IN" else "en-US"
            )
            components.html(
                f"""
                <button id="speakButton"
                    style="padding:10px 16px; font-size:16px;
                    border-radius:10px; cursor:pointer;">
                    ▶ Speak Response
                </button>
                <button id="stopButton"
                    style="padding:10px 16px; font-size:16px;
                    border-radius:10px; cursor:pointer;">
                    ■ Stop
                </button>
                <script>
                const textToSpeak = '{safe_text}';
                const language = '{browser_language}';
                document.getElementById('speakButton').onclick = () => {{
                    window.speechSynthesis.cancel();
                    const utterance = new SpeechSynthesisUtterance(textToSpeak);
                    utterance.lang = language;
                    utterance.rate = 0.95;
                    window.speechSynthesis.speak(utterance);
                }};
                document.getElementById('stopButton').onclick = () => {{
                    window.speechSynthesis.cancel();
                }};
                </script>
                """,
                height=65,
            )

    if st.session_state.speech_audio:
        st.audio(
            st.session_state.speech_audio,
            format="audio/mp3",
        )
        st.download_button(
            "⬇️ Download Speech (MP3)",
            data=st.session_state.speech_audio,
            file_name="baithak_with_ai.mp3",
            mime="audio/mpeg",
        )

# ============================================================
# SECRETS HELP
# ============================================================

with st.expander("🔐 API Credentials Setup"):
    st.markdown(
        """
        Add your credentials in **Streamlit → App → Settings → Secrets**.
        Never publish real API keys in your Python code or public repository.
        """
    )

    st.code(
        'OPENAI_API_KEY = "your-openai-api-key"\n'
        'OPENAI_MODEL = "gpt-4o-mini"\n'
        'GOOGLE_TTS_API_KEY = "your-google-cloud-api-key"',
        language="toml",
    )

    st.markdown(
        "[OpenAI Billing](https://platform.openai.com/settings/organization/billing/)"
    )
    st.markdown(
        "[Google Cloud Text-to-Speech](https://console.cloud.google.com/apis/library/texttospeech.googleapis.com)"
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        <strong>Designed by Certified Generative and Agentic AI
        Application Developer</strong><br>
        Engr. Bilal Mehmood
    </div>
    """,
    unsafe_allow_html=True,
)
