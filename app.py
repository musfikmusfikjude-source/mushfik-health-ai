import requests
import streamlit as st

# ==========================================
# 🌟 কনফিগারেশন ও স্টাইল
# ==========================================
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
        background: #1c2541; padding: 25px; border-radius: 15px;
        border: 1px solid rgba(0, 180, 216, 0.25);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 🌟 সেশন স্টেট
# ==========================================
if "current_user" not in st.session_state:
  st.session_state.current_user = "Patient_1"
if "chat_histories" not in st.session_state:
  st.session_state.chat_histories = {"Patient_1": []}

GROQ_API_KEY = "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"


# ==========================================
# 🌟 AI রেসপন্স ফাংশন
# ==========================================
def call_groq_ai(chat_history):
  if not GROQ_API_KEY:
    return "দুঃখিত, এআই এপিআই কি সেট করা হয়নি।"

  url = "https://api.groq.com/openai/v1/chat/completions"
  headers = {
      "Authorization": f"Bearer {GROQ_API_KEY}",
      "Content-Type": "application/json",
  }

  messages = [{
      "role": "system",
      "content": (
          "You are a professional, caring medical assistant named 'MUSHFIK'S"
          " HEALTH ASSISTANT AI'. Reply strictly in formal Bengali script (বাংলা"
          " হরফে). Provide health advice, preliminary diagnoses, and"
          " professional suggestions."
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
      return f"এআই সার্ভার ত্রুটি: {response.status_code}"
  except Exception as e:
    return f"কানেকশন সমস্যা: {str(e)}"


# ==========================================
# 🌟 সাইডবার ও ইউজার ইন্টারফেস
# ==========================================
with st.sidebar:
  st.markdown(
      "<h2 style='text-align: center; color: #00f5d4;'>🩺 কন্ট্রোল প্যানেল</h2>",
      unsafe_allow_html=True,
  )
  st.markdown("---")
  if st.button("🗑️ চ্যাট হিস্ট্রি মুছে ফেলুন", use_container_width=True):
    st.session_state.chat_histories[st.session_state.current_user] = []
    st.rerun()

  st.markdown("---")
  st.markdown(
      "<p style='color: #94a3b8; font-size: 14px; text-align: center;'>প্রোজেক্ট:"
      " Mushfik's Health Assistant AI</p>",
      unsafe_allow_html=True,
  )

# মূল স্ক্রিন
st.markdown(
    """
    <div style="text-align: center; padding-bottom: 20px;">
        <h1 style="color: #00f5d4 !important; font-size: 38px;">🩺 MUSHFIK'S HEALTH ASSISTANT AI</h1>
        <p style="color: #94a3b8; font-size: 16px;">আপনার স্বাস্থ্যগত সমস্যা বা প্রশ্ন নিচে লিখুন, এআই তাৎক্ষণিকভাবে সাহায্য করবে।</p>
    </div>
    """,
    unsafe_allow_html=True,
)

current_history = st.session_state.chat_histories[st.session_state.current_user]

# চ্যাট হিস্ট্রি রেন্ডার করা
for message in current_history:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# ইনপুট ফিল্ড
if prompt := st.chat_input(
    "আপনার সমস্যা বাংলায় লিখুন (যেমন: মাথা ব্যথা, জ্বর বা পেট ব্যথা)..."
):
  current_history.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    with st.spinner("চিকিৎসা পরামর্শ প্রস্তুত করা হচ্ছে..."):
      response = call_groq_ai(current_history)
      st.markdown(response)

  current_history.append({"role": "assistant", "content": response})
