import streamlit as st
from deepface import DeepFace
from PIL import Image
import numpy as np
import time

# -------------------------------------------------------------
# LinkedIn URLs (New Constants)
# -------------------------------------------------------------
MY_LINKEDIN_URL = "https://www.linkedin.com/in/parekh-vivekkumar-gp-kheda-it-dte-03b3572b6?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3B%2BFmiVhRSQcWTHq7oN7aIkA%3D%3D"
DHRUV_LINKEDIN_URL = "https://www.linkedin.com/in/dhruvdave2807?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BM7UvANbjQO%2BG%2BRNnFvfO6Q%3D%3D"

# -------------------------------------------------------------
# Streamlit Page Config (should be before any other Streamlit call)
# -------------------------------------------------------------
st.set_page_config(
    page_title="MoodWave AI",
    page_icon="🎭",
    layout="wide"
)

# -------------------------------------------------------------
# Top small (empty) title block – you can remove if not needed
# -------------------------------------------------------------
st.markdown(
    f"""
    <p>  </p>
    <p><div class="main-title">  </div></p>
    <div class="main-title">  </div>
    """,
    unsafe_allow_html=True,
)

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
# LANGUAGE SETUP
# -------------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"  # default English

def set_lang(l):
    st.session_state["lang"] = l

def L(key: str) -> str:
    """Helper to get translated text based on current language"""
    lang = st.session_state.get("lang", "en")
    return TEXT[key][lang]

TEXT = {
    "app_title": {
        "en": "MoodWave AI",
        "hi": "मूडवेव एआई",
        "gu": "મૂડવેવ એઆઇ",
    },
    "app_subtitle": {
        "en": "Capture your mood & instantly get handpicked songs that vibe with your emotion.",
        "hi": "अपना मूड कैप्चर करें और तुरंत अपने इमोशन से मेल खाते चुने हुए गाने पाएं।",
        "gu": "તમારો મૂડ કેપ્ચર કરો અને તરત જ તમારા ઈમોશન સાથે મેળ ખાતા પસંદગીના ગીતો મેળવો.",
    },
    "sidebar_title": {
        "en": "MoodWave AI",
        "hi": "मूडवेव एआई",
        "gu": "મૂડવેવ એઆઇ",
    },
    "sidebar_desc": {
        "en": "Capture your mood using your camera or a photo, and instantly get songs that vibe with your emotion.",
        "hi": "कैमरा या फोटो से अपना मूड कैप्चर करें और तुरंत अपने इमोशन से मेल खाते गाने पाएं।",
        "gu": "કેમેરા અથવા ફોટાથી તમારો મૂડ કેપ્ચર કરો અને તરત જ તમારા ઈમોશન પ્રમાણે ગીતો મેળવો.",
    },
    "sidebar_how_title": {
        "en": "How it works",
        "hi": "कैसे काम करता है",
        "gu": "કેવી રીતે કામ કરે છે",
    },
    "sidebar_how_points": {
        "en": "- Take or upload a selfie.\n- AI detects your dominant emotion.\n- We show curated songs from Hindi, English & Gujarati.\n- Or select your mood manually anytime.",
        "hi": "- एक सेल्फी लें या फोटो अपलोड करें।\n- एआई आपका डॉमिनेंट इमोशन पहचानता है।\n- हम हिंदी, इंग्लिश और गुजराती के चुने हुए गाने दिखाते हैं।\n- या कभी भी अपना मूड मैन्युअली चुनें।",
        "gu": "- સેલ્ફી લો અથવા ફોટો અપલોડ કરો.\n- એઆઇ તમારો ડોમિનેન્ટ ઈમોશન ઓળખે છે.\n- અમે હિન્દી, અંગ્રેજી અને ગુજરાતી ગીતોની પસંદગી બતાવીએ છીએ.\n- અથવા તમે ક્યારેય મેન્યુઅલી મૂડ પસંદ કરી શકો છો.",
    },
    "sidebar_creators": {
        "en": "Creators",
        "hi": "निर्माता",
        "gu": "ક્રિએટર્સ",
    },
    "choose_input": {
        "en": "Choose input method:",
        "hi": "इनपुट तरीका चुनें:",
        "gu": "ઇનપુટ પદ્ધતિ પસંદ કરો:",
    },
    "opt_camera": {
        "en": "📷 Camera",
        "hi": "📷 कैमरा",
        "gu": "📷 કેમેરા",
    },
    "opt_upload": {
        "en": "📁 Upload Photo",
        "hi": "📁 फोटो अपलोड करें",
        "gu": "📁 ફોટો અપલોડ કરો",
    },
    "camera_take_pic": {
        "en": "📸 Take a picture",
        "hi": "📸 फोटो लें",
        "gu": "📸 ફોટો લો",
    },
    "upload_label": {
        "en": "📁 Upload a photo",
        "hi": "📁 एक फोटो अपलोड करें",
        "gu": "📁 એક ફોટો અપલોડ કરો",
    },
    "manual_hint": {
        "en": "If camera / detection fails, choose a mood and explore songs manually.",
        "hi": "अगर कैमरा / डिटेक्शन फेल हो जाए, तो मूड चुनें और मैन्युअली गाने देखें।",
        "gu": "જો કેમેરા / ડિટેક્શન નિષ્ફળ જાય, તો મૂડ પસંદ કરો અને મેન્યુઅલી ગીતો જુઓ.",
    },
    "quick_mood_title": {
        "en": "🎧 Quick Mood Shortcuts (Manual Mood Selection)",
        "hi": "🎧 क्विक मूड शॉर्टकट (मैन्युअल मूड चयन)",
        "gu": "🎧 ક્વિક મૂડ શોર્ટકટ (મેન્યુઅલ મૂડ પસંદગી)",
    },
    "detect_spinner": {
        "en": "Detecting your emotion... 🔍",
        "hi": "आपका इमोशन पहचाना जा रहा है... 🔍",
        "gu": "તમારો ઈમોશન ઓળખાઈ રહ્યો છે... 🔍",
    },
    "closing_message": { # New closing message
        "en": "Thank you for visiting MoodWave AI! What's your current vibe? 😄🎶 Try another picture or pick a mood! 💖",
        "hi": "MoodWave AI पर आने के लिए धन्यवाद! आपका वर्तमान मूड कैसा है? 😄🎶 एक और तस्वीर आज़माएं या मूड चुनें! 💖",
        "gu": "MoodWave AI ની મુલાકાત લેવા બદલ આભાર! તમારો વર્તમાન વાઇબ કેવો છે? 😄🎶 બીજો ફોટો ટ્રાય કરો અથવા મૂડ પસંદ કરો! 💖",
    },
}

# -------------------------------------------------------------
# Data: Emotion → Songs
# -------------------------------------------------------------
emotion_to_songs = {
    'happy': [
        ("Aankh Marey – Simmba", "https://open.spotify.com/track/63MvWd6T6yoS7h4AJ4Hjrm"),
        ("Nashe Si Chadh गई – Befikre", "https://open.spotify.com/track/3uoQUnKEedaeLKxUeVaJwj"),
        ("Happy – Pharrell Williams", "https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH"),
        ("Can’t Stop the Feeling – Justin Timberlake", "https://open.spotify.com/track/6JV2JOEocMycZxYSZelKcc"),
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

# ----------------------- Custom CSS (Updated for Creator Buttons) -----------------------
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
    
    /* New Keyframes for staggered entry */
    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* Song Card List Item (MODIFIED FOR ANIMATION) */
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
        
        /* Apply the staggered animation */
        animation: fadeInUp 0.5s ease-out forwards; 
        opacity: 0; /* Start hidden */
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
    
    /* Fancy button tweak (global buttons) */
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

    /* ---------------------- GOLD STYLES FOR INPUT METHOD & CAMERA ---------------------- */

    /* Gold label for "Choose input method:" */
    .gold-label {
        color: #facc15;
        font-weight: 800;
        font-size: 1.1rem;
        text-shadow: 0 0 10px rgba(250,204,21,0.6);
        margin-bottom: 0.3rem;
    }

    /* Gold animated label for "📸 Take a picture" */
    .camera-gold {
        color: #facc15;
        font-weight: 900;
        font-size: 1.15rem;
        text-shadow: 0 0 12px rgba(250,204,21,0.8);
        animation: pulseGold 1.5s ease-in-out infinite alternate;
    }

    @keyframes pulseGold {
        from { text-shadow: 0 0 6px rgba(250,204,21,0.5); }
        to  { text-shadow: 0 0 16px rgba(250,204,21,1); }
    }

    /* Radio options gold color */
    [data-testid="stRadio"] label {
        color: #facc15 !important;
        font-weight: 700 !important;
    }

    /* Selected radio option glow */
    [data-testid="stRadio"] div[role="radiogroup"] > div:has(input:checked) {
        background: rgba(250,204,21,0.18);
        border-radius: 12px;
        padding: 3px 10px;
        box-shadow: 0 0 15px rgba(250,204,21,0.7);
        animation: goldSelect 0.2s ease-out;
    }

    @keyframes goldSelect {
        from { box-shadow: 0 0 0 rgba(250,204,21,0.0); }
        to  { box-shadow: 0 0 15px rgba(250,204,21,0.9); }
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

    /* Language buttons container special styling */
    .lang-btn-container .stButton>button {
        background: linear-gradient(135deg, #facc15, #fb7185);
        box-shadow: 0 0 18px rgba(250,204,21,0.6);
        animation: langPulse 1.8s ease-in-out infinite alternate;
    }

    @keyframes langPulse {
        from { box-shadow: 0 0 8px rgba(250,204,21,0.4); }
        to  { box-shadow: 0 0 22px rgba(250,204,21,0.95); }
    }
    
    /* Closing Footer Message (NEW) */
    .closing-message {
        text-align: center;
        margin-top: 3rem;
        padding: 1.5rem;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.05);
        font-size: 1.1rem;
        font-weight: 600;
        color: #facc15; 
        text-shadow: 0 0 10px rgba(250,204,21, 0.4);
        border: 1px solid rgba(250,204,21, 0.3);
    }
    
    /* ---------------------- CREATOR BUTTON STYLING (NEW) ---------------------- */
    .creator-connect-header {
        font-size: 0.9rem;
        font-weight: 700;
        color: #38bdf8; /* Cyan/Blue */
        text-shadow: 0 0 8px rgba(56, 189, 248, 0.5);
        text-align: right;
        margin-bottom: 5px; /* Spacing above buttons */
    }
    
    @keyframes creatorPulse {
        0% { transform: scale(1); box-shadow: 0 0 10px rgba(56, 189, 248, 0.5); }
        50% { transform: scale(1.03); box-shadow: 0 0 25px rgba(56, 189, 248, 0.9); }
        100% { transform: scale(1); box-shadow: 0 0 10px rgba(56, 189, 248, 0.5); }
    }
    
    /* Styling for the small top-right buttons */
    .top-right-creator-btn .stButton>button {
        background: linear-gradient(135deg, #38bdf8, #1d4ed8); /* Blue gradient */
        color: white;
        border: none;
        padding: 0.3rem 0.6rem;
        font-size: 0.8rem;
        border-radius: 999px;
        animation: creatorPulse 2s ease-in-out infinite;
        transition: all 0.2s;
    }

    .top-right-creator-btn .stButton>button:hover {
        transform: scale(1.05);
        filter: brightness(1.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# Data: Emotion → Songs
# -------------------------------------------------------------
emotion_to_songs = {
    'happy': [
        ("Aankh Marey – Simmba", "https://open.spotify.com/track/63MvWd6T6yoS7h4AJ4Hjrm"),
        ("Nashe Si Chadh गई – Befikre", "https://open.spotify.com/track/3uoQUnKEedaeLKxUeVaJwj"),
        ("Happy – Pharrell Williams", "https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH"),
        ("Can’t Stop the Feeling – Justin Timberlake", "https://open.spotify.com/track/6JV2JOEocMycZxYSZelKcc"),
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

# ----------------------- SIDEBAR -----------------------
with st.sidebar:
    # --- LANGUAGE BUTTONS (MOVED TO SIDEBAR) ---
    st.markdown("### 🌐 Select Language")
    # Use smaller labels for better fit in the narrow sidebar columns
    lang_cols_sb = st.columns(3)
    with lang_cols_sb[0]:
        if st.button("EN", key="btn_en"):
            set_lang("en")
    with lang_cols_sb[1]:
        if st.button("HI", key="btn_hi"):
            set_lang("hi")
    with lang_cols_sb[2]:
        if st.button("GU", key="btn_gu"):
            set_lang("gu")
    
    st.markdown("---")
    # --- END LANGUAGE BUTTONS ---

    st.markdown(f"## 🎭 {L('sidebar_title')}")
    st.markdown(L("sidebar_desc"))
    if not DEEPFACE_AVAILABLE:
        st.warning(
            "⚠ DeepFace not available.\n\nAutomatic emotion detection is disabled. "
            "Please use Manual Mood Selection or Quick Mood Shortcuts."
        )

    st.markdown("---")
    st.markdown(f"### ℹ {L('sidebar_how_title')}")
    st.markdown(L("sidebar_how_points"))

    st.markdown("---")
    st.markdown(f"👨‍💻 **{L('sidebar_creators')}**")
    # Updated: Added LinkedIn links to sidebar creator names
    st.markdown(f"- [Me (Vivekkumar)]({MY_LINKEDIN_URL})")
    st.markdown(f"- [Dhruv]({DHRUV_LINKEDIN_URL})")

# Removed the old language button block from the main content area

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------- MAIN TITLE -----------------------
st.markdown(
    f"""
    <div style="text-align:center; margin-bottom: 1.2rem;">
        <div class="main-title" style="font-weight: 900;">
            🎭 {L('app_title')}
        </div>
        <div class="subtitle" style="font-weight: 700; margin-top: 0.25rem;">
            <b>{L('app_subtitle')}</b>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------- TOP RIGHT CREATOR LINKS (GLOBAL PLACEMENT) -----------------------

# Header spanning the two button columns (aligned to the right)
st.markdown(
    f'<div style="text-align: right; margin-bottom: 5px;">'
    f'<span class="creator-connect-header">🔗 Connect with Creators</span>'
    f'</div>',
    unsafe_allow_html=True
)

# Buttons below the header
# Adjust column widths to push content to the far right
creator_btn_cols = st.columns([7, 1.5, 1.5]) 

with creator_btn_cols[1]:
    # Using the CSS class for the button to apply animation and glow
    st.markdown('<div class="top-right-creator-btn">', unsafe_allow_html=True)
    st.link_button("Me 🧑‍💻", MY_LINKEDIN_URL, help="Connect with Vivekkumar on LinkedIn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
with creator_btn_cols[2]:
    # Using the CSS class for the button to apply animation and glow
    st.markdown('<div class="top-right-creator-btn">', unsafe_allow_html=True)
    st.link_button("Dhruv 🧑‍💻", DHRUV_LINKEDIN_URL, help="Connect with Dhruv on LinkedIn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---") # Separator before the main columns start
# ----------------------- END TOP RIGHT CREATOR LINKS -----------------------


# ----------------------- INPUT METHOD -----------------------
col_left, col_right = st.columns([1.2, 1])

with col_left:
    input_options = ["camera", "upload"]  # logical keys

    # Gold custom label for "Choose input method:"
    st.markdown(
        f"""
        <div class="gold-label">
            {L('choose_input')}
        </div>
        """,
        unsafe_allow_html=True
    )

    input_method = st.radio(
        "",
        input_options,
        horizontal=True,
        key="input_method",
        label_visibility="collapsed",
        format_func=lambda x: L("opt_camera") if x == "camera" else L("opt_upload"),
    )

    uploaded_image = None

    if input_method == "camera":
        # Gold animated label for "📸 Take a picture"
        st.markdown(
            f"""
            <div class="camera-gold">
                {L('camera_take_pic')}
            </div>
            """,
            unsafe_allow_html=True
        )
        uploaded_image = st.camera_input(
            "",
            key="camera_input_main",
            label_visibility="collapsed",
        )
    else:
        uploaded_file = st.file_uploader(L("upload_label"), type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            uploaded_image = uploaded_file

    detected_emotion = None
    detected_confidence = None

    # ----------------------- AUTO MODE (DeepFace) -----------------------
    if uploaded_image is not None and DEEPFACE_AVAILABLE:
        img = Image.open(uploaded_image)
        st.image(img, caption="Your Photo", use_column_width=True)

        img_np = np.array(img.convert("RGB"))

        with st.spinner(L("detect_spinner")):
            time.sleep(1.3)  # smooth animation
            detected_emotion, detected_confidence = detect_emotion(img_np)

    # show auto-detected songs
    if detected_emotion:
        emo_key = detected_emotion.lower()
        emo_icon = emotion_emoji.get(emo_key, "🎭")

        conf_str = ""
        if detected_confidence is not None:
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
        for idx, (name, url) in enumerate(songs):
            delay = idx * 0.15  # Stagger delay for each card
            # The CSS 'fadeInUp' animation is applied here via the style attribute
            st.markdown(
                f"""
                <div class="song-card" style="animation-delay: {delay}s;">
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
    # ----------------------- QUICK MOOD SHORTCUTS -----------------------
    st.markdown(f"### {L('quick_mood_title')}")
    st.markdown(
        f"<span class='hint-label'>{L('manual_hint')}</span>",
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
        for idx, (name, url) in enumerate(songs):
            delay = idx * 0.15 # Stagger delay for each card
            # The CSS 'fadeInUp' animation is applied here via the style attribute
            st.markdown(
                f"""
                <div class="song-card" style="animation-delay: {delay}s;">
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

# ----------------------- CLOSING MESSAGE (Thank You) -----------------------
st.markdown("---") # Add a separator before the final message
st.markdown(
    f"""
    <div class="closing-message">
        {L('closing_message')}
        <br><br>
        <span style="color: #ec4899; font-size: 1.5rem;">💖</span>
        <span style="color: #facc15; font-size: 1.5rem;">✨</span>
        <span style="color: #38bdf8; font-size: 1.5rem;">🎉</span>
    </div>
    """,
    unsafe_allow_html=True
)
