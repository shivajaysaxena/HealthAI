# 🩺 AI Medical Assistant - Conversational Healthcare Platform

An intelligent, multilingual medical consultation platform featuring conversational AI, voice interaction, RAG-enhanced analysis, and automatic consultation history tracking.

## ✨ Key Features

### 🤖 Conversational AI Doctor
- Interactive multi-turn conversations like a real doctor consultation
- AI asks intelligent follow-up questions (2-4 questions)
- Automatically determines when enough information is gathered
- Provides comprehensive medical analysis

### 💬 Dual Interaction Modes
- **Chat Mode**: Type-based conversation interface
- **Voice Mode**: Speak in any supported Indian language
- Seamlessly switch between modes during consultation

### 🧠 RAG-Enhanced Analysis
- Medical knowledge base with keyword-based retrieval
- Context-aware responses backed by medical references
- Urgency level detection and specialist recommendations

### 💾 Automatic History Tracking
- Consultations automatically saved when complete
- No manual save required - it just works!
- Complete conversation history preserved
- Secure, user-specific medical records

### 🔐 User Authentication
- Secure signup/login system
- Password encryption
- Personal medical history for each user
- Privacy-focused data storage

### 🌍 Multi-Language Support
Hindi, English, Bengali, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu, Gujarati

## 📁 Project Structure

```
medical-assistant/
│
├── app.py                      # Main Streamlit application
│
├── modules/
│   ├── speech_to_text.py       # Sarvam AI speech-to-text
│   ├── translate.py            # Sarvam AI translation
│   ├── auth.py                 # User authentication system
│   ├── rag_medical.py          # RAG knowledge base
│   └── conversation.py         # Conversational AI manager
│
├── medical_db/                 # Medical knowledge base (auto-created)
│   └── medical_kb.json         # JSON storage
│
├── users.db                    # SQLite user database (auto-created)
├── .env                        # API keys (create this)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Microphone access (for voice mode)
- Internet connection (for API calls)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd medical-assistant
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install PyAudio

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### Step 4: Get API Keys

#### Sarvam AI API Key
1. Visit [dashboard.sarvam.ai](https://dashboard.sarvam.ai)
2. Sign up for a free account
3. Create API key
4. Copy the key (starts with `sk_...`)

#### Mistral AI API Key
1. Visit [console.mistral.ai](https://console.mistral.ai)
2. Create account
3. Generate API key
4. Copy the key

### Step 5: Create `.env` File

Create a file named `.env` in the project root:

```env
SARVAM_API_KEY=your_sarvam_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
```

**Important:** Each key on a separate line, no quotes, no spaces around `=`

### Step 6: Run Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📖 How to Use

### First Time Setup

1. **Create Account**
   - Click "Sign Up" on login page
   - Enter username, email, and password (min 6 characters)
   - Click "Sign Up"

2. **Login**
   - Enter your credentials
   - Click "Login"

### Starting a Consultation

#### Chat Mode (Recommended)

1. Select **💬 Chat Mode**
2. Type your initial symptom
   - Example: "I have been having headaches for 3 days"
3. AI will ask follow-up questions
4. Answer each question naturally
5. After 2-4 questions, AI provides comprehensive analysis
6. ✅ **Automatically saved to your history!**
7. Click "New Consultation" to start fresh

#### Voice Mode

1. Select **🎤 Voice Mode**
2. Click "Start Recording"
3. Speak your symptom in any supported language
4. Click "Stop Recording"
5. Click "Send Voice Message"
6. AI transcribes, translates, and responds
7. Continue conversation with voice or text
8. ✅ **Automatically saved when complete!**

### Viewing History

1. Click **📜 History** in sidebar
2. View all your past consultations
3. Expand any consultation to see:
   - Initial symptom
   - Full conversation
   - Final medical analysis
   - Date and type

## 🎯 Consultation Flow Example

```
You: "I have stomach pain and nausea"
    ↓
AI Doctor: "I understand you're experiencing stomach pain and nausea. 
            To help you better:
            1. How long have you had these symptoms?
            2. Is the pain constant or does it come and go?
            3. Have you noticed any triggers like certain foods?"
    ↓
You: "Started yesterday morning. Pain comes and goes. 
      Worse after eating spicy food."
    ↓
AI Doctor: "Thank you for the details. One more question:
            Have you had any fever or diarrhea?"
    ↓
You: "No fever, but slight diarrhea this morning"
    ↓
AI Doctor: [Provides Comprehensive Analysis]

## 🩺 Medical Consultation Summary

### Symptom Overview
Based on your description of stomach pain, nausea, and diarrhea...

### Possible Conditions
1. Gastroenteritis (most likely)
2. Food poisoning
3. Gastritis

### Key Medical Points
- Symptoms started after spicy food
- Intermittent abdominal pain
- Associated with digestive upset

### Recommended Specialist
Gastroenterologist or General Physician

### Immediate Care Advice
- Stay hydrated
- Avoid spicy and fatty foods
- If symptoms worsen, seek immediate care
- Urgency Level: MEDIUM

✅ Consultation automatically saved to your history!
```

## 🛠️ Technologies Used

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Speech-to-Text | Sarvam AI (Saarika v2.5) |
| Translation | Sarvam AI (Mayura v1) |
| AI Analysis | Mistral AI (Mistral Small) |
| RAG System | Custom keyword-based |
| Database | SQLite |
| Authentication | Hashlib (SHA-256) |
| Audio Recording | PyAudio |

## ⚙️ Advanced Features

### RAG (Retrieval-Augmented Generation)
- 11+ medical knowledge documents
- Keyword-based similarity matching
- Context-aware response generation
- Urgency level detection

### Rate Limit Handling
- Automatic retry with exponential backoff
- 2-second delay between API calls
- Fallback responses when rate limited
- Graceful error handling

### Conversation Management
- Tracks consultation stages
- Smart question generation
- Knows when to stop asking questions
- Complete conversation history

### Security
- Password hashing (SHA-256)
- User-specific data isolation
- No plaintext password storage
- Secure session management

## 📊 System Requirements

- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB for application + space for medical records
- **Internet**: Required for API calls
- **Microphone**: Required for voice mode
- **Browser**: Modern browser (Chrome, Firefox, Safari, Edge)

## 🔒 Privacy & Security

- All data stored locally in SQLite database
- Passwords encrypted with SHA-256
- API keys stored in `.env` (never committed to git)
- User data isolated per account
- No data shared between users

## ⚠️ Important Disclaimers

### Medical Disclaimer
**THIS APPLICATION IS FOR EDUCATIONAL AND INFORMATIONAL PURPOSES ONLY.**

- ❌ NOT a substitute for professional medical advice, diagnosis, or treatment
- ❌ NOT intended for medical emergencies
- ❌ NOT a replacement for consulting qualified healthcare providers
- ✅ Always seek advice from licensed medical professionals
- ✅ Call emergency services (108 in India) for emergencies

### Accuracy Disclaimer
- AI responses are generated based on patterns and may not always be accurate
- Medical knowledge base is limited and may not cover all conditions
- Always verify information with healthcare professionals
- Do not make medical decisions based solely on AI advice

### Data Disclaimer
- Consultations saved locally on your device
- No cloud backup by default
- Users responsible for their own data backup
- Uninstalling may result in data loss

## 🐛 Troubleshooting

### Common Issues

**1. PyAudio Installation Error**
```bash
# Windows
pip install pipwin
pipwin install pyaudio

# If still failing, download wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install <downloaded-wheel-file>
```

**2. API Rate Limit (429 Error)**
- Wait 30-60 seconds between consultations
- App has automatic retry built-in
- Consider upgrading API plan if persistent

**3. Microphone Not Working**
- Check browser permissions
- Verify system microphone settings
- Try running with admin/sudo privileges
- Restart browser/application

**4. Database Locked Error**
- Close all instances of the app
- Delete `users.db` (will lose data)
- Restart application

**5. Audio Transcription Fails**
- Speak clearly and slowly
- Reduce background noise
- Check internet connection
- Verify Sarvam API key is valid

## 🔄 Updates & Maintenance

### Version History
- **v2.0** - Conversational AI, Auto-save, Dual modes
- **v1.5** - RAG implementation, User authentication
- **v1.0** - Basic voice transcription and analysis

### Updating
```bash
git pull origin main
pip install -r requirements.txt --upgrade
streamlit run app.py
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional medical knowledge documents
- Support for more languages
- Export to PDF feature
- Mobile app version
- Cloud sync capabilities

## 📞 Support

For issues or questions:
- Check troubleshooting section above
- Review existing issues on GitHub
- Create new issue with details:
  - Error message
  - Steps to reproduce
  - System information

## 📄 License

This project is for educational purposes. Not licensed for commercial medical use.

## 🙏 Acknowledgments

- **Sarvam AI** - Speech-to-text and translation APIs
- **Mistral AI** - Conversational AI capabilities
- **Streamlit** - Web application framework
- Medical knowledge from public health resources

---

**Made with ❤️ for improving healthcare accessibility in India**

*Remember: This is a learning tool, not a medical device. Always consult qualified healthcare professionals for medical decisions.*