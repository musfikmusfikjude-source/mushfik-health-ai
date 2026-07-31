import requests
import serial
import streamlit as st
import time

# পৃষ্ঠা কনফিগারেশন
st.set_page_config(
    page_title="MUSHFIK'S HEALTH ASSISTANT AI", page_icon="🩺", layout="wide"
)

# 🌟 ওপেনিং অ্যানিমেশন বা স্প্ল্যাশ স্ক্রিন
if "loaded" not in st.session_state:
  st.session_state.loaded = False

if not st.session_state.loaded:
  splash_html = """
    <div id="splash-screen" style="
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1a365d);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 999999;
        color: white;
        font-family: sans-serif;
        transition: opacity 0.8s ease;
    ">
        <div style="font-size: 60px; animation: pulse 1.2s infinite ease-in-out;">🩺</div>
        <h1 style="margin-top: 20px; letter-spacing: 2px; color: #ffffff; text-align: center;">MUSHFIK'S HEALTH ASSISTANT AI</h1>
        <p style="color: #00ffcc; font-size: 18px; margin-top: 10px; font-weight: bold;">সিস্টেম লোড হচ্ছে, একটু অপেক্ষা করুন...</p>
    </div>
    
    <style>
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes pulse {
        0% { transform: scale(0.9); opacity: 0.7; }
        50% { transform: scale(1.15); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.7; }
    }
    </style>
    
    <script>
        setTimeout(function() {
            var splash = document.getElementById('splash-screen');
            if(splash) {
                splash.style.opacity = '0';
                setTimeout(function() { splash.style.display = 'none'; }, 800);
            }
        }, 2200);
    </script>
    """
  st.components.v1.html(splash_html, height=0)
  st.session_state.loaded = True

# 🌟 ডায়নামিক হেলথ ব্যাকগ্রাউন্ড এবং কাস্টম স্টাইল CSS
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1a365d);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    h1, h2, h3, h4, h5, h6, p, label {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: rgba(15, 32, 39, 0.9) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# সেশন স্টেট ইনিশিয়ালাইজেশন
if "users" not in st.session_state:
  st.session_state.users = {"mushfik": "1234"}
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "current_user" not in st.session_state:
  st.session_state.current_user = "Guest"
if "chat_histories" not in st.session_state:
  st.session_state.chat_histories = {"Guest": []}

GROQ_API_KEY = "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"


# 🌟 নিখুঁত কনটেক্সট ট্র্যাকিং সহ Groq AI কল ফাংশন
def call_groq_ai(chat_history):
  if not GROQ_API_KEY:
    return "দুঃখিত, এআই সিস্টেম কনফিগার করা হয়নি।"
  url = "https://api.groq.com/openai/v1/chat/completions"
  headers = {
      "Authorization": f"Bearer {GROQ_API_KEY}",
      "Content-Type": "application/json",
  }

  messages = [{
      "role": "system",
      "content": (
          "You are a professional, knowledgeable, and empathetic medical"
          " assistant named 'MUSHFIK'S HEALTH ASSISTANT AI' for a school science"
          " fair project in Bangladesh. "
          "CRITICAL RULE 1: Always reply strictly in proper, correct, and formal"
          " Bengali script (বাংলা হরফে), no matter what language or script the"
          " user writes in. "
          "CRITICAL RULE 2: You MUST carefully read, remember, and connect the"
          " entire conversation history. If the user asks a follow-up question"
          " (such as asking about taking medicine like Napa), you must"
          " explicitly link it to the symptoms, pain, or issues they mentioned"
          " earlier in the conversation and answer accordingly. Never forget"
          " prior context. "
          "CRITICAL RULE 3: NEVER include emergency hospital phone numbers or"
          " helplines unless specifically asked."
      ),
  }]

  for msg in chat_history:
    messages.append({"role": msg["role"], "content": msg["content"]})

  data = {
      "model": "llama-3.3-70b-versatile",
      "messages": messages,
      "temperature": 0.5,
  }
  try:
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
      return response.json()["choices"][0]["message"]["content"]
    else:
      return "এআই সার্ভার রেসপন্স করছে না। একটু পরে চেষ্টা করুন।"
  except Exception as e:
    return f"কানেকশন সমস্যা: {str(e)}"


# ----------------- সাইডবারের লগইন / সাইন-আপ প্যানেল -----------------
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
  st.sidebar.info("💡 বর্তমানে Guest মোডে আছেন। হিস্ট্রি সেভ রাখতে লগইন করুন।")
else:
  st.sidebar.success(f"👤 ইউজার: **{st.session_state.current_user}**")
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
    st.subheader("📊 লাইভ সেন্সর ডেটা (DHT11/Sensor)")
    demo_mode = st.checkbox("ডেমো বা টেস্ট ডেটা ব্যবহার করুন", value=True)
    if demo_mode:
      temp = st.slider("শরীরের/রুমের তাপমাত্রা (°F)", 96.0, 105.0, 98.6, 0.1)
      heart_rate = st.slider("হৃদস্পন্দন / আর্দ্রতা", 50, 150, 75)
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
                float(parts[1]),
                float(parts[2]),
            )
        except:
          pass
      st.metric(label="🌡️ তাপমাত্রা", value=f"{temp} °F")
      st.metric(label="💓 হার্ট রেট/আর্দ্রতা", value=f"{heart_rate}")
      st.metric(label="🩸 SpO2", value=f"{spo2} %")
  with col2:
    st.subheader("🤖 AI স্বাস্থ্য বিশ্লেষণ")
    if st.button("📈 ডেটা এআই দ্বারা বিশ্লেষণ করুন"):
      with st.spinner("AI স্বাস্থ্য রিপোর্ট তৈরি করছে..."):
        sensor_prompt = f"রোগীর তাপমাত্রা: {temp} °F, মান ২: {heart_rate}, SpO2: {spo2}%। বাংলায় একটি বিস্তারিত স্বাস্থ্য রিপোর্ট তৈরি করুন।"
        temp_history = st.session_state.chat_histories[current_user] + [{
            "role": "user",
            "content": sensor_prompt,
        }]
        response = call_groq_ai(temp_history)
        st.write(response)
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
      response = call_groq_ai(st.session_state.chat_histories[current_user])

    with st.chat_message("assistant"):
      st.markdown(response)

    st.session_state.chat_histories[current_user].append(
        {"role": "assistant", "content": response}
    )
