import requests
import serial
import streamlit as st
import streamlit.components.v1 as components
import time

# পৃষ্ঠা কনফিগারেশন
st.set_page_config(
    page_title="MUSHFIK'S HEALTH ASSISTANT AI", page_icon="🩺", layout="wide"
)

# সেশন স্টেট ইনিশিয়ালাইজেশন
if "users" not in st.session_state:
  st.session_state.users = {
      "mushfik": "1234"
  }  # ডিফল্ট টেস্ট একাউন্ট (ইউজারনেম: mushfik, পাসওয়ার্ড: 1234)
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "current_user" not in st.session_state:
  st.session_state.current_user = "Guest"
if "chat_histories" not in st.session_state:
  st.session_state.chat_histories = {"Guest": []}

GROQ_API_KEY = "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"


# Groq AI কল ফাংশন
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


# ব্রাউজারের মাধ্যমে পড়ে শোনানোর ফাংশন
def speak_response(text):
  clean_text = (
      text.replace("\n", " ")
      .replace('"', "'")
      .replace("`", "__")
      .replace("*", "")
  )
  html_code = f"""
    <script>
        function playSpeech() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance("{clean_text}");
                utterance.lang = 'bn-BD';
                utterance.rate = 0.95;
                window.speechSynthesis.speak(utterance);
            }}
        }}
        playSpeech();
    </script>
    """
  components.html(html_code, height=0)


# ----------------- সাইডবারের একদম উপরে লগইন / সাইন-আপ প্যানেল -----------------
st.sidebar.title("👤 ইউজার অ্যাকাউন্ট")

if not st.session_state.logged_in:
  with st.sidebar.expander("🔑 লগইন বা সাইন-আপ করুন", expanded=False):
    auth_tab1, auth_tab2 = st.tabs(["লগইন", "সাইন-আপ"])

    with auth_tab1:
      l_user = st.text_input("ইউজারনেম", key="l_user")
      l_pass = st.text_input("পাসওয়ার্ড", type="password", key="l_pass")
      if st.button("লগইন", use_container_width=True):
        if (
            l_user in st.session_state.users
            and st.session_state.users[l_user] == l_pass
        ):
          st.session_state.logged_in = True
          st.session_state.current_user = l_user
          if l_user not in st.session_state.chat_histories:
            st.session_state.chat_histories[l_user] = []
          st.success("সফলভাবে লগইন হয়েছে!")
          time.sleep(0.8)
          st.rerun()
        else:
          st.error("ভুল ইউজারনেম বা পাসওয়ার্ড!")

    with auth_tab2:
      s_user = st.text_input("নতুন ইউজারনেম", key="s_user")
      s_pass = st.text_input("নতুন পাসওয়ার্ড", type="password", key="s_pass")
      if st.button("একাউন্ট তৈরি", use_container_width=True):
        if s_user and s_pass:
          if s_user in st.session_state.users:
            st.warning("এই নাম আগেই আছে!")
          else:
            st.session_state.users[s_user] = s_pass
            st.session_state.logged_in = True
            st.session_state.current_user = s_user
            st.session_state.chat_histories[s_user] = []
            st.success("একাউন্ট তৈরি ও লগইন সফল!")
            time.sleep(0.8)
            st.rerun()
        else:
          st.error("সবগুলো ঘর পূরণ করুন!")
  st.sidebar.info(
      "💡 আপনি বর্তমানে **Guest** হিসেবে ব্যবহার করছেন। হিস্ট্রি সেভ রাখতে"
      " লগইন করতে পারেন।"
  )
else:
  st.sidebar.success(
      f"активных: **{st.session_state.current_user}** (লগইন করা)"
  )
  if st.sidebar.button("🚪 লগআউট", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.current_user = "Guest"
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Settings & Controls")

# ----------------- মূল অ্যাপ ইন্টারফেস -----------------
st.title("🩺 MUSHFIK'S HEALTH ASSISTANT AI")
st.write(
    "নবম শ্রেণীর বিজ্ঞান মেলার জন্য তৈরি একটি উদ্ভাবনী স্বাস্থ্যসেবা এআই প্রজেক্ট।"
)

# বর্তমান ইউজারের চ্যাট হিস্ট্রি নিশ্চিত করা
current_user = st.session_state.current_user
if current_user not in st.session_state.chat_histories:
  st.session_state.chat_histories[current_user] = []

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
        speak_response(response)
  if ser:
    ser.close()
else:
  st.warning(
      f"⚠️ সেন্সর পাওয়া যায়নি। (চ্যাট হিস্ট্রি মোড সক্রিয় - ব্যবহারকারী:"
      f" {current_user})"
  )

  # পুরোনো চ্যাট হিস্ট্রি রেন্ডার করা
  for message in st.session_state.chat_histories[current_user]:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input("আপনার স্বাস্থ্যগত সমস্যা বাংলায় লিখুন..."):
    with st.chat_message("user"):
      st.markdown(prompt)
    st.session_state.chat_histories[current_user].append(
        {"role": "user", "content": prompt}
    )

    with st.spinner("AI উত্তর ভাবছে..."):
      response = call_groq_ai(
          f"রোগীর প্রশ্ন: '{prompt}'। সহানুভূতিশীল ডাক্তারের মতো বিস্তারিত প্রাথমিক স্বাস্থ্য পরামর্শ দিন।"
      )

    with st.chat_message("assistant"):
      st.markdown(response)
      speak_response(response)

    st.session_state.chat_histories[current_user].append(
        {"role": "assistant", "content": response}
    )
