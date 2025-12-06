import streamlit as st
from PIL import Image
import numpy as np

# -------------------------------------------------------------------
# Try to import DeepFace – if it fails (TensorFlow issue on cloud),
# we fall back to manual mood selection.
# -------------------------------------------------------------------
DEEPFACE_AVAILABLE = True
DEEPFACE_ERROR = None

try:
    from deepface import DeepFace
except Exception as e:
    DEEPFACE_AVAILABLE = False
    DEEPFACE_ERROR = str(e)

emotion_to_songs = {
    'happy': [
        ("Aankh Marey – Simmba", "https://open.spotify.com/track/63MvWd6T6yoS7h4AJ4Hjrm"),
        ("Nashe Si Chadh Gayi – Befikre", "https://open.spotify.com/track/3uoQUnKEedaeLKxUeVaJwj"),
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

def detect_emotion(image):
    """Use DeepFace if available, otherwise return None."""
    if not DEEPFACE_AVAILABLE:
        return None

    try:
        result = DeepFace.analyze(
            img_path=image,
            actions=['emotion'],
            enforce_detection=False
        )

        # DeepFace 0.0.96 ક્યારેક list આપે, ક્યારેક dict
        if isinstance(result, list):
            return result[0].get('dominant_emotion')
        elif isinstance(result, dict):
            # કેટલાક versions માં result["emotion"]["dominant"] હોય
            if 'dominant_emotion' in result:
                return result['dominant_emotion']
            elif 'emotion' in result and isinstance(result['emotion'], dict):
                return result['emotion'].get('dominant')
        return None

    except Exception as e:
        st.error(f"Error detecting emotion: {e}")
        return None


st.title("🎭 MoodWave AI – Emotion Based Song Recommendation")

if DEEPFACE_AVAILABLE:
    st.caption("✅ DeepFace loaded successfully – automatic emotion detection is ON.")
else:
    st.warning(
        "⚠️ DeepFace / TensorFlow આ hosting environment માં load થતું નથી.\n\n"
        "Cloud પર automatic emotion detection બંધ છે, પણ તમે નીચે mood manually select કરી શકો છો."
    )
    if DEEPFACE_ERROR:
        with st.expander("🔍 Technical details (for debugging)"):
            st.code(DEEPFACE_ERROR)

# -------------------------------------------------------------------
# MODE 1: Automatic (only if DeepFace available)
# -------------------------------------------------------------------

emotion_style = {
    "happy":   {"color": "#FACC15", "emoji": "😄"},
    "sad":     {"color": "#60A5FA", "emoji": "😢"},
    "angry":   {"color": "#F97373", "emoji": "😠"},
    "surprise":{"color": "#FB923C", "emoji": "😲"},
    "neutral": {"color": "#9CA3AF", "emoji": "😐"},
    "fear":    {"color": "#A855F7", "emoji": "😨"},
    "disgust": {"color": "#22C55E", "emoji": "🤢"},
}
if DEEPFACE_AVAILABLE:
    uploaded_image = st.camera_input("📸 Take a picture")

    if uploaded_image is not None:
        img = Image.open(uploaded_image)
        st.image(img, caption="Your Photo", use_column_width=True)

        img_np = np.array(img.convert("RGB"))
        emotion = detect_emotion(img_np)

        if emotion:
            st.success(f"🎭 Detected Emotion: **{emotion.upper()}**")

            st.subheader("🎧 Recommended Songs:")
            songs = emotion_to_songs.get(emotion.lower(), [])

            if not songs:
                st.info("આ emotion માટે preset songs નથી. Try another mood 🙂")
            else:
                for name, url in songs:
                    st.markdown(f"- 🎵 [{name}]({url})")
        else:
            st.info("Emotion detect નથઈ શક્યું. Try again અથવા નીચે manual mood select કરો.")

# -------------------------------------------------------------------
# MODE 2: Fallback – Manual mood selection (always available)
# -------------------------------------------------------------------
st.divider()
st.subheader("🎚️ Manual Mood Selection (Fallback Mode)")

selected_emotion = st.selectbox(
    "તમારું mood પસંદ કરો:",
    options=list(emotion_to_songs.keys()),
    index=0,
    format_func=lambda x: x.capitalize()
)

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
