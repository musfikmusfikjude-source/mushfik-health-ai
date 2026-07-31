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

st.title("🩺 MUSHFIK'S HEALTH ASSISTANT AI")
st.write(
    "নবম শ্রেণীর বিজ্ঞান মেলার জন্য তৈরি একটি উদ্ভাবনী স্বাস্থ্যসেবা এআই প্রজেক্ট।"
)

st.sidebar.header("⚙️ Settings & Controls")
GROQ_API_KEY = "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"


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


# গুগল ভয়েস দিয়ে বাংলায় অডিও তৈরি করে বাজানোর ফাংশন
def speak_bengali(text):
  try:
    tts = gTTS(text=text, lang="bn", slow=False)
    audio_file = "temp_audio.mp3"
    tts.save(audio_file)
    st.audio(audio_file, format="audio/mp3", autoplay=True)
  except Exception as e:
    st.error(f"ভয়েস জেনারেট করতে সমস্যা হচ্ছে: {e}")


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
    st.subheader("🤖 AI স্বাস্থ্য বিশ্লেষণ ও ভয়েস আউটপুট")
    if st.button("📈 ডেটা এআই দ্বারা বিশ্লেষণ করুন"):
      with st.spinner("AI স্বাস্থ্য রিপোর্ট তৈরি করছে এবং ভয়েস প্রস্তুত হচ্ছে..."):
        prompt = f"একজন অভিজ্ঞ প্রবীণ ডাক্তারের মতো আচরণ করুন। রোগীর তাপমাত্রা: {temp} °F, হার্ট রেট: {heart_rate} bpm, SpO2: {spo2}%। বাংলায় একটি বিস্তারিত স্বাস্থ্য রিপোর্ট তৈরি করুন।"
        response = call_groq_ai(prompt)
        st.write(response)
        speak_bengali(response)
  if ser:
    ser.close()
else:
  st.warning("⚠️ সেন্সর পাওয়া যায়নি। (AI চ্যাটবট ও ভয়েস রিডিং মোড সক্রিয়)")
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
