import streamlit as st
from deepface import DeepFace
from PIL import Image
import numpy as np
import time

# ----------------------- CUSTOM CSS (ANIMATIONS + UI) -----------------------
st.markdown("""
<style>
/* Gradient Animated Background */
body {
    background: linear-gradient(-45deg, #ff9a9e, #fad0c4, #a18cd1, #fbc2eb);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Remove extra padding so no blank rectangles appear */
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1.2rem;
}

/* Title Animation */
.title-animate {
    animation: fadeInDown 1.2s ease-out;
    font-size: 2.1rem;
    font-weight: 800;
    color: #0f172a;
    text-shadow: 0 6px 18px rgba(15,23,42,0.25);
}

@keyframes fadeInDown {
    from {opacity: 0; transform: translateY(-25px);}
    to {opacity: 1; transform: translateY(0);}
}

/* Small subtitle */
.subtitle {
    font-size: 0.9rem;
    color: #111827;
    opacity: 0.8;
}

/* Emotion chip (😄 HAPPY) */
.emotion-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 1.1rem;
    border-radius: 999px;
    color: #111827;
    font-weight: 600;
    font-size: 0.9rem;
    background: #fde68a;
    box-shadow: 0 10px 25px rgba(0,0,0,0.18);
    animation: chipIn 0.35s ease-out;
}

@keyframes chipIn {
    from {opacity:0; transform: translateY(-8px) scale(0.9);}
    to {opacity:1; transform: translateY(0) scale(1);}
}

/* Different chip colors per emotion */
.chip-happy   { background: linear-gradient(135deg,#facc15,#fb923c); color:#111827; }
.chip-sad     { background: linear-gradient(135deg,#38bdf8,#6366f1); color:#e5f2ff; }
.chip-angry   { background: linear-gradient(135deg,#f97373,#b91c1c); color:#fee2e2; }
.chip-surprise{ background: linear-gradient(135deg,#f97316,#ec4899); color:#fef3c7; }
.chip-neutral { background: linear-gradient(135deg,#9ca3af,#6b7280); color:#f9fafb; }
.chip-fear    { background: linear-gradient(135deg,#22c55e,#0f766e); color:#ecfdf5; }
.chip-disgust { background: linear-gradient(135deg,#a855f7,#6d28d9); color:#f5f3ff; }

/* Song pill list container */
.song-list {
    margin-top: 0.8rem;
}

/* Full-width pill for each song */
.song-pill {
    width: 100%;
    border-radius: 999px;
    padding: 0.85rem 1.4rem;
    margin: 0.35rem 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
    box-shadow: 0 14px 28px rgba(15,23,42,0.45);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(15,23,42,0.3);
    background: rgba(15,23,42,0.94);
    color: #e5e7eb;
    transition: transform 0.22s ease, box-shadow 0.22s ease, background 0.22s ease, border 0.22s ease;
    animation: fadeIn 0.7s ease;
}

.song-pill:hover {
    transform: translateY(-2px);
    box-shadow: 0 18px 36px rgba(15,23,42,0.75);
    background: #020617;
}

/* Left part (icon + title) */
.song-left {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    font-size: 0.95rem;
    font-weight: 500;
}

/* Right link */
.song-right a {
    font-size: 0.85rem;
    text-decoration: none;
    font-weight: 600;
    color: #38bdf8;
}
.song-right a:hover {
    text-decoration: underline;
}

/* Small animation */
@keyframes fadeIn {
    from {opacity:0; transform: translateY(4px);}
    to {opacity:1; transform: translateY(0);}
}

/* Emotion-based border glow for pills */
.song-happy   { border-color:#facc15; box-shadow:0 14px 30px rgba(250,204,21,0.25); }
.song-sad     { border-color:#38bdf8; box-shadow:0 14px 30px rgba(56,189,248,0.25); }
.song-angry   { border-color:#f97373; box-shadow:0 14px 30px rgba(248,113,113,0.25); }
.song-surprise{ border-color:#fb923c; box-shadow:0 14px 30px rgba(251,146,60,0.25); }
.song-neutral { border-color:#9ca3af; box-shadow:0 14px 30px rgba(156,163,175,0.25); }
.song-fear    { border-color:#22c55e; box-shadow:0 14px 30px rgba(34,197,94,0.25); }
.song-disgust { border-color:#a855f7; box-shadow:0 14px 30px rgba(168,85,247,0.25); }

/* Manual-section label */
.hint-label {
    font-size: 0.8rem;
    color: #111827;
    opacity: 0.7;
}
</style>
""", unsafe_allow_html=True)

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
        result = DeepFace.analyze(
            img_path=image,
            actions=['emotion'],
            enforce_detection=False
        )
        # DeepFace returns list in version 0.0.96
        return result[0]['dominant_emotion']
    except Exception as e:
        st.error(f"Error detecting emotion: {e}")
        return None

# ----------------------- UI TITLE -----------------------
st.markdown(
    """
    <div class='title-animate'>
        🎭 MoodWave AI – Emotion Based Song Recommender
    </div>
    <div class="subtitle">
        Capture your selfie, let AI read your mood, and enjoy songs that match your vibes.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------- CAMERA -----------------------
uploaded_image = st.camera_input("📸 Take a picture")

detected_emotion = None

if uploaded_image is not None:
    img = Image.open(uploaded_image)
    st.image(img, caption="Your Photo", use_column_width=True)

    img_np = np.array(img.convert("RGB"))

    with st.spinner("Detecting your emotion... 🔍"):
        time.sleep(1.3)  # smooth animation
        detected_emotion = detect_emotion(img_np)

# ----------------------- AUTO MODE (DeepFace) -----------------------
if detected_emotion:
    emo_key = detected_emotion.lower()
    emo_icon = emotion_emoji.get(emo_key, "🎭")

    # Emotion chip
    st.markdown(
        f"""
        <div class="emotion-chip chip-{emo_key}">
            <span>{emo_icon}</span>
            <span>{emo_key.upper()}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='song-list'>", unsafe_allow_html=True)

    songs = emotion_to_songs.get(emo_key, [])
    for name, url in songs:
        st.markdown(
            f"""
            <div class="song-pill song-{emo_key}">
                <div class="song-left">
                    <span>🎵</span>
                    <span>{name}</span>
                </div>
                <div class="song-right">
                    <a href="{url}" target="_blank">Play on Spotify ↗</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------- MANUAL FALLBACK MODE -----------------------
st.divider()
st.subheader("🎚️ Manual Mood Selection (Fallback Mode)")
st.markdown(
    "<span class='hint-label'>If camera / detection fails, choose a mood and explore songs manually.</span>",
    unsafe_allow_html=True
)

selected_emotion = st.selectbox(
    "તમારું mood પસંદ કરો:",
    options=list(emotion_to_songs.keys()),
    index=0,
    format_func=lambda x: x.capitalize()
)

if st.button("🎧 Show Songs for this Mood"):
    emo_icon = emotion_emoji.get(selected_emotion, "🎭")

    st.markdown(
        f"""
        <div class="emotion-chip chip-{selected_emotion}">
            <span>{emo_icon}</span>
            <span>{selected_emotion.upper()}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='song-list'>", unsafe_allow_html=True)

    songs = emotion_to_songs.get(selected_emotion, [])
    for name, url in songs:
        st.markdown(
            f"""
            <div class="song-pill song-{selected_emotion}">
                <div class="song-left">
                    <span>🎵</span>
                    <span>{name}</span>
                </div>
                <div class="song-right">
                    <a href="{url}" target="_blank">Play on Spotify ↗</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
