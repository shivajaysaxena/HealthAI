# 🩺 AI Medical Assistant

A voice-based health symptom analyzer that transcribes speech in multiple Indian languages, translates to English, and provides AI-powered medical analysis.

## 🌟 About the Project

This application allows users to:
- Record their symptoms in any supported Indian language
- Get automatic transcription using Sarvam AI
- Translate the transcript to English
- Receive AI-generated medical analysis with specialist recommendations using Mistral AI

**Supported Languages:** Hindi, English, Bengali, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu, Gujarati

## 📁 Project Structure

```
medical-assistant/
│
├── app.py                      # Main Streamlit application
│
├── modules/
│   ├── speech_to_text.py       # Sarvam AI speech-to-text
│   ├── translate.py            # Sarvam AI translation
│   └── llm_analysis.py         # Mistral AI medical analysis
│
├── .env                        # API keys (create this file)
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation
```

## 🚀 How to Run

### 1. Clone the Repository
```bash
git clone <repository-url>
cd medical-assistant
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

For PyAudio installation:
- **Windows:** `pip install pipwin && pipwin install pyaudio`
- **macOS:** `brew install portaudio && pip install pyaudio`
- **Linux:** `sudo apt-get install portaudio19-dev python3-pyaudio && pip install pyaudio`

### 3. Get API Keys

- **Sarvam AI:** Sign up at [dashboard.sarvam.ai](https://dashboard.sarvam.ai)
- **Mistral AI:** Sign up at [console.mistral.ai](https://console.mistral.ai)

### 4. Create `.env` File

Create a `.env` file in the project root:
```
SARVAM_API_KEY=your_sarvam_api_key
MISTRAL_API_KEY=your_mistral_api_key
```

### 5. Run the Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📖 Usage

1. Click **"🎤 Start Recording"** and speak your symptoms
2. Click **"⏹️ Stop Recording"** when done
3. Click **"🩺 Process Audio"** to analyze
4. View the transcript, translation, and medical analysis

## ⚠️ Disclaimer

This is for educational purposes only and not a substitute for professional medical advice.

## 🛠️ Technologies

- Streamlit - Web interface
- Sarvam AI - Speech-to-text & Translation
- Mistral AI - Medical analysis
- PyAudio - Audio recording