import streamlit as st
import serial
import requests
import time

# পৃষ্ঠা কনফিগারেশন
st.set_page_config(page_title="MUSHFIK'S HEALTH ASSISTANT AI", page_icon="🩺", layout="wide")

st.title("🩺 MUSHFIK'S HEALTH ASSISTANT AI")
st.write("নবম শ্রেণীর বিজ্ঞান মেলার জন্য তৈরি একটি উদ্ভাবনী দ্বিমুখী (Dual-Mode) স্বাস্থ্যসেবা প্রজেক্ট।")

st.sidebar.header("⚙️ Settings")
GROQ_API_KEY = "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"

def call_groq_ai(prompt):
    if not GROQ_API_KEY: return "দুঃখিত, এআই সিস্টেম কনফিগার করা হয়নি।"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are a highly professional, knowledgeable, and empathetic medical assistant named 'MUSHFIK'S HEALTH ASSISTANT AI' for a school science fair project in Bangladesh. Answer the user's questions in perfectly natural, grammatically correct, and polite Bengali. Give detailed, accurate, and helpful medical guidance or general information related to their query. NEVER append or include emergency hospital phone numbers or helplines unless the user specifically and explicitly asks for them."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200: return response.json()['choices'][0]['message']['content']
        else: return "এআই সার্ভার রেসপন্স করছে না। একটু পরে চেষ্টা করুন।"
    except Exception as e: return f"কানেকশন সমস্যা: {str(e)}"

def analyze_vitals(temp, heart_rate, spo2):
    prompt = f"একজন অভিজ্ঞ প্রবীণ ডাক্তারের মতো আচরণ করুন। রোগীর তাপমাত্রা: {temp} °F, হার্ট রেট: {heart_rate} bpm, SpO2: {spo2}%। বাংলায় একটি বিস্তারিত স্বাস্থ্য রিপোর্ট তৈরি করুন (শারীরিক অবস্থা, সম্ভাব্য কারণ, করণীয় পদক্ষেপ ও বিপদের লক্ষণ)।"
    return call_groq_ai(prompt)

def ask_chatbot(question):
    prompt = f"রোগীর প্রশ্ন: '{question}'। সহানুভূতিশীল ডাক্তারের মতো বিস্তারিত প্রাথমিক স্বাস্থ্য পরামর্শ, জীবনযাত্রার পরিবর্তন ও করণীয় বিষয়গুলো খুব ভালোভাবে বুঝিয়ে বলুন।"
    return call_groq_ai(prompt)

port = st.sidebar.selectbox("Arduino Port সিলেক্ট করুন", ["COM3", "COM4", "COM5", "COM6", "/dev/ttyUSB0"])
arduino_connected = False
ser = None

try:
    ser = serial.Serial(port, 9600, timeout=1)
    arduino_connected = True
except:
    arduino_connected = False

if arduino_connected:
    st.success("✅ সেন্সর বুথ সংযুক্ত আছে! (মোড ১: সেন্সর মোড সক্রিয়)")
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
                    line = ser.readline().decode('utf-8').strip()
                    parts = line.split(',')
                    if len(parts) == 3:
                        temp, heart_rate, spo2 = float(parts[0]), int(parts[1]), int(parts[2])
                except: pass
            st.metric(label="🌡️ তাপমাত্রা", value=f"{temp} °F")
            st.metric(label="💓 হার্ট রেট", value=f"{heart_rate} BPM")
            st.metric(label="🩸 SpO2", value=f"{spo2} %")
    with col2:
        st.subheader("🤖 AI স্বাস্থ্য বিশ্লেষণ ও পরামর্শ")
        if st.button("📈 ডেটা এআই দ্বারা বিশ্লেষণ করুন"):
            with st.spinner("AI আপনার স্বাস্থ্য রিপোর্ট তৈরি করছে..."):
                st.write(analyze_vitals(temp, heart_rate, spo2))
    if ser: ser.close()
else:
    st.warning("⚠️ সেন্সর পাওয়া যায়নি। (মোড ২: AI চ্যাটবট মোড সক্রিয়)")
    if "messages" not in st.session_state: st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])
    if prompt := st.chat_input("আপনার সমস্যা বা লক্ষণগুলো এখানে লিখুন..."):
        with st.chat_message("user"): st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("AI উত্তর ভাবছে..."): response = ask_chatbot(prompt)
        with st.chat_message("assistant"): st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
