import requests
import streamlit as st
from PIL import Image
import io

# ==========================================
# 🌟 কনফিগারেশন ও স্টাইল
# ==========================================
st.set_page_config(
    page_title="MUSHFIK'S HEALTH ASSISTANT AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 🌟 প্রিমিয়াম স্প্ল্যাশ স্ক্রিন (প্রথম লোডের জন্য)
if "loaded" not in st.session_state:
  st.session_state.loaded = False

if not st.session_state.loaded:
  splash_html = """
    <div id="splash-screen" style="
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: #0b132b; display: flex; flex-direction: column;
        justify-content: center; align-items: center; z-index: 999999;
        color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        transition: opacity 0.8s ease;
    ">
        <div style="font-size: 70px; animation: pulse 1.5s infinite ease-in-out;">🩺</div>
        <h1 style="margin-top: 20px; letter-spacing: 2px; color: #00f5d4; font-weight: 700;">MUSHFIK'S HEALTH ASSISTANT AI</h1>
        <p style="color: #94a3b8; font-size: 16px; margin-top: 10px; font-weight: 500;">সিস্টেম লোড হচ্ছে...</p>
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

# 🌟 পার্মানেন্ট ডার্ক মোড CSS
st.markdown(
    """
    <style>
    .stApp, body, html {
        background-color: #0b132b !important;
        color: #f1f5f9 !important;
        font-family: 'Segoe UI', sans-serif;
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
        color: white; border-radius: 10px; border: none;
        padding: 10px 20px; font-weight: 600;
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
        background-color: #1c2541 !important; color: white !important;
        border-radius: 10px !important; border: 1px solid rgba(0, 180, 216, 0.3) !important;
    }
    .custom-card {
        background: #1c2541; padding: 20px; border-radius: 15px;
        border: 1px solid rgba(0, 180, 216, 0.25);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 20px;
    }
    .mode-box {
        background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%);
        padding: 40px; border-radius: 20px; border: 2px solid #00f5d4;
        text-align: center; box-shadow: 0 10px 30px rgba(0, 245, 212, 0.2);
        margin-top: 50px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 🌟 সেশন স্টেট ইনিশিয়ালাইজেশন
# ==========================================
if "app_mode" not in st.session_state:
  st.session_state.app_mode = None
if "sign_sub_view" not in st.session_state:
  st.session_state.sign_sub_view = "translator"
if "current_user" not in st.session_state:
  st.session_state.current_user = "Guest"
if "chat_histories" not in st.session_state:
  st.session_state.chat_histories = {"Guest": []}
if "sign_histories" not in st.session_state:
  st.session_state.sign_histories = []

# ⚠️ এখানে তোমার Groq API Key বসাও
GROQ_API_KEY = "PASTE_YOUR_GROQ_API_KEY_HERE"

# ==========================================
# 🌟 গ্রোথ এআই কল ফাংশন
# ==========================================
def call_groq_ai(chat_history):
  if not GROQ_API_KEY or GROQ_API_KEY == "PASTE_YOUR_GROQ_API_KEY_HERE":
    return "❌ ত্রুটি: API Key সেট করা হয়নি। অনুগ্রহ করে `app.py`-তে আপনার Groq API Key যুক্ত করুন।"
  
  url = "https://api.groq.com/openai/v1/chat/completions"
  headers = {
      "Authorization": f"Bearer {GROQ_API_KEY}",
      "Content-Type": "application/json",
  }
  
  # সিস্টেম প্রম্পট - যা এআই-কে তার দায়িত্ব শেখায়
  messages = [{
      "role": "system",
      "content": (
          "You are a professional, empathetic medical assistant named 'MUSHFIK'S HEALTH ASSISTANT AI'. "
          "Your goal is to assist users, including those who use sign language. "
          "Strictly reply ONLY in formal Bengali script (বাংলা হরফে). "
          "If the user provides an image description or asks a question based on sign language, "
          "interpret their need and provide clear medical advice or guidance in Bengali."
      ),
  }]
  
  # চ্যাট হিস্ট্রি যোগ করা
  for msg in chat_history:
    messages.append({"role": msg["role"], "content": msg["content"]})
  
  data = {
      "model": "llama-3.3-70b-versatile",
      "messages": messages,
      "temperature": 0.4, # കുറഞ്ഞ ടെമ്പারেച്ചർ കൂടുതൽ കൃത്യമായ উত্তরের জন্য
      "max_tokens": 4096
  }
  
  try:
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
      return response.json()["choices"][0]["message"]["content"]
    else:
      return f"❌ এআই সার্ভার ত্রুটি: {response.status_code}"
  except Exception as e:
    return f"❌ কানেকশন সমস্যা: {str(e)}"


# ==========================================
# 🌟 ১. মূল মোড সিলেকশন স্ক্রিন
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
                <h2>সাধারণ মোড</h2>
                <p style="color: #94a3b8;">স্বাভাবিক কথা বা টেক্সট চ্যাট এবং স্বাস্থ্য টিপস।</p>
            </div>
            """,
        unsafe_allow_html=True,
    )
    if st.button("সাধারণ মোড শুরু করুন", use_container_width=True, key="btn_normal"):
      st.session_state.app_mode = "normal"
      st.rerun()

  with col2:
    st.markdown(
        """
            <div class="mode-box" style="border-color: #00b4d8;">
                <div style="font-size: 60px;">🤟</div>
                <h2>ইশারা ভাষা (সাইন) মোড</h2>
                <p style="color: #94a3b8;">ক্যামেরা ক্যাপচার, ইশারা অনুবাদ ও শেখার ইন্টারফেস।</p>
            </div>
            """,
        unsafe_allow_html=True,
    )
    if st.button("ইশারা ভাষা মোড শুরু করুন", use_container_width=True, key="btn_sign"):
      st.session_state.app_mode = "sign"
      st.rerun()

# ==========================================
# 🌟 ২. সাধারণ চ্যাট মোড
# ==========================================
elif st.session_state.app_mode == "normal":
  # সাইডবার
  with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00f5d4;'>🩺 কন্ট্রোল প্যানেল</h2>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔄 হোম পেজে ফিরে যান", use_container_width=True):
      st.session_state.app_mode = None
      st.rerun()
    if st.button("🗑️ চ্যাট হিস্ট্রি মুছুন", use_container_width=True):
      st.session_state.chat_histories[st.session_state.current_user] = []
      st.rerun()

  # মূল চ্যাট ইন্টারফেস
  st.markdown("<div style='text-align:center;'><h1>🩺 সাধারণ স্বাস্থ্য সহায়ক মোড</h1></div>", unsafe_allow_html=True)
  
  # চ্যাট হিস্ট্রি লোড করা
  current_history = st.session_state.chat_histories[st.session_state.current_user]
  for message in current_history:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # ইউজার ইনপুট
  if prompt := st.chat_input("আপনার স্বাস্থ্য সমস্যা বা প্রশ্ন এখানে লিখুন..."):
    # ইউজারের মেসেজ সেভ ও ডিসপ্লে
    st.session_state.chat_histories[st.session_state.current_user].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    # এআই রেসপন্স
    with st.chat_message("assistant"):
      with st.spinner("⏳ এআই চিন্তা করছে..."):
        response = call_groq_ai(st.session_state.chat_histories[st.session_state.current_user])
        st.markdown(response)
    
    # এআই-এর মেসেজ সেভ করা
    st.session_state.chat_histories[st.session_state.current_user].append({"role": "assistant", "content": response})

# ==========================================
# 🌟 ৩. সাইন ল্যাঙ্গুয়েজ (ইশারা) মোড
# ==========================================
elif st.session_state.app_mode == "sign":
  # সাইডবার
  with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00f5d4;'>🤟 ইশারা ভাষা প্যানেল</h2>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔄 হোম পেজে ফিরে যান", use_container_width=True):
      st.session_state.app_mode = None
      st.rerun()
    st.markdown("---")
    if st.button("📸 ইশারা অনুবাদক ক্যামেরা", use_container_width=True):
      st.session_state.sign_sub_view = "translator"
    if st.button("📖 ইশারা ভাষা শিখুন", use_container_width=True):
      st.session_state.sign_sub_view = "learn"

  # 3a. অনুবাদক ইন্টারফেস (ক্যামেরা সহ)
  if st.session_state.sign_sub_view == "translator":
    st.markdown("<div style='text-align:center;'><h1>📸 ইশারা ভাষা অনুবাদক ও এআই পরামর্শ</h1></div>", unsafe_allow_html=True)
    st.write("আপনার ইশারার ছবি তুলুন এবং এআই-কে আপনার সমস্যার কথা লিখে জানান।")
    
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
      st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
      st.subheader("📷 ক্যামেরা ক্যাপচার")
      # Streamlit-এর নিজস্ব নিরাপদ ক্যামেরা ইনপুট
      img_file_buffer = st.camera_input("আপনার ইশারা সামনে ধরুন")

      if img_file_buffer is not None:
        st.success("✅ ছবি সফলভাবে তোলা হয়েছে!")
        
        # ছবি প্রসেসিং (ঐচ্ছিক: দেখানোর জন্য)
        bytes_data = img_file_buffer.getvalue()
        img = Image.open(io.BytesData(bytes_data))
        # st.image(img, caption="ক্যাপচার করা ইশারা", use_column_width=True)
        
        user_sign_prompt = st.text_
