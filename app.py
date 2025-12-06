import streamlit as st
from deepface import DeepFace
from PIL import Image
import numpy as np
import time

# -------------------------------------------------------------
# Streamlit Page Config (optional)
# -------------------------------------------------------------
st.markdown(
    f"""
    <p>  </p>
    <p><div class="main-title">  </div></p>
    <div class="main-title">  </div>
    """,
    unsafe_allow_html=True,
)
st.set_page_config(
    page_title=" MoodWave AI",
    page_icon="🎭",
    layout="wide"
)

# -------------------------------------------------------------
# Top small credit text
# -------------------------------------------------------------


# -------------------------------------------------------------
# Dependency Check (Handle DeepFace/TensorFlow loading errors gracefully)
# -------------------------------------------------------------
DEEPFACE_AVAILABLE = True
try:
    import deepface  # quick import test
except ImportError:
    DEEPFACE_AVAILABLE = False
except Exception:
    DEEPFACE_AVAILABLE = False

# -------------------------------------------------------------
# Custom CSS – Animated Gradient BG, Glassmorphism Cards, Hover Effects
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* 1. Page and Layout Setup */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(120deg, #1e293b, #0f172a, #020617);
        background-size: 300% 300%;
        animation: gradientMove 12s ease infinite;
    }

    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stApp {
        color: white;
    }

    /* Title Glow */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #e5e7eb;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.5), 0 0 5px rgba(56, 189, 248, 0.3);
    }
    
    .subtitle {
        font-size: 0.95rem;
        color: #e5e7eb;
        opacity: 0.85;
    }
    
    /* Glass Card Container */
    .glass-card {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(148, 163, 184, 0.4);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(18px);
    }

    /* Emotion Badge (Chip) */
    .emotion-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.85rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #f97316, #fb7185);
        color: white;
        font-size: 0.9rem;
        font-weight: 600;
        animation: popIn 0.5s ease-out;
        margin-bottom: 1rem;
    }

    @keyframes popIn {
        0% { transform: scale(0.6); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    /* Song Card List Item */
    .song-card {
        margin-bottom: 0.6rem;
        border-radius: 14px;
        padding: 0.8rem 1rem;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(148, 163, 184, 0.45);
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border 0.18s ease, background 0.18s ease;
    }

    .song-card:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 14px 32px rgba(15, 23, 42, 0.9);
        border-color: #38bdf8;
        background: rgba(15, 23, 42, 0.95);
    }

    .song-title {
        font-size: 0.95rem;
        color: #e5e7eb;
        font-weight: 500;
    }

    .song-link a {
        font-size: 0.85rem;
        text-decoration: none;
        font-weight: 600;
        color: #38bdf8;
    }

    .song-link a:hover {
        text-decoration: underline;
    }
    
    /* Fancy button tweak */
    .stButton>button {
        background: linear-gradient(135deg, #f97316, #ec4899);
        color: white;
        border-radius: 999px;
        border: none;
        padding: 0.45rem 1.3rem;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 10px 25px rgba(236, 72, 153, 0.55);
        transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
    }

    .stButton>button:hover {
        transform: translateY(-1px) scale(1.02);
        box-shadow: 0 14px 30px rgba(236, 72, 153, 0.75);
        filter: brightness(1.05);
    }
    
    /* Widget Labels */
    [data-testid="stWidgetLabel"] > label {
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
    }

    /* Hint/Footer Label */
    .hint-label {
        font-size: 1rem;
        color: white;
        font-weight: 500;
        opacity: 1;
    }

    /* Quick mood shortcut badge style */
    .mood-chip {
        display: inline-block;
        padding: 0.4rem 0.9rem;
        border-radius: 999px;
        border: 1px solid rgba(148, 163, 184, 0.6);
        background: rgba(15, 23, 42, 0.7);
        font-size: 0.85rem;
        margin: 0.15rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

    /* ---------------------- GOLD STYLES FOR INPUT METHOD & CAMERA ---------------------- */

    /* Gold label for “Choose input method:” */
    .gold-label {
        color: #facc15;
        font-weight: 800;
        font-size: 1.1rem;
        text-shadow: 0 0 10px rgba(250,204,21,0.6);
        margin-bottom: 0.3rem;
    }

    /* Gold animated label for “📸 Take a picture” */
    .camera-gold {
        color: #facc15;
        font-weight: 900;
        font-size: 1.15rem;
        text-shadow: 0 0 12px rgba(250,204,21,0.8);
        animation: pulseGold 1.5s ease-in-out infinite alternate;
    }

    @keyframes pulseGold {
        from { text-shadow: 0 0 6px rgba(250,204,21,0.5); }
        to   { text-shadow: 0 0 16px rgba(250,204,21,1); }
    }

    /* Radio options gold color */
    [data-testid="stRadio"] label {
        color: #facc15 !important;
        font-weight: 700 !important;
    }

    /* Selected mood option glow */
    [data-testid="stRadio"] div[role="radiogroup"] > div:has(input:checked) {
        background: rgba(250,204,21,0.18);
        border-radius: 12px;
        padding: 3px 10px;
        box-shadow: 0 0 15px rgba(250,204,21,0.7);
        animation: goldSelect 0.2s ease-out;
    }

    @keyframes goldSelect {
        from { box-shadow: 0 0 0 rgba(250,204,21,0.0); }
        to   { box-shadow: 0 0 15px rgba(250,204,21,0.9); }
    }

    /* Camera widget Take Photo button */
    [data-testid="stCameraInput"] button {
        color: #facc15 !important;
        border: 1px solid #facc15 !important;
        background: transparent !important;
        font-weight: 800 !important;
        transition: 0.2s;
    }

    [data-testid="stCameraInput"] button:hover {
        background: rgba(250,204,21,0.18) !important;
        transform: scale(1.03);
        box-shadow: 0 0 20px rgba(250,204,21,0.75);
    }

    [data-testid="stCameraInput"] button:active {
        transform: scale(0.96);
        box-shadow: 0 0 28px rgba(250,204,21,1);
    }


# -------------------------------------------------------------
# Data: Emotion → Songs
# -------------------------------------------------------------
emotion_to_songs = {
    'happy': [
        ("Aankh Marey – Simmba", "https://open.spotify.com/track/63MvWd6T6yoS7h4AJ4Hjrm"),
        ("Nashe Si Chadh गई – Befikre", "https://open.spotify.com/track/3uoQUnKEedaeLKxUeVaJwj"),
        ("Happy – Pharrell Williams", "https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH"),
        ("Can’t Stop the Feeling – Justin Timberlake", "https://open.spotify.com/track/6JV2JOEocMgcZxYSZelKcc"),
        ("Hokaliyo", "https://open.spotify.com/artist/535ascn4f13hFo2kjCodKE"),
        ("Vaagyo Re Dhol – Hellaro", "https://open.spotify.com/track/3GSyZg9iVdj1WjKzBcLakX"),
        ("Bhuli Javu Che – Sachin–Jigar", "https://open.spotify.com/track/7s1pfz5zIMBJdYVc3bWEku"),
    ],

    'sad': [
        ("Arambha Hai Prachand", "https://open.spotify.com/track/1PZZtXR7nsNIyRcqd7UeiF"),
        ("Channa Mereya – Arijit Singh", "https://open.spotify.com/track/0H2iJVgorRR0ZFgRqGUjUM"),
        ("Tujhe Kitna Chahne Lage – Kabir Singh", "https://open.spotify.com/track/3dYD57lRAUcMHufyqn9GcI"),
        ("Let Her Go – Passenger", "https://open.spotify.com/track/0JmiBCpWc1IAc0et7Xm7FL"),
        ("Someone Like You – Adele", "https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB"),
        ("Mane Yaad Ave – Parthiv Gohil", "https://open.spotify.com/track/1JVAoIO4NtjlejraxemhLh"),
        ("Chand Ne Kaho – Jigardan Gadhavi", "https://open.spotify.com/track/6ci9DNOBLvA7jVDkMYf5Df"),
    ],

    'angry': [
        ("Zinda – Bhaag Milkha Bhaag", "https://open.spotify.com/track/6Zo8diPZAjkUH4rWDMgeiE"),
        ("Sultan Title Track", "https://open.spotify.com/track/3LJhJG3EsmhCq9bNn047lu"),
        ("Believer – Imagine Dragons", "https://open.spotify.com/track/0pqnGHJpmpxLKifKRmU6WP"),
        ("Lose Yourself – Eminem", "https://open.spotify.com/track/7MJQ9Nfxzh8LPZ9e9u68Fq"),
        ("Rag Rag Mein – Kirtidan Gadhvi", "https://open.spotify.com/artist/7odYFkW15De3A7aAuk5x9h"),
        ("Jode Tame Rahejo – Gujarati Garba", "https://open.spotify.com/track/3ByO0k09IsJPqAGncEVuYQ"),
    ],

    'surprise': [
        ("Senorita – ZNMD", "https://open.spotify.com/track/6b8zsc3BxT59Yg62wjt7qA"),
        ("Odhani – Made In China", "https://open.spotify.com/track/2q0V50aNlI1RQXJyE5HDgD"),
        ("Uptown Funk – Bruno Mars", "https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS"),
        ("Sugar – Maroon 5", "https://open.spotify.com/track/55h7vJchibLdUkxdlX3fK7"),
        ("Hokaliyo", "https://open.spotify.com/artist/535ascn4f13hFo2kjCodKE"),
        ("Halaji Tara Fulwadi", "https://open.spotify.com/track/58kDGOUvK1foT7UGnZYaFQ"),
        ("Kaka Bapa Na Gaam Nu", "https://open.spotify.com/track/4YigRMdxg9DJNL0rh6V1KK"),
    ],

    'neutral': [
        ("Ilahi – Yeh Jawaani Hai Deewani", "https://open.spotify.com/track/0VxgNsSywsjapKGXvzj8RH"),
        ("Tera Yaar Hoon Main", "https://open.spotify.com/track/3ZCTVFBt2Brf31RLEnCkWJ"),
        ("Counting Stars – OneRepublic", "https://open.spotify.com/track/2tpWsVSb9UEmDRxAl1zhX1"),
        ("Perfect – Ed Sheeran", "https://open.spotify.com/track/0tgVpDi06FyKpA1z0VMD4v"),
        ("Kaka Bapa Na Gaam Nu", "https://open.spotify.com/track/3GmKe3YkJ4YuMZ1GNy9jjW"),
        ("Gujarati Folk Mashup – RJ Dhvanit", "https://open.spotify.com/artist/7AeKpTtsd8BgYZAAGZ4s48"),
        ("Arambha Hai Prachand", "https://open.spotify.com/track/1PZZtXR7nsNIyRcqd7UeiF"),
    ],

    'fear': [
        ("Arambha Hai Prachand", "https://open.spotify.com/track/1PZZtXR7nsNIyRcqd7UeiF"),
        ("Namo Namo – Kedarnath", "https://open.spotify.com/track/5Fx864foKMyZtJbBiwvyBz"),
        ("Kun Faya Kun – Rockstar", "https://open.spotify.com/track/7F8RNvTQlvbeBLeenycvN6"),
        ("Demons – Imagine Dragons", "https://open.spotify.com/track/3LlAyCYU26dvFZBDUIMb7a"),
        ("Scared to Be Lonely – Dua Lipa", "https://open.spotify.com/track/3ebXMykcMXOcLeJ9xZ17XH"),
        ("Bhuli Javu Che – Sachin–Jigar", "https://open.spotify.com/track/7s1pfz5zIMBJdYVc3bWEku"),
        ("Kadi Aevi Yaad – Rakesh Barot", "https://open.spotify.com/track/748eQN6KCbOO1ylkwHdaXD"),
    ],

    'disgust': [
        ("Apna Time Aayega – Gully Boy", "https://open.spotify.com/track/5FLgOuLoVwwUUF7IL36Lux"),
        ("Sher Aaya Sher – Gully Boy", "https://open.spotify.com/track/7zT92EewVvLfiPyKSTJUT6"),
        ("Power – Kanye West", "https://open.spotify.com/track/2gZUPNdnz5Y45eiGxpH"),
        ("Stronger – Kanye West", "https://open.spotify.com/track/0j2T0R9dR9qdJYsB7ciXhf"),
        ("Helo Mara Dholida", "https://open.spotify.com/track/35tJHVflwKQ8pMYV1QaiJ2"),
        ("Baap Dhamaal – Jignesh Kaviraj", "https://open.spotify.com/album/2MhZPFL3YT4szEQQCZ8BoN"),
    ],
}

emotion_emoji = {
    "happy": "😄",
    "sad": "😢",
    "angry": "😡",
    "surprise": "😲",
    "neutral": "😐",
    "fear": "😨",
    "disgust": "🤢",
}

# ----------------------- Emotion Detection Function -----------------------
def detect_emotion(image):
    """
    Returns (dominant_emotion, confidence_percent) or (None, None) on failure.
    """
    if not DEEPFACE_AVAILABLE:
        st.error("DeepFace (or its dependencies) could not be loaded. Please check your environment.")
        return None, None

    try:
        result = DeepFace.analyze(
            img_path=image,
            actions=['emotion'],
            enforce_detection=False
        )
        # DeepFace returns a list in newer versions
        r0 = result[0] if isinstance(result, list) else result
        dominant = r0.get('dominant_emotion', None)
        confidence = None
        if dominant and 'emotion' in r0 and isinstance(r0['emotion'], dict):
            # score for that emotion
            score = r0['emotion'].get(dominant)
            if score is not None:
                confidence = float(score)
        return dominant, confidence
    except Exception as e:
        st.error(f"Error detecting emotion: {e}")
        return None, None

# ----------------------- SIDEBAR (NEW FEATURE) -----------------------
with st.sidebar:
    st.markdown("## 🎭 MoodWave AI")
    st.markdown(
        "Capture your mood using your **camera or a photo**, and instantly get songs that vibe with your emotion."
    )
    if not DEEPFACE_AVAILABLE:
        st.warning(
            "⚠ DeepFace not available.\n\nAutomatic emotion detection is disabled. "
            "Please use **Manual Mood Selection** or Quick Mood Shortcuts."
        )

    st.markdown("---")
    st.markdown("### ℹ How it works")
    st.markdown(
        "- Take or upload a selfie.\n"
        "- AI detects your dominant emotion.\n"
        "- We show you curated songs from **Hindi, English & Gujarati**.\n"
        "- Or select your mood manually anytime."
    )

    st.markdown("---")
    st.markdown("👨‍💻 **Creators**\n\n- You\n- Dhruv")

# ----------------------- MAIN TITLE -----------------------
st.markdown(
    """
    <div style="text-align:center; margin-bottom: 1.2rem;">
        <div class="main-title" style="font-weight: 900;">
            🎭 MoodWave AI
        </div>
        <div class="subtitle" style="font-weight: 700; margin-top: 0.25rem;">
            <b>Capture your mood &amp; instantly get handpicked songs that vibe with your emotion.</b>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------- INPUT METHOD (NEW FEATURE) -----------------------
col_left, col_right = st.columns([1.2, 1])

with col_left:
    input_options = ["📷 Camera", "📁 Upload Photo"]
    if not DEEPFACE_AVAILABLE:
        # If DeepFace not available, camera/upload will not be used for detection,
        # but we still allow upload just to see photo (optional)
        pass

    input_method = st.radio("Choose input method:", input_options, horizontal=True)

    uploaded_image = None

    if input_method == "📷 Camera":
        uploaded_image = st.camera_input("📸 Take a picture")
    else:
        uploaded_file = st.file_uploader("📁 Upload a photo", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            uploaded_image = uploaded_file

    detected_emotion = None
    detected_confidence = None

    # ----------------------- AUTO MODE (DeepFace) -----------------------
    if uploaded_image is not None and DEEPFACE_AVAILABLE:
        img = Image.open(uploaded_image)
        st.image(img, caption="Your Photo", use_column_width=True)

        img_np = np.array(img.convert("RGB"))

        with st.spinner("Detecting your emotion... 🔍"):
            time.sleep(1.3)  # smooth animation
            detected_emotion, detected_confidence = detect_emotion(img_np)

    # show auto-detected songs
    if detected_emotion:
        emo_key = detected_emotion.lower()
        emo_icon = emotion_emoji.get(emo_key, "🎭")

        conf_str = ""
        if detected_confidence is not None:
            # DeepFace often gives raw scores; normalizing is tricky.
            # Assume it's already percentage-like if <= 100.
            if detected_confidence > 1:
                conf_str = f"{detected_confidence:.1f}%"
            else:
                conf_str = f"{detected_confidence*100:.1f}%"
        chip_text = f"{emo_key.upper()}"
        if conf_str:
            chip_text += f" · {conf_str}"

        st.markdown(
            f"""
            <div class="emotion-badge">
                <span>{emo_icon}</span>
                <span>{chip_text}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div class='song-list'>", unsafe_allow_html=True)

        songs = emotion_to_songs.get(emo_key, [])
        for name, url in songs:
            st.markdown(
                f"""
                <div class="song-card">
                    <div class="song-title">
                        <span>🎵</span>
                        <span>{name}</span>
                    </div>
                    <div class="song-link">
                        <a href="{url}" target="_blank">Play on Spotify ↗</a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    # ----------------------- QUICK MOOD SHORTCUTS (NEW FEATURE) -----------------------
    st.markdown("### 🎧 Quick Mood Shortcuts (Manual Mood Selection) ")
    st.markdown(
        "<span class='hint-label'>If camera / detection fails, choose a mood and explore songs manually.</span>",
        unsafe_allow_html=True
    )
    quick_cols = st.columns(2)
    moods_row1 = ["happy", "sad", "angry", "neutral"]
    moods_row2 = ["surprise", "fear", "disgust"]

    selected_quick_mood = None

    for i, mood in enumerate(moods_row1):
        with quick_cols[i % 2]:
            if st.button(f"{emotion_emoji[mood]} {mood.capitalize()}", key=f"quick_{mood}"):
                selected_quick_mood = mood

    quick_cols2 = st.columns(2)
    for i, mood in enumerate(moods_row2):
        with quick_cols2[i % 2]:
            if st.button(f"{emotion_emoji[mood]} {mood.capitalize()}", key=f"quick2_{mood}"):
                selected_quick_mood = mood

    if selected_quick_mood:
        emo_icon = emotion_emoji.get(selected_quick_mood, "🎭")
        st.markdown(
            f"""
            <div class="emotion-badge">
                <span>{emo_icon}</span>
                <span>{selected_quick_mood.upper()}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div class='song-list'>", unsafe_allow_html=True)
        songs = emotion_to_songs.get(selected_quick_mood, [])
        for name, url in songs:
            st.markdown(
                f"""
                <div class="song-card">
                    <div class="song-title">
                        <span>🎵</span>
                        <span>{name}</span>
                    </div>
                    <div class="song-link">
                        <a href="{url}" target="_blank">Play on Spotify ↗</a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
        st.markdown("</div>", unsafe_allow_html=True)
