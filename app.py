import requests
import serial
import streamlit as st
import time

# পৃষ্ঠা কনফিগারেশন (পার্মানেন্ট ডার্ক থিম নিশ্চিত করা)
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
        <p style="color: #94a3b8; font-size: 16px; margin-top: 10px; font-weight: 500;">অ্যাক্সেসিবিলিটি সিস্টেম লোড হচ্ছে...</p>
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

# 🌟 ১০০% পার্মানেন্ট ডার্ক মোড এবং মোবাইল রিফ্রেশ বন্ধ করার CSS
st.markdown(
    """
    <style>
    .stApp, body, html {
        background-color: #0b132b !important;
        color: #f1f5f9 !important;
        font-family: 'Segoe UI', sans-serif;
        overscroll-behavior-y: none !important;
    }

    h1, h2, h3, h4, h5, h6, span, p, label {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] {
        background-color: #1c2541 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

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

    [data-testid="stChatMessage"] {
        background-color: #1c2541 !important;
        border-radius: 15px !important;
        border: 1px solid rgba(0, 180, 216, 0.2) !important;
        padding: 15px !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }

    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1c2541 !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0, 180, 216, 0.3) !important;
    }
    
    .custom-card {
        background: #1c2541;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(0, 180, 216, 0.25);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    
    .mode-box {
        background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%);
        padding: 40px;
        border-radius: 20px;
        border: 2px solid #00f5d4;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 245, 212, 0.2);
        margin-top: 50px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# সেশন স্টেট ইনিশিয়ালাইজেশন
if "app_mode" not in st.session_state:
  st.session_state.app_mode = None  # None, "normal", "sign"
if "sign_sub_view" not in st.session_state:
  st.session_state.sign_sub_view = "translator"  # "translator" or "learn"
if "users" not in st.session_state:
  st.session_state.users = {"mushfik": "1234"}
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "current_user" not in st.session_state:
  st.session_state.current_user = "Guest"
if "chat_histories" not in st.session_state:
  st.session_state.chat_histories = {"Guest": []}
if "sign_histories" not in st.session_state:
  st.session_state.sign_histories = []

GROQ_API_KEY = "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"


# 🌟 Groq AI কল ফাংশন
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
          " Bengali script (বাংলা হরফে). "
          "CRITICAL RULE 2: If the user is using Sign Language mode, acknowledge"
          " that they are communicating via sign language, interpret their"
          " symptoms or queries carefully from the context provided, and give"
          " clear medical advice in Bengali."
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


# ==========================================
# 🌟 ১. মোড সিলেকশন স্ক্রিন (যখন মোড সিলেক্ট করা নেই)
# ==========================================
if st.session_state.app_mode is None:
  st.markdown(
      """
        <div style="text-align: center; padding-top: 20px;">
            <h1 style="color: #00f5d4 !important; font-size: 42px;">🩺 MUSHFIK'S HEALTH ASSISTANT AI</h1>
            <p style="color: #94a3b8; font-size: 18px;">আপনার যোগাযোগের মাধ্যমটি সিলেক্ট করুন</p>
        </div>
        """,
      unsafe_allow_html=True,
  )

  col1, col2 = st.columns(2, gap="large")

  with col1:
    st.markdown(
        """
            <div class="mode-box">
                <div style="font-size: 60px;">🗣️</div>
                <h2>সাধারণ কথোপকথন ও সেন্সর</h2>
                <p style="color: #94a3b8;">স্বাভাবিক কথা বা টেক্সট চ্যাট এবং হার্ডওয়্যার সেন্সর ডেটা বিশ্লেষণ মোড।</p>
            </div>
            """,
        unsafe_allow_html=True,
    )
    if st.button(
        "সাধারণ মোড শুরু করুন", use_container_width=True, key="btn_normal"
    ):
      st.session_state.app_mode = "normal"
      st.rerun()

  with col2:
    st.markdown(
        """
            <div class="mode-box" style="border-color: #00b4d8;">
                <div style="font-size: 60px;">🤟</div>
                <h2>সাইন ল্যাঙ্গুয়েজ (ইশারা ভাষা)</h2>
                <p style="color: #94a3b8;">যাঁরা কথা বলতে বা শুনতে পান না, তাঁদের জন্য ক্যামেরাভিত্তিক ইশারা ও শেখার ব্যবস্থা।</p>
            </div>
            """,
        unsafe_allow_html=True,
    )
    if st.button("সাইন ল্যাঙ্গুয়েজ মোড শুরু করুন", use_container_width=True, key="btn_sign"):
      st.session_state.app_mode = "sign"
      st.rerun()

# ==========================================
# 🌟 ২. সাধারণ চ্যাট ও সেন্সর মোড
# ==========================================
elif st.session_state.app_mode == "normal":
  # সাইডবার
  st.sidebar.markdown(
      "<h2 style='text-align: center; color: #00f5d4;'>🩺 কন্ট্রোল প্যানেল</h2>",
      unsafe_allow_html=True,
  )
  st.sidebar.markdown("---")
  if st.sidebar.button(
      "🔄 হোম পেজে ফিরে যান (মোড পরিবর্তন)", use_container_width=True
  ):
    st.session_state.app_mode = None
    st.rerun()

  st.sidebar.markdown("---")
  port = st.sidebar.selectbox(
      "Arduino Port সিলেক্ট করুন", ["COM3", "COM4", "COM5", "COM6", "/dev/ttyUSB0"]
  )
  current_user = st.session_state.current_user
  if current_user not in st.session_state.chat_histories:
    st.session_state.chat_histories[current_user] = []

  if st.sidebar.button("🗑️ চ্যাট মুছুন", use_container_width=True):
    st.session_state.chat_histories[current_user] = []
    st.rerun()

  # মূল ইন্টারফেস
  st.markdown(
      """
        <div style="background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%); padding: 30px; border-radius: 20px; border: 1px solid rgba(0, 180, 216, 0.3); text-align: center;">
            <h1 style="color: #00f5d4 !important; font-size: 38px; margin: 0;">🩺 সাধারণ স্বাস্থ্য সহায়ক মোড</h1>
        </div>
        """,
      unsafe_allow_html=True,
  )
  st.markdown("<br>", unsafe_allow_html=True)

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
      st.metric(label="🌡️ তাপমাত্রা", value=f"{temp} °F")
      st.metric(label="💓 হার্ট রেট", value=f"{heart_rate}")
      st.metric(label="🩸 SpO2", value=f"{spo2} %")
      st.markdown("</div>", unsafe_allow_html=True)

    with col2:
      st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
      st.subheader("🤖 এআই স্বাস্থ্য বিশ্লেষণ রিপোর্ট")
      if st.button("📈 সেন্সর ডেটা বিশ্লেষণ করুন", use_container_width=True):
        with st.spinner("AI রিপোর্ট তৈরি করছে..."):
          sensor_prompt = f"তাপমাত্রা: {temp} °F, হার্ট রেট: {heart_rate}, SpO2: {spo2}%। বাংলায় রিপোর্ট দিন।"
          temp_history = st.session_state.chat_histories[current_user] + [{
              "role": "user",
              "content": sensor_prompt,
          }]
          response = call_groq_ai(temp_history)
          st.markdown(response)
      st.markdown("</div>", unsafe_allow_html=True)
  else:
    st.markdown(
        "<h3 style='color: #00f5d4;'>💬 এআই চ্যাট অ্যাসিস্ট্যান্ট</h3>",
        unsafe_allow_html=True,
    )
    for message in st.session_state.chat_histories[current_user]:
      with st.chat_message(message["role"]):
        st.markdown(message["content"])

    prompt = st.chat_input("আপনার স্বাস্থ্যগত সমস্যা বাংলায় লিখুন...")
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

# ==========================================
# 🌟 ৩. সাইন ল্যাঙ্গুয়েজ ও লার্নিং মোড
# ==========================================
elif st.session_state.app_mode == "sign":
  st.sidebar.markdown(
      "<h2 style='text-align: center; color: #00f5d4;'>🤟 সাইন ল্যাঙ্গুয়েজ প্যানেল</h2>",
      unsafe_allow_html=True,
  )
  st.sidebar.markdown("---")
  if st.sidebar.button(
      "🔄 হোম পেজে ফিরে যান (মোড পরিবর্তন)", use_container_width=True
  ):
    st.session_state.app_mode = None
    st.rerun()

  st.sidebar.markdown("---")
  # শেখার ইন্টারফেস বা অনুবাদক পাল্টানোর বাটন
  if st.sidebar.button(
      "📖 সাইন ল্যাঙ্গুয়েজ শিখুন (Learn Interface)", use_container_width=True
  ):
    st.session_state.sign_sub_view = "learn"
  if st.sidebar.button(
      "📸 ইশারা অনুবাদক ক্যামেরা", use_container_width=True
  ):
    st.session_state.sign_sub_view = "translator"

  # যদি ইউজার 'translator' মোডে থাকে
  if st.session_state.sign_sub_view == "translator":
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%; padding: 30px; border-radius: 20px; border: 1px solid rgba(0, 180, 216, 0.3); text-align: center;">
            <h1 style="color: #00f5d4 !important; font-size: 38px; margin: 0;">🤟 সাইন ল্যাঙ্গুয়েজ হেলথ অ্যাসিস্ট্যান্ট</h1>
            <p style="color: #94a3b8; font-size: 15px; margin-top: 5px;">আপনার ইশারা বা সাইন ল্যাঙ্গুয়েজের ছবি ক্যামেরায় ক্যাপচার করুন অথবা সমস্যা লিখে জানান</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
      st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
      st.subheader("📸 ক্যামেরা ইশারা ক্যাপচার")
      img_file = st.camera_input("ইশারা বা অঙ্গভঙ্গি দেখান")

      if img_file:
        st.success("ইশারা সফলভাবে ক্যাপচার করা হয়েছে!")
        sign_input_text = st.text_input(
            "ক্যাপচারকৃত ইশারার বিবরণ বা সমস্যা লিখুন (যেমন: মাথা ব্যথা বা পেট ব্যথা)"
        )
        if st.button("এআই দিয়ে ইশারা অনুবাদ ও সমাধান নিন"):
          with st.spinner("ইশারা বিশ্লেষণ করা হচ্ছে..."):
            prompt = f"[Sign Language User]: {sign_input_text} (রোগী কথা বলতে পারেন না, ইশারার মাধ্যমে স্বাস্থ্য সমস্যা প্রকাশ করেছেন)।"
            st.session_state.sign_histories.append(
                {"role": "user", "content": prompt}
            )
            response = call_groq_ai(st.session_state.sign_histories)
            st.session_state.sign_histories.append(
                {"role": "assistant", "content": response}
            )
            st.rerun()
      st.markdown("</div>", unsafe_allow_html=True)

    with col2:
      st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
      st.subheader("💬 কনভারসেশন ও প্রেসক্রিপশন ফিডব্যাক")

      for message in st.session_state.sign_histories:
        with st.chat_message(message["role"]):
          st.markdown(message["content"])

      direct_sign_prompt = st.chat_input(
          "অথবা আপনার সমস্যাটি সরাসরি টাইপ করে জানান..."
      )
      if direct_sign_prompt:
        user_msg = f"[Sign Language User]: {direct_sign_prompt}"
        st.session_state.sign_histories.append(
            {"role": "user", "content": user_msg}
        )
        with st.spinner("AI উত্তর তৈরি করছে..."):
          response = call_groq_ai(st.session_state.sign_histories)
        st.session_state.sign_histories.append(
            {"role": "assistant", "content": response}
        )
        st.rerun()
      st.markdown("</div>", unsafe_allow_html=True)

  # যদি ইউজার 'learn' মোডে থাকে (সাইন ল্যাঙ্গুয়েজ শেখার ইন্টারফেস)
  elif st.session_state.sign_sub_view == "learn":
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%); padding: 30px; border-radius: 20px; border: 1px solid rgba(0, 180, 216, 0.3); text-align: center;">
            <h1 style="color: #00f5d4 !important; font-size: 38px; margin: 0;">📖 সাইন ল্যাঙ্গুয়েজ শেখার কর্নার</h1>
            <p style="color: #94a3b8; font-size: 15px; margin-top: 5px;">প্রাথমিক চিকিৎসা ও স্বাস্থ্য সম্পর্কিত সাধারণ ইশারা ভাষা শিখুন</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
      st.markdown(
          """
            <div class='custom-card'>
                <h3>১. ব্যথা ও অসুস্থতা</h3>
                <p><b>মাথা ব্যথা:</b> কপালে দুই আঙুল দিয়ে চাপ দিয়ে গোল গোল ঘোরানো।</p>
                <p><b>পেট ব্যথা:</b> পেটের ওপর হাত রেখে হালকা মسا করা।</p>
                <p><b>বুক ব্যথা:</b> বুকের বামপাশে হাত চেপে ধরা।</p>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with col2:
      st.markdown(
          """
            <div class='custom-card'>
                <h3>২. জরুরি শব্দসমূহ</h3>
                <p><b>সাহায্য চাই:</b> এক হাতের মুঠি অন্য হাতের ওপর রাখা।</p>
                <p><b>পানি লাগবে:</b> থুতনির কাছে হাত দিয়ে 'W' শেপ বা পানের ইশারা।</p>
                <p><b>ডাক্তার:</b> কবজির নাড়ি ধরার ভঙ্গি করা।</p>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with col3:
      st.markdown(
          """
            <div class='custom-card'>
                <h3>৩. অনুভূতি প্রকাশ</h3>
                <p><b>খুব বেশি কষ্ট:</b> মুখে ব্যথার অভিব্যক্তি ফুটিয়ে বুক বা মাথায় হাত দেওয়া।</p>
                <p><b>ভালো আছি:</b> বুড়ো আঙুল ওপরের দিকে তোলা (Thumbs Up)।</p>
                <p><b>ধন্যবাদ:</b> চিবুক থেকে হাত সামনে প্রসারিত করা।</p>
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ অনুবাদক ক্যামেরায় ফিরে যান", use_container_width=False):
      st.session_state.sign_sub_view = "translator"
      st.rerun()
