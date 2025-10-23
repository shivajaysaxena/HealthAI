import streamlit as st
import pyaudio
import wave
import threading
import tempfile
import time
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from modules.speech_to_text import transcribe_audio
from modules.translate import translate_to_english
from modules.llm_analysis import analyze_symptoms_with_rag
from modules.auth import AuthSystem
from modules.rag_medical import MedicalRAG

# Initialize systems
auth = AuthSystem()
rag = MedicalRAG()

st.set_page_config(page_title="AI Medical Assistant", layout="centered", initial_sidebar_state="expanded")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "audio_file" not in st.session_state:
    st.session_state.audio_file = None
if "recording" not in st.session_state:
    st.session_state.recording = False
if "recording_thread" not in st.session_state:
    st.session_state.recording_thread = None
if "recording_event" not in st.session_state:
    st.session_state.recording_event = threading.Event()
if "page" not in st.session_state:
    st.session_state.page = "login"

def record_audio(file_path, event):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []

        while event.is_set():
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(file_path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
    except Exception as e:
        st.error(f"Recording error: {e}")
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        if 'p' in locals():
            p.terminate()

# ===== AUTHENTICATION PAGES =====

def login_page():
    st.title("🩺 AI Medical Assistant")
    st.subheader("🔐 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if username and password:
                success, result = auth.login(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user = result
                    st.success(f"Welcome back, {result['username']}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(result)
            else:
                st.warning("Please enter both username and password")
    
    st.markdown("---")
    if st.button("Don't have an account? Sign Up"):
        st.session_state.page = "signup"
        st.rerun()

def signup_page():
    st.title("🩺 AI Medical Assistant")
    st.subheader("📝 Create Account")
    
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if not (username and email and password and confirm_password):
                st.warning("Please fill all fields")
            elif password != confirm_password:
                st.error("Passwords don't match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                success, message = auth.signup(username, email, password)
                if success:
                    st.success(message)
                    st.info("Please login with your credentials")
                    time.sleep(2)
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(message)
    
    st.markdown("---")
    if st.button("Already have an account? Login"):
        st.session_state.page = "login"
        st.rerun()

# ===== MAIN APPLICATION =====

def main_app():
    # Sidebar
    with st.sidebar:
        st.title(f"👤 {st.session_state.user['username']}")
        st.markdown("---")
        
        menu = st.radio("Navigation", ["🏠 Home", "📜 History", "ℹ️ About"])
        
        st.markdown("---")
        
        # RAG Stats
        stats = rag.get_collection_stats()
        st.info(f"📚 Medical KB: {stats['total_documents']} documents")
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.audio_file = None
            st.session_state.page = "login"
            st.rerun()
    
    if menu == "🏠 Home":
        home_page()
    elif menu == "📜 History":
        history_page()
    elif menu == "ℹ️ About":
        about_page()

def home_page():
    st.title("🩺 Voice-based Health Symptom Analyzer")
    st.write("🎙️ Speak in any language — get transcript, translation, and AI-powered medical analysis with RAG.")
    
    # Recording controls
    col1, col2 = st.columns(2)

    if col1.button("🎤 Start Recording") and not st.session_state.recording:
        st.session_state.recording = True
        st.session_state.recording_event.set()
        
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        st.session_state.audio_file = temp_wav.name
        temp_wav.close()
        
        st.session_state.recording_thread = threading.Thread(
            target=record_audio, 
            args=(st.session_state.audio_file, st.session_state.recording_event), 
            daemon=True
        )
        st.session_state.recording_thread.start()
        st.info("🎙️ Recording started... Speak now!")

    if col2.button("⏹️ Stop Recording") and st.session_state.recording:
        st.session_state.recording_event.clear()
        st.session_state.recording = False
        
        if st.session_state.recording_thread:
            st.session_state.recording_thread.join(timeout=2)
        
        time.sleep(0.5)
        st.success("✅ Recording stopped!")
        
        if st.session_state.audio_file:
            try:
                with open(st.session_state.audio_file, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/wav")
            except Exception as e:
                st.error(f"Could not load audio: {e}")

    # Process audio
    if st.session_state.audio_file and not st.session_state.recording:
        if st.button("🩺 Process Audio"):
            st.info("Processing audio... please wait ⏳")
            try:
                if not os.path.exists(st.session_state.audio_file):
                    st.error("❌ Audio file not found")
                elif os.path.getsize(st.session_state.audio_file) == 0:
                    st.error("❌ Audio file is empty")
                else:
                    with st.spinner("Transcribing audio..."):
                        transcript, lang = transcribe_audio(st.session_state.audio_file)
                    
                    if transcript:
                        st.subheader("🗣️ Transcript")
                        st.write(transcript)
                        st.info(f"Detected language: {lang}")

                        with st.spinner("Translating to English..."):
                            english_text = translate_to_english(transcript)
                        
                        st.subheader("🌐 English Translation")
                        st.write(english_text)

                        with st.spinner("Analyzing symptoms with RAG..."):
                            analysis = analyze_symptoms_with_rag(english_text, rag)
                        
                        st.subheader("🩺 Medical Analysis (RAG-Enhanced)")
                        st.markdown(analysis)
                        
                        # Save to history
                        auth.save_medical_record(
                            st.session_state.user['id'],
                            transcript,
                            english_text,
                            analysis,
                            lang
                        )
                        st.success("✅ Consultation saved to your history")
                    else:
                        st.error("❌ Could not transcribe audio. Please try recording again.")
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ API Error: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    st.error(f"Response: {e.response.text}")
            except Exception as e:
                st.error(f"❌ Error processing audio: {e}")

    # Reset button
    if st.session_state.audio_file:
        if st.button("🔄 Reset / New Recording"):
            st.session_state.audio_file = None
            st.session_state.recording = False
            st.session_state.recording_event.clear()
            st.rerun()

def history_page():
    st.title("📜 Medical History")
    
    records = auth.get_user_history(st.session_state.user['id'])
    
    if not records:
        st.info("No medical consultations yet. Start by recording your symptoms!")
    else:
        st.write(f"Total consultations: {len(records)}")
        st.markdown("---")
        
        for idx, record in enumerate(records, 1):
            with st.expander(f"Consultation #{idx} - {record[5][:16]}"):
                st.subheader("🗣️ Transcript")
                st.write(record[1])
                
                st.subheader("🌐 Translation")
                st.write(record[2])
                
                st.subheader("🩺 Analysis")
                st.markdown(record[3])
                
                st.caption(f"Language: {record[4]} | Date: {record[5]}")

def about_page():
    st.title("ℹ️ About")
    
    st.markdown("""
    ### AI Medical Assistant with RAG
    
    This application uses:
    - **Speech-to-Text**: Sarvam AI
    - **Translation**: Sarvam AI
    - **Medical Analysis**: Mistral AI + RAG (Retrieval-Augmented Generation)
    - **Knowledge Base**: ChromaDB with medical information
    
    #### Features:
    - 🎤 Multi-language voice input
    - 🌐 Automatic translation
    - 🧠 RAG-enhanced medical analysis
    - 📜 Personal medical history
    - 🔐 Secure user authentication
    
    #### Supported Languages:
    Hindi, English, Bengali, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu, Gujarati
    
    ---
    
    ⚠️ **Disclaimer**: This is for educational purposes only and not a substitute for professional medical advice.
    """)

# ===== MAIN ROUTING =====

if not st.session_state.authenticated:
    if st.session_state.page == "login":
        login_page()
    else:
        signup_page()
else:
    main_app()