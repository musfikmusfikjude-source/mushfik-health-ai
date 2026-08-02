import requests
import streamlit as st

# পৃষ্ঠা কনফিগারেশন (পার্মানেন্ট ডার্ক থিম)
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

# 🌟 ১০০% পার্মানেন্ট ডার্ক মোড CSS
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
    </style>
    """,
    unsafe_allow_html=True,
)

# সেশন স্টেট ইনিশিয়ালাইজেশন
if "current_user" not in st.session_state:
  st.session_state.current_user = "Guest"
if "chat_histories" not in st.session_state:
  st.session_state.chat_histories = {"Guest": []}

GROQ_API_KEY = "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"


# AI কল ফাংশন
def call_groq_ai(chat_history):
  if not GROQ_API_KEY:
    return "দুঃখিত, এআই সিস্টেম কনফিগার করা হয়নি।"
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
          " fair project in Bangladesh. Always reply strictly in proper, correct,"
          " and formal Bengali script (বাংলা হরফে)."
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
      return "এআই সার্ভার রেসপন্স করছে না।"
  except Exception as e:
    return f"কানেকশন সমস্যা: {str(e)}"


# সাইডবার প্যানেল
st.sidebar.markdown(
    "<h2 style='text-align: center; color: #00f5d4;'>🩺 কন্ট্রোল প্যানেল</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")
if st.sidebar.button(
    "🗑️ বর্তমান চ্যাট মুছুন (Clear Chat)", use_container_width=True
):
  st.session_state.chat_histories[st.session_state.current_user] = []
  st.rerun()

# মূল ইন্টারফেস
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%); padding: 30px; border-radius: 20px; border: 1px solid rgba(0, 180, 216, 0.3); text-align: center;">
        <h1 style="color: #00f5d4 !important; font-size: 38px; margin: 0;">🩺 MUSHFIK'S HEALTH ASSISTANT AI</h1>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# কু্যইক সমস্যা বাটনসমূহ
st.markdown(
    "<p style='color: #94a3b8; font-size: 14px;'>সরাসরি নিচের সমস্যাগুলোতে ক্লিক"
    " করতে পারো:</p>",
    unsafe_allow_html=True,
)
q_col1, q_col2, q_col3, q_col4 = st.columns(4)

quick_prompt = None
with q_col1:
  if st.button("🦵 পায়ে ব্যথা", use_container_width=True):
    quick_prompt = "আমার পায়ে প্রচণ্ড ব্যথা করছে, কী করব?"
with q_col2:
  if st.button("🤒 জ্বর ও ঠান্ডা", use_container_width=True):
    quick_prompt = "আমার গায়ে জ্বর ও ঠান্ডা লাগার ভাব আছে, করণীয় কী?"
with q_col3:
  if st.button("🤕 মাথা ব্যথা", use_container_width=True):
    quick_prompt = "আমার মাথা ব্যথা করছে, এখন কি করা উচিত?"
with q_col4:
  if st.button("💊 নাপা খাওয়া যাবে?", use_container_width=True):
    quick_prompt = "আমার কি এখন নাপা খাওয়া উচিত?"

st.markdown("<br>", unsafe_allow_html=True)

# চ্যাট হিস্ট্রি প্রদর্শন
for message in st.session_state.chat_histories[st.session_state.current_user]:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

prompt = st.chat_input("আপনার স্বাস্থ্যগত সমস্যা বাংলায় বা বাংলিশে লিখুন...")

if quick_prompt:
  prompt = quick_prompt

if prompt:
  with st.chat_message("user"):
    st.markdown(prompt)
  st.session_state.chat_histories[st.session_state.current_user].append(
      {"role": "user", "content": prompt}
  )

  with st.spinner("AI উত্তর তৈরি করছে..."):
    response = call_groq_ai(
        st.session_state.chat_histories[st.session_state.current_user]
    )

  with st.chat_message("assistant"):
    st.markdown(response)

  st.session_state.chat_histories[st.session_state.current_user].append(
      {"role": "assistant", "content": response}
  )
  if quick_prompt:
    st.rerun()
