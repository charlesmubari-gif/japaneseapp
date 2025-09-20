# Install packages before running:
# pip install streamlit openai rapidfuzz gTTS --quiet

import streamlit as st
from rapidfuzz import fuzz
import openai
from gtts import gTTS
from io import BytesIO
import os

# ---- OpenAI API key handling ----
# Try Streamlit secrets first, fallback to environment variable
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

if not openai.api_key:
    st.error("OpenAI API key not found! Set it in .streamlit/secrets.toml or as an environment variable.")
    st.stop()

# ---- Sample Words (Hiragana + Romaji + Meaning) ----
words = [
    {"japanese": "ねこ", "meaning": "cat", "romaji": "neko"},
    {"japanese": "ねこ", "meaning": "sleeping child", "romaji": "neko"},
    {"japanese": "いぬ", "meaning": "dog", "romaji": "inu"},
    {"japanese": "さる", "meaning": "monkey", "romaji": "saru"},
    {"japanese": "さかな", "meaning": "fish", "romaji": "sakana"},
    {"japanese": "とり", "meaning": "bird", "romaji": "tori"},
    {"japanese": "はな", "meaning": "flower", "romaji": "hana"},
    {"japanese": "はな", "meaning": "nose", "romaji": "hana"},
    {"japanese": "ひ", "meaning": "fire", "romaji": "hi"},
    {"japanese": "こおり", "meaning": "ice", "romaji": "koori"}
]

# ---- Phonetic Clustering ----
clusters = []
remaining = words.copy()
while remaining:
    base = remaining.pop(0)
    cluster = [base]
    to_remove = []
    for other in remaining:
        if fuzz.ratio(base['romaji'], other['romaji']) >= 70:
            cluster.append(other)
            to_remove.append(other)
    for r in to_remove:
        remaining.remove(r)
    clusters.append(cluster)

# ---- Memory Palace Locations ----
locations = ["Front Door", "Living Room", "Kitchen", "Bedroom", "Garden", "Balcony"]

# ---- GPT Story Generator ----
def generate_gpt_story(cluster):
    # Fixed f-string syntax
    word_list = ", ".join([f"{w['japanese']} ({w['romaji']}) meaning {w['meaning']}" for w in cluster])
    prompt = (
        f"Create a short, funny, vivid story that helps someone memorize these Japanese words: {word_list}. "
        "Each word should appear in a memorable, visual, and playful way, like a scene in a memory palace. "
        "Make it exaggerated
