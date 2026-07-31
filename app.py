import streamlit as st
import serial
import requests
import time

# পৃষ্ঠা কনফিগারেশন (Page Configuration)
st.set_page_config(page_title="MUSHFIK'S HEALTH ASSISTANT AI", page_icon="🩺", layout="wide")

# অ্যাপের শিরোনাম ও পরিচিতি
st.title("🩺 MUSHFIK'S HEALTH ASSISTANT AI")
st.write("নবম শ্রেণীর বিজ্ঞান মেলার জন্য তৈরি একটি উদ্ভাবনী দ্বিমুখী (Dual-Mode) স্বাস্থ্যসেবা প্রজেক্ট।")

# সাইডবার কনফিগারেশন (Port Selection)
st.sidebar.header("⚙️ সেটিংস ও কনফিগারেশন")

# Groq API Key (সুরক্ষিত ও কোডের ভেতরে লুকানো)
GROQ_API_KEY = "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"

# এআই সার্ভারে রিকোয়েস্ট পাঠানোর ফাংশন
def call_groq_ai(prompt):
    if not GROQ_API_KEY:
        return "দুঃখিত, এআই সিস্টেম কনফিগার করা হয়নি।"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # এখানে এআই-এর সিস্টেমে তোমার নতুন নাম সেট করে দেওয়া হয়েছে
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": """You are a professional medical assistant named 'MUSHFIK'S HEALTH ASSISTANT AI' for a science fair project in Bangladesh. 
                You must respond in perfectly natural, grammatically correct, and empathetic Bengali. 
                
                CRITICAL KNOWLEDGE BASE FOR HOSPITAL NUMBERS:
                If the user asks for emergency numbers, hospital phone numbers, or contacts (e.g., 'dhaka medical er number', 'hospital number', 'emergency helpline'), you must provide these real and verified numbers from your knowledge base:
                1. সরকারি স্বাস্থ্য বাতায়ন (Health Helpline): ১৬২৬৩ (২৪ ঘণ্টা ফ্রি চিকিৎসা পরামর্শ)
                2. জাতীয় জরুরী সেবা (National Emergency): ৯৯৯ (অ্যাম্বুলেন্স ও পুলিশ)
                3. ঢাকা মেডিকেল কলেজ hospital (DMCH): ০২-৫৫১৬৭১০০, ০২-৫৫১৬৭১০২
                4. বঙ্গবন্ধু শেখ মুজিব মেডিকেল বিশ্ববিদ্যালয় (BSMMU): ০২-৫৫১৬৫৭৬০
                5. স্কয়ার হাসপাতাল (Square Hospital): ১০৬১৬
                6. এভারকেয়ার হাসপাতাল (Evercare Dhaka): ১০৬৭৮
                7. ইউনাইটেড হাসপাতাল (United Hospital): ১০৬৬৬
                8. বারডেম জেনারেল হাসপাতাল (BIRDEM): ১০৬১৭
                
                Always explain nicely that while you cannot browse the live internet for every small local diagnostic center, you have the most important and critical national healthcare numbers pre-saved for them."""
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return "এআই সার্ভার সাময়িকভাবে রেসপন্স করছে না। অনুগ্রহ করে একটু পরে চেষ্টা করুন।"
    except Exception as e:
        return f"কানেকশন সমস্যা: {str(e)}"

# ফাংশন: সেন্সর ডেটা বিশ্লেষণ করার জন্য
def analyze_vitals(temp, heart_rate, spo2):
    prompt = f"""
    একজন অভিজ্ঞ প্রবীণ ডাক্তারের মতো আচরণ করুন। একজন রোগীর নিচের ভাইটাল সাইনগুলো পাওয়া গেছে:
    - শরীরের তাপমাত্রা: {temp} °F
    - হৃদস্পন্দন (Heart Rate): {heart_rate} bpm
    - রক্তে অক্সিজেনের মাত্রা (SpO2): {spo2}%
    
    এই ডেটা গভীরভাবে বিশ্লেষণ করে বাংলায় একটি বিস্তারিত স্বাস্থ্য রিপোর্ট তৈরি করুন। রিপোর্টে নিচের অংশগুলো স্পষ্টভাবে থাকতে হবে:
    ১. রোগীর বর্তমান শারীরিক অবস্থা কেমন (সাধারণ, মাঝারি নাকি ঝুঁকিপূর্ণ)।
    ২. এই লক্ষণের সম্ভাব্য কারণ কী হতে পারে।
    ৩. তাৎক্ষণিকভাবে ঘরে বসে রোগীর কী কী করা উচিত (করণীয় পদক্ষেপসমূহ পয়েন্ট আকারে)।
    ৪. কোনো বিপদের লক্ষণ আছে কিনা এবং কখন দ্রুত হাসপাতালে বা ডাক্তারের কাছে যেতে হবে।
    """
    return call_groq_ai(prompt)

# ফাংশন: চ্যাটবট মোডের জন্য
def ask_chatbot(question):
    prompt = f"""
    রোগীর প্রশ্ন অথবা সমস্যা: "{question}"
    
    যদি রোগী কোনো হাসপাতালের নম্বর বা জরুরী যোগাযোগের তথ্য চায়, তবে সিস্টেমের নলেজ বেস থেকে সঠিক নম্বরগুলো সুন্দর করে পয়েন্ট আকারে সাজিয়ে দিন।
    অন্যথায়, একজন সহানুভূতিশীল ডাক্তারের মতো রোগীকে বিস্তারিত প্রাথমিক স্বাস্থ্য পরামর্শ ও করণীয় বিষয়গুলো বুঝিয়ে বলুন।
    """
    return call_groq_ai(prompt)

# আর্ডুইনোর পোর্ট সিলেক্ট করার অপশন
port = st.sidebar.selectbox("Arduino Port সিলেক্ট করুন", ["COM3", "COM4", "COM5", "COM6", "/dev/ttyUSB0"])

# আর্ডুইনো সংযোগ পরীক্ষা করা
arduino_connected = False
ser = None

try:
    ser = serial.Serial(port, 9600, timeout=1)
    arduino_connected = True
except (serial.SerialException, ValueError):
    arduino_connected = False

# মূল ইন্টারফেস লজিক (Main UI Logic)
if arduino_connected:
    st.success("✅ সেন্সর বুথ সংযুক্ত আছে! (মোড ১: সেন্সর মোড সক্রিয়)")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 লাইভ সেন্সর ডেটা")
        demo_mode = st.checkbox("ডেমো বা টেস্ট ডেটা ব্যবহার করুন (আর্ডুইনো ছাড়া টেস্ট করার জন্য)", value=True)
        
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
                        temp = float(parts[0])
                        heart_rate = int(parts[1])
                        spo2 = int(parts[2])
                except:
                    pass
            
            st.metric(label="🌡️ শরীরের তাপমাত্রা", value=f"{temp} °F")
            st.metric(label="💓 হৃদস্পন্দন (Heart Rate)", value=f"{heart_rate} BPM")
            st.metric(label="🩸 অক্সিজেন মাত্রা (SpO2)", value=f"{spo2} %")

    with col2:
        st.subheader("🤖 AI স্বাস্থ্য বিশ্লেষণ ও পরামর্শ")
        if st.button("📈 ডেটা এআই দ্বারা বিশ্লেষণ করুন"):
            with st.spinner("AI আপনার স্বাস্থ্য রিপোর্ট তৈরি করছে..."):
                advice = analyze_vitals(temp, heart_rate, spo2)
                st.write(advice)
    if ser:
        ser.close()

else:
    st.warning("⚠️ সেন্সর পাওয়া যায়নি। (মোড ২: AI চ্যাটবট মোড সক্রিয়)")
    st.info("💡 হার্ডওয়্যার ডিসকানেক্টেড থাকলেও আপনি এখানে যেকোনো স্বাস্থ্য বিষয়ক প্রশ্ন করতে পারেন।")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("আপনার সমস্যা বা লক্ষণগুলো এখানে লিখুন..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("AI আপনার প্রশ্নের উত্তর ভাবছে..."):
            response = ask_chatbot(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})