# Install packages before running:
# pip install streamlit openai rapidfuzz gTTS --quiet

import streamlit as st
from rapidfuzz import fuzz
import openai
from gtts import gTTS
from io import BytesIO

# ---- OpenAI API key from Streamlit secrets ----
openai.api_key = st.secrets["OPENAI_API_KEY"]

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
    word_list = ", ".join([f]()_
