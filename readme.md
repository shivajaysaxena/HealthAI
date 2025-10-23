# 🩺 **AI Medical Assistant**

### A voice-powered health symptom analyzer that listens in **multiple Indian languages**, transcribes and translates your speech into English, and delivers **AI-driven medical analysis** using Retrieval-Augmented Generation (RAG).

---

## 🚀 **Newly Added Features**

### 🔐 **User Authentication**
- Secure **Login / Signup** system  
- **Password hashing** using industry standards  
- **SQLite database** for user management  

### 📜 **Personal Medical History**
- Automatically save **all past consultations**  
- View your **complete health history** anytime  
- Acts as your **personal health record**  

### 🧠 **RAG-Powered AI Analysis**
- Integrated **ChromaDB** medical knowledge base  
- Context-aware responses with **retrieved insights**  
- Smarter and more reliable **diagnostic explanations**

---

## 🗂️ **Updated Project Structure**

```
medical-assistant/
│
├── app.py                      # Main Streamlit application (auth + RAG)
│
├── modules/
│   ├── speech_to_text.py       # Sarvam AI - Speech Recognition
│   ├── translate.py            # Sarvam AI - Translation
│   ├── llm_analysis.py         # Mistral AI - Medical Analysis with RAG
│   ├── auth.py                 # User Authentication (NEW)
│   └── rag_medical.py          # RAG Implementation (NEW)
│
├── medical_db/                 # ChromaDB vector store (auto-created)
├── users.db                    # SQLite database (auto-created)
├── .env                        # API keys
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```

---

## ⚙️ **Installation Guide**

### **1️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2️⃣ Install PyAudio (for voice input)**

**Windows**
```bash
pip install pipwin
pipwin install pyaudio
```

**macOS**
```bash
brew install portaudio
pip install pyaudio
```

**Linux**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### **3️⃣ Set Up Environment Variables**

Create a `.env` file in the project root:
```
SARVAM_API_KEY=your_sarvam_api_key
MISTRAL_API_KEY=your_mistral_api_key
```

### **4️⃣ Run the Application**
```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501)

---

## 🧾 **First-Time Setup**

1. **Sign Up** for a new account  
2. Provide **username, email, and password**  
3. Passwords must be **6+ characters**  
4. After login, your **health records** and **RAG analyses** are automatically saved  

---

## 🌟 **How It Works**

1. Click **🎤 Start Recording** and describe your symptoms in your native language  
2. Click **⏹️ Stop Recording** when done  
3. Click **🩺 Process Audio** to analyze  
4. View:
   - **Transcription** (via Sarvam AI)
   - **English Translation**
   - **Medical Analysis & Recommendations** (via Mistral AI + RAG)

---

## 🧩 **Supported Languages**

> Hindi | English | Bengali | Kannada | Malayalam | Marathi | Odia | Punjabi | Tamil | Telugu | Gujarati  

---

## 🧠 **Behind the Scenes**

| Component | Technology | Purpose |
|------------|-------------|----------|
| 🎤 Speech Recognition | Sarvam AI STT | Converts user’s speech into text |
| 🌐 Translation | Sarvam AI Translator | Translates local language → English |
| 🧠 AI Analysis | Mistral AI | Generates contextual medical insights |
| 📚 Knowledge Retrieval | ChromaDB | Provides relevant medical information |
| 🔒 Authentication | SQLite + Hashing | Manages users and data security |
| 💾 Storage | Streamlit + Local DB | Stores consultations and RAG data |

---

## ⚠️ **Disclaimer**
This application is designed **for educational and research purposes only**.  
It is **not a substitute for professional medical consultation**. Always seek advice from a certified healthcare provider.

---

## 🛠️ **Tech Stack**

- **Streamlit** – Interactive web interface  
- **Sarvam AI** – Speech recognition & translation  
- **Mistral AI** – Large language model for medical insights  
- **ChromaDB** – Vector-based medical knowledge retrieval  
- **SQLite** – Lightweight database for users & records  
- **PyAudio** – Real-time voice recording  

---

## 📦 **Quick Start**

```bash
# Clone the repository
git clone <repository-url>
cd medical-assistant

# Install dependencies
pip install -r requirements.txt

# Configure API keys
echo "SARVAM_API_KEY=your_sarvam_api_key" >> .env
echo "MISTRAL_API_KEY=your_mistral_api_key" >> .env

# Run the app
streamlit run app.py
```

---

## ❤️ **Contributors**
**Developed by:** [Shivajay Saxena](https://github.com/shivajaysaxena)
