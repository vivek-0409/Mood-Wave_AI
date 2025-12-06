import streamlit as st
from PIL import Image
import numpy as np

# -------------------------------------------------------------
# Try importing DeepFace safely (so Cloud પર crash ના થાય)
# -------------------------------------------------------------
DEEPFACE_AVAILABLE = True
DEEPFACE_ERROR = None

try:
    from deepface import DeepFace
except Exception as e:
    DEEPFACE_AVAILABLE = False
    DEEPFACE_ERROR = str(e)

# -------------------------------------------------------------
# Streamlit Page Config
# -------------------------------------------------------------
st.set_page_config(
    page_title="MoodWave AI",
    page_icon="🎭",
    layout="wide"
)

# -------------------------------------------------------------
# Custom CSS – Gradient BG, Animations, Cards, Hover Effects
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

    /* Animated gradient background */
    body {
        background: linear-gradient(120deg, #1e293b, #0f172a, #020617);
        background-size: 300% 300%;
        animation: gradientMove 12s ease infinite;
    }

    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
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

    /* 🔴 HEADER CARD – rectangle remove: make it transparent & flat */
    .glass-soft {
        background: transparent;
        border-radius: 0;
        padding: 0;
        border: none;
        box-shadow: none;
        backdrop-filter: none;
    }

    .subtitle {
        font-size: 0.95rem;
        color: #e5e7eb;
        opacity: 0.85;
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
        f
