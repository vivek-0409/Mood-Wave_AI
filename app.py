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

/* Title Animation */
.title-animate {
    animation: fadeInDown 1.2s ease-out;
}

@keyframes fadeInDown {
    from {opacity: 0; transform: translateY(-25px);}
    to {opacity: 1; transform: translateY(0);}
}

/* Card Glow */
.song-card {
    background: rgba(255,255,255,0.25);
    padding: 15px;
    margin: 10px 0;
    border-radius: 15px;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.3);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.song-card:hover {
    transform: scale(1.03);
    box-shadow: 0 4px 20px rgba(255,255,255,0.5);
}

/* Fade-in Animation */
.fade-in {
    animation: fadeIn 1.4s ease;
}

@keyframes fadeIn {
    from {opacity:0;}
    to {opacity:1;}
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
st.markdown("<h1 class='title-animate'>🎭 MoodWave AI – Emotion Based Song Recommender</h1>", unsafe_allow_html=True)

# ----------------------- CAMERA -----------------------
uploaded_image = st.camera_input("📸 Take a picture")

if uploaded_image is not None:
    img = Image.open(uploaded_image)
    st.image(img, caption="Your Photo", use_column_width=True)

    img_np = np.array(img.convert("RGB"))

    with st.spinner("Detecting your emotion... 🔍"):
        time.sleep(1.3)  # smooth animation
        emotion = detect_emotion(img_np)

    if emotion:
        st.success(f"🎭 Detected Emotion: **{emotion.upper()}**")

        st.subheader("🎧 Your Personalized Songs")
        songs = emotion_to_songs.get(emotion.lower(), [])

        for name, url in songs:
            st.markdown(
                f"""
                <div class='song-card fade-in'>
                    🎵 <b>{name}</b><br>
                    <a href="{url}" target="_blank">▶ Play on Spotify</a>
                </div>
                """,
                unsafe_allow_html=True
            )

st.divider()
st.subheader("🎚️ Manual Mood Selection (Fallback Mode)")

selected_emotion = st.selectbox(
    "તમારું mood પસંદ કરો:",
    options=list(emotion_to_songs.keys()),
    index=0,
    format_func=lambda x: x.capitalize()
)

if st.button("🎧 Show Songs for this Mood"):
    st.success(f"Selected Emotion: **{selected_emotion.upper()}**")
    songs = emotion_to_songs.get(selected_emotion, [])
    if not songs:
        st.info("આ emotion માટે preset songs નથી.")
    else:
        for name, url in songs:
            st.markdown(f"- 🎵 [{name}]({url})")
