# Install packages before running:
# pip install streamlit openai rapidfuzz gTTS playsound==1.2.2

import streamlit as st
from rapidfuzz import fuzz
import openai
from gtts import gTTS
import os

# ---- Set OpenAI API key securely ----
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
    word_list = ", ".join([f"{w['japanese']} ({w['romaji']}) meaning {w['meaning']}" for w in cluster])
    prompt = (
        f"Create a short, funny, vivid story that helps someone memorize these Japanese words: {word_list}. "
        "Each word should appear in a memorable, visual, and playful way, like a scene in a memory palace. "
        "Make it exaggerated, easy to visualize, and fun."
    )
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

# ---- Prepare Memory Palace Dictionary ----
memory_palace = {}
for i, cluster in enumerate(clusters):
    location = locations[i % len(locations)]
    memory_palace[location] = {
        "words": cluster,
        "story": None
    }

# ---- Streamlit UI ----
st.title("Japanese Memory Palace")

# Select Palace Location
location = st.selectbox("Choose a Palace Location", list(memory_palace.keys()))

if st.button("Show Words & Story"):
    cluster = memory_palace[location]["words"]
    
    # Generate GPT story if not already done
    if memory_palace[location]["story"] is None:
        st.info("Generating story... (may take a few seconds)")
        memory_palace[location]["story"] = generate_gpt_story(cluster)

    st.subheader("Words in this location:")
    for word in cluster:
        st.write(f"{word['japanese']} ({word['romaji']}) - {word['meaning']}")
        
        # Optional: audio playback button
        if st.button(f"🔊 Play {word['japanese']}"):
            tts = gTTS(text=word['japanese'], lang='ja')
            filename = f"{word['romaji']}.mp3"
            tts.save(filename)
            os.system(f"start {filename}" if os.name=='nt' else f"afplay {filename}")  # Windows / Mac
            st.success(f"Playing {word['japanese']}")

    st.subheader("Memory Palace Story:")
    st.write(memory_palace[location]["story"])
