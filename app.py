import requests
import serial
import streamlit as st
import time

# পৃষ্ঠা কনফিগারেশন
st.set_page_config(
    page_title="MUSHFIK'S HEALTH ASSISTANT AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 🌟 প্রিমিয়াম স্প্ল্যাশ স্ক্রিন
if "loaded" not in st.session_state:
  st.session_state.loaded = False

if not st.session_state.loaded:
  splash_html = """
    <div id="splash-screen" style="
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: #0b132b;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 999999;
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        transition: opacity 0.8s ease;
    ">
        <div style="font-size: 70px; animation: pulse 1.5s infinite ease-in-out;">🩺</div>
        <h1 style="margin-top: 20px; letter-spacing: 2px; color: #00f5d4; font-weight: 700;">MUSHFIK'S HEALTH ASSISTANT AI</h1>
        <p style="color: #94a3b8; font-size: 16px; margin-top: 10px; font-weight: 500;">অ্যাডভান্সড মেডিক্যাল সিস্টেম লোড হচ্ছে...</p>
    </div>
    
    <style>
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.7; }
        50% { transform: scale(1.08); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.7; }
    }
    </style>
    
    <script>
        setTimeout(function() {
            var splash = document.getElementById('splash-screen');
            if(splash) {
                splash.style.opacity = '0';
                setTimeout(function() { splash.style.display = 'none'; }, 800);
            }
        }, 1800);
    </script>
    """
  st.components.v1.html(splash_html, height=0)
  st.session_state.loaded = True

# 🌟 অ্যাডভান্সড মডার্ন কাস্টম CSS (UI উন্নত করার জন্য)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b132b;
        color: #f1f5f9;
        font-family: 'Segoe UI', sans-serif;
    }

    /* হেডার ও টেক্সট ডিজাইন */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* সাইডবার ডিজাইন */
    [data-testid="stSidebar"] {
        background-color: #1c2541 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* প্রিমিয়াম বাটন */
    .stButton>button {
        background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0, 180, 216, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0096c7 0%, #03045e 100%);
        box-shadow: 0 0 20px rgba(0, 180, 216, 0.6);
        transform: translateY(-2px);
    }

    /* চ্যাট মেসেজ বক্স গ্লাস ডিজাইন */
    [data-testid="stChatMessage"] {
        background-color: #1c2541 !important;
        border-radius: 15px !important;
        border: 1px solid rgba(0, 180, 216, 0.2) !important;
        padding: 15px !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }

    /* ইনপুট বক্স */
    .stTextInput>div>div>input {
        background-color: #1c2541 !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0, 180, 216, 0.3) !important;
    }
    
    /* কাস্টম কার্ড ডিজাইন */
    .custom-card {
        background: #1c2541;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(0, 180, 216, 0.25);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
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
          " user writes in (including Banglish). "
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


# ----------------- সাইডবারের আধুনিক প্যানেল -----------------
st.sidebar.markdown(
    "<h2 style='text-align: center; color: #00f5d4;'>🩺 কন্ট্রোল প্যানেল</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

# ইউজার অ্যাকাউন্ট সেকশন
if not st.session_state.logged_in:
  with st.sidebar.expander("🔑 ইউজার লগইন / সাইন-আপ", expanded=False):
    auth_tab1, auth_tab2 = st.tabs(["লগইন", "সাইন-আপ"])

    with auth_tab1:
      l_user = st.text_input("ইউজারনেম", key="l_user")
      l_pass = st.text_input("পাসওয়ার্ড", type="password", key="l_pass")
      if st.button("লগইন করুন", use_container_width=True):
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
      if st.button("একাউন্ট তৈরি করুন", use_container_width=True):
        if s_user and s_pass:
          if s_user in st.session_state.users:
            st.warning("এই নাম আগেই আছে!")
          else:
            st.session_state.users[s_user] = s_pass
            st.session_state.logged_in = True
            st.session_state.current_user = s_user
            st.session_state.chat_histories[s_user] = []
            st.success("একাউন্ট তৈরি সফল!")
            time.sleep(0.8)
            st.rerun()
        else:
          st.error("সবগুলো ঘর পূরণ করুন!")
  st.sidebar.info("💡 বর্তমান মোড: **Guest**")
else:
  st.sidebar.success(f"👤 ইউজার: **{st.session_state.current_user}**")
  if st.sidebar.button("🚪 লগআউট", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.current_user = "Guest"
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ হার্ডওয়্যার ও সেটিংস")
port = st.sidebar.selectbox(
    "Arduino Port সিলেক্ট করুন", ["COM3", "COM4", "COM5", "COM6", "/dev/ttyUSB0"]
)

# চ্যাট ক্লিয়ার করার বাটন
st.sidebar.markdown("---")
current_user = st.session_state.current_user
if current_user not in st.session_state.chat_histories:
  st.session_state.chat_histories[current_user] = []

if st.sidebar.button(
    "🗑️ বর্তমান চ্যাট মুছুন (Clear Chat)", use_container_width=True
):
  st.session_state.chat_histories[current_user] = []
  st.rerun()

# ----------------- মূল অ্যাপ ইন্টারফেস (মডার্ন হেডার) -----------------
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%); padding: 30px; border-radius: 20px; border: 1px solid rgba(0, 180, 216, 0.3); text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.4);">
        <h1 style="color: #00f5d4 !important; font-size: 38px; margin-bottom: 10px;">🩺 MUSHFIK'S HEALTH ASSISTANT AI</h1>
        <p style="color: #94a3b8; font-size: 18px; margin: 0;">নবম শ্রেণীর বিজ্ঞান মেলার জন্য তৈরি একটি অ্যাডভান্সড এবং ইন্টেলিজেন্ট মেডিকেল এআই প্রজেক্ট।</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# সেন্সর কানেকশন চেক
arduino_connected = False
ser = None
try:
  ser = serial.Serial(port, 9600, timeout=1)
  arduino_connected = True
except:
  arduino_connected = False

if arduino_connected:
  st.success("✅ সেন্সর বুথ সফলভাবে সংযুক্ত আছে!")
  col1, col2 = st.columns([1, 2], gap="large")
  with col1:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.subheader("📊 লাইভ সেন্সর ডেটা")
    demo_mode = st.checkbox("ডেমো টেস্ট মোড", value=True)
    if demo_mode:
      temp = st.slider("শরীরের তাপমাত্রা (°F)", 96.0, 105.0, 98.6, 0.1)
      heart_rate = st.slider("হৃদস্পন্দন / হার্ট রেট", 50, 150, 75)
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
      st.metric(label="💓 হার্ট রেট", value=f"{heart_rate}")
      st.metric(label="🩸 SpO2", value=f"{spo2} %")
    st.markdown("</div>", unsafe_allow_html=True)

  with col2:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.subheader("🤖 এআই স্বাস্থ্য বিশ্লেষণ রিপোর্ট")
    if st.button(
        "📈 সেন্সর ডেটা এআই দ্বারা বিশ্লেষণ করুন", use_container_width=True
    ):
      with st.spinner("AI স্বাস্থ্য রিপোর্ট তৈরি করছে..."):
        sensor_prompt = f"রোগীর তাপমাত্রা: {temp} °F, হার্ট রেট: {heart_rate}, SpO2: {spo2}%। বাংলায় একটি বিস্তারিত স্বাস্থ্য রিপোর্ট তৈরি করুন।"
        temp_history = st.session_state.chat_histories[current_user] + [{
            "role": "user",
            "content": sensor_prompt,
        }]
        response = call_groq_ai(temp_history)
        st.markdown(response)
    st.markdown("</div>", unsafe_allow_html=True)
  if ser:
    ser.close()
else:
  # 🌟 অ্যাডভান্সড চ্যাট ইন্টারফেস ও কুইক চিপস
  st.markdown(
      "<h3 style='color: #00f5d4;'>💬 এআই চ্যাট অ্যাসিস্ট্যান্ট</h3>",
      unsafe_allow_html=True,
  )

  # কুইক সাজেশন বাটন (Quick Suggestion Chips)
  st.markdown(
      "<p style='color: #94a3b8; font-size: 14px;'>সরাসরি নিচের সমস্যাগুলোতে ক্লিক"
      " করতে পারো:</p>",
      unsafe_allow_html=True,
  )
  q_col1, q_col2, q_col3, q_col4 = st.columns(4)

  quick_prompt = None
  with q_col1:
    if st.button("🦵 পায়ে ব্যথা", use_container_width=True):
      quick_prompt = "আমার পায়ে প্রচণ্ড ব্যথা করছে, কী করব?"
  with q_col2:
    if st.button("🤒 জ্বর ও ঠান্ডা", use_container_width=True):
      quick_prompt = "আমার গায়ে জ্বর ও ঠান্ডা লাগার ভাব আছে, করণীয় কী?"
  with q_col3:
    if st.button("🤕 মাথা ব্যথা", use_container_width=True):
      quick_prompt = "আমার মাথা ব্যথা করছে, এখন কি করা উচিত?"
  with q_col4:
    if st.button("💊 নাপা খাওয়া যাবে?", use_container_width=True):
      quick_prompt = "আমার কি এখন নাপা খাওয়া উচিত?"

  st.markdown("<br>", unsafe_allow_html=True)

  # চ্যাট হিস্ট্রি রেন্ডার করা
  for message in st.session_state.chat_histories[current_user]:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # যদি কুইক বাটন ক্লিক করা হয় অথবা চ্যাট ইনপুট দেওয়া হয়
  prompt = st.chat_input("আপনার স্বাস্থ্যগত সমস্যা বাংলায় বা বাংলিশে লিখুন...")

  if quick_prompt:
    prompt = quick_prompt

  if prompt:
    with st.chat_message("user"):
      st.markdown(prompt)
    st.session_state.chat_histories[current_user].append(
        {"role": "user", "content": prompt}
    )

    with st.spinner("AI উত্তর তৈরি করছে..."):
      response = call_groq_ai(st.session_state.chat_histories[current_user])

    with st.chat_message("assistant"):
      st.markdown(response)

    st.session_state.chat_histories[current_user].append(
        {"role": "assistant", "content": response}
    )
    if quick_prompt:
      st.rerun()
