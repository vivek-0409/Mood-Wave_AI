import streamlit as st
from deepface import DeepFace
from PIL import Image
import numpy as np
import time

# -------------------------------------------------------------
# Streamlit Page Config
# -------------------------------------------------------------
st.set_page_config(
    page_title="MoodWave AI",
    page_icon="🎭",
    layout="wide"
)

# -------------------------------------------------------------
# Custom CSS – Animated Gradient BG, Glassmorphism Cards, Hover Effects
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Remove default padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Animated gradient background (Applied to Streamlit's main div) */
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
    
    /* Ensure text is white for dark background */
    .stApp {
        color: white;
    }

    /* Glassmorphism card */
    .glass-card {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(148, 163, 184, 0.4);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(18px);
    }
    
    /* Emotion badge */
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
    }

    @keyframes popIn {
        0% { transform: scale(0.6); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    /* Song card */
    .song-card-list {
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

    .song-card-list:hover {
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
    
    /* Fancy button tweak for the manual selection */
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
    
    /* Apply glow to the main title */
    .main-title {
        color: #e5e7eb;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.5), 0 0 5px rgba(56, 189, 248, 0.3);
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------- Emotion → Song Mapping -----------------------
emotion_to_songs = {
    'happy': [
        ("Aankh Marey – Simmba", "https://open.spotify.com/track/63MvWd6T6yoS7h4AJ4Hjrm"),
        ("Nashe Si Chadh Gayi – Befikre", "https://open.spotify.com/track/3uoQUnKEedaeLKxUeVaJwj"),
        ("Happy – Pharrell Williams", "https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH"),
        ("Can’t Stop the Feeling – Justin Timberlake", "https://open.spotify.com/track/6JV2JOEocMgcZxYSZelKcc"),
        ("Hokaliyo", "https://open.spotify.com/artist/535ascn4f13hFo2kjCodKE"),
        ("Vaagyo Re Dhol – Hellaro", "https://open.spotify.com/track/3GSyZg9iVdj1WjKzBcLakX"),
        ("Bhuli Javu Che – Sachin–Jigar", "https://open.spotify.com/track/7s1pfz5zIMBJdYVc3bWEku")
    ],
    'sad': [
        ("Arambha hai prachand","https://open.spotify.com/track/1PZZtXR7nsNIyRcqd7UeiF"),
        ("Channa Mereya – Arijit Singh", "https://open.spotify.com/track/0H2iJVgorRR0ZFgRqGUjUM"),
        ("Tujhe Kitna Chahne Lage – Kabir Singh", "https://open.spotify.com/track/3dYD57lRAUcMHufyqn9GcI"),
        ("Let Her Go – Passenger", "https://open.spotify.com/track/0JmiBCpWc1IAc0et7Xm7FL"),
        ("Someone Like You – Adele", "https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB"),
        ("Mane Yaad Ave – Parthiv Gohil", "https://open.spotify.com/track/1JVAoIO4NtjlejraxemhLh"),
        ("Chand Ne Kaho – Jigardan Gadhavi", "https://open.spotify.com/track/6ci9DNOBLvA7jVDkMYf5Df")
    ],
    'angry': [
        ("Zinda – Bhaag Milkha Bhaag", "https://open.spotify.com/track/6Zo8diPZAjkUH4rWDMgeiE"),
        ("Sultan Title Track", "https://open.spotify.com/track/3LJhJG3EsmhCq9bNn047lu"),
        ("Believer – Imagine Dragons", "https://open.spotify.com/track/0pqnGHJpmpxLKifKRmU6WP"),
        ("Lose Yourself – Eminem", "https://open.spotify.com/track/7MJQ9Nfxzh8LPZ9e9u68Fq"),
        ("Rag Rag Mein – Kirtidan Gadhvi", "https://open.spotify.com/artist/7odYFkW15De3A7aAuk5x9h"),
        ("Jode Tame Rahejo – Gujarati Garba", "https://open.spotify.com/track/3ByO0k09IsJPqAGncEVuYQ")
    ],
    'surprise': [
        ("Senorita – ZNMD", "https://open.spotify.com/track/6b8zsc3BxT59Yg62wjt7qA"),
        ("Odhani – Made In China", "https://open.spotify.com/track/2q0V50aNlI1RQXJyE5HDgD"),
        ("Uptown Funk – Bruno Mars", "https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS"),
        ("Sugar – Maroon 5", "https://open.spotify.com/track/55h7vJchibLdUkxdlX3fK7"),
        ("Hokaliyo", "https://open.spotify.com/artist/535ascn4f13hFo2kjCodKE"),
        ("Halaji Tara Fulwadi", "https://open.spotify.com/track/58kDGOUvK1foT7UGnZYaFQ"),
        ("Kaka Bapa Na Gaam Nu", "https://open.spotify.com/track/4YigRMdxg9DJNL0rh6V1KK")
    ],
    'neutral': [
        ("Ilahi – Yeh Jawaani Hai Deewani", "https://open.spotify.com/track/0VxgNsSywsjapKGXvzj8RH"),
        ("Tera Yaar Hoon Main", "https://open.spotify.com/track/3ZCTVFBt2Brf31RLEnCkWJ"),
        ("Counting Stars – OneRepublic", "https://open.spotify.com/track/2tpWsVSb9UEmDRxAl1zhX1"),
        ("Perfect – Ed Sheeran", "https://open.spotify.com/track/0tgVpDi06FyKpA1z0VMD4v"),
        ("Kaka Bapa Na Gaam Nu", "https://open.spotify.com/track/3GmKe3YkJ4YuMZ1GNy9jjW"),
        ("Gujarati Folk Mashup – RJ Dhvanit", "https://open.spotify.com/artist/7AeKpTtsd8BgYZAAGZ4s48"),
        ("Arambha hai prachand","https://open.spotify.com/track/1PZZtXR7nsNIyRcqd7UeiF")
    ],
    'fear': [
        ("Arambha hai prachand","https://open.spotify.com/track/1PZZtXR7nsNIyRcqd7UeiF"),
        ("Namo Namo – Kedarnath", "https://open.spotify.com/track/5Fx864foKMyZtJbBiwvyBz"),
        ("Kun Faya Kun – Rockstar", "https://open.spotify.com/track/7F8RNvTQlvbeBLeenycvN6"),
        ("Demons – Imagine Dragons", "https://open.spotify.com/track/3LlAyCYU26dvFZBDUIMb7a"),
        ("Scared to Be Lonely – Dua Lipa", "https://open.spotify.com/track/3ebXMykcMXOcLeJ9xZ17XH"),
        ("Bhuli Javu Che – Sachin–Jigar", "https://open.spotify.com/track/7s1pfz5zIMBJdYVc3bWEku"),
        ("Kadi Aevi Yaad – Rakesh Barot", "https://open.spotify.com/track/748eQN6KCbOO1ylkwHdaXD")
    ],
    'disgust': [
        ("Apna Time Aayega", "https://open.spotify.com/track/5FLgOuLoVwwUUF7IL36Lux"),
        ("Sher Aaya Sher – Gully Boy", "https://open.spotify.com/track/7zT92EewVvLfiPyKSTJUT6"),
        ("Power – Kanye West", "https://open.spotify.com/track/2gZUPNdnz5Y45eiGxpH"),
        ("Stronger – Kanye West", "https://open.spotify.com/track/0j2T0R9dR9qdJYsB7ciXhf"),
        ("Helo Mara Dholida", "https://open.spotify.com/track/35tJHVflwKQ8pMYV1QaiJ2"),
        ("Baap Dhamaal – Jignesh Kaviraj", "https://open.spotify.com/album/2MhZPFL3YT4szEQQCZ8BoN")
    ]
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
    try:
        # DeepFace requires the image to be saved or passed as a numpy array
        result = DeepFace.analyze(
            img_path=image,
            actions=['emotion'],
            enforce_detection=False
        )

        # DeepFace result handling (can be list or dict)
        if isinstance(result, list):
            return result[0].get('dominant_emotion')
        elif isinstance(result, dict):
            if 'dominant_emotion' in result:
                return result['dominant_emotion']
            # Fallback for deepface older/specific result structure
            elif 'emotion' in result and isinstance(result['emotion'], dict):
                return result['emotion'].get('dominant')
        
        return None

    except Exception as e:
        # The Streamlit environment sometimes struggles with DeepFace
        # Show an error and fall back to manual selection
        st.error(f"Error detecting emotion (DeepFace error): {e}")
        return None


# ----------------------- UI LAYOUT -----------------------

st.markdown("<h1 class='main-title'>🎭 MoodWave AI – Emotion Based Song Recommender</h1>", unsafe_allow_html=True)
st.markdown("---")

left_col, right_col = st.columns([1, 1])

# --- LEFT COLUMN: CAMERA INPUT ---
with left_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📸 Capture Your Mood")
    
    st.markdown(
        '<span style="font-size: 0.85rem; color: #9ca3af;">Tip: Good lighting & clear face → better emotion detection.</span>',
        unsafe_allow_html=True,
    )
    
    uploaded_image = st.camera_input("")

    if uploaded_image is not None:
        img = Image.open(uploaded_image)
        # Convert image to numpy array for DeepFace
        img_np = np.array(img.convert("RGB")) 
        
        st.image(img, caption="Your Photo", use_column_width=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

# --- RIGHT COLUMN: RESULT / MANUAL SELECTION ---
with right_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🎧 Your Mood Playlist")
    
    detected_emotion = None
    
    # Run detection only if an image is uploaded
    if uploaded_image is not None:
        with st.spinner("🔍 Analyzing your emotion..."):
            time.sleep(0.5) # Slight delay for visual appeal
            detected_emotion = detect_emotion(img_np)

    # --- SHOW RESULTS (Auto Detected) ---
        
detected_emotion:
        emo_key = detected_emotion.lower()
        emo_icon = emotion_emoji.get(emo_key, "🎭")

        st.markdown(
            f"""
            <div style="margin-bottom:1rem;">
                <span class="emotion-badge">
                    <span>{emo_icon}</span>
                    <span>{detected_emotion.upper()}</span>
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        songs = emotion_to_songs.get(emo_key, [])
        if songs:
            for name, url in songs:
                st.markdown(
                    f"""
                    <div class="song-card-list">
                        <div class="song-title">🎵 {name}</div>
                        <div class="song-link"><a href="{url}" target="_blank">Play on Spotify ↗</a></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("There are no preset songs for this Emotion. Try another mood 🙂")

    # --- FALLBACK (Manual Selection) ---
   
        st.info("Take a photo above to detect your mood, or manually select your mood below. 👇")

        st.markdown("<h3 style='margin-top: 1.5rem;'>🎚️ Manual Mood Selection</h3>", unsafe_allow_html=True)

        selected_emotion = st.selectbox(
            "Choose your Mood:",
            options=list(emotion_to_songs.keys()),
            index=0,
            format_func=lambda x: x.capitalize(),
            key="manual_select" # Added key for uniqueness
        )

        # Separate button for manual selection results
        if st.button("🎧 Show Songs for this Mood", key="show_manual_songs"):
            emo_icon = emotion_emoji.get(selected_emotion, "🎭")
            
            st.markdown(
                f"""
                <div style="margin-top:1rem; margin-bottom:0.8rem;">
                    <span class="emotion-badge">
                        <span>{emo_icon}</span>
                        <span>{selected_emotion.upper()}</span>
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            songs = emotion_to_songs.get(selected_emotion, [])
            if songs:
                for name, url in songs:
                    st.markdown(
                        f"""
                        <div class="song-card-list">
                            <div class="song-title">🎵 {name}</div>
                            <div class="song-link"><a href="{url}" target="_blank">Play on Spotify ↗</a></div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("આ emotion માટે preset songs નથી.")
            
    st.markdown("</div>", unsafe_allow_html=True)
    

    

# Footer hint
st.markdown(
    """
    <div style="margin-top: 2rem; text-align: center;">
        <span style="font-size: 0.8rem; color: #9ca3af;">
            Built with ME and Dhruv Dave using Streamlit &amp; DeepFace · Capture → Detect → Vibe 🎶
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
