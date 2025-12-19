import streamlit as st
from PIL import Image
import requests, numpy as np, tempfile
from gtts import gTTS

# ---------------- CAMERA ----------------
try:
    from streamlit_camera_input import camera_input
    CAMERA = True
except:
    CAMERA = False

st.set_page_config(page_title="Farm Assist", layout="centered")

# ---------------- BACK BUTTON STYLE ----------------
st.markdown("""
<style>
.back-btn {
    position: fixed;
    bottom: 20px;
    left: 20px;
    z-index: 9999;
}
.center {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = 1

# ---------------- WEATHER ----------------
API_KEY = "509887fc92045e1768a7d412cd7c9d1c"

CITIES = [
    "Delhi","Mumbai","Chennai","Kolkata","Hyderabad","Bengaluru","Pune","Nagpur",
    "Warangal","Vijayawada","Guntur","Vizag","Tirupati","Madurai","Coimbatore",
    "Mysuru","Hubli","Belagavi","Nashik","Indore","Bhopal","Jaipur","Udaipur",
    "Jodhpur","Aurangabad","Amravati","Kolhapur","Solapur","Nellore","Kurnool"
]

# ---------------- DISEASES ----------------
DISEASES = {
    "Healthy":"✅","Leaf Blight":"🍂","Rust":"🔴","Brown Spot":"🟤",
    "Root Rot":"🌱","Stem Rot":"🪵","Powdery Mildew":"⚪",
    "Downy Mildew":"💧","Wilt":"🦠","Leaf Curl":"🍃"
}

# ---------------- SOIL ----------------
SOILS = {
    "Alluvial":"Rice, Wheat – Maintain moisture",
    "Black":"Cotton – Improve drainage",
    "Red":"Millets – Add compost",
    "Laterite":"Tea, Coffee – Control pH",
    "Sandy":"Groundnut – Frequent irrigation",
    "Clay":"Paddy – Drain excess water",
    "Loamy":"Vegetables – Balanced nutrients"
}

# ---------------- LANGUAGES ----------------
LANG = {
    "English":{"dashboard":"Dashboard","weather":"Weather","soil":"Soil","pest":"Pest Detection","chat":"Farmer Chat","settings":"Settings","solution":"Apply recommended treatment immediately","rain":"Rain Alert","temp":"Temperature","humidity":"Humidity"},
    "Hindi":{"dashboard":"डैशबोर्ड","weather":"मौसम","soil":"मिट्टी","pest":"कीट पहचान","chat":"किसान चैट","settings":"सेटिंग्स","solution":"तुरंत उपचार करें","rain":"बारिश चेतावनी","temp":"तापमान","humidity":"नमी"},
    "Telugu":{"dashboard":"డాష్‌బోర్డ్","weather":"వాతావరణం","soil":"మట్టి","pest":"పురుగు గుర్తింపు","chat":"రైతు చాట్","settings":"సెట్టింగ్స్","solution":"తక్షణమే చికిత్స చేయండి","rain":"వర్ష హెచ్చరిక","temp":"ఉష్ణోగ్రత","humidity":"ఆర్ద్రత"},
    "Tamil":{"dashboard":"டாஷ்போர்டு","weather":"வானிலை","soil":"மண்","pest":"பூச்சி கண்டறிதல்","chat":"விவசாயி அரட்டை","settings":"அமைப்புகள்","solution":"உடனடியாக பரிந்துரைக்கப்பட்ட சிகிச்சையை செய்யவும்","rain":"மழை எச்சரிக்கை","temp":"வெப்பநிலை","humidity":"ஈரப்பதம்"},
    "Kannada":{"dashboard":"ಡ್ಯಾಶ್‌ಬೋರ್ಡ್","weather":"ಹವಾಮಾನ","soil":"ಮಣ್ಣು","pest":"ಕೀಟ ಗುರುತು","chat":"ರೈತ ಚಾಟ್","settings":"ಸೆಟ್ಟಿಂಗ್ಗಳು","solution":"ತಕ್ಷಣ ಶಿಫಾರಸು ಮಾಡಿದ ಚಿಕಿತ್ಸೆ ಅನುಸರಿಸಿ","rain":"ಮಳೆ ಎಚ್ಚರಿಕೆ","temp":"ತಾಪಮಾನ","humidity":"ಆದ್ರತೆ"},
    "Malayalam":{"dashboard":"ഡാഷ്ബോർഡ്","weather":"കാലാവസ്ഥ","soil":"മണ്ണ്","pest":"കീട കണ്ടെത്തൽ","chat":"കർഷക ചാറ്റ","settings":"ക്രമീകരണങ്ങൾ","solution":"ഉടൻ ശുപാർശ ചെയ്ത ചികിത്സ നടപ്പാക്കുക","rain":"മഴ മുന്നറിയിപ്പ്","temp":"താപനില","humidity":"ആർദ്രത"},
    "Gujarati":{"dashboard":"ડેશબોર્ડ","weather":"હવામાન","soil":"માટી","pest":"જીવાત ઓળખ","chat":"ખેડૂત ચેટ","settings":"સેટિંગ્સ","solution":"તાત્કાલિક ભલામણ કરેલ સારવાર કરો","rain":"વરસાદ ચેતવણી","temp":"તાપમાન","humidity":"ભેજ"},
    "Punjabi":{"dashboard":"ਡੈਸ਼ਬੋਰਡ","weather":"ਮੌਸਮ","soil":"ਮਿੱਟੀ","pest":"ਕੀੜੇ ਪਛਾਣ","chat":"ਕਿਸਾਨ ਚੈਟ","settings":"ਸੈਟਿੰਗਾਂ","solution":"ਤੁਰੰਤ ਸਿਫਾਰਸ਼ੀ ਇਲਾਜ ਕਰੋ","rain":"ਬਰਸਾਤ ਚੇਤਾਵਨੀ","temp":"ਤਾਪਮਾਨ","humidity":"ਨਮੀ"},
    "Odia":{"dashboard":"ଡ୍ୟାଶବୋର୍ଡ","weather":"ଆବହାଓଆ","soil":"ମାଟି","pest":"କୀଟ ଚିହ୍ନଟ","chat":"କୃଷକ ଚାଟ","settings":"ସେଟିଂସ୍","solution":"ତୁରନ୍ତ ସୁପାରିଶିତ ଚିକିତ୍ସା କରନ୍ତୁ","rain":"ବର୍ଷା ସତର୍କତା","temp":"ତାପମାତ୍ରା","humidity":"ଆର୍ଦ୍ରତା"},
    "Bengali":{"dashboard":"ড্যাশবোর্ড","weather":"আবহাওয়া","soil":"মাটি","pest":"পোকা শনাক্তকরণ","chat":"কৃষক চ্যাট","settings":"সেটিংস","solution":"অবিলম্বে প্রস্তাবিত চিকিৎসা করুন","rain":"বৃষ্টি সতর্কতা","temp":"তাপমাত্রা","humidity":"আর্দ্রতা"}
}

# ---------------- FUNCTIONS ----------------
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

def speak(text):
    tts = gTTS(text)
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(f.name)
    return f.name

def chat_reply(q):
    return (
        "🌾 Fertilizer: Use NPK (19:19:19) every 20 days\n\n"
        "🐛 Pesticides: Neem oil spray weekly\n\n"
        "🦟 Insecticides: Imidacloprid only for heavy infestation\n\n"
        "🌿 Weeds: Manual weeding or Pendimethalin\n\n"
        "💧 Irrigation: Water every 3–4 days in morning\n\n"
        "⚠️ Follow agriculture officer advice"
    )

# ==================================================
# SCREEN FLOW
# ==================================================
if st.session_state.page == 1:
    st.markdown("<h2 class='center'>🌾 Welcome</h2>", unsafe_allow_html=True)
    st.markdown("<h1 class='center' style='color:green;'>Farm Assist 🌿</h1>", unsafe_allow_html=True)

    if st.button("🟢 Continue"):
        st.session_state.page = 2
        st.rerun()

elif st.session_state.page == 2:
    st.image("images/crop.jpg", use_column_width=True)
    if st.button("Continue ➡"):
        st.session_state.page = 3
        st.rerun()
    if st.button("⬅ Back"):
        st.session_state.page = 1
        st.rerun()

elif st.session_state.page == 3:
    # ---- BUTTONS ON TOP ----
    c1, c2 = st.columns(2)
    if c1.button("👨‍🌾 Farmer Profile"):
        st.session_state.page = 4
        st.rerun()
    if c2.button("📊 Dashboard"):
        st.session_state.page = 5
        st.rerun()

    # ---- IMAGES BELOW ----
    st.image("images/crop.jpg", use_column_width=True)
    st.image("images/soil.jpg", use_column_width=True)
    st.image("images/tools.jpg", use_column_width=True)
    st.image("images/weather.jpg", use_column_width=True)
    st.image("images/pests.jpg", use_column_width=True)

elif st.session_state.page == 4:
    st.text_input("Farmer Name")
    st.text_input("Village / District")
    st.text_input("Land Size (Acres)")
    st.text_input("Crops Grown")
    if st.button("⬅ Back"):
        st.session_state.page = 3
        st.rerun()

elif st.session_state.page == 5:
    lang = st.selectbox("🌐 Select Language", list(LANG.keys()))
    T = LANG[lang]

    st.title("📊 " + T["dashboard"])

    st.subheader("🌥️ " + T["weather"])
    city = st.selectbox("City", CITIES)
    data = get_weather(city)

    if data:
        st.write(f"{T['temp']}: {data['main']['temp']} °C")
        st.write(f"{T['humidity']}: {data['main']['humidity']} %")

        weather_type = data["weather"][0]["main"].lower()
        if "rain" in weather_type or "drizzle" in weather_type or "thunderstorm" in weather_type:
            st.warning("⚠️ " + T["rain"])
            st.audio(speak(T["rain"]))

    st.subheader("🪰 " + T["pest"])
    upload = st.file_uploader("Upload Crop Image", ["jpg","png"])
    if upload:
        img = Image.open(upload)
        st.image(img, width=220)
        disease = np.random.choice(list(DISEASES.keys()))
        st.success(DISEASES[disease] + " " + disease)
        st.audio(speak(T["solution"]))

    st.subheader("🌱 " + T["soil"])
    soil = st.selectbox("Soil Type", SOILS.keys())
    st.info(SOILS[soil])

    st.subheader("💬 " + T["chat"])
    q = st.text_input("Ask your farming problem")
    if q:
        st.success(chat_reply(q))

    if st.button("⬅ Back"):
        st.session_state.page = 3
        st.rerun()