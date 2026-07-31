from gTTS import gTTS
import os
import requests
import serial
import streamlit as st
import time

# পৃষ্ঠা কনফিগারেশন
st.set_page_config(
    page_title="MUSHFIK'S HEALTH ASSISTANT AI", page_icon="🩺", layout="wide"
)

st.title("🩺 MUSHFIK'S HEALTH ASSISTANT AI (Voice & Sensor Pro)")
st.write(
    "নবম শ্রেণীর বিজ্ঞান মেলার জন্য তৈরি একটি উদ্ভাবনী ভয়েস ও সেন্সর ভিত্তিক"
    " স্বাস্থ্যসেবা এআই প্রজেক্ট।"
)

st.sidebar.header("⚙️ Settings & Controls")
GROQ_API_KEY = "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"


# Groq AI চ্যাট ফাংশন (Llama 3.3)
def call_groq_ai(prompt):
  if not GROQ_API_KEY:
    return "দুঃখিত, এআই সিস্টেম কনফিগার করা হয়নি।"
  url = "https://api.groq.com/openai/v1/chat/completions"
  headers = {
      "Authorization": f"Bearer {GROQ_API_KEY}",
      "Content-Type": "application/json",
  }
  data = {
      "model": "llama-3.3-70b-versatile",
      "messages": [
          {
              "role": "system",
              "content": (
                  "You are a professional, knowledgeable, and empathetic"
                  " medical assistant named 'MUSHFIK'S HEALTH ASSISTANT AI' for a"
                  " school science fair project in Bangladesh. Answer the user's"
                  " questions in natural, grammatically correct, and polite"
                  " Bengali. Give detailed, accurate, and helpful medical"
                  " guidance or general information related to their query."
                  " NEVER include emergency hospital phone numbers or"
                  " helplines unless specifically asked."
              ),
          },
          {"role": "user", "content": prompt},
      ],
      "temperature": 0.6,
  }
  try:
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
      return response.json()["choices"][0]["message"]["content"]
    else:
      return "এআই সার্ভার রেসপন্স করছে না। একটু পরে চেষ্টা করুন।"
  except Exception as e:
    return f"কানেকশন সমস্যা: {str(e)}"


# Groq Whisper API দিয়ে ভয়েস (অডিও) থেকে বাংলায় রূপান্তর করার ফাংশন
def transcribe_audio(audio_bytes):
  url = "https://api.groq.com/openai/v1/audio/transcriptions"
  headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
  files = {"file": ("audio.webm", audio_bytes, "audio/webm")}
  data = {"model": "whisper-large-v3", "language": "bn"}
  try:
    response = requests.post(url, headers=headers, files=files, data=data)
    if response.status_code == 200:
      return response.json().get("text", "")
    else:
      return None
  except Exception as e:
    return None


# টেক্সটকে ভয়েসে রূপান্তর করে বাজানোর ফাংশন
def speak_bengali(text):
  try:
    tts = gTTS(text=text, lang="bn", slow=False)
    audio_file = "temp_audio.mp3"
    tts.save(audio_file)
    st.audio(audio_file, format="audio/mp3", autoplay=True)
  except Exception as e:
    pass


# 🎤 আলাদা পপ-আপ ভয়েস চ্যাট ইন্টারফেস (Dialog)
@st.dialog("🎙️ এআই ভয়েস অ্যাসিস্ট্যান্ট ইন্টারফেস")
def voice_chat_modal():
  st.write(
      "মাইক্রোফোন আইকনে ক্লিক করে আপনার স্বাস্থ্যগত সমস্যা বা প্রশ্ন বাংলায়"
      " বলুন।"
  )

  # স্ট্রিমলিটের বিল্ট-ইন অডিও রেকর্ডার
  audio_value = st.audio_input("এখানে কথা রেকর্ড করুন:")

  if audio_value is not None:
    st.info("আপনার কথা প্রসেস করা হচ্ছে...")
    audio_bytes = audio_value.read()

    # Whisper দিয়ে কথাটিকে টেক্সটে রূপান্তর
    user_speech_text = transcribe_audio(audio_bytes)

    if user_speech_text:
      st.success(f"**আপনি বলেছেন:** {user_speech_text}")

      with st.spinner("এআই ডাক্তার উত্তর প্রস্তুত করছে..."):
        ai_response = call_groq_ai(user_speech_text)

      st.markdown(f"**এআই ডাক্তারের পরামর্শ:** {ai_response}")
      speak_bengali(ai_response)
    else:
      st.error(
          "দুঃখিত, আপনার কথাটি পরিষ্কার শোনা যায়নি। আবার স্পষ্টভাবে বলুন।"
      )


# মূল হোম স্ক্রিনে ভয়েস চ্যাট ওপেন করার বাটন
st.markdown("---")
col_v1, col_v2 = st.columns([3, 1])
with col_v1:
  st.info(
      "💡 আপনি চাইলে নিচের বোতামে ক্লিক করে সরাসরি মাইক্রোফোনে কথা বলে এআই-এর"
      " সাথে ভয়েস চ্যাট করতে পারেন!"
  )
with col_v2:
  if st.button("🎙️ ভয়েস চ্যাট শুরু করুন", use_container_width=True):
    voice_chat_modal()
st.markdown("---")

# সেন্সর বা চ্যাটবট মোড হ্যান্ডলিং
port = st.sidebar.selectbox(
    "Arduino Port সিলেক্ট করুন", ["COM3", "COM4", "COM5", "COM6", "/dev/ttyUSB0"]
)
arduino_connected = False
ser = None

try:
  ser = serial.Serial(port, 9600, timeout=1)
  arduino_connected = True
except:
  arduino_connected = False

if arduino_connected:
  st.success("✅ সেন্সর বুথ সংযুক্ত আছে! (সেন্সর মোড সক্রিয়)")
  col1, col2 = st.columns([1, 2])
  with col1:
    st.subheader("📊 লাইভ সেন্সর ডেটা")
    demo_mode = st.checkbox("ডেমো বা টেস্ট ডেটা ব্যবহার করুন", value=True)
    if demo_mode:
      temp = st.slider("শরীরের তাপমাত্রা (°F)", 96.0, 105.0, 98.6, 0.1)
      heart_rate = st.slider("হৃদস্পন্দন (BPM)", 50, 150, 75)
      spo2 = st.slider("অক্সিজেন মাত্রা (SpO2 %)", 80, 100, 98)
    else:
      temp, heart_rate, spo2 = 98.6, 75, 98
      if ser and ser.in_waiting > 0:
        try:
          line = ser.readline().decode("utf-8").strip()
          parts = line.split(",")
          if len(parts) == 3:
            temp, heart_rate, spo2 = (
                float(parts[0]),
                int(parts[1]),
                int(parts[2]),
            )
        except:
          pass
      st.metric(label="🌡️ তাপমাত্রা", value=f"{temp} °F")
      st.metric(label="💓 হার্ট রেট", value=f"{heart_rate} BPM")
      st.metric(label="🩸 SpO2", value=f"{spo2} %")
  with col2:
    st.subheader("🤖 AI স্বাস্থ্য বিশ্লেষণ")
    if st.button("📈 ডেটা এআই দ্বারা বিশ্লেষণ করুন"):
      with st.spinner("AI স্বাস্থ্য রিপোর্ট তৈরি করছে..."):
        prompt = f"একজন অভিজ্ঞ প্রবীণ ডাক্তারের মতো আচরণ করুন। রোগীর তাপমাত্রা: {temp} °F, হার্ট রেট: {heart_rate} bpm, SpO2: {spo2}%। বাংলায় একটি বিস্তারিত স্বাস্থ্য রিপোর্ট তৈরি করুন।"
        response = call_groq_ai(prompt)
        st.write(response)
        speak_bengali(response)
  if ser:
    ser.close()
else:
  st.warning("⚠️ সেন্সর পাওয়া যায়নি। (AI টেক্সট চ্যাটবট মোড সক্রিয়)")
  if "messages" not in st.session_state:
    st.session_state.messages = []
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input("আপনার স্বাস্থ্যগত সমস্যা বাংলায় লিখুন..."):
    with st.chat_message("user"):
      st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("AI উত্তর ভাবছে..."):
      response = call_groq_ai(
          f"রোগীর প্রশ্ন: '{prompt}'। সহানুভূতিশীল ডাক্তারের মতো বিস্তারিত প্রাথমিক স্বাস্থ্য পরামর্শ দিন।"
      )

    with st.chat_message("assistant"):
      st.markdown(response)
      speak_bengali(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
      
