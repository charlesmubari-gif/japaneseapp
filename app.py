# Install packages before running:
# pip install streamlit openai rapidfuzz gTTS --quiet

import streamlit as st
from rapidfuzz import fuzz
import openai
from gtts import gTTS
from io import BytesIO
import os

# ---- OpenAI API key handling ----
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
    word_list = ", ".join([f"{w['japanese']} ({w['romaji']}) meaning {w['meaning']}" for w in cluster])
    prompt = f"""Create a short, funny, vivid story that helps someone memorize these Japanese words: {word_list}.
Each word should appear in a memorable, visual, and playful way, like a scene in a memory palace.
Make it exaggerated, easy to visualize, and fun."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=300
        )
        story = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        story = f"[Error generating story: {e}]"
    return story

# ---- Prepare Memory Palace ----
memory_palace = {}
for i, cluster in enumerate(clusters):
    location = locations[i % len(locations)]
    memory_palace[location] = {"words": cluster, "story": None}

# ---- Streamlit UI ----
st.title("Japanese Memory Palace")

# Select Palace Location
location = st.selectbox("Choose a Palace Location", list(memory_palace.keys()))

if st.button("Show Words & Story"):
    cluster = memory_palace[location]["words"]
    
    # Generate GPT story if not done
    if memory_palace[location]["story"] is None:
        st.info("Generating story... (may take a few seconds)")
        memory_palace[location]["story"] = generate_gpt_story(cluster)

    st.subheader("Words in this location:")
    for idx, word in enumerate(cluster):
        st.write(f"{word['japanese']} ({word['romaji']}) - {word['meaning']}")

        # ---- Audio playback (fixed) ----
        tts = gTTS(text=word['japanese'], lang='ja')
        audio_bytes_io = BytesIO()
        tts.write_to_fp(audio_bytes_io)
        audio_bytes = audio_bytes_io.getvalue()  # convert BytesIO to bytes
        st.audio(audio_bytes, format='audio/mp3', start_time=0, key=f"audio_{location}_{idx}")

    st.subheader("Memory Palace Story:")
    st.write(memory_palace[location]["story"])
