# # import requests
# # import os
# # import json
# # import time

# # MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# # class MedicalConversation:
# #     """Manages conversational medical consultation - one question at a time"""
    
# #     def __init__(self):
# #         self.conversation_history = []
# #         self.stage = "initial"  # initial, follow_up, final_analysis
# #         self.collected_info = {
# #             "initial_symptom": "",
# #             "follow_ups": [],
# #             "total_exchanges": 0,
# #             "topics_covered": []  # Track what's been asked
# #         }
# #         self.api_call_count = 0
# #         self.last_api_call = 0
    
# #     def reset(self):
# #         """Reset conversation for new consultation"""
# #         self.conversation_history = []
# #         self.stage = "initial"
# #         self.collected_info = {
# #             "initial_symptom": "",
# #             "follow_ups": [],
# #             "total_exchanges": 0,
# #             "topics_covered": []
# #         }
# #         self.api_call_count = 0
    
# #     def add_to_history(self, role, content):
# #         """Add message to conversation history"""
# #         self.conversation_history.append({
# #             "role": role,
# #             "content": content
# #         })
    
# #     def _rate_limit_check(self):
# #         """Check if we should wait before making API call"""
# #         current_time = time.time()
# #         time_since_last_call = current_time - self.last_api_call
        
# #         # Wait at least 2 seconds between API calls
# #         if time_since_last_call < 2:
# #             time.sleep(2 - time_since_last_call)
        
# #         self.last_api_call = time.time()
    
# #     def get_ai_response(self, user_message, rag_system=None):
# #         """Get AI response based on conversation stage"""
        
# #         # Add user message to history
# #         self.add_to_history("user", user_message)
# #         self.collected_info["total_exchanges"] += 1
        
# #         if self.stage == "initial":
# #             # First interaction - acknowledge symptom and ask ONE question
# #             self.collected_info["initial_symptom"] = user_message
# #             response = self._ask_first_question(user_message, rag_system)
# #             self.stage = "follow_up"
        
# #         elif self.stage == "follow_up":
# #             # Store follow-up response
# #             self.collected_info["follow_ups"].append(user_message)
            
# #             # Decide: ask another question OR provide analysis
# #             response = self._continue_conversation(user_message, rag_system)
        
# #         elif self.stage == "final_analysis":
# #             # This shouldn't happen, but handle it
# #             response = "The consultation is complete. You can start a new consultation."
        
# #         # Add AI response to history
# #         self.add_to_history("assistant", response)
        
# #         return response
    
# #     def _ask_first_question(self, initial_symptom, rag_system):
# #         """Ask the FIRST follow-up question based on initial symptom"""
        
# #         # Get relevant medical context from RAG
# #         context = ""
# #         if rag_system:
# #             documents, _ = rag_system.query_medical_knowledge(initial_symptom, n_results=2)
# #             context = "\n".join(documents[:2]) if documents else ""
        
# #         prompt = f"""
# # You are a doctor starting a consultation. The patient just said: "{initial_symptom}"

# # Medical Context (if available):
# # {context}

# # Your task:
# # 1. Briefly acknowledge their symptom with empathy (1 sentence)
# # 2. Ask ONE specific, relevant follow-up question

# # The question should help you understand:
# # - Duration (how long they've had it) - MOST IMPORTANT FIRST
# # - Or severity if duration is already mentioned

# # Keep it conversational and warm. Ask ONLY ONE question.

# # Format:
# # [Brief acknowledgment]. [Single question]?

# # Example: "I understand you're experiencing headaches. How long have you been having these headaches?"
# # """
        
# #         # Track that we're asking about duration
# #         self.collected_info['topics_covered'].append('duration')
        
# #         return self._call_mistral_api(prompt)
    
# #     def _continue_conversation(self, follow_up_response, rag_system):
# #         """Decide whether to ask another question or provide final analysis"""
        
# #         # HARD STOP: Maximum 5 follow-up questions
# #         if len(self.collected_info['follow_ups']) >= 5:
# #             return self._generate_final_analysis(rag_system)
        
# #         # Build conversation summary
# #         conversation_summary = f"""
# # Initial Symptom: {self.collected_info['initial_symptom']}

# # Patient's Responses:
# # """
# #         for i, response in enumerate(self.collected_info['follow_ups'], 1):
# #             conversation_summary += f"Q{i} Answer: {response}\n"
        
# #         # Strict decision prompt
# #         decision_prompt = f"""
# # You are a doctor. You've asked {len(self.collected_info['follow_ups'])} questions so far.

# # PATIENT CASE:
# # {conversation_summary}

# # STRICT RULES:
# # 1. Maximum 5 questions total - you have {5 - len(self.collected_info['follow_ups'])} questions left
# # 2. If you have duration + severity + checked key symptoms → STOP NOW
# # 3. If patient answered "no" to additional symptoms → You have enough, STOP
# # 4. Never ask about the same topic twice
# # 5. For simple symptoms like headache/fever → 3-4 questions is enough

# # WHAT YOU KNOW:
# # - The symptom itself
# # - Duration and severity (likely covered in first 2 questions)
# # - {len(self.collected_info['follow_ups'])} answers about associated symptoms

# # DECISION TIME:
# # Option 1: If you can reasonably diagnose with 3-4 possible conditions → Type: "READY_FOR_ANALYSIS"
# # Option 2: If you CRITICALLY need 1 more key piece of info (not already asked) → Ask 1 brief question

# # For a headache case, after knowing duration, severity, and checking nausea/vision - you should STOP.

# # Your response:
# # """
        
# #         decision = self._call_mistral_api(decision_prompt)
        
# #         # Safety check: Force stop if repetitive or too many questions
# #         if len(self.collected_info['follow_ups']) >= 4:
# #             # After 4 questions, be very strict
# #             if "READY_FOR_ANALYSIS" not in decision:
# #                 # Check if question is too similar to previous ones
# #                 if "Have you" in decision or "experienced" in decision.lower():
# #                     # Force analysis - AI is being repetitive
# #                     return self._generate_final_analysis(rag_system)
        
# #         # Check if AI is ready for final analysis
# #         if "READY_FOR_ANALYSIS" in decision:
# #             return self._generate_final_analysis(rag_system)
# #         else:
# #             # Track this new topic
# #             return decision
    
# #     def _generate_final_analysis(self, rag_system):
# #         """Generate comprehensive final medical analysis"""
        
# #         self.stage = "final_analysis"
        
# #         # Compile all information
# #         full_conversation = f"""
# # Initial Symptom: {self.collected_info['initial_symptom']}

# # Patient's Responses to Follow-up Questions:
# # """
# #         for i, response in enumerate(self.collected_info['follow_ups'], 1):
# #             full_conversation += f"{i}. {response}\n"
        
# #         # Get RAG context
# #         rag_context = ""
# #         max_urgency = 'medium'
        
# #         if rag_system:
# #             documents, metadatas = rag_system.query_medical_knowledge(
# #                 self.collected_info['initial_symptom'], 
# #                 n_results=3
# #             )
# #             rag_context = "\n\n".join([f"Medical Reference {i+1}:\n{doc}" 
# #                                         for i, doc in enumerate(documents)])
            
# #             # Determine urgency
# #             urgency_levels = [meta.get('urgency', 'medium') for meta in metadatas]
# #             max_urgency = 'high' if 'high' in urgency_levels else ('medium' if 'medium' in urgency_levels else 'low')
        
# #         analysis_prompt = f"""
# # You are a doctor providing a final consultation summary after a thorough conversation.

# # RETRIEVED MEDICAL KNOWLEDGE:
# # {rag_context}

# # COMPLETE PATIENT CONSULTATION:
# # {full_conversation}

# # Provide a comprehensive yet concise analysis in this EXACT format:

# # ## 🩺 Medical Consultation Summary

# # ### Symptom Overview
# # [2-3 sentences summarizing what the patient described]

# # ### Possible Conditions
# # Based on the symptoms described, possible conditions include:
# # 1. **[Condition Name]** - [Brief 1-sentence explanation and likelihood]
# # 2. **[Condition Name]** - [Brief 1-sentence explanation and likelihood]
# # 3. **[Condition Name]** - [Brief 1-sentence explanation and likelihood]

# # ### Key Medical Points
# # - [Important observation based on symptoms]
# # - [Risk factor or concerning detail]
# # - [Timing or pattern observation]

# # ### Recommended Specialist
# # **[Specific type of doctor]** (e.g., Cardiologist, Neurologist, General Physician)

# # ### Immediate Care Advice
# # **What you can do:**
# # - [Immediate home care step 1]
# # - [Immediate home care step 2]

# # **When to seek immediate care:**
# # - [Warning sign 1]
# # - [Warning sign 2]

# # **Urgency Level: {max_urgency.upper()}**

# # ### Disclaimer
# # This AI-generated analysis is based on the information provided and medical references. It is NOT a substitute for professional medical consultation. Please consult a qualified healthcare provider for proper diagnosis and treatment.

# # ---

# # Be clear, professional, and empathetic. Focus on actionable medical advice.
# # """
        
# #         analysis = self._call_mistral_api(analysis_prompt)
        
# #         return analysis
    
# #     def _call_mistral_api(self, prompt, max_retries=3):
# #         """Call Mistral API with retry logic and rate limiting"""
        
# #         # Rate limit check
# #         self._rate_limit_check()
        
# #         url = "https://api.mistral.ai/v1/chat/completions"
        
# #         headers = {
# #             "Authorization": f"Bearer {MISTRAL_API_KEY}",
# #             "Content-Type": "application/json"
# #         }
        
# #         # Build messages with system prompt
# #         messages = [
# #             {
# #                 "role": "system",
# #                 "content": "You are an empathetic and knowledgeable medical AI assistant. You conduct consultations by asking ONE question at a time, listening carefully to responses, and building understanding gradually like a real doctor."
# #             }
# #         ]
        
# #         # Add recent conversation history (last 8 messages for context)
# #         messages.extend(self.conversation_history[-8:])
        
# #         # Add current prompt
# #         messages.append({
# #             "role": "user",
# #             "content": prompt
# #         })
        
# #         payload = {
# #             "model": "mistral-small-latest",
# #             "messages": messages,
# #             "temperature": 0.7,
# #             "max_tokens": 1000
# #         }
        
# #         # Retry logic with exponential backoff
# #         for attempt in range(max_retries):
# #             try:
# #                 response = requests.post(url, headers=headers, json=payload, timeout=30)
# #                 response.raise_for_status()
# #                 result = response.json()
                
# #                 self.api_call_count += 1
# #                 return result['choices'][0]['message']['content']
                
# #             except requests.exceptions.HTTPError as e:
# #                 if e.response.status_code == 429:  # Rate limit
# #                     if attempt < max_retries - 1:
# #                         wait_time = (2 ** attempt) * 3
# #                         print(f"⏳ Rate limit. Waiting {wait_time}s... (Attempt {attempt + 2}/{max_retries})")
# #                         time.sleep(wait_time)
# #                         continue
# #                     else:
# #                         return self._generate_fallback_response()
# #                 else:
# #                     return f"⚠️ API Error (HTTP {e.response.status_code}). Please try again."
                    
# #             except requests.exceptions.Timeout:
# #                 if attempt < max_retries - 1:
# #                     time.sleep(3)
# #                     continue
# #                 return "⚠️ Request timed out. Please try again."
                
# #             except Exception as e:
# #                 return f"⚠️ Unexpected error: {str(e)}. Please try again."
        
# #         return "⚠️ Service temporarily unavailable. Please wait and try again."
    
# #     def _generate_fallback_response(self):
# #         """Generate a simple fallback response when API is rate limited"""
# #         if self.stage == "initial":
# #             return "Thank you for sharing that. How long have you been experiencing this symptom?"
        
# #         elif self.stage == "follow_up":
# #             if len(self.collected_info['follow_ups']) < 2:
# #                 return "I see. Could you describe the severity? Is it mild, moderate, or severe?"
# #             else:
# #                 return """Based on what you've described, I recommend consulting a general physician for a proper examination. If symptoms worsen or become severe, please seek immediate medical attention.

# # This is general advice - please see a healthcare professional for proper diagnosis."""
        
# #         return "Please consult a healthcare professional for medical advice."
    
# #     def is_consultation_complete(self):
# #         """Check if consultation is complete"""
# #         return self.stage == "final_analysis"
    
# #     def get_full_consultation_summary(self):
# #         """Get complete consultation for storage"""
# #         return {
# #             "initial_symptom": self.collected_info["initial_symptom"],
# #             "conversation": self.conversation_history,
# #             "stage": self.stage,
# #             "total_exchanges": self.collected_info["total_exchanges"]
# #         }





# import requests
# import os
# import json
# import time

# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# class MedicalConversation:
#     """Manages conversational medical consultation - one question at a time"""
    
#     def __init__(self):
#         self.conversation_history = []
#         self.stage = "initial"  # initial, follow_up, final_analysis
#         self.collected_info = {
#             "initial_symptom": "",
#             "follow_ups": [],
#             "total_exchanges": 0,
#             "topics_covered": [],
#             "medical_documents": []  # Store uploaded document context
#         }
#         self.api_call_count = 0
#         self.last_api_call = 0
    
#     def reset(self):
#         """Reset conversation for new consultation"""
#         self.conversation_history = []
#         self.stage = "initial"
#         self.collected_info = {
#             "initial_symptom": "",
#             "follow_ups": [],
#             "total_exchanges": 0,
#             "topics_covered": [],
#             "medical_documents": []
#         }
#         self.api_call_count = 0
    
#     def add_medical_documents(self, documents_context):
#         """Add medical documents context to conversation"""
#         self.collected_info["medical_documents"].append(documents_context)
    
#     def add_to_history(self, role, content):
#         """Add message to conversation history"""
#         self.conversation_history.append({
#             "role": role,
#             "content": content
#         })
    
#     def _rate_limit_check(self):
#         """Check if we should wait before making API call"""
#         current_time = time.time()
#         time_since_last_call = current_time - self.last_api_call
        
#         # Wait at least 2 seconds between API calls
#         if time_since_last_call < 2:
#             time.sleep(2 - time_since_last_call)
        
#         self.last_api_call = time.time()
    
#     def get_ai_response(self, user_message, rag_system=None):
#         """Get AI response based on conversation stage"""
        
#         # Add user message to history
#         self.add_to_history("user", user_message)
#         self.collected_info["total_exchanges"] += 1
        
#         if self.stage == "initial":
#             # First interaction - acknowledge symptom and ask ONE question
#             self.collected_info["initial_symptom"] = user_message
#             response = self._ask_first_question(user_message, rag_system)
#             self.stage = "follow_up"
        
#         elif self.stage == "follow_up":
#             # Store follow-up response
#             self.collected_info["follow_ups"].append(user_message)
            
#             # Decide: ask another question OR provide analysis
#             response = self._continue_conversation(user_message, rag_system)
        
#         elif self.stage == "final_analysis":
#             # This shouldn't happen, but handle it
#             response = "The consultation is complete. You can start a new consultation."
        
#         # Add AI response to history
#         self.add_to_history("assistant", response)
        
#         return response
    
#     def _ask_first_question(self, initial_symptom, rag_system):
#         """Ask the FIRST follow-up question based on initial symptom"""
        
#         # Get relevant medical context from RAG
#         context = ""
#         if rag_system:
#             documents, _ = rag_system.query_medical_knowledge(initial_symptom, n_results=2)
#             context = "\n".join(documents[:2]) if documents else ""
        
#         # Add medical documents context if available
#         medical_docs_context = ""
#         if self.collected_info["medical_documents"]:
#             medical_docs_context = "\n\nPATIENT'S MEDICAL HISTORY:\n" + "\n".join(self.collected_info["medical_documents"])
        
#         prompt = f"""
# You are a doctor starting a consultation. The patient just said: "{initial_symptom}"

# Medical Context (if available):
# {context}

# {medical_docs_context}

# Your task:
# 1. Briefly acknowledge their symptom with empathy (1 sentence)
# 2. Ask ONE specific, relevant follow-up question

# IMPORTANT: If the patient has provided medical history (prescriptions/reports), acknowledge it briefly and adjust your questions accordingly.

# The question should help you understand:
# - Duration (how long they've had it) - MOST IMPORTANT FIRST
# - Or severity if duration is already mentioned

# Keep it conversational and warm. Ask ONLY ONE question.

# Format:
# [Brief acknowledgment]. [Single question]?

# Example: "I understand you're experiencing headaches. How long have you been having these headaches?"
# """
        
#         # Track that we're asking about duration
#         self.collected_info['topics_covered'].append('duration')
        
#         return self._call_mistral_api(prompt)
    
#     def _continue_conversation(self, follow_up_response, rag_system):
#         """Decide whether to ask another question or provide final analysis"""
        
#         # HARD STOP: Maximum 5 follow-up questions
#         if len(self.collected_info['follow_ups']) >= 5:
#             return self._generate_final_analysis(rag_system)
        
#         # Build conversation summary
#         conversation_summary = f"""
# Initial Symptom: {self.collected_info['initial_symptom']}

# Patient's Responses:
# """
#         for i, response in enumerate(self.collected_info['follow_ups'], 1):
#             conversation_summary += f"Q{i} Answer: {response}\n"
        
#         # Strict decision prompt
#         decision_prompt = f"""
# You are a doctor. You've asked {len(self.collected_info['follow_ups'])} questions so far.

# PATIENT CASE:
# {conversation_summary}

# STRICT RULES:
# 1. Maximum 5 questions total - you have {5 - len(self.collected_info['follow_ups'])} questions left
# 2. If you have duration + severity + checked key symptoms → STOP NOW
# 3. If patient answered "no" to additional symptoms → You have enough, STOP
# 4. Never ask about the same topic twice
# 5. For simple symptoms like headache/fever → 3-4 questions is enough

# WHAT YOU KNOW:
# - The symptom itself
# - Duration and severity (likely covered in first 2 questions)
# - {len(self.collected_info['follow_ups'])} answers about associated symptoms

# DECISION TIME:
# Option 1: If you can reasonably diagnose with 3-4 possible conditions → Type: "READY_FOR_ANALYSIS"
# Option 2: If you CRITICALLY need 1 more key piece of info (not already asked) → Ask 1 brief question

# For a headache case, after knowing duration, severity, and checking nausea/vision - you should STOP.

# Your response:
# """
        
#         decision = self._call_mistral_api(decision_prompt)
        
#         # Safety check: Force stop if repetitive or too many questions
#         if len(self.collected_info['follow_ups']) >= 4:
#             # After 4 questions, be very strict
#             if "READY_FOR_ANALYSIS" not in decision:
#                 # Check if question is too similar to previous ones
#                 if "Have you" in decision or "experienced" in decision.lower():
#                     # Force analysis - AI is being repetitive
#                     return self._generate_final_analysis(rag_system)
        
#         # Check if AI is ready for final analysis
#         if "READY_FOR_ANALYSIS" in decision:
#             return self._generate_final_analysis(rag_system)
#         else:
#             # Track this new topic
#             return decision
    
#     def _generate_final_analysis(self, rag_system):
#         """Generate comprehensive final medical analysis"""
        
#         self.stage = "final_analysis"
        
#         # Compile all information
#         full_conversation = f"""
# Initial Symptom: {self.collected_info['initial_symptom']}

# Patient's Responses to Follow-up Questions:
# """
#         for i, response in enumerate(self.collected_info['follow_ups'], 1):
#             full_conversation += f"{i}. {response}\n"
        
#         # Get RAG context
#         rag_context = ""
#         max_urgency = 'medium'
        
#         if rag_system:
#             documents, metadatas = rag_system.query_medical_knowledge(
#                 self.collected_info['initial_symptom'], 
#                 n_results=3
#             )
#             rag_context = "\n\n".join([f"Medical Reference {i+1}:\n{doc}" 
#                                         for i, doc in enumerate(documents)])
            
#             # Determine urgency
#             urgency_levels = [meta.get('urgency', 'medium') for meta in metadatas]
#             max_urgency = 'high' if 'high' in urgency_levels else ('medium' if 'medium' in urgency_levels else 'low')
        
#         analysis_prompt = f"""
# You are a doctor providing a final consultation summary after a thorough conversation.

# RETRIEVED MEDICAL KNOWLEDGE:
# {rag_context}

# COMPLETE PATIENT CONSULTATION:
# {full_conversation}

# Provide a comprehensive yet concise analysis in this EXACT format:

# ## 🩺 Medical Consultation Summary

# ### Symptom Overview
# [2-3 sentences summarizing what the patient described]

# ### Possible Conditions
# Based on the symptoms described, possible conditions include:
# 1. **[Condition Name]** - [Brief 1-sentence explanation and likelihood]
# 2. **[Condition Name]** - [Brief 1-sentence explanation and likelihood]
# 3. **[Condition Name]** - [Brief 1-sentence explanation and likelihood]

# ### Key Medical Points
# - [Important observation based on symptoms]
# - [Risk factor or concerning detail]
# - [Timing or pattern observation]

# ### Recommended Specialist
# **[Specific type of doctor]** (e.g., Cardiologist, Neurologist, General Physician)

# ### Immediate Care Advice
# **What you can do:**
# - [Immediate home care step 1]
# - [Immediate home care step 2]

# **When to seek immediate care:**
# - [Warning sign 1]
# - [Warning sign 2]

# **Urgency Level: {max_urgency.upper()}**

# ### Disclaimer
# This AI-generated analysis is based on the information provided and medical references. It is NOT a substitute for professional medical consultation. Please consult a qualified healthcare provider for proper diagnosis and treatment.

# ---

# Be clear, professional, and empathetic. Focus on actionable medical advice.
# """
        
#         analysis = self._call_mistral_api(analysis_prompt)
        
#         return analysis
    
#     def _call_mistral_api(self, prompt, max_retries=3):
#         """Call Mistral API with retry logic and rate limiting"""
        
#         # Rate limit check
#         self._rate_limit_check()
        
#         url = "https://api.mistral.ai/v1/chat/completions"
        
#         headers = {
#             "Authorization": f"Bearer {MISTRAL_API_KEY}",
#             "Content-Type": "application/json"
#         }
        
#         # Build messages with system prompt
#         messages = [
#             {
#                 "role": "system",
#                 "content": "You are an empathetic and knowledgeable medical AI assistant. You conduct consultations by asking ONE question at a time, listening carefully to responses, and building understanding gradually like a real doctor."
#             }
#         ]
        
#         # Add recent conversation history (last 8 messages for context)
#         messages.extend(self.conversation_history[-8:])
        
#         # Add current prompt
#         messages.append({
#             "role": "user",
#             "content": prompt
#         })
        
#         payload = {
#             "model": "mistral-small-latest",
#             "messages": messages,
#             "temperature": 0.7,
#             "max_tokens": 1000
#         }
        
#         # Retry logic with exponential backoff
#         for attempt in range(max_retries):
#             try:
#                 response = requests.post(url, headers=headers, json=payload, timeout=30)
#                 response.raise_for_status()
#                 result = response.json()
                
#                 self.api_call_count += 1
#                 return result['choices'][0]['message']['content']
                
#             except requests.exceptions.HTTPError as e:
#                 if e.response.status_code == 429:  # Rate limit
#                     if attempt < max_retries - 1:
#                         wait_time = (2 ** attempt) * 3
#                         print(f"⏳ Rate limit. Waiting {wait_time}s... (Attempt {attempt + 2}/{max_retries})")
#                         time.sleep(wait_time)
#                         continue
#                     else:
#                         return self._generate_fallback_response()
#                 else:
#                     return f"⚠️ API Error (HTTP {e.response.status_code}). Please try again."
                    
#             except requests.exceptions.Timeout:
#                 if attempt < max_retries - 1:
#                     time.sleep(3)
#                     continue
#                 return "⚠️ Request timed out. Please try again."
                
#             except Exception as e:
#                 return f"⚠️ Unexpected error: {str(e)}. Please try again."
        
#         return "⚠️ Service temporarily unavailable. Please wait and try again."
    
#     def _generate_fallback_response(self):
#         """Generate a simple fallback response when API is rate limited"""
#         if self.stage == "initial":
#             return "Thank you for sharing that. How long have you been experiencing this symptom?"
        
#         elif self.stage == "follow_up":
#             if len(self.collected_info['follow_ups']) < 2:
#                 return "I see. Could you describe the severity? Is it mild, moderate, or severe?"
#             else:
#                 return """Based on what you've described, I recommend consulting a general physician for a proper examination. If symptoms worsen or become severe, please seek immediate medical attention.

# This is general advice - please see a healthcare professional for proper diagnosis."""
        
#         return "Please consult a healthcare professional for medical advice."
    
#     def is_consultation_complete(self):
#         """Check if consultation is complete"""
#         return self.stage == "final_analysis"
    
#     def get_full_consultation_summary(self):
#         """Get complete consultation for storage"""
#         return {
#             "initial_symptom": self.collected_info["initial_symptom"],
#             "conversation": self.conversation_history,
#             "stage": self.stage,
#             "total_exchanges": self.collected_info["total_exchanges"]
#         }


import requests
import os
import json
import time

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

class MedicalConversation:
    """Manages conversational medical consultation - one question at a time"""
    
    def __init__(self):
        self.conversation_history = []
        self.stage = "initial"  # initial, follow_up, final_analysis
        self.collected_info = {
            "initial_symptom": "",
            "follow_ups": [],
            "total_exchanges": 0,
            "topics_covered": [],
            "medical_documents": []  # Store uploaded document context
        }
        self.api_call_count = 0
        self.last_api_call = 0
    
    def reset(self):
        """Reset conversation for new consultation"""
        self.conversation_history = []
        self.stage = "initial"
        self.collected_info = {
            "initial_symptom": "",
            "follow_ups": [],
            "total_exchanges": 0,
            "topics_covered": [],
            "medical_documents": []
        }
        self.api_call_count = 0
    
    def add_medical_documents(self, documents_context):
        """Add medical documents context to conversation"""
        self.collected_info["medical_documents"].append(documents_context)
    
    def add_to_history(self, role, content):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def _rate_limit_check(self):
        """Check if we should wait before making API call"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        # Wait at least 2 seconds between API calls
        if time_since_last_call < 2:
            time.sleep(2 - time_since_last_call)
        
        self.last_api_call = time.time()
    
    def get_ai_response(self, user_message, rag_system=None):
        """Get AI response based on conversation stage"""
        
        # Add user message to history
        self.add_to_history("user", user_message)
        self.collected_info["total_exchanges"] += 1
        
        if self.stage == "initial":
            # First interaction - acknowledge symptom and ask ONE question
            self.collected_info["initial_symptom"] = user_message
            response = self._ask_first_question(user_message, rag_system)
            self.stage = "follow_up"
        
        elif self.stage == "follow_up":
            # Store follow-up response
            self.collected_info["follow_ups"].append(user_message)
            
            # Decide: ask another question OR provide analysis
            response = self._continue_conversation(user_message, rag_system)
        
        elif self.stage == "final_analysis":
            # This shouldn't happen, but handle it
            response = "The consultation is complete. You can start a new consultation."
        
        # Add AI response to history
        self.add_to_history("assistant", response)
        
        return response
    
    def _ask_first_question(self, initial_symptom, rag_system):
        """Ask the FIRST follow-up question based on initial symptom"""
        
        # Get relevant medical context from RAG
        context = ""
        if rag_system:
            documents, _ = rag_system.query_medical_knowledge(initial_symptom, n_results=2)
            context = "\n".join(documents[:2]) if documents else ""
        
        # Add medical documents context if available
        medical_docs_context = ""
        if self.collected_info["medical_documents"]:
            medical_docs_context = "\n\nPATIENT'S MEDICAL HISTORY:\n" + "\n".join(self.collected_info["medical_documents"])
        
        prompt = f"""
You are a doctor starting a consultation. The patient just said: "{initial_symptom}"

Medical Context (if available):
{context}

{medical_docs_context}

Your task:
1. Briefly acknowledge their symptom with empathy (1 sentence)
2. Ask ONE specific, relevant follow-up question

IMPORTANT: If the patient has provided medical history (prescriptions/reports), acknowledge it briefly and adjust your questions accordingly.

The question should help you understand:
- Duration (how long they've had it) - MOST IMPORTANT FIRST
- Or severity if duration is already mentioned

Keep it conversational and warm. Ask ONLY ONE question.

Format:
[Brief acknowledgment]. [Single question]?

Example: "I understand you're experiencing headaches. How long have you been having these headaches?"
"""
        
        # Track that we're asking about duration
        self.collected_info['topics_covered'].append('duration')
        
        return self._call_mistral_api(prompt)
    
    def _continue_conversation(self, follow_up_response, rag_system):
        """Decide whether to ask another question or provide final analysis"""
        
        # HARD STOP: Maximum 5 follow-up questions
        if len(self.collected_info['follow_ups']) >= 5:
            return self._generate_final_analysis(rag_system)
        
        # Build conversation summary
        conversation_summary = f"""
Initial Symptom: {self.collected_info['initial_symptom']}

Patient's Responses:
"""
        for i, response in enumerate(self.collected_info['follow_ups'], 1):
            conversation_summary += f"Q{i} Answer: {response}\n"
        
        # Add medical history context for decision making
        medical_context_note = ""
        if self.collected_info["medical_documents"]:
            medical_context_note = f"""

IMPORTANT MEDICAL HISTORY CONTEXT:
The patient has uploaded medical documents showing:
{self.collected_info["medical_documents"][0][:500]}...

You MUST consider this history when asking questions. For example:
- If they mention medications not working, ask about the specific medications from their prescription
- If they have chronic conditions, ask how current symptoms relate
- Reference their previous treatments and ask about effectiveness
- Ask about drug interactions or side effects from current medications
"""
        
        # Strict decision prompt
        decision_prompt = f"""
You are a doctor with access to the patient's medical history. You've asked {len(self.collected_info['follow_ups'])} questions so far.

PATIENT CASE:
{conversation_summary}
{medical_context_note}

STRICT RULES:
1. Maximum 5 questions total - you have {5 - len(self.collected_info['follow_ups'])} questions left
2. If patient uploaded medical documents, reference them in your questions
3. Ask targeted questions based on their medication history
4. If you have duration + severity + checked key symptoms → STOP NOW
5. If patient answered "no" to additional symptoms → You have enough, STOP
6. Never ask about the same topic twice

EXAMPLES OF GOOD FOLLOW-UPS WITH MEDICAL HISTORY:
- "I see from your prescription you were taking [Medicine X]. Did this headache start after taking it?"
- "Your report shows [Test Result]. Has this value changed recently?"
- "You're on [Medicine Y] for [Condition]. Are you still taking it regularly?"

WHAT YOU KNOW:
- The symptom itself
- Duration and severity (likely covered in first 2 questions)
- {len(self.collected_info['follow_ups'])} answers about associated symptoms
- Medical history from uploaded documents (if any)

DECISION TIME:
Option 1: If you can reasonably diagnose with 3-4 possible conditions → Type: "READY_FOR_ANALYSIS"
Option 2: If you CRITICALLY need 1 more key piece of info (especially about their medications/history) → Ask 1 brief, targeted question

Your response:
"""
        
        decision = self._call_mistral_api(decision_prompt)
        
        # Safety check: Force stop if repetitive or too many questions
        if len(self.collected_info['follow_ups']) >= 4:
            # After 4 questions, be very strict
            if "READY_FOR_ANALYSIS" not in decision:
                # Check if question is too similar to previous ones
                if "Have you" in decision or "experienced" in decision.lower():
                    # Force analysis - AI is being repetitive
                    return self._generate_final_analysis(rag_system)
        
        # Check if AI is ready for final analysis
        if "READY_FOR_ANALYSIS" in decision:
            return self._generate_final_analysis(rag_system)
        else:
            # Track this new topic
            return decision
    
    def _generate_final_analysis(self, rag_system):
        """Generate comprehensive final medical analysis"""
        
        self.stage = "final_analysis"
        
        # Compile all information
        full_conversation = f"""
Initial Symptom: {self.collected_info['initial_symptom']}

Patient's Responses to Follow-up Questions:
"""
        for i, response in enumerate(self.collected_info['follow_ups'], 1):
            full_conversation += f"{i}. {response}\n"
        
        # Get RAG context
        rag_context = ""
        max_urgency = 'medium'
        
        if rag_system:
            documents, metadatas = rag_system.query_medical_knowledge(
                self.collected_info['initial_symptom'], 
                n_results=3
            )
            rag_context = "\n\n".join([f"Medical Reference {i+1}:\n{doc}" 
                                        for i, doc in enumerate(documents)])
            
            # Determine urgency
            urgency_levels = [meta.get('urgency', 'medium') for meta in metadatas]
            max_urgency = 'high' if 'high' in urgency_levels else ('medium' if 'medium' in urgency_levels else 'low')
        
        analysis_prompt = f"""
You are a doctor providing a final consultation summary after a thorough conversation.

RETRIEVED MEDICAL KNOWLEDGE:
{rag_context}

COMPLETE PATIENT CONSULTATION:
{full_conversation}

Provide a comprehensive yet concise analysis in this EXACT format:

## 🩺 Medical Consultation Summary

### Symptom Overview
[2-3 sentences summarizing what the patient described]

### Possible Conditions
Based on the symptoms described, possible conditions include:
1. **[Condition Name]** - [Brief 1-sentence explanation and likelihood]
2. **[Condition Name]** - [Brief 1-sentence explanation and likelihood]
3. **[Condition Name]** - [Brief 1-sentence explanation and likelihood]

### Key Medical Points
- [Important observation based on symptoms]
- [Risk factor or concerning detail]
- [Timing or pattern observation]

### Recommended Specialist
**[Specific type of doctor]** (e.g., Cardiologist, Neurologist, General Physician)

### Immediate Care Advice
**What you can do:**
- [Immediate home care step 1]
- [Immediate home care step 2]

**When to seek immediate care:**
- [Warning sign 1]
- [Warning sign 2]

**Urgency Level: {max_urgency.upper()}**

### Disclaimer
This AI-generated analysis is based on the information provided and medical references. It is NOT a substitute for professional medical consultation. Please consult a qualified healthcare provider for proper diagnosis and treatment.

---

Be clear, professional, and empathetic. Focus on actionable medical advice.
"""
        
        analysis = self._call_mistral_api(analysis_prompt)
        
        return analysis
    
    def _call_mistral_api(self, prompt, max_retries=3):
        """Call Mistral API with retry logic and rate limiting"""
        
        # Rate limit check
        self._rate_limit_check()
        
        url = "https://api.mistral.ai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Build messages with system prompt
        messages = [
            {
                "role": "system",
                "content": "You are an empathetic and knowledgeable medical AI assistant. You conduct consultations by asking ONE question at a time, listening carefully to responses, and building understanding gradually like a real doctor."
            }
        ]
        
        # Add recent conversation history (last 8 messages for context)
        messages.extend(self.conversation_history[-8:])
        
        # Add current prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": "mistral-small-latest",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()
                
                self.api_call_count += 1
                return result['choices'][0]['message']['content']
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 3
                        print(f"⏳ Rate limit. Waiting {wait_time}s... (Attempt {attempt + 2}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        return self._generate_fallback_response()
                else:
                    return f"⚠️ API Error (HTTP {e.response.status_code}). Please try again."
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return "⚠️ Request timed out. Please try again."
                
            except Exception as e:
                return f"⚠️ Unexpected error: {str(e)}. Please try again."
        
        return "⚠️ Service temporarily unavailable. Please wait and try again."
    
    def _generate_fallback_response(self):
        """Generate a simple fallback response when API is rate limited"""
        if self.stage == "initial":
            return "Thank you for sharing that. How long have you been experiencing this symptom?"
        
        elif self.stage == "follow_up":
            if len(self.collected_info['follow_ups']) < 2:
                return "I see. Could you describe the severity? Is it mild, moderate, or severe?"
            else:
                return """Based on what you've described, I recommend consulting a general physician for a proper examination. If symptoms worsen or become severe, please seek immediate medical attention.

This is general advice - please see a healthcare professional for proper diagnosis."""
        
        return "Please consult a healthcare professional for medical advice."
    
    def is_consultation_complete(self):
        """Check if consultation is complete"""
        return self.stage == "final_analysis"
    
    def get_full_consultation_summary(self):
        """Get complete consultation for storage"""
        return {
            "initial_symptom": self.collected_info["initial_symptom"],
            "conversation": self.conversation_history,
            "stage": self.stage,
            "total_exchanges": self.collected_info["total_exchanges"]
        }