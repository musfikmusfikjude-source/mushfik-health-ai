import streamlit as st
import requests
import sqlite3
from datetime import datetime
import serial

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MUSHFIK'S HEALTH ASSISTANT AI",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 MUSHFIK'S HEALTH ASSISTANT AI")
st.caption("নবম শ্রেণীর বিজ্ঞান মেলার জন্য তৈরি একটি Dual-Mode AI Health Assistant")

st.info(
    "ℹ️ এটি একটি শিক্ষামূলক স্বাস্থ্য-সহায়ক প্রজেক্ট। "
    "AI-এর তথ্য সরাসরি চিকিৎসকের বিকল্প নয়।"
)

# =========================================================
# GROQ API KEY
# Streamlit Cloud:
# Manage app → Settings → Secrets
#
# GROQ_API_KEY = "YOUR_NEW_KEY"
# =========================================================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = ""

# =========================================================
# DATABASE
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
        (role, content, datetime.now().isoformat())
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
        {"role": role, "content": content}
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
# AI SYSTEM PROMPT
# =========================================================

# =========================================================
# SPECIAL GREETING RESPONSES
# =========================================================

GREETING_RESPONSES = {
    "hello": (
        "হ্যালো! আমি MUSHFIK'S HEALTH AI। "
        "আপনার স্বাস্থ্য-সংক্রান্ত কোনো প্রশ্ন, লক্ষণ বা উদ্বেগ থাকলে "
        "আমাকে বলতে পারেন। আপনি যে তথ্য দেবেন, সেগুলো বিশ্লেষণ করে "
        "সহজ ও পরিষ্কারভাবে বিষয়টি বুঝতে সাহায্য করব।"
    ),

    "hi": (
        "হাই! আমি MUSHFIK'S HEALTH AI। "
        "আপনার স্বাস্থ্য-সংক্রান্ত প্রশ্ন বা কোনো লক্ষণ থাকলে "
        "আমাকে বলতে পারেন।"
    ),

    "hey": (
        "হেই! আমি MUSHFIK'S HEALTH AI। "
        "আপনার কী নিয়ে জানতে ইচ্ছে করছে?"
    ),

    "হ্যালো": (
        "হ্যালো! আমি MUSHFIK'S HEALTH AI। "
        "আপনার স্বাস্থ্য-সংক্রান্ত কোনো প্রশ্ন, লক্ষণ বা উদ্বেগ থাকলে "
        "আমাকে বলতে পারেন।"
    ),

    "হাই": (
        "হাই! আমি MUSHFIK'S HEALTH AI। "
        "আপনার স্বাস্থ্য-সংক্রান্ত প্রশ্ন বা কোনো লক্ষণ থাকলে "
        "আমাকে বলতে পারেন।"
    ),

    "হেই": (
        "হেই! আমি MUSHFIK'S HEALTH AI। "
        "আপনার কী নিয়ে জানতে ইচ্ছে করছে?"
    )
}


# =========================================================
# CHECK WHETHER USER IS JUST GREETING
# =========================================================

def get_greeting_response(text):
    """
    শুধু greeting হলে সরাসরি response দেয়।
    এতে greeting Groq medical analysis-এর মধ্যে যাবে না।
    """

    cleaned = text.strip().lower()

    # Extra punctuation remove
    cleaned = cleaned.replace("!", "")
    cleaned = cleaned.replace("?", "")
    cleaned = cleaned.replace(".", "")
    cleaned = cleaned.replace(",", "")
    cleaned = cleaned.replace("।", "")

    # Multiple spaces normalize
    cleaned = " ".join(cleaned.split())

    if cleaned in GREETING_RESPONSES:
        return GREETING_RESPONSES[cleaned]

    return None


# =========================================================
# ADVANCED CHATBOT RESPONSE
# =========================================================

def ask_chatbot(question):

    # -----------------------------------------
    # STEP 1 — CHECK GREETING FIRST
    # -----------------------------------------

    greeting_response = get_greeting_response(question)

    if greeting_response is not None:
        return greeting_response

    # -----------------------------------------
    # STEP 2 — HEALTH QUESTION
    # -----------------------------------------

    previous_messages = st.session_state.messages[:-1]

    response = call_groq_ai(
        question,
        history=previous_messages
    )

    return response

# =========================================================
# GROQ FUNCTION
# =========================================================


def call_groq_ai(user_prompt, history=None):
    if not GROQ_API_KEY:
        return (
            "⚠️ Groq API Key পাওয়া যায়নি।\n\n"
            "Streamlit Cloud-এর **Manage app → Settings → Secrets** "
            "এ গিয়ে `GROQ_API_KEY` সেট করুন।"
        )

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # সর্বশেষ 20টি message context হিসেবে পাঠানো হবে।
    # এতে memory থাকবে, কিন্তু request অতিরিক্ত বড় হবে না।
    if history:
        for message in history[-20:]:
            messages.append({
                "role": message["role"],
                "content": message["content"]
            })

    messages.append({
        "role": "user",
        "content": user_prompt
    })

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.35,
        "max_tokens": 1800
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]

        try:
            error_data = response.json()
            return (
                f"⚠️ Groq API Error ({response.status_code})\n\n"
                f"{error_data}"
            )
        except Exception:
            return f"⚠️ Groq API Error: {response.status_code}"

    except requests.exceptions.Timeout:
        return "⏱️ AI server response দিতে বেশি সময় নিচ্ছে। আবার চেষ্টা করুন।"

    except requests.exceptions.ConnectionError:
        return "🌐 Internet connection সমস্যা হয়েছে।"

    except Exception as error:
        return f"⚠️ Unexpected error: {error}"


# =========================================================
# SENSOR ANALYSIS
# =========================================================


def analyze_vitals(temp, heart_rate, spo2):
    prompt = f"""
একজন ব্যবহারকারীর বর্তমান sensor measurements:

🌡️ Temperature: {temp:.1f} °F
💓 Heart Rate: {heart_rate} BPM
🩸 SpO₂: {spo2} %

এই তিনটি measurement একসাথে বিশ্লেষণ করো।

প্রথমে analysis করো:

1. প্রতিটি measurement সাধারণভাবে কেমন দেখাচ্ছে।
2. কোনো value উল্লেখযোগ্যভাবে অস্বাভাবিক কি না।
3. তিনটি measurement একসাথে বিবেচনা করলে কোনো গুরুত্বপূর্ণ pattern আছে কি না।
4. Sensor বা measurement error-এর সম্ভাবনা আছে কি না।
5. User-এর symptoms জানা না থাকায় কোন conclusions করা যাবে না।

তারপর পরিস্থিতি অনুযায়ী উত্তর দাও।

যদি measurements মোটামুটি স্বাভাবিক দেখায়:
- স্বাভাবিকভাবে ব্যাখ্যা করো।
- অপ্রয়োজনীয়ভাবে doctor দেখানোর কথা বলবে না।

যদি কোনো measurement একটু আলাদা হয় কিন্তু immediate concern না হয়:
- কীভাবে measurement পুনরায় যাচাই করা যায় তার সাধারণ নিরাপদ পরামর্শ দাও।
- কী observe করতে হবে বলো।
- অযথা ভয় দেখাবে না।

যদি measurements বা তাদের combination দেখে medical evaluation
যুক্তিসঙ্গতভাবে প্রয়োজন হতে পারে:
- কোন measurement বা pattern-এর কারণে এমন মনে হচ্ছে তা ব্যাখ্যা করো।
- তখন medical help নেওয়ার কথা বলো।

যদি গুরুতর warning sign-এর সাথে compatible measurement পাওয়া যায়:
- বিষয়টি urgent হিসেবে উল্লেখ করো।
- responsible adult-এর সাহায্য নেওয়ার কথা বলো।

কোনো definitive diagnosis দেবে না।
"""

    return call_groq_ai(
        prompt,
        history=st.session_state.messages
    )


# =========================================================
# CHATBOT
# =========================================================


def ask_chatbot(question):
    prompt = f"""
ব্যবহারকারীর বর্তমান প্রশ্ন:

{question}

আগের conversation context মনোযোগ দিয়ে বিশ্লেষণ করো।

বর্তমান প্রশ্নের সাথে আগের কোনো symptom, measurement,
সময়কাল বা concern সম্পর্কিত হলে সেই তথ্য ব্যবহার করো।

প্রথমে প্রশ্নটি analyze করবে।
তারপর risk অনুযায়ী উত্তর দেবে।

শুধুমাত্র প্রয়োজন হলে medical evaluation-এর কথা বলবে।
সাধারণ প্রশ্নে অপ্রয়োজনীয় doctor recommendation দেবে না।
"""

    return call_groq_ai(
        prompt,
        history=st.session_state.messages
    )


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Settings")

st.sidebar.subheader("🧠 AI Memory")

if st.sidebar.button(
    "🗑️ Conversation Memory মুছে ফেলুন",
    use_container_width=True
):
    clear_memory()
    st.session_state.messages = []
    st.rerun()

st.sidebar.caption(
    f"বর্তমান Memory: {len(st.session_state.messages)} টি message"
)

st.sidebar.divider()

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


# =========================================================
# ARDUINO CONNECTION
# =========================================================


def connect_arduino(selected_port):
    try:
        current = st.session_state.arduino

        if (
            current is not None
            and current.is_open
            and st.session_state.arduino_port == selected_port
        ):
            return current

        if current is not None:
            try:
                current.close()
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


arduino = connect_arduino(port)


# =========================================================
# MODE 1: SENSOR MODE
# =========================================================

if arduino:

    st.success(
        "✅ Sensor Booth Connected — Mode 1: Sensor AI সক্রিয়"
    )

    col1, col2 = st.columns([1, 2])

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

        st.write({
            "Temperature": f"{temp:.1f} °F",
            "Heart Rate": f"{heart_rate} BPM",
            "SpO₂": f"{spo2} %"
        })

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

            sensor_request = (
                f"Sensor data: "
                f"Temperature {temp:.1f} °F, "
                f"Heart Rate {heart_rate} BPM, "
                f"SpO₂ {spo2}%"
            )

            save_message("user", sensor_request)
            save_message("assistant", report)

            st.session_state.messages.append({
                "role": "user",
                "content": sensor_request
            })

            st.session_state.messages.append({
                "role": "assistant",
                "content": report
            })


# =========================================================
# MODE 2: AI CHATBOT
# =========================================================

else:

    st.warning(
        "⚠️ Arduino sensor পাওয়া যায়নি। "
        "Mode 2: AI Chatbot সক্রিয়।"
    )

    st.subheader("🤖 MUSHFIK AI Health Chat")

    st.caption(
        "AI আগে প্রশ্ন বিশ্লেষণ করবে এবং প্রয়োজন অনুযায়ী উত্তর দেবে। "
        "প্রতিটি প্রশ্নে automatic doctor recommendation দেওয়া হবে না।"
    )

    # Existing memory
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input(
        "আপনার সমস্যা, প্রশ্ন বা লক্ষণ লিখুন..."
    )

    if user_prompt:

        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Save user message
        save_message("user", user_prompt)

        st.session_state.messages.append({
            "role": "user",
            "content": user_prompt
        })

        with st.chat_message("assistant"):
            with st.spinner(
                "🧠 আগের কথোপকথনসহ AI উত্তর তৈরি করছে..."
            ):
                response = ask_chatbot(user_prompt)

            st.markdown(response)

        # Save AI response
        save_message("assistant", response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })


# =========================================================
# PROJECT INFORMATION
# =========================================================

st.sidebar.divider()

st.sidebar.subheader("📚 Project Features")

st.sidebar.markdown("""
- 🧠 AI Conversation Memory
- 💾 SQLite Persistent Memory
- 🤖 Advanced Bengali AI
- 🌡️ Temperature Monitoring
- 💓 Heart Rate Monitoring
- 🩸 SpO₂ Monitoring
- 🔌 Arduino Integration
- 📊 AI Sensor Analysis
- 💬 Context-Aware Chat
- ⚠️ Risk-Based Health Guidance
- 🇧🇩 Bengali Interface
""")

st.sidebar.divider()

st.sidebar.caption(
    "MUSHFIK'S HEALTH ASSISTANT AI\n"
    "Science Fair Project"
)
