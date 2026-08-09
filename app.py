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


st.markdown("""
<style>
[data-testid="stAppViewContainer"]{
    background:
      radial-gradient(circle at 10% 0%,rgba(14,165,233,.12),transparent 28%),
      radial-gradient(circle at 90% 5%,rgba(37,99,235,.10),transparent 25%),
      #07111f;
}
[data-testid="stHeader"]{background:rgba(7,17,31,.72);}
.main .block-container{max-width:1450px;padding-top:1.8rem;padding-bottom:3rem;}
section[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#0b1730 0%,#0a1428 55%,#08111f 100%);
    border-right:1px solid rgba(148,163,184,.12);
}
section[data-testid="stSidebar"]>div{padding-top:1.2rem;}
section[data-testid="stSidebar"] hr{border-color:rgba(148,163,184,.14);}
.mushfik-hero{
    position:relative;overflow:hidden;padding:28px 30px;margin-bottom:18px;
    border:1px solid rgba(56,189,248,.18);border-radius:24px;
    background:linear-gradient(135deg,rgba(14,165,233,.16),
    rgba(37,99,235,.08) 45%,rgba(15,23,42,.55));
    box-shadow:0 20px 55px rgba(0,0,0,.22);
}
.mushfik-hero:after{
    content:"";position:absolute;width:190px;height:190px;right:-70px;top:-90px;
    border-radius:50%;background:rgba(56,189,248,.11);
}
.hero-kicker{color:#7dd3fc;font-size:.78rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px;}
.hero-title{color:#f8fafc;font-size:clamp(1.8rem,3vw,2.65rem);line-height:1.1;font-weight:800;margin:0;}
.hero-subtitle{color:#94a3b8;margin-top:10px;font-size:1rem;}
.status-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px;}
.status-card{padding:15px 17px;border-radius:16px;background:rgba(15,23,42,.68);border:1px solid rgba(148,163,184,.12);}
.status-label{color:#94a3b8;font-size:.75rem;margin-bottom:5px;}
.status-value{color:#e2e8f0;font-weight:700;}
.status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px;background:#22c55e;box-shadow:0 0 12px rgba(34,197,94,.7);}
[data-testid="stMetric"]{padding:16px 18px;border-radius:17px;background:linear-gradient(145deg,rgba(15,23,42,.94),rgba(17,30,53,.74));border:1px solid rgba(56,189,248,.12);}
[data-testid="stMetricLabel"]{color:#94a3b8 !important;}
[data-testid="stMetricValue"]{color:#f8fafc !important;font-weight:800;}
.stButton>button{border-radius:13px;border:1px solid rgba(56,189,248,.20);background:linear-gradient(135deg,#0ea5e9,#2563eb);color:white;font-weight:700;min-height:44px;box-shadow:0 8px 22px rgba(37,99,235,.20);transition:all .18s ease;}
.stButton>button:hover{transform:translateY(-1px);border-color:rgba(125,211,252,.55);box-shadow:0 12px 28px rgba(37,99,235,.30);}
[data-baseweb="select"]>div,.stTextInput input,.stTextArea textarea{border-radius:12px !important;}
[data-testid="stChatMessage"]{border-radius:18px;border:1px solid rgba(148,163,184,.08);margin-bottom:10px;}
[data-testid="stChatInput"]{border-radius:18px;}
[data-testid="stAlert"]{border-radius:15px;border:1px solid rgba(148,163,184,.12);}
.mushfik-footer{text-align:center;color:#64748b;font-size:.78rem;padding:22px 0 8px;}
@media(max-width:800px){.status-grid{grid-template-columns:1fr;}.mushfik-hero{padding:22px;}.main .block-container{padding-left:1rem;padding-right:1rem;}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="mushfik-hero">
    <div class="hero-kicker">🩺 Intelligent Health Assistant</div>
    <div class="hero-title">MUSHFIK'S HEALTH ASSISTANT AI</div>
    <div class="hero-subtitle">
        স্মার্ট স্বাস্থ্য-তথ্য, context-aware conversation এবং sensor analysis —
        একটি পরিষ্কার ও আধুনিক interface-এ।
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="status-grid">
    <div class="status-card"><div class="status-label">AI ENGINE</div><div class="status-value"><span class="status-dot"></span>Ready</div></div>
    <div class="status-card"><div class="status-label">CONVERSATION</div><div class="status-value">🧠 Context Aware</div></div>
    <div class="status-card"><div class="status-label">SENSOR MODE</div><div class="status-value">🔌 Arduino Supported</div></div>
</div>
""", unsafe_allow_html=True)

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

SYSTEM_PROMPT = """
তুমি "MUSHFIK'S HEALTH ASSISTANT AI" নামের একটি উন্নত
শিক্ষামূলক AI Health Assistant।

তোমার কাজ হলো ব্যবহারকারীর প্রশ্ন, লক্ষণ, sensor data এবং
আগের conversation context বিশ্লেষণ করে পরিষ্কার, যুক্তিসঙ্গত,
সহানুভূতিশীল এবং সহজবোধ্য স্বাস্থ্য-তথ্য প্রদান করা।

সবসময় স্বাভাবিক ও ভদ্র বাংলায় উত্তর দেবে।

============================================================
সবচেয়ে গুরুত্বপূর্ণ নিয়ম: আগে ANALYZE, তারপর RECOMMEND
============================================================

প্রতিটি প্রশ্নের উত্তরে স্বয়ংক্রিয়ভাবে বা অভ্যাসবশত
"ডাক্তারের কাছে যান", "ডাক্তারের পরামর্শ নিন",
"doctor দেখান" অথবা "healthcare professional-এর সাথে দেখা করুন"
বলবে না।

প্রথমে ব্যবহারকারীর প্রশ্ন ও context বিশ্লেষণ করবে।

তারপর পরিস্থিতিকে নিচের স্তরগুলোর একটি হিসেবে বিবেচনা করবে।

LEVEL 1 — সাধারণ / কম ঝুঁকির বিষয়
---------------------------------
যদি প্রশ্ন বা লক্ষণ সাধারণ হয় এবং গুরুতর warning sign না থাকে:

- সরাসরি প্রশ্নের উত্তর দাও।
- সাধারণ সম্ভাব্য কারণ ব্যাখ্যা করো।
- নিরাপদ সাধারণ করণীয় বলো।
- অপ্রয়োজনীয়ভাবে doctor দেখানোর পরামর্শ দেবে না।

LEVEL 2 — পর্যবেক্ষণ প্রয়োজন
-----------------------------
যদি বিষয়টি আপাতত খুব গুরুতর না মনে হয়, কিন্তু পরিবর্তন
হলে গুরুত্ব পেতে পারে:

- কী observe করতে হবে বলো।
- কোন পরিবর্তন হলে বিষয়টি বেশি গুরুত্বপূর্ণ হবে তা বলো।
- শুধু প্রয়োজনীয় পরিস্থিতিতে medical evaluation-এর কথা বলো।

LEVEL 3 — medical evaluation বিবেচনা করা উচিত
----------------------------------------------
যদি symptoms, duration, severity, repeated pattern বা
sensor data দেখে যুক্তিসঙ্গতভাবে মনে হয় যে professional
medical evaluation প্রয়োজন হতে পারে:

- কেন বিষয়টি গুরুত্বপূর্ণ তা সংক্ষেপে ব্যাখ্যা করো।
- কোন তথ্য বা warning sign-এর কারণে এমন মনে হচ্ছে তা বলো।
- তখন চিকিৎসা সহায়তা নেওয়ার পরামর্শ দাও।

EMERGENCY / URGENT LEVEL
------------------------
যদি ব্যবহারকারীর কথায় গুরুতর বা জরুরি বিপদের স্পষ্ট লক্ষণ থাকে:

- বিষয়টি জরুরি হিসেবে পরিষ্কারভাবে উল্লেখ করো।
- একজন responsible adult-এর সাহায্য নেওয়া এবং জরুরি
  চিকিৎসা সহায়তা নেওয়ার পরামর্শ দাও।

============================================================
IMPORTANT BEHAVIOR RULES
============================================================

1. প্রতিটি উত্তরের শেষে automatic doctor recommendation দেবে না।

2. শুধু disclaimer দেওয়ার জন্য "ডাক্তারের কাছে যান" বলবে না।

3. ব্যবহারকারীর প্রশ্ন ছোট হলে অপ্রয়োজনীয় বড় lecture দেবে না।

4. সাধারণ health question হলে সরাসরি উত্তর দেবে।

5. কোনো রোগকে নিশ্চিত diagnosis হিসেবে ঘোষণা করবে না।

6. "সম্ভাব্য", "হতে পারে", "অনেক ক্ষেত্রে" ইত্যাদি ভাষা ব্যবহার করবে।

7. একটি মাত্র abnormal sensor value দেখেই ভয় দেখাবে না।

8. Sensor data-এর accuracy, measurement error এবং context বিবেচনা করবে।

9. Symptoms-এর severity, duration, frequency এবং relevant context
   থাকলে সেগুলো বিবেচনা করবে।

10. আগের conversation বর্তমান প্রশ্নের সাথে সম্পর্কিত হলে memory ব্যবহার করবে।

11. আগের conversation সম্পর্কিত না হলে জোর করে ব্যবহার করবে না।

12. একই বিষয় আগে আলোচনা হয়ে থাকলে আগের তথ্যের সাথে সামঞ্জস্য রাখবে।

13. অপ্রয়োজনীয় ভয় বা panic তৈরি করবে না।

14. Prescription-style medication instructions দেবে না।

15. শিশু/কিশোর ব্যবহারকারীর ক্ষেত্রে কোনো গুরুতর বা উদ্বেগজনক
    বিষয় হলে responsible adult-এর সাহায্য নিতে উৎসাহিত করবে।

============================================================
RESPONSE STYLE
============================================================

প্রয়োজন অনুযায়ী section ব্যবহার করবে।
প্রতিটি উত্তরে সব section ব্যবহার করা বাধ্যতামূলক নয়।

📋 সম্ভাব্য কারণ / ব্যাখ্যা

✅ কী করা যেতে পারে

👀 কী পর্যবেক্ষণ করা উচিত

⚠️ কখন বিষয়টি গুরুত্বপূর্ণ হয়ে উঠতে পারে

🏥 চিকিৎসা সহায়তা প্রয়োজন কি না
(শুধুমাত্র analysis অনুযায়ী প্রয়োজন মনে হলে এই section দেখাবে)

তুমি একজন AI Health Assistant।
তুমি definitive diagnosis বা prescription দেবে না।
"""

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

st.sidebar.markdown("""
<div style="padding:4px 2px 12px;">
<div style="font-size:1.35rem;font-weight:800;color:#f8fafc;">⚙️ Control Center</div>
<div style="font-size:.78rem;color:#64748b;margin-top:4px;">MUSHFIK'S HEALTH AI</div>
</div>
""", unsafe_allow_html=True)

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
                "🧠 MUSHFIK'S HEALTH AI উত্তর তৈরি করছে..."
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
# SIDEBAR FEATURES / FOOTER
# =========================================================

st.sidebar.divider()
st.sidebar.subheader("✨ Features")

st.sidebar.markdown("""
<div style="background:rgba(15,23,42,.58);border:1px solid rgba(148,163,184,.10);border-radius:16px;padding:14px;line-height:1.9;color:#cbd5e1;">
🧠 AI Conversation Memory<br>
💾 SQLite Persistent Memory<br>
🤖 Advanced Bengali AI<br>
🌡️ Temperature Monitoring<br>
💓 Heart Rate Monitoring<br>
🩸 SpO₂ Monitoring<br>
🔌 Arduino Integration<br>
📊 AI Sensor Analysis<br>
💬 Context-Aware Chat<br>
⚠️ Risk-Based Health Guidance<br>
🇧🇩 Bengali Interface
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="text-align:center;margin-top:18px;padding:12px;color:#64748b;font-size:.75rem;">
🩺 <b style="color:#94a3b8;">MUSHFIK'S HEALTH AI</b><br>
Intelligent • Context-Aware • Bengali
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="mushfik-footer">
MUSHFIK'S HEALTH AI • Smart Health Assistant
</div>
""", unsafe_allow_html=True)
