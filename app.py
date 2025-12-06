import streamlit as st
from deepface import DeepFace
from PIL import Image
import numpy as np

# ---------------- EMOTION → SONGS MAP ---------------- #
emotion_to_songs = {
    "happy": [
        ("Aankh Marey – Simmba", "https://open.spotify.com/track/63MvWd6T6yoS7h4AJ4Hjrm"),
        ("Nashe Si Chadh Gayi – Befikre", "https://open.spotify.com/track/3uoQUnKEedaeLKxUeVaJwj"),
        ("Happy – Pharrell Williams", "https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH"),
        ("Can’t Stop the Feeling – Justin Timberlake", "https://open.spotify.com/track/6JV2JOEocMgcZxYSZelKcc"),
        ("Hokaliyo", "https://open.spotify.com/artist/535ascn4f13hFo2kjCodKE"),
        ("Vaagyo Re Dhol – Hellaro", "https://open.spotify.com/track/3GSyZg9iVdj1WjKzBcLakX"),
        ("Bhuli Javu Che – Sachin–Jigar", "https://open.spotify.com/track/7s1pfz5zIMBJdYVc3bWEku"),
    ],
    "sad": [
        ("Arambha Hai Prachand", "https://open.spotify.com/track/1PZZtXR7nsNIyRcqd7UeiF"),
        ("Channa Mereya – Arijit Singh", "https://open.spotify.com/track/0H2iJVgorRR0ZFgRqGUjUM"),
        ("Tujhe Kitna Chahne Lage – Kabir Singh", "https://open.spotify.com/track/3dYD57lRAUcMHufyqn9GcI"),
        ("Let Her Go – Passenger", "https://open.spotify.com/track/0JmiBCpWc1IAc0et7Xm7FL"),
        ("Someone Like You – Adele", "https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB"),
        ("Mane Yaad Ave – Parthiv Gohil", "https://open.spotify.com/track/1JVAoIO4NtjlejraxemhLh"),
        ("Chand Ne Kaho – Jigardan Gadhavi", "https://open.spotify.com/track/6ci9DNOBLvA7jVDkMYf5Df"),
    ],
    "angry": [
        ("Zinda – Bhaag Milkha Bhaag", "https://open.spotify.com/track/6Zo8diPZAjkUH4rWDMgeiE"),
        ("Sultan Title Track", "https://open.spotify.com/track/3LJhJG3EsmhCq9bNn047lu"),
        ("Believer – Imagine Dragons", "https://open.spotify.com/track/0pqnGHJpmpxLKifKRmU6WP"),
        ("Lose Yourself – Eminem", "https://open.spotify.com/track/7MJQ9Nfxzh8LPZ9e9u68Fq"),
        ("Rag Rag Mein – Kirtidan Gadhvi", "https://open.spotify.com/artist/7odYFkW15De3A7aAuk5x9h"),
        ("Jode Tame Rahejo – Gujarati Garba", "https://open.spotify.com/track/3ByO0k09IsJPqAGncEVuYQ"),
    ],
    "surprise": [
        ("Senorita – ZNMD", "https://open.spotify.com/track/6b8zsc3BxT59Yg62wjt7qA"),
        ("Odhani – Made In China", "https://open.spotify.com/track/2q0V50aNlI1RQXJyE5HDgD"),
        ("Uptown Funk – Bruno Mars", "https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS"),
        ("Sugar – Maroon 5", "https://open.spotify.com/track/55h7vJchibLdUkxdlX3fK7"),
        ("Hokaliyo", "https://open.spotify.com/artist/535ascn4f13hFo2kjCodKE"),
        ("Halaji Tara Fulwadi", "https://open.spotify.com/track/58kDGOUvK1foT7UGnZYaFQ"),
        ("Kaka Bapa Na Gaam Nu", "https://open.spotify.com/track/4YigRMdxg9DJNL0rh6V1KK"),
    ],
    "neutral": [
        ("Ilahi – Yeh Jawaani Hai Deewani", "https://open.spotify.com/track/0VxgNsSywsjapKGXvzj8RH"),
        ("Tera Yaar Hoon Main", "https://open.spotify.com/track/3ZCTVFBt2Brf31RLEnCkWJ"),
        ("Counting Stars – OneRepublic", "https://open.spotify.com/track/2tpWsVSb9UEmDRxAl1zhX1"),
        ("Perfect – Ed Sheeran", "https://open.spotify.com/track/0tgVpDi06FyKpA1z0VMD4v"),
        ("Kaka Bapa Na Gaam Nu", "https://open.spotify.com/track/3GmKe3YkJ4YuMZ1GNy9jjW"),
        ("Gujarati Folk Mashup – RJ Dhvanit", "https://open.spotify.com/artist/7AeKpTtsd8BgYZAAGZ4s48"),
        ("Arambha Hai Prachand", "https://open.spotify.com/track/1PZZtXR7nsNIyRcqd7UeiF"),
    ],
    "fear": [
        ("Arambha Hai Prachand", "https://open.spotify.com/track/1PZZtXR7nsNIyRcqd7UeiF"),
        ("Namo Namo – Kedarnath", "https://open.spotify.com/track/5Fx864foKMyZtJbBiwvyBz"),
        ("Kun Faya Kun – Rockstar", "https://open.spotify.com/track/7F8RNvTQlvbeBLeenycvN6"),
        ("Demons – Imagine Dragons", "https://open.spotify.com/track/3LlAyCYU26dvFZBDUIMb7a"),
        ("Scared to Be Lonely – Dua Lipa", "https://open.spotify.com/track/3ebXMykcMXOcLeJ9xZ17XH"),
        ("Bhuli Javu Che – Sachin–Jigar", "https://open.spotify.com/track/7s1pfz5zIMBJdYVc3bWEku"),
        ("Kadi Aevi Yaad – Rakesh Barot", "https://open.spotify.com/track/748eQN6KCbOO1ylkwHdaXD"),
    ],
    "disgust": [
        ("Apna Time Aayega – Gully Boy", "https://open.spotify.com/track/5FLgOuLoVwwUUF7IL36Lux"),
        ("Sher Aaya Sher – Gully Boy", "https://open.spotify.com/track/7zT92EewVvLfiPyKSTJUT6"),
        ("Power – Kanye West", "https://open.spotify.com/track/2gZUPNdnz5Y45eiGxpH"),
        ("Stronger – Kanye West", "https://open.spotify.com/track/0j2T0R9dR9qdJYsB7ciXhf"),
        ("Helo Mara Dholida", "https://open.spotify.com/track/35tJHVflwKQ8pMYV1QaiJ2"),
        ("Baap Dhamaal – Jignesh Kaviraj", "https://open.spotify.com/album/2MhZPFL3YT4szEQQCZ8BoN"),
    ],
}

# ------------- EMOTION → COLOR / EMOJI ------------- #
emotion_style = {
    "happy":   {"color": "#FACC15", "emoji": "😄"},
    "sad":     {"color": "#60A5FA", "emoji": "😢"},
    "angry":   {"color": "#F97373", "emoji": "😠"},
    "surprise":{"color": "#FB923C", "emoji": "😲"},
    "neutral": {"color": "#9CA3AF", "emoji": "😐"},
    "fear":    {"color": "#A855F7", "emoji": "😨"},
    "disgust": {"color": "#22C55E", "emoji": "🤢"},
}

# ------------- SESSION STATE ------------- #
if "detected_emotion" not in st.session_state:
    st.session_state.detected_emotion = None

# ------------- EMOTION DETECTION ------------- #
def detect_emotion(image):
    try:
        result = DeepFace.analyze(
            img_path=image,
            actions=["emotion"],
            enforce_detection=False
        )
        # DeepFace 0.0.96 ઘણી વાર list આપે છે
        if isinstance(result, list):
            return result[0]["dominant_emotion"]
        return result.get("dominant_emotion")
    except Exception as e:
        st.error(f"Error detecting emotion: {e}")
        return None

# ------------- DYNAMIC THEME (BG + TITLE) ------------- #
current_emotion = st.session_state.detected_emotion

if current_emotion and current_emotion.lower() in emotion_style:
    base_color = emotion_style[current_emotion.lower()]["color"]
    title_emoji = emotion_style[current_emotion.lower()]["emoji"]
    # Mood set થઈ ગયા પછી – no animation, solid mood color
    animation_css = "none"
    gradient_start = base_color
    gradient_end = "#0f172a"
else:
    # First load – 2 second color changing animation
    base_color = "#6366F1"
    title_emoji = "🎵"
    animation_css = "pulseColors 2s ease-in-out infinite"
    gradient_start = "#6366F1"
    gradient_end = "#EC4899"

# ------------- GLOBAL STYLING + ANIMATIONS ------------- #
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');

html, body {{
    background: radial-gradient(circle at top, #111827, #020617);
}}

[data-testid="stAppViewContainer"] {{
    background: radial-gradient(circle at top, #111827, #020617);
    color: #E5E7EB;
    font-family: 'Poppins', system-ui, sans-serif;
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

.main-block {{
    max-width: 950px;
    margin: 0 auto;
}}

#mood-title {{
    margin-top: 0.3rem;
    margin-bottom: 0.8rem;
    display: flex;
    justify-content: center;
}}

.mood-title-pill {{
    padding: 0.8rem 2.8rem;
    border-radius: 999px;
    background: linear-gradient(120deg, {gradient_start}, {gradient_end});
    color: white;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-weight: 800;
    font-size: 1.35rem;
    box-shadow: 0 20px 55px rgba(0,0,0,0.55);
    display: inline-flex;
    align-items: center;
    gap: 0.7rem;
    animation: {animation_css};
}}

.mood-title-pill span.emoji {{
    font-size: 1.8rem;
}}

@keyframes pulseColors {{
    0% {{
        filter: hue-rotate(0deg);
        transform: translateY(0px) scale(1);
        box-shadow: 0 20px 45px rgba(0,0,0,0.45);
    }}
    50% {{
        filter: hue-rotate(35deg);
        transform: translateY(-4px) scale(1.03);
        box-shadow: 0 26px 70px rgba(0,0,0,0.75);
    }}
    100% {{
        filter: hue-rotate(0deg);
        transform: translateY(0px) scale(1);
        box-shadow: 0 20px 45px rgba(0,0,0,0.45);
    }}
}}

.glass-card {{
    background: rgba(15,23,42,0.86);
    border-radius: 26px;
    padding: 1.8rem 1.7rem 1.5rem;
    box-shadow:
        0 18px 45px rgba(0,0,0,0.75),
        0 0 0 1px rgba(148,163,184,0.18);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(148,163,184,0.28);
}}

.sub-title {{
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: #9CA3AF;
    margin-bottom: 0.6rem;
}}

.cam-wrapper {{
    border-radius: 22px;
    padding: 0.9rem;
    background: radial-gradient(circle at top, rgba(55,65,81,0.9), rgba(15,23,42,1));
    box-shadow: inset 0 0 0 1px rgba(148,163,184,0.35);
}}

.song-card {{
    border-radius: 16px;
    padding: 0.75rem 0.95rem;
    margin-bottom: 0.5rem;
    background: linear-gradient(115deg, rgba(15,23,42,0.96), rgba(30,64,175,0.65));
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 28px rgba(15,23,42,0.85);
    border: 1px solid rgba(148,163,184,0.35);
    transition: transform 0.18s ease-out, box-shadow 0.18s ease-out, border-color 0.18s ease-out;
}}

.song-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 18px 40px rgba(15,23,42,0.95);
    border-color: {base_color};
}}

.song-name {{
    font-size: 0.96rem;
    font-weight: 500;
    color: #E5E7EB;
}}

.song-link a {{
    font-size: 0.83rem;
    padding: 0.28rem 0.7rem;
    border-radius: 999px;
    border: 1px solid rgba(148,163,184,0.7);
    text-decoration: none !important;
}}

.song-link a:hover {{
    border-color: {base_color};
}}

.emotion-tag {{
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.22rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8rem;
    background: rgba(15,23,42,0.95);
    border: 1px solid rgba(148,163,184,0.6);
    color: #E5E7EB;
}}

.emotion-dot {{
    width: 10px;
    height: 10px;
    border-radius: 999px;
    background: {base_color};
    box-shadow: 0 0 12px {base_color};
}}

footer {{
    visibility: hidden;
}}
</style>
""",
    unsafe_allow_html=True,
)

# ------------- TITLE (NO OLD GREY BAR) ------------- #
st.markdown(
    f"""
<div class="main-block">
  <div id="mood-title">
    <div class="mood-title-pill">
      <span class="emoji">{title_emoji}</span>
      <span>MOODWAVE AI</span>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="main-block">
  <div class="glass-card">
    <div class="sub-title">Emotion-based music • Smart recommendations</div>
""",
    unsafe_allow_html=True,
)

# ------------- CAMERA + EMOTION DETECTION ------------- #
with st.container():
    col1, col2 = st.columns([1.1, 1])

    with col1:
        st.markdown('<div class="cam-wrapper">', unsafe_allow_html=True)
        uploaded_image = st.camera_input("📸 Take a picture to detect your mood")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if uploaded_image is not None:
            img = Image.open(uploaded_image)
            st.image(img, caption="Your Photo", use_column_width=True)

            img_np = np.array(img.convert("RGB"))
            emotion = detect_emotion(img_np)

            if emotion:
                st.session_state.detected_emotion = emotion.lower()
                style = emotion_style.get(emotion.lower(), {"color": "#6366F1", "emoji": "🎵"})
                st.markdown(
                    f"""
                    <div style="margin-top:0.4rem;">
                        <span class="emotion-tag">
                            <span class="emotion-dot"></span>
                            <span>{style["emoji"]} Detected emotion: <b>{emotion.upper()}</b></span>
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.info("Emotion detect નથઈ શક્યું. Try again 🙂")

# ------------- SONG RECOMMENDATIONS ------------- #
st.markdown("### 🎧 Recommended Songs")

active_emotion = st.session_state.detected_emotion or "neutral"
songs = emotion_to_songs.get(active_emotion, [])

if not songs:
    st.info("આ emotion માટે preset songs નથી. Try another mood.")
else:
    for name, url in songs:
        st.markdown(
            f"""
            <div class="song-card">
                <div class="song-name">🎵 {name}</div>
                <div class="song-link">
                    <a href="{url}" target="_blank">Open in Spotify</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("</div></div>", unsafe_allow_html=True)
