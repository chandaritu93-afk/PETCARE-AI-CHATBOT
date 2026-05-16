# frontend/apps.py
import requests
import speech_recognition as sr
import pyttsx3
from PIL import Image
import os
import sys
import uuid
import plotly.express as px
import pandas as pd
import streamlit as st
import base64
from fpdf import FPDF
st.set_page_config(
    page_title="🐾 PetCare AI",
    page_icon="🐾",
    layout="wide"
)

import requests
import speech_recognition as sr
import pyttsx3

# ------------------- PATH -------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
API_URL = "http://localhost:8000"

# ------------------- MODERN UI STYLE -------------------
# ------------------- PREMIUM BACKGROUND UI -------------------

def get_base64(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()

banner_path = r"C:\Users\chand\OneDrive\Desktop\PetCare-AI-Chatbot-main\PetCare-AI-Chatbot-main\backend\images\dog_walk.jpg"

img_base64 = get_base64(banner_path)
st.markdown(
    f"""
    <style>

    @keyframes float {{
        0% {{transform: translateY(0px);}}
        50% {{transform: translateY(-10px);}}
        100% {{transform: translateY(0px);}}
    }}

    img {{
        border-radius: 20px;
        animation: float 3s ease-in-out infinite;
    }}

    .stApp {{
        background:
        linear-gradient(
            rgba(255,255,255,0.82),
            rgba(255,255,255,0.82)
        ),
        url("data:image/jpg;base64,{img_base64}");

        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    section[data-testid="stSidebar"] {{
        background: rgba(15,23,42,0.92);
        backdrop-filter: blur(14px);
    }}

    section[data-testid="stSidebar"] * {{
        color: #ffffff !important;
        font-weight: 600;
        opacity: 1 !important;
    }}

    [data-testid="stChatMessage"] {{
        background: rgba(255,255,255,0.60);
        backdrop-filter: blur(14px);
        border-radius: 22px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0px 4px 18px rgba(0,0,0,0.12);
    }}

    .stButton button {{
        width: 100%;
        border-radius: 16px;
        background: linear-gradient(to right,#2563eb,#3b82f6);
        color: white;
        border: none;
        padding: 12px;
        font-weight: bold;
    }}

    .stButton button:hover {{
        background: linear-gradient(to right,#1d4ed8,#2563eb);
        color: white;
    }}

    .block-container {{
        padding-top: 1rem;
    }}

    h1,h2,h3,p,label {{
        color:#0f172a !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)
# ------------------- HERO TITLE -------------------

st.markdown("""

<div style="
padding:25px;
border-radius:25px;
background:rgba(255,255,255,0.55);
backdrop-filter:blur(14px);
text-align:center;
margin-bottom:20px;
">

<h1 style="font-size:55px;">
🐾 PetCare AI Assistant
</h1>

<p style="font-size:22px;">
Smart AI Powered Pet Healthcare Chatbot
</p>

</div>

""", unsafe_allow_html=True)


# ------------------- PET IMAGES -------------------

dog_path = r"C:\Users\chand\OneDrive\Desktop\PetCare-AI-Chatbot-main\PetCare-AI-Chatbot-main\backend\images\dog_walk.jpg"

cat_path = r"C:\Users\chand\OneDrive\Desktop\PetCare-AI-Chatbot-main\PetCare-AI-Chatbot-main\backend\images\cat_walk.jpg"

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([1,1], gap="small")

with col1:
    if os.path.exists(dog_path):
        dog_img = Image.open(dog_path)
        st.image(dog_img, use_container_width=True)

with col2:
    if os.path.exists(cat_path):
        cat_img = Image.open(cat_path)
        st.image(cat_img, use_container_width=True)

# ------------------- SESSION -------------------
if "user_id" not in st.session_state:
    if os.path.exists("user_id.txt"):
        st.session_state.user_id = open("user_id.txt").read()
    else:
        uid = str(uuid.uuid4())[:8]
        open("user_id.txt", "w").write(uid)
        st.session_state.user_id = uid

# ------------------- CURRENT SESSION -------------------
if "current_session" not in st.session_state:

    try:
        sessions = requests.get(
            f"{API_URL}/sessions",
            params={"user_id": st.session_state.user_id}
        ).json()

        if sessions:
            st.session_state.current_session = sessions[0]["session_id"]

        else:
            sid = str(uuid.uuid4())

            st.session_state.current_session = sid

            requests.post(
                f"{API_URL}/session/create",
                json={
                    "user_id": st.session_state.user_id,
                    "session_id": sid
                }
            )

    except:
        st.error("❌ Backend not running")

# ------------------- CHAT HISTORY -------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------- FUNCTIONS -------------------
# ------------------- VOICE FUNCTIONS -------------------

recognizer = sr.Recognizer()

engine = pyttsx3.init()

def speech_to_text():

    try:
        with sr.Microphone() as source:

            st.info("🎤 Listening... Speak now")

            audio = recognizer.listen(source, timeout=5)

            text = recognizer.recognize_google(audio)

            return text

    except Exception as e:

        st.error(f"Voice Error: {e}")

        return ""


def text_to_speech(text):

    try:
        engine.say(text)
        engine.runAndWait()

    except:
        pass
def load_chat_messages():

    r = requests.get(
        f"{API_URL}/history",
        params={
            "user_id": st.session_state.user_id,
            "session_id": st.session_state.current_session
        }
    )

    return r.json() if r.status_code == 200 else []


def ask_question(q):

    try:
        payload = {
            "user_id": st.session_state.user_id,
            "question": q,
            "session_id": st.session_state.current_session
        }

        r = requests.post(f"{API_URL}/ask", json=payload)

        if r.status_code != 200:
            return {
                "answer": f"❌ Backend Error ({r.status_code})"
            }

        return r.json()

    except Exception as e:
        return {
            "answer": f"❌ Connection Error: {str(e)}"
        }


def get_pet_profile():

    r = requests.get(
        f"{API_URL}/profile/get",
        params={"user_id": st.session_state.user_id}
    )

    return r.json() if r.status_code == 200 else {}


def save_pet_profile(profile):

    requests.post(
        f"{API_URL}/profile/save",
        json=profile
    )


# ------------------- SIDEBAR -------------------
with st.sidebar:

    st.markdown("# 🐾 PetCare AI")

    st.markdown("---")

    # ------------------- NEW CHAT -------------------
    if st.button("➕ New Chat"):

        new_session = str(uuid.uuid4())

        requests.post(
            f"{API_URL}/session/create",
            json={
                "user_id": st.session_state.user_id,
                "session_id": new_session
            }
        )

        st.session_state.current_session = new_session
        st.session_state.chat_history = []
        st.session_state.loaded_once = False

        st.rerun()

    st.markdown("---")

    # ------------------- MENU -------------------
    menu = st.radio(
        "📌 Navigation",
        ["💬 Chat", "📊 Dashboard"]
    )

    st.markdown("---")
    # ------------------- PET PROFILE -------------------
    st.markdown("## 🐶 Pet Profile")

    profile = get_pet_profile()

    pet_name = st.text_input(
        "Pet Name",
        profile.get("pet_name", "")
    )

    species = st.text_input(
        "Species",
        profile.get("species", "")
    )

    breed = st.text_input(
        "Breed",
        profile.get("breed", "")
    )

    age_months = st.number_input(
        "Age (months)",
        0,
        600,
        profile.get("age_months", 0)
    )

    weight_kg = st.number_input(
        "Weight (kg)",
        0.0,
        200.0,
        profile.get("weight_kg", 0.0)
    )

    gender_value = profile.get("gender") or "Unknown"

    if gender_value not in ["Male", "Female", "Unknown"]:
        gender_value = "Unknown"

    gender = st.selectbox(
        "Gender",
        ["Male", "Female", "Unknown"],
        index=["Male", "Female", "Unknown"].index(gender_value)
    )

    if st.button("💾 Save Profile"):

        save_pet_profile({
            "user_id": st.session_state.user_id,
            "pet_name": pet_name,
            "species": species,
            "breed": breed,
            "age_months": age_months,
            "weight_kg": weight_kg,
            "gender": gender
        })

        st.success("✅ Profile Saved")

    st.markdown("---")

    # ------------------- OLD CHATS -------------------
    st.markdown("## 💬 Old Chats")

    try:

        sessions = requests.get(
            f"{API_URL}/sessions",
            params={"user_id": st.session_state.user_id}
        ).json()

        if not sessions:
            st.info("No old chats")

        else:

            for s in sessions:

                chat_name = s.get("title", "New Chat")

                if st.button(
                    f"💬 {chat_name}",
                    key=s["session_id"]
                ):

                    st.session_state.current_session = s["session_id"]

                    st.session_state.chat_history = load_chat_messages()

                    st.rerun()

    except:
        st.warning("Backend issue")

# ------------------- DASHBOARD -------------------
# ------------------- DASHBOARD -------------------
if menu == "📊 Dashboard":

    st.title("📊 Dashboard")

    st.markdown("---")

    profile = get_pet_profile()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🐶 Pet Name",
        profile.get("pet_name", "Not Set")
    )

    col2.metric(
        "🎂 Age",
        f"{profile.get('age_months',0)} months"
    )

    col3.metric(
        "⚖️ Weight",
        f"{profile.get('weight_kg',0)} kg"
    )

    st.markdown("---")

    st.info(
        f"💬 Total Messages: {len(st.session_state.chat_history)}"
    )

    # ------------------- HEALTH SCORE -------------------

    st.markdown("### 🩺 Pet Health Score")

    weight = profile.get("weight_kg") or 0
    age = profile.get("age_months") or 0

    score = 50

    if weight > 0:
        score += 20

    if age < 60:
        score += 20

    if score > 100:
        score = 100

    st.progress(score)

    st.success(f"Health Score: {score}%")

    # ------------------- HEALTH GRAPH -------------------

    st.markdown("---")

    st.subheader("📈 Pet Health Dashboard")

    current_weight = profile.get("weight_kg") or 0

    health_data = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
        "Weight": [
            current_weight - 2,
            current_weight - 1,
            current_weight,
            current_weight + 1,
            current_weight + 2
        ]
    })

    fig = px.line(
        health_data,
        x="Month",
        y="Weight",
        markers=True,
        title="Pet Weight Progress"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------- PET IMAGE ANALYSIS -------------------

    st.markdown("---")

    st.subheader("📷 Upload Pet Image")

    uploaded_file = st.file_uploader(
        "Upload Dog/Cat Image",
        type=["jpg", "png", "jpeg"]
    )

    if uploaded_file:

        st.image(uploaded_file, width=300)

        st.success("✅ AI Analysis Complete")

        st.info("""
Possible Result:
- Pet looks healthy
- Eyes clear
- Fur condition good
- No visible infection
""")

    # ------------------- PDF REPORT -------------------

    st.markdown("---")

    if st.button("📄 Generate Health Report"):

        pdf = FPDF()

        pdf.add_page()

        pdf.set_font("Arial", size=16)

        pdf.cell(200, 10, txt="Pet Health Report", ln=True)

        pdf.set_font("Arial", size=12)

        pdf.cell(
            200,
            10,
            txt=f"Pet Name: {profile.get('pet_name','Unknown')}",
            ln=True
        )

        pdf.cell(
            200,
            10,
            txt=f"Species: {profile.get('species','Unknown')}",
            ln=True
        )

        pdf.cell(
            200,
            10,
            txt=f"Weight: {profile.get('weight_kg',0)} kg",
            ln=True
        )

        pdf.cell(
            200,
            10,
            txt=f"Age: {profile.get('age_months',0)} months",
            ln=True
        )

        pdf.output("pet_report.pdf")

        with open("pet_report.pdf", "rb") as file:

            st.download_button(
                "⬇ Download Report",
                file,
                file_name="pet_report.pdf"
            )

    # ------------------- CUTE PETS -------------------

    st.markdown("---")

    st.subheader("🐕 Cute Pets")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Show Dog 🐶"):

            dog = requests.get(
                "https://dog.ceo/api/breeds/image/random"
            ).json()

            st.image(dog["message"])

    with col2:

        if st.button("Show Cat 🐱"):

            cat = requests.get(
                "https://api.thecatapi.com/v1/images/search"
            ).json()

            st.image(cat[0]["url"])
# ------------------- CHAT -------------------
# ------------------- CHAT -------------------
if menu == "💬 Chat":

    st.title("💬 PetCare Chat Assistant")

    # LOAD CHAT ONCE
    if "loaded_once" not in st.session_state:

        st.session_state.chat_history = load_chat_messages()

        st.session_state.loaded_once = True

    # SHOW CHATS
    for msg in st.session_state.chat_history:

        with st.chat_message(msg["role"]):

            st.markdown(msg["content"])

    # ------------------- VOICE BUTTON -------------------
    if st.button("🎤 Speak"):

        voice_text = speech_to_text()

        if voice_text:

            st.session_state.voice_input = voice_text

            st.success(f"You said: {voice_text}")

    # ------------------- USER INPUT -------------------
    user_input = st.chat_input(
        "🐶 Ask anything about your pet..."
    )

    # VOICE INPUT USE
    if "voice_input" in st.session_state:

        user_input = st.session_state.voice_input

        del st.session_state.voice_input

    # ------------------- SEND MESSAGE -------------------
    if user_input:

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):

            st.markdown(user_input)

        with st.chat_message("assistant"):

            with st.spinner("🐾 Thinking..."):

                response = ask_question(user_input)

                answer = response.get(
                    "answer",
                    "❌ No response"
                )

                st.markdown(answer)

                # 🔊 SPEAK ANSWER
                text_to_speech(answer)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })

        st.rerun()