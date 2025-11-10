# import streamlit as st
# import pyaudio
# import wave
# import threading
# import tempfile
# import time
# import requests
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# from modules.speech_to_text import transcribe_audio
# from modules.translate import translate_to_english
# from modules.text_to_speech import text_to_speech, translate_from_english
# from modules.auth import AuthSystem
# from modules.rag_medical import MedicalRAG
# from modules.conversation import MedicalConversation

# # Initialize systems
# auth = AuthSystem()
# rag = MedicalRAG()

# st.set_page_config(page_title="AI Medical Assistant", layout="centered", initial_sidebar_state="expanded")

# # Initialize session state
# if "authenticated" not in st.session_state:
#     st.session_state.authenticated = False
# if "user" not in st.session_state:
#     st.session_state.user = None
# if "audio_file" not in st.session_state:
#     st.session_state.audio_file = None
# if "recording" not in st.session_state:
#     st.session_state.recording = False
# if "recording_thread" not in st.session_state:
#     st.session_state.recording_thread = None
# if "recording_event" not in st.session_state:
#     st.session_state.recording_event = threading.Event()
# if "page" not in st.session_state:
#     st.session_state.page = "login"
# if "conversation" not in st.session_state:
#     st.session_state.conversation = MedicalConversation()
# if "chat_messages" not in st.session_state:
#     st.session_state.chat_messages = []
# if "consultation_mode" not in st.session_state:
#     st.session_state.consultation_mode = "chat"  # chat or voice
# if "user_language" not in st.session_state:
#     st.session_state.user_language = "en-IN"  # Detected language
# if "voice_enabled" not in st.session_state:
#     st.session_state.voice_enabled = False  # AI voice responses on/off

# def record_audio(file_path, event):
#     CHUNK = 1024
#     FORMAT = pyaudio.paInt16
#     CHANNELS = 1
#     RATE = 16000

#     p = pyaudio.PyAudio()
    
#     try:
#         stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
#         frames = []

#         while event.is_set():
#             data = stream.read(CHUNK, exception_on_overflow=False)
#             frames.append(data)

#         stream.stop_stream()
#         stream.close()
#         p.terminate()

#         wf = wave.open(file_path, 'wb')
#         wf.setnchannels(CHANNELS)
#         wf.setsampwidth(p.get_sample_size(FORMAT))
#         wf.setframerate(RATE)
#         wf.writeframes(b''.join(frames))
#         wf.close()
#     except Exception as e:
#         st.error(f"Recording error: {e}")
#         if 'stream' in locals():
#             stream.stop_stream()
#             stream.close()
#         if 'p' in locals():
#             p.terminate()

# # ===== AUTHENTICATION PAGES =====

# def login_page():
#     st.title("🩺 AI Medical Assistant")
#     st.subheader("🔐 Login")
    
#     with st.form("login_form"):
#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")
#         submit = st.form_submit_button("Login")
        
#         if submit:
#             if username and password:
#                 success, result = auth.login(username, password)
#                 if success:
#                     st.session_state.authenticated = True
#                     st.session_state.user = result
#                     st.success(f"Welcome back, {result['username']}!")
#                     time.sleep(1)
#                     st.rerun()
#                 else:
#                     st.error(result)
#             else:
#                 st.warning("Please enter both username and password")
    
#     st.markdown("---")
#     if st.button("Don't have an account? Sign Up"):
#         st.session_state.page = "signup"
#         st.rerun()

# def signup_page():
#     st.title("🩺 AI Medical Assistant")
#     st.subheader("📝 Create Account")
    
#     with st.form("signup_form"):
#         username = st.text_input("Username")
#         email = st.text_input("Email")
#         password = st.text_input("Password", type="password")
#         confirm_password = st.text_input("Confirm Password", type="password")
#         submit = st.form_submit_button("Sign Up")
        
#         if submit:
#             if not (username and email and password and confirm_password):
#                 st.warning("Please fill all fields")
#             elif password != confirm_password:
#                 st.error("Passwords don't match")
#             elif len(password) < 6:
#                 st.error("Password must be at least 6 characters")
#             else:
#                 success, message = auth.signup(username, email, password)
#                 if success:
#                     st.success(message)
#                     st.info("Please login with your credentials")
#                     time.sleep(2)
#                     st.session_state.page = "login"
#                     st.rerun()
#                 else:
#                     st.error(message)
    
#     st.markdown("---")
#     if st.button("Already have an account? Login"):
#         st.session_state.page = "login"
#         st.rerun()

# # ===== MAIN APPLICATION =====

# def main_app():
#     # Sidebar
#     with st.sidebar:
#         st.title(f"👤 {st.session_state.user['username']}")
#         st.markdown("---")
        
#         menu = st.radio("Navigation", ["🏠 Consultation", "📜 History", "ℹ️ About"])
        
#         st.markdown("---")
        
#         # RAG Stats
#         stats = rag.get_collection_stats()
#         st.info(f"📚 Medical KB: {stats['total_documents']} documents")
        
#         # Show consultation count
#         records = auth.get_user_history(st.session_state.user['id'])
#         st.success(f"💾 Saved Consultations: {len(records)}")
        
#         if st.button("🚪 Logout"):
#             st.session_state.authenticated = False
#             st.session_state.user = None
#             st.session_state.audio_file = None
#             st.session_state.conversation = MedicalConversation()
#             st.session_state.chat_messages = []
#             st.session_state.page = "login"
#             if "last_saved_consultation" in st.session_state:
#                 del st.session_state.last_saved_consultation
#             st.rerun()
    
#     if menu == "🏠 Consultation":
#         consultation_page()
#     elif menu == "📜 History":
#         history_page()
#     elif menu == "ℹ️ About":
#         about_page()

# def consultation_page():
#     st.title("🩺 Medical Consultation")
    
#     # Mode selector
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("💬 Chat Mode", use_container_width=True, 
#                     type="primary" if st.session_state.consultation_mode == "chat" else "secondary"):
#             st.session_state.consultation_mode = "chat"
#             st.rerun()
#     with col2:
#         if st.button("🎤 Voice Mode", use_container_width=True,
#                     type="primary" if st.session_state.consultation_mode == "voice" else "secondary"):
#             st.session_state.consultation_mode = "voice"
#             st.rerun()
    
#     st.markdown("---")
    
#     if st.session_state.consultation_mode == "chat":
#         chat_consultation()
#     else:
#         voice_consultation()

# def chat_consultation():
#     """Chat-based consultation"""
    
#     st.write("💬 **Chat with the AI Doctor**")
    
#     # Display chat messages
#     chat_container = st.container()
#     with chat_container:
#         for message in st.session_state.chat_messages:
#             with st.chat_message(message["role"]):
#                 st.markdown(message["content"])
    
#     # Show consultation status
#     if st.session_state.conversation.is_consultation_complete():
#         # Auto-save if not already saved
#         if "last_saved_consultation" not in st.session_state or \
#            st.session_state.last_saved_consultation != len(st.session_state.chat_messages):
#             save_consultation_to_history()
#             st.session_state.last_saved_consultation = len(st.session_state.chat_messages)
#             st.success("✅ Consultation Complete! Automatically saved to your history.")
#         else:
#             st.success("✅ Consultation Complete! Saved in your medical history.")
        
#         if st.button("🔄 New Consultation", use_container_width=True):
#             st.session_state.conversation.reset()
#             st.session_state.chat_messages = []
#             if "last_saved_consultation" in st.session_state:
#                 del st.session_state.last_saved_consultation
#             st.rerun()
#     else:
#         # Chat input
#         user_input = st.chat_input("Describe your symptoms or answer the doctor's questions...")
        
#         if user_input:
#             # Add user message to display
#             st.session_state.chat_messages.append({"role": "user", "content": user_input})
            
#             # Get AI response
#             with st.spinner("Doctor is thinking..."):
#                 ai_response = st.session_state.conversation.get_ai_response(user_input, rag)
            
#             # Add AI response to display
#             st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
            
#             st.rerun()
        
#         # Reset button
#         if len(st.session_state.chat_messages) > 0:
#             if st.button("🔄 Start Over"):
#                 st.session_state.conversation.reset()
#                 st.session_state.chat_messages = []
#                 if "last_saved_consultation" in st.session_state:
#                     del st.session_state.last_saved_consultation
#                 st.rerun()

# def voice_consultation():
#     """Voice-based consultation with AI speaking back"""
    
#     st.write("🎤 **Full Voice Conversation Mode**")
    
#     # Voice toggle - more prominent
#     voice_col1, voice_col2 = st.columns([2, 1])
#     with voice_col1:
#         st.info(f"🌍 **Detected Language:** {st.session_state.user_language}")
#     with voice_col2:
#         voice_toggle = st.checkbox("🔊 AI Voice", value=st.session_state.voice_enabled, key="voice_toggle")
#         if voice_toggle != st.session_state.voice_enabled:
#             st.session_state.voice_enabled = voice_toggle
#             st.rerun()
    
#     if st.session_state.voice_enabled:
#         st.success("✅ AI will speak back to you in your language!")
#     else:
#         st.warning("ℹ️ AI will respond with text only")
    
#     st.markdown("---")
    
#     # Display conversation history
#     if st.session_state.chat_messages:
#         st.subheader("💬 Conversation")
#         for idx, message in enumerate(st.session_state.chat_messages):
#             with st.chat_message(message["role"]):
#                 st.markdown(message["content"])
                
#                 # Play audio if it's an assistant message and has audio
#                 if message["role"] == "assistant" and "audio" in message:
#                     st.audio(message["audio"], format="audio/wav")
#                     st.caption("🔊 Playing AI voice response")
#         st.markdown("---")
    
#     # Check if consultation is complete
#     if st.session_state.conversation.is_consultation_complete():
#         # Auto-save if not already saved
#         if "last_saved_consultation" not in st.session_state or \
#            st.session_state.last_saved_consultation != len(st.session_state.chat_messages):
#             save_consultation_to_history()
#             st.session_state.last_saved_consultation = len(st.session_state.chat_messages)
#             st.success("✅ Consultation Complete! Automatically saved to your history.")
#         else:
#             st.success("✅ Consultation Complete! Saved in your medical history.")
        
#         if st.button("🔄 New Consultation", use_container_width=True):
#             st.session_state.conversation.reset()
#             st.session_state.chat_messages = []
#             st.session_state.audio_file = None
#             st.session_state.user_language = "en-IN"
#             if "last_saved_consultation" in st.session_state:
#                 del st.session_state.last_saved_consultation
#             st.rerun()
#     else:
#         # Recording controls
#         col1, col2 = st.columns(2)

#         if col1.button("🎤 Start Recording") and not st.session_state.recording:
#             st.session_state.recording = True
#             st.session_state.recording_event.set()
            
#             temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
#             st.session_state.audio_file = temp_wav.name
#             temp_wav.close()
            
#             st.session_state.recording_thread = threading.Thread(
#                 target=record_audio, 
#                 args=(st.session_state.audio_file, st.session_state.recording_event), 
#                 daemon=True
#             )
#             st.session_state.recording_thread.start()
#             st.info("🎙️ Recording... Speak now!")

#         if col2.button("⏹️ Stop Recording") and st.session_state.recording:
#             st.session_state.recording_event.clear()
#             st.session_state.recording = False
            
#             if st.session_state.recording_thread:
#                 st.session_state.recording_thread.join(timeout=2)
            
#             time.sleep(0.5)
#             st.success("✅ Recording stopped!")
            
#             if st.session_state.audio_file:
#                 try:
#                     with open(st.session_state.audio_file, 'rb') as audio_file:
#                         audio_bytes = audio_file.read()
#                         st.audio(audio_bytes, format="audio/wav")
#                 except Exception as e:
#                     st.error(f"Could not load audio: {e}")

#         # Process audio
#         if st.session_state.audio_file and not st.session_state.recording:
#             if st.button("📤 Send Voice Message", use_container_width=True):
#                 process_voice_message_with_response()
        
#         # Reset button
#         if len(st.session_state.chat_messages) > 0:
#             if st.button("🔄 Start Over"):
#                 st.session_state.conversation.reset()
#                 st.session_state.chat_messages = []
#                 st.session_state.audio_file = None
#                 st.session_state.user_language = "en-IN"
#                 if "last_saved_consultation" in st.session_state:
#                     del st.session_state.last_saved_consultation
#                 st.rerun()

# def process_voice_message_with_response():
#     """Process voice message and get AI voice response"""
#     try:
#         with st.spinner("🎧 Processing your audio..."):
#             transcript, lang = transcribe_audio(st.session_state.audio_file)
        
#         if transcript:
#             # Update detected language
#             st.session_state.user_language = lang
#             st.success(f"✅ Detected: {lang}")
            
#             with st.spinner("🌐 Translating to English..."):
#                 english_text = translate_to_english(transcript)
            
#             # Add user message to chat
#             st.session_state.chat_messages.append({
#                 "role": "user", 
#                 "content": f"**Original ({lang}):** {transcript}\n\n**Translation:** {english_text}"
#             })
            
#             # Get AI response in English
#             with st.spinner("🤖 Doctor is thinking..."):
#                 ai_response_english = st.session_state.conversation.get_ai_response(english_text, rag)
            
#             # Prepare AI response with voice if enabled
#             ai_response_translated = ai_response_english
#             audio_data = None
            
#             if st.session_state.voice_enabled:
#                 st.info(f"🔊 Voice mode is ON - Generating speech in {lang}")
                
#                 # Translate AI response back to user's language (if not English)
#                 if lang != "en-IN":
#                     with st.spinner(f"🌍 Translating response to {lang}..."):
#                         ai_response_translated = translate_from_english(ai_response_english, lang)
#                         if not ai_response_translated:
#                             ai_response_translated = ai_response_english
#                             lang = "en-IN"
                
#                 # Generate speech
#                 with st.spinner(f"🎙️ Converting to speech ({lang})..."):
#                     audio_data = text_to_speech(ai_response_translated, lang)
#                     if audio_data:
#                         st.success("✅ Voice generated successfully!")
#                     else:
#                         st.warning("⚠️ Voice generation failed, showing text only")
            
#             # Build AI message content
#             message_content = f"**English:** {ai_response_english}"
            
#             if lang != "en-IN" and ai_response_translated != ai_response_english:
#                 message_content += f"\n\n**{lang} Translation:**\n{ai_response_translated}"
            
#             # Add AI message to chat
#             ai_message = {
#                 "role": "assistant",
#                 "content": message_content
#             }
            
#             if audio_data:
#                 ai_message["audio"] = audio_data
            
#             st.session_state.chat_messages.append(ai_message)
            
#             # Clear audio file
#             st.session_state.audio_file = None
            
#             st.success("✅ Response ready! Check conversation above.")
#             time.sleep(1)
#             st.rerun()
#         else:
#             st.error("❌ Could not transcribe audio. Please try again.")
#     except Exception as e:
#         st.error(f"❌ Error processing audio: {e}")
#         import traceback
#         st.error(traceback.format_exc())

# def save_consultation_to_history():
#     """Save completed consultation to database"""
#     consultation_data = st.session_state.conversation.get_full_consultation_summary()
    
#     # Format for storage
#     transcript = consultation_data['initial_symptom']
#     conversation_text = "\n\n".join([
#         f"{'Patient' if msg['role'] == 'user' else 'Doctor'}: {msg['content']}"
#         for msg in consultation_data['conversation']
#     ])
    
#     # Get the final analysis (last assistant message)
#     final_analysis = ""
#     for msg in reversed(consultation_data['conversation']):
#         if msg['role'] == 'assistant' and '##' in msg['content']:
#             final_analysis = msg['content']
#             break
    
#     # Save to database
#     success = auth.save_medical_record(
#         st.session_state.user['id'],
#         transcript,
#         conversation_text,
#         final_analysis if final_analysis else conversation_text,
#         "Conversational Consultation"
#     )
    
#     return success

# def history_page():
#     st.title("📜 Medical History")
    
#     records = auth.get_user_history(st.session_state.user['id'])
    
#     if not records:
#         st.info("No medical consultations yet. Start a consultation to build your history!")
#     else:
#         st.write(f"Total consultations: {len(records)}")
#         st.markdown("---")
        
#         for idx, record in enumerate(records, 1):
#             with st.expander(f"Consultation #{idx} - {record[5][:16]}"):
#                 st.subheader("🗣️ Initial Symptom")
#                 st.write(record[1])
                
#                 st.subheader("💬 Conversation")
#                 st.text_area("Full conversation", record[2], height=200, key=f"conv_{idx}")
                
#                 st.subheader("🩺 Final Analysis")
#                 st.markdown(record[3])
                
#                 st.caption(f"Type: {record[4]} | Date: {record[5]}")

# def about_page():
#     st.title("ℹ️ About")
    
#     st.markdown("""
#     ### AI Medical Assistant with Conversational Consultation
    
#     This application provides an interactive medical consultation experience:
    
#     #### 🎯 Features:
#     - 💬 **Chat Mode**: Type your symptoms and have a conversation with the AI doctor
#     - 🎤 **Voice Mode**: Speak in any supported language
#     - 🤖 **Intelligent Follow-ups**: AI asks relevant questions like a real doctor
#     - 🧠 **RAG-Enhanced**: Analysis backed by medical knowledge base
#     - 📜 **Medical History**: All consultations saved for your reference
#     - 🔐 **Secure**: Personal account with encrypted passwords
    
#     #### 🩺 How It Works:
#     1. Describe your initial symptom (chat or voice)
#     2. AI doctor asks 2-4 follow-up questions
#     3. Receive comprehensive medical analysis
#     4. Get specialist recommendation and care advice
#     5. Consultation saved to your history
    
#     #### 🌍 Supported Languages:
#     Hindi, English, Bengali, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu, Gujarati
    
#     #### 🛠️ Technology Stack:
#     - **Speech-to-Text**: Sarvam AI
#     - **Translation**: Sarvam AI
#     - **Medical AI**: Mistral AI
#     - **Knowledge Base**: Custom RAG system
    
#     ---
    
#     ⚠️ **Disclaimer**: This is for educational purposes only and not a substitute for professional medical advice.
#     Always consult qualified healthcare providers for medical decisions.
#     """)

# # ===== MAIN ROUTING =====

# if not st.session_state.authenticated:
#     if st.session_state.page == "login":
#         login_page()
#     else:
#         signup_page()
# else:
#     main_app()



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
from modules.text_to_speech import text_to_speech, translate_from_english
from modules.auth import AuthSystem
from modules.rag_medical import MedicalRAG
from modules.conversation import MedicalConversation

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
if "conversation" not in st.session_state:
    st.session_state.conversation = MedicalConversation()
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "consultation_mode" not in st.session_state:
    st.session_state.consultation_mode = "chat"  # chat or voice
if "user_language" not in st.session_state:
    st.session_state.user_language = "en-IN"  # Detected language
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = False  # AI voice responses on/off

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
        
        menu = st.radio("Navigation", ["🏠 Consultation", "📜 History", "ℹ️ About"])
        
        st.markdown("---")
        
        # RAG Stats
        stats = rag.get_collection_stats()
        st.info(f"📚 Medical KB: {stats['total_documents']} documents")
        
        # Show consultation count
        records = auth.get_user_history(st.session_state.user['id'])
        st.success(f"💾 Saved Consultations: {len(records)}")
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.audio_file = None
            st.session_state.conversation = MedicalConversation()
            st.session_state.chat_messages = []
            st.session_state.page = "login"
            if "last_saved_consultation" in st.session_state:
                del st.session_state.last_saved_consultation
            st.rerun()
    
    if menu == "🏠 Consultation":
        consultation_page()
    elif menu == "📜 History":
        history_page()
    elif menu == "ℹ️ About":
        about_page()

def consultation_page():
    st.title("🩺 Medical Consultation")
    
    # Mode selector
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 Chat Mode", use_container_width=True, 
                    type="primary" if st.session_state.consultation_mode == "chat" else "secondary"):
            st.session_state.consultation_mode = "chat"
            st.rerun()
    with col2:
        if st.button("🎤 Voice Mode", use_container_width=True,
                    type="primary" if st.session_state.consultation_mode == "voice" else "secondary"):
            st.session_state.consultation_mode = "voice"
            st.rerun()
    
    st.markdown("---")
    
    if st.session_state.consultation_mode == "chat":
        chat_consultation()
    else:
        voice_consultation()

def chat_consultation():
    """Chat-based consultation"""
    
    st.write("💬 **Chat with the AI Doctor**")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Show consultation status
    if st.session_state.conversation.is_consultation_complete():
        # Auto-save if not already saved
        if "last_saved_consultation" not in st.session_state or \
           st.session_state.last_saved_consultation != len(st.session_state.chat_messages):
            save_consultation_to_history()
            st.session_state.last_saved_consultation = len(st.session_state.chat_messages)
            st.success("✅ Consultation Complete! Automatically saved to your history.")
        else:
            st.success("✅ Consultation Complete! Saved in your medical history.")
        
        if st.button("🔄 New Consultation", use_container_width=True):
            st.session_state.conversation.reset()
            st.session_state.chat_messages = []
            if "last_saved_consultation" in st.session_state:
                del st.session_state.last_saved_consultation
            st.rerun()
    else:
        # Chat input
        user_input = st.chat_input("Describe your symptoms or answer the doctor's questions...")
        
        if user_input:
            # Add user message to display
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            
            # Get AI response
            with st.spinner("Doctor is thinking..."):
                ai_response = st.session_state.conversation.get_ai_response(user_input, rag)
            
            # Add AI response to display
            st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
            
            st.rerun()
        
        # Reset button
        if len(st.session_state.chat_messages) > 0:
            if st.button("🔄 Start Over"):
                st.session_state.conversation.reset()
                st.session_state.chat_messages = []
                if "last_saved_consultation" in st.session_state:
                    del st.session_state.last_saved_consultation
                st.rerun()

def voice_consultation():
    """Voice-based consultation with AI speaking back"""
    
    st.write("🎤 **Full Voice Conversation Mode**")
    
    # Voice toggle - more prominent
    voice_col1, voice_col2 = st.columns([2, 1])
    with voice_col1:
        st.info(f"🌍 **Detected Language:** {st.session_state.user_language}")
    with voice_col2:
        voice_toggle = st.checkbox("🔊 AI Voice", value=st.session_state.voice_enabled, key="voice_toggle")
        if voice_toggle != st.session_state.voice_enabled:
            st.session_state.voice_enabled = voice_toggle
            st.rerun()
    
    if st.session_state.voice_enabled:
        st.success("✅ AI will speak back to you in your language!")
    else:
        st.warning("ℹ️ AI will respond with text only")
    
    st.markdown("---")
    
    # Display conversation history
    if st.session_state.chat_messages:
        st.subheader("💬 Conversation")
        for idx, message in enumerate(st.session_state.chat_messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Play audio if it's an assistant message and has audio
                if message["role"] == "assistant" and "audio" in message:
                    st.audio(message["audio"], format="audio/wav")
                    st.caption("🔊 Playing AI voice response")
        st.markdown("---")
    
    # Check if consultation is complete
    if st.session_state.conversation.is_consultation_complete():
        # Auto-save if not already saved
        if "last_saved_consultation" not in st.session_state or \
           st.session_state.last_saved_consultation != len(st.session_state.chat_messages):
            save_consultation_to_history()
            st.session_state.last_saved_consultation = len(st.session_state.chat_messages)
            st.success("✅ Consultation Complete! Automatically saved to your history.")
        else:
            st.success("✅ Consultation Complete! Saved in your medical history.")
        
        if st.button("🔄 New Consultation", use_container_width=True):
            st.session_state.conversation.reset()
            st.session_state.chat_messages = []
            st.session_state.audio_file = None
            st.session_state.user_language = "en-IN"
            if "last_saved_consultation" in st.session_state:
                del st.session_state.last_saved_consultation
            st.rerun()
    else:
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
            st.info("🎙️ Recording... Speak now!")

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
            if st.button("📤 Send Voice Message", use_container_width=True):
                process_voice_message_with_response()
        
        # Reset button
        if len(st.session_state.chat_messages) > 0:
            if st.button("🔄 Start Over"):
                st.session_state.conversation.reset()
                st.session_state.chat_messages = []
                st.session_state.audio_file = None
                st.session_state.user_language = "en-IN"
                if "last_saved_consultation" in st.session_state:
                    del st.session_state.last_saved_consultation
                st.rerun()

def process_voice_message_with_response():
    """Process voice message and get AI voice response"""
    try:
        with st.spinner("🎧 Processing your audio..."):
            transcript, lang = transcribe_audio(st.session_state.audio_file)
        
        if transcript:
            # Update detected language
            st.session_state.user_language = lang
            st.success(f"✅ Detected: {lang}")
            
            with st.spinner("🌐 Translating to English..."):
                english_text = translate_to_english(transcript)
            
            # Add user message to chat
            st.session_state.chat_messages.append({
                "role": "user", 
                "content": f"**Original ({lang}):** {transcript}\n\n**Translation:** {english_text}"
            })
            
            # Get AI response in English
            with st.spinner("🤖 Doctor is thinking..."):
                ai_response_english = st.session_state.conversation.get_ai_response(english_text, rag)
            
            # Check if this is final analysis
            is_final_analysis = st.session_state.conversation.is_consultation_complete()
            
            # Prepare AI response with voice if enabled
            ai_response_translated = ai_response_english
            audio_data = None
            
            if st.session_state.voice_enabled:
                st.info(f"🔊 Voice mode is ON - Generating speech in {lang}")
                
                # Extract speech-friendly text
                if is_final_analysis:
                    # For final analysis, extract only important content
                    speech_text = extract_analysis_for_speech(ai_response_english)
                else:
                    # For questions, use full text
                    speech_text = ai_response_english
                
                # Translate AI response back to user's language (if not English)
                if lang != "en-IN":
                    with st.spinner(f"🌍 Translating response to {lang}..."):
                        ai_response_translated = translate_from_english(ai_response_english, lang)
                        speech_text_translated = translate_from_english(speech_text, lang)
                        
                        if not ai_response_translated:
                            ai_response_translated = ai_response_english
                            speech_text_translated = speech_text
                            lang = "en-IN"
                else:
                    speech_text_translated = speech_text
                
                # Generate speech
                with st.spinner(f"🎙️ Converting to speech ({lang})..."):
                    audio_data = text_to_speech(speech_text_translated, lang)
                    if audio_data:
                        st.success("✅ Voice generated successfully!")
                    else:
                        st.warning("⚠️ Voice generation failed, showing text only")
            
            # Build AI message content
            message_content = f"**English:** {ai_response_english}"
            
            if lang != "en-IN" and ai_response_translated != ai_response_english:
                message_content += f"\n\n**{lang} Translation:**\n{ai_response_translated}"
            
            # Add AI message to chat
            ai_message = {
                "role": "assistant",
                "content": message_content
            }
            
            if audio_data:
                ai_message["audio"] = audio_data
            
            st.session_state.chat_messages.append(ai_message)
            
            # Clear audio file
            st.session_state.audio_file = None
            
            st.success("✅ Response ready! Check conversation above.")
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Could not transcribe audio. Please try again.")
    except Exception as e:
        st.error(f"❌ Error processing audio: {e}")
        import traceback
        st.error(traceback.format_exc())

def extract_analysis_for_speech(analysis_text):
    """Extract speech-friendly content from medical analysis"""
    
    # Remove markdown formatting
    import re
    
    # Remove headers (##, ###)
    text = re.sub(r'#{1,6}\s+', '', analysis_text)
    
    # Remove markdown bold (**text**)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    
    # Remove bullet points and list markers
    text = re.sub(r'^[\-\*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Extract key sections for speech
    speech_parts = []
    
    # Look for key sections
    sections = {
        'Symptom Overview': [],
        'Possible Conditions': [],
        'Recommended Specialist': [],
        'Immediate Care': [],
        'Urgency Level': []
    }
    
    current_section = None
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line is a section header
        for section in sections.keys():
            if section.lower() in line.lower():
                current_section = section
                break
        
        # Add content to current section
        if current_section and line and not any(s.lower() in line.lower() for s in sections.keys()):
            # Skip disclaimer and formatting
            if 'disclaimer' not in line.lower() and '---' not in line and len(line) > 10:
                sections[current_section].append(line)
    
    # Build speech text
    if sections['Symptom Overview']:
        speech_parts.append("Based on your symptoms: " + " ".join(sections['Symptom Overview'][:2]))
    
    if sections['Possible Conditions']:
        speech_parts.append("The possible conditions include: " + " ".join(sections['Possible Conditions'][:3]))
    
    if sections['Recommended Specialist']:
        speech_parts.append("You should consult: " + " ".join(sections['Recommended Specialist'][:1]))
    
    if sections['Immediate Care']:
        speech_parts.append("For immediate care: " + " ".join(sections['Immediate Care'][:3]))
    
    if sections['Urgency Level']:
        speech_parts.append(" ".join(sections['Urgency Level'][:1]))
    
    # If no sections found, extract first 3-4 sentences
    if not speech_parts:
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        speech_parts = sentences[:4]
    
    speech_text = ". ".join(speech_parts)
    
    # Add closing
    speech_text += ". Please consult a healthcare provider for proper diagnosis and treatment."
    
    return speech_text

def save_consultation_to_history():
    """Save completed consultation to database"""
    consultation_data = st.session_state.conversation.get_full_consultation_summary()
    
    # Format for storage
    transcript = consultation_data['initial_symptom']
    conversation_text = "\n\n".join([
        f"{'Patient' if msg['role'] == 'user' else 'Doctor'}: {msg['content']}"
        for msg in consultation_data['conversation']
    ])
    
    # Get the final analysis (last assistant message)
    final_analysis = ""
    for msg in reversed(consultation_data['conversation']):
        if msg['role'] == 'assistant' and '##' in msg['content']:
            final_analysis = msg['content']
            break
    
    # Save to database
    success = auth.save_medical_record(
        st.session_state.user['id'],
        transcript,
        conversation_text,
        final_analysis if final_analysis else conversation_text,
        "Conversational Consultation"
    )
    
    return success

def history_page():
    st.title("📜 Medical History")
    
    records = auth.get_user_history(st.session_state.user['id'])
    
    if not records:
        st.info("No medical consultations yet. Start a consultation to build your history!")
    else:
        st.write(f"Total consultations: {len(records)}")
        st.markdown("---")
        
        for idx, record in enumerate(records, 1):
            with st.expander(f"Consultation #{idx} - {record[5][:16]}"):
                st.subheader("🗣️ Initial Symptom")
                st.write(record[1])
                
                st.subheader("💬 Conversation")
                st.text_area("Full conversation", record[2], height=200, key=f"conv_{idx}")
                
                st.subheader("🩺 Final Analysis")
                st.markdown(record[3])
                
                st.caption(f"Type: {record[4]} | Date: {record[5]}")

def about_page():
    st.title("ℹ️ About")
    
    st.markdown("""
    ### AI Medical Assistant with Conversational Consultation
    
    This application provides an interactive medical consultation experience:
    
    #### 🎯 Features:
    - 💬 **Chat Mode**: Type your symptoms and have a conversation with the AI doctor
    - 🎤 **Voice Mode**: Speak in any supported language
    - 🤖 **Intelligent Follow-ups**: AI asks relevant questions like a real doctor
    - 🧠 **RAG-Enhanced**: Analysis backed by medical knowledge base
    - 📜 **Medical History**: All consultations saved for your reference
    - 🔐 **Secure**: Personal account with encrypted passwords
    
    #### 🩺 How It Works:
    1. Describe your initial symptom (chat or voice)
    2. AI doctor asks 2-4 follow-up questions
    3. Receive comprehensive medical analysis
    4. Get specialist recommendation and care advice
    5. Consultation saved to your history
    
    #### 🌍 Supported Languages:
    Hindi, English, Bengali, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu, Gujarati
    
    #### 🛠️ Technology Stack:
    - **Speech-to-Text**: Sarvam AI
    - **Translation**: Sarvam AI
    - **Medical AI**: Mistral AI
    - **Knowledge Base**: Custom RAG system
    
    ---
    
    ⚠️ **Disclaimer**: This is for educational purposes only and not a substitute for professional medical advice.
    Always consult qualified healthcare providers for medical decisions.
    """)

# ===== MAIN ROUTING =====

if not st.session_state.authenticated:
    if st.session_state.page == "login":
        login_page()
    else:
        signup_page()
else:
    main_app()