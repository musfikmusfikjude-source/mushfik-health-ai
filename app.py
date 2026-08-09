```python
import streamlit as st
import serial
import requests
import sqlite3
import json
from datetime import datetime

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="MUSHFIK'S HEALTH ASSISTANT AI",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 MUSHFIK'S HEALTH ASSISTANT AI")
st.caption(
    "নবম শ্রেণীর বিজ্ঞান মেলার জন্য তৈরি একটি Dual-Mode AI Health Assistant"
)

st.info(
    "ℹ️ এটি একটি শিক্ষামূলক স্বাস্থ্য-সহায়ক প্রজেক্ট। "
    "AI-এর তথ্য চিকিৎসকের সরাসরি বিকল্প নয়।"
)

# =========================================================
# SETTINGS
# =========================================================

st.sidebar.header("⚙️ Settings")

# ---------------------------------------------------------
# API KEY
# ---------------------------------------------------------
# .streamlit/secrets.toml এ রাখবে:
#
# GROQ_API_KEY = "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"
#
# সরাসরি Python code-এ API key রাখবে না।

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = ""

# =========================================================
# DATABASE / MEMORY SYSTEM
# =========================================================

DB_FILE = "health_assistant_memory.db"


def init_database():
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_message(role, content):
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO conversations (role, content, timestamp)
        VALUES (?, ?, ?)
        """,
        (
            role,
            content,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def load_messages():
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT role, content
        FROM conversations
        ORDER BY id ASC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "role": role,
            "content": content
        }
        for role, content in rows
    ]


def clear_memory():
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("DELETE FROM conversations")

    conn.commit()
    conn.close()


init_database()

# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

if "arduino" not in st.session_state:
    st.session_state.arduino = None

if "arduino_port" not in st.session_state:
    st.session_state.arduino_port = None

# =========================================================
# MEMORY CONTROLS
# =========================================================

st.sidebar.subheader("🧠 AI Memory")

if st.sidebar.button("🗑️ Conversation Memory মুছে ফেলুন"):

    clear_memory()

    st.session_state.messages = []

    st.rerun()

st.sidebar.caption(
    f"বর্তমান Memory: {len(st.session_state.messages)} টি message"
)

# =========================================================
# GROQ AI FUNCTION
# =========================================================

def call_groq_ai(prompt, conversation_history=None):

    if not GROQ_API_KEY:
        return (
            "⚠️ Groq API Key পাওয়া যায়নি।\n\n"
            "`.streamlit/secrets.toml` ফাইলে GROQ_API_KEY সেট করুন।"
        )

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = """
তুমি "MUSHFIK'S HEALTH ASSISTANT AI" নামের একটি উন্নত
শিক্ষামূলক AI Health Assistant।

তোমার কাজ:

1. ব্যবহারকারীর প্রশ্ন বাংলায় পরিষ্কারভাবে বোঝানো।
2. আগের কথোপকথনের context ব্যবহার করা।
3. একই বিষয় আগে আলোচনা হয়ে থাকলে সেটি মনে রেখে উত্তর দেওয়া।
4. স্বাস্থ্য বিষয়ক তথ্য বৈজ্ঞানিক ও সতর্কভাবে দেওয়া।
5. সম্ভাব্য কারণগুলোকে নিশ্চিত রোগ হিসেবে উপস্থাপন না করা।
6. প্রয়োজন হলে ব্যবহারকারীকে অভিভাবক, শিক্ষক বা qualified healthcare professional-এর
   সাহায্য নিতে বলা।
7. জরুরি warning signs থাকলে পরিষ্কারভাবে উল্লেখ করা।
8. অপ্রয়োজনীয় ভয় সৃষ্টি করা যাবে না।
9. কোনো ব্যক্তির definitive diagnosis দেওয়া যাবে না।
10. ওষুধের ক্ষেত্রে নির্দিষ্ট prescription-style নির্দেশনা না দিয়ে
    সাধারণ নিরাপত্তামূলক তথ্য দেওয়া।
11. ব্যবহারকারীর আগের প্রশ্ন/উত্তরকে relevant হলে reference করা।
12. উত্তরকে structured করা।

উত্তরের format:

🩺 সংক্ষিপ্ত উত্তর

🔍 বিষয়টি কী হতে পারে

📋 সম্ভাব্য ব্যাখ্যা

✅ কী করা যেতে পারে

⚠️ কোন লক্ষণগুলো গুরুত্বপূর্ণ

👨‍⚕️ কখন healthcare professional-এর সাহায্য নেওয়া উচিত

🧠 আগের কথোপকথনের সাথে সম্পর্ক
(শুধুমাত্র relevant হলে)

সবসময় স্বাভাবিক, ভদ্র ও সহজবোধ্য বাংলায় উত্তর দেবে।

মনে রাখবে:
তুমি একটি educational AI assistant, সরাসরি চিকিৎসক নও।
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # -----------------------------------------------------
    # MEMORY
    # -----------------------------------------------------

    if conversation_history:

        # সর্বশেষ 20টি message AI-কে দেওয়া হচ্ছে
        recent_history = conversation_history[-20:]

        for msg in recent_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # Current question
    messages.append({
        "role": "user",
        "content": prompt
    })

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 1800
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:

            result = response.json()

            return result["choices"][0]["message"]["content"]

        else:

            try:
                error_data = response.json()
                return (
                    "⚠️ AI Server Error:\n\n"
                    + json.dumps(error_data, ensure_ascii=False)
                )
            except Exception:
                return (
                    f"⚠️ AI server response error "
                    f"(Status: {response.status_code})"
                )

    except requests.exceptions.Timeout:

        return "⏱️ AI server response দিতে বেশি সময় নিচ্ছে। আবার চেষ্টা করুন।"

    except requests.exceptions.ConnectionError:

        return "🌐 Internet connection সমস্যা হয়েছে।"

    except Exception as e:

        return f"⚠️ Unexpected error: {str(e)}"


# =========================================================
# HEALTH ANALYSIS
# =========================================================

def analyze_vitals(temp, heart_rate, spo2):

    prompt = f"""
একজন ব্যবহারকারীর sensor data:

🌡️ Temperature: {temp} °F
💓 Heart Rate: {heart_rate} BPM
🩸 SpO2: {spo2} %

এই তিনটি measurement শিক্ষামূলকভাবে বিশ্লেষণ করো।

নিচের বিষয়গুলো আলাদা করে ব্যাখ্যা করো:

1. Overall observation
2. কোন measurement সাধারণ range থেকে আলাদা মনে হচ্ছে কি না
3. তিনটি measurement একসাথে দেখলে কী বোঝা যেতে পারে
4. সম্ভাব্য সাধারণ কারণ
5. কীভাবে measurement আবার যাচাই করা উচিত
6. কোন warning signs থাকলে দ্রুত একজন responsible adult/healthcare professional-এর সাহায্য নেওয়া উচিত
7. Sensor measurement ভুল হওয়ার সম্ভাবনা

কোনো definitive diagnosis দেবে না।

বাংলায় structured health report তৈরি করো।
"""

    return call_groq_ai(
        prompt,
        conversation_history=st.session_state.messages
    )


# =========================================================
# CHATBOT
# =========================================================

def ask_chatbot(question):

    prompt = f"""
ব্যবহারকারীর বর্তমান প্রশ্ন:

{question}

আগের conversation context খুব মনোযোগ দিয়ে বিবেচনা করো।

যদি ব্যবহারকারী আগে কোনো symptom, measurement বা concern উল্লেখ করে থাকে
এবং বর্তমান প্রশ্নের সাথে সেটির সম্পর্ক থাকে, তাহলে সেই context ব্যবহার করো।

যদি আগের কথোপকথনের তথ্য বর্তমান প্রশ্নের সাথে সম্পর্কিত না হয়,
তাহলে সেটি জোর করে ব্যবহার করবে না।
"""

    return call_groq_ai(
        prompt,
        conversation_history=st.session_state.messages
    )


# =========================================================
# ARDUINO SETTINGS
# =========================================================

st.sidebar.subheader("🔌 Arduino")

port = st.sidebar.selectbox(
    "Arduino Port নির্বাচন করুন",
    [
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "/dev/ttyUSB0",
        "/dev/ttyACM0"
    ]
)

baud_rate = st.sidebar.selectbox(
    "Baud Rate",
    [9600, 115200],
    index=0
)


def connect_arduino(selected_port):

    try:

        if (
            st.session_state.arduino is not None
            and st.session_state.arduino.is_open
            and st.session_state.arduino_port == selected_port
        ):
            return st.session_state.arduino

        if st.session_state.arduino is not None:

            try:
                st.session_state.arduino.close()
            except Exception:
                pass

        ser = serial.Serial(
            selected_port,
            baud_rate,
            timeout=1
        )

        st.session_state.arduino = ser
        st.session_state.arduino_port = selected_port

        return ser

    except Exception:

        st.session_state.arduino = None
        st.session_state.arduino_port = None

        return None


# =========================================================
# MAIN MODE
# =========================================================

arduino = connect_arduino(port)

# =========================================================
# SENSOR MODE
# =========================================================

if arduino:

    st.success(
        "✅ Sensor Booth Connected — Mode 1: Sensor AI সক্রিয়"
    )

    col1, col2 = st.columns([1, 2])

    # -----------------------------------------------------
    # SENSOR PANEL
    # -----------------------------------------------------

    with col1:

        st.subheader("📊 Live Sensor Data")

        demo_mode = st.checkbox(
            "🧪 Demo / Test Mode",
            value=True
        )

        if demo_mode:

            temp = st.slider(
                "🌡️ শরীরের তাপমাত্রা (°F)",
                95.0,
                105.0,
                98.6,
                0.1
            )

            heart_rate = st.slider(
                "💓 Heart Rate (BPM)",
                40,
                180,
                75
            )

            spo2 = st.slider(
                "🩸 SpO₂ (%)",
                80,
                100,
                98
            )

        else:

            temp = 98.6
            heart_rate = 75
            spo2 = 98

            if arduino.in_waiting > 0:

                try:

                    line = arduino.readline().decode(
                        "utf-8",
                        errors="ignore"
                    ).strip()

                    parts = line.split(",")

                    if len(parts) == 3:

                        temp = float(parts[0])
                        heart_rate = int(parts[1])
                        spo2 = int(parts[2])

                except Exception:
                    pass

        # -------------------------------------------------
        # METRICS
        # -------------------------------------------------

        st.metric(
            "🌡️ Temperature",
            f"{temp:.1f} °F"
        )

        st.metric(
            "💓 Heart Rate",
            f"{heart_rate} BPM"
        )

        st.metric(
            "🩸 SpO₂",
            f"{spo2} %"
        )

        st.divider()

        st.subheader("📌 Sensor Summary")

        sensor_data = {
            "Temperature": f"{temp:.1f} °F",
            "Heart Rate": f"{heart_rate} BPM",
            "SpO₂": f"{spo2} %"
        }

        st.json(sensor_data)

    # -----------------------------------------------------
    # AI ANALYSIS
    # -----------------------------------------------------

    with col2:

        st.subheader("🤖 AI Health Analysis")

        if st.button(
            "📈 Sensor Data AI দিয়ে বিশ্লেষণ করুন",
            use_container_width=True
        ):

            with st.spinner(
                "🧠 AI sensor data বিশ্লেষণ করছে..."
            ):

                report = analyze_vitals(
                    temp,
                    heart_rate,
                    spo2
                )

            st.markdown(report)

            # Save report to memory
            save_message(
                "user",
                f"""
Sensor Report Request:

Temperature: {temp} °F
Heart Rate: {heart_rate} BPM
SpO₂: {spo2} %
"""
            )

            save_message(
                "assistant",
                report
            )

            st.session_state.messages.append({
                "role": "user",
                "content": (
                    f"Sensor data: "
                    f"Temperature {temp} °F, "
                    f"Heart Rate {heart_rate} BPM, "
                    f"SpO₂ {spo2}%"
                )
            })

            st.session_state.messages.append({
                "role": "assistant",
                "content": report
            })


# =========================================================
# CHATBOT MODE
# =========================================================

else:

    st.warning(
        "⚠️ Arduino sensor পাওয়া যায়নি। "
        "Mode 2: AI Chatbot সক্রিয়।"
    )

    st.subheader("🤖 MUSHFIK AI Health Chat")

    st.caption(
        "আগের কথোপকথনের context ব্যবহার করে AI উত্তর দেওয়ার চেষ্টা করবে।"
    )

    # -----------------------------------------------------
    # DISPLAY HISTORY
    # -----------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(
                message["content"]
            )

    # -----------------------------------------------------
    # CHAT INPUT
    # -----------------------------------------------------

    user_prompt = st.chat_input(
        "আপনার সমস্যা, প্রশ্ন বা লক্ষণ লিখুন..."
    )

    if user_prompt:

        # User message
        with st.chat_message("user"):

            st.markdown(user_prompt)

        save_message(
            "user",
            user_prompt
        )

        st.session_state.messages.append({
            "role": "user",
            "content": user_prompt
        })

        # AI response
        with st.chat_message("assistant"):

            with st.spinner(
                "🧠 আগের কথোপকথনসহ AI উত্তর তৈরি করছে..."
            ):

                response = ask_chatbot(
                    user_prompt
                )

            st.markdown(response)

        save_message(
            "assistant",
            response
        )

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })


# =========================================================
# SIDEBAR PROJECT INFORMATION
# =========================================================

st.sidebar.divider()

st.sidebar.subheader("📚 Project Features")

st.sidebar.markdown("""
- 🧠 AI Conversation Memory
- 💾 SQLite Persistent Memory
- 🤖 Advanced AI Responses
- 🌡️ Temperature Monitoring
- 💓 Heart Rate Monitoring
- 🩸 SpO₂ Monitoring
- 🔌 Arduino Integration
- 📊 AI Sensor Analysis
- 🇧🇩 Bengali AI Interface
- ⚠️ Safety-focused Health Guidance
""")

st.sidebar.divider()

st.sidebar.caption(
    "MUSHFIK'S HEALTH ASSISTANT AI\n"
    "Science Fair Project"
)
```
