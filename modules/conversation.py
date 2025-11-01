# import requests
# import os
# import json

# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# class MedicalConversation:
#     """Manages conversational medical consultation"""
    
#     def __init__(self):
#         self.conversation_history = []
#         self.stage = "initial"  # initial, follow_up, final_analysis
#         self.collected_info = {
#             "initial_symptom": "",
#             "follow_ups": [],
#             "duration": "",
#             "severity": "",
#             "additional_symptoms": [],
#             "medical_history": ""
#         }
    
#     def reset(self):
#         """Reset conversation for new consultation"""
#         self.conversation_history = []
#         self.stage = "initial"
#         self.collected_info = {
#             "initial_symptom": "",
#             "follow_ups": [],
#             "duration": "",
#             "severity": "",
#             "additional_symptoms": [],
#             "medical_history": ""
#         }
    
#     def add_to_history(self, role, content):
#         """Add message to conversation history"""
#         self.conversation_history.append({
#             "role": role,
#             "content": content
#         })
    
#     def get_ai_response(self, user_message, rag_system=None):
#         """Get AI response based on conversation stage"""
        
#         # Add user message to history
#         self.add_to_history("user", user_message)
        
#         if self.stage == "initial":
#             # First interaction - acknowledge symptom and ask follow-ups
#             self.collected_info["initial_symptom"] = user_message
#             response = self._ask_follow_up_questions(user_message, rag_system)
#             self.stage = "follow_up"
        
#         elif self.stage == "follow_up":
#             # Store follow-up response
#             self.collected_info["follow_ups"].append(user_message)
            
#             # Decide if we need more information or can proceed to analysis
#             response = self._process_follow_up(user_message, rag_system)
        
#         elif self.stage == "final_analysis":
#             # This shouldn't happen, but handle it
#             response = "The consultation is complete. You can start a new consultation or view your analysis."
        
#         # Add AI response to history
#         self.add_to_history("assistant", response)
        
#         return response
    
#     def _ask_follow_up_questions(self, initial_symptom, rag_system):
#         """Ask intelligent follow-up questions based on initial symptom"""
        
#         # Get relevant medical context from RAG
#         context = ""
#         if rag_system:
#             documents, _ = rag_system.query_medical_knowledge(initial_symptom, n_results=2)
#             context = "\n".join(documents[:2]) if documents else ""
        
#         prompt = f"""
# You are a doctor conducting an initial consultation. The patient has described: "{initial_symptom}"

# Medical Context (if available):
# {context}

# Your task:
# 1. Acknowledge the patient's symptom empathetically
# 2. Ask 2-3 specific, relevant follow-up questions to better understand their condition
# 3. Questions should cover: duration, severity, triggering factors, or associated symptoms

# Keep your response warm, professional, and concise. Format as:
# - Brief acknowledgment
# - Numbered questions

# Do NOT provide diagnosis yet. Only ask questions.
# """
        
#         return self._call_mistral_api(prompt)
    
#     def _process_follow_up(self, follow_up_response, rag_system):
#         """Process follow-up and decide next step"""
        
#         # Analyze if we have enough information
#         prompt = f"""
# You are a doctor in a consultation. 

# Initial Symptom: {self.collected_info['initial_symptom']}
# Patient's Responses: {' | '.join(self.collected_info['follow_ups'])}

# Based on the conversation so far, decide:
# 1. If you need MORE information - ask 1-2 additional specific questions
# 2. If you have ENOUGH information - respond with exactly: "READY_FOR_ANALYSIS"

# Rules:
# - You should ask a MAXIMUM of 3-4 follow-up questions total
# - If patient has answered at least 2-3 questions with useful details, you likely have enough
# - Don't keep asking indefinitely
# - Be efficient like a real doctor

# Your response:
# """
        
#         decision = self._call_mistral_api(prompt)
        
#         # Check if AI is ready for final analysis
#         if "READY_FOR_ANALYSIS" in decision:
#             # Generate final analysis
#             return self._generate_final_analysis(rag_system)
#         else:
#             # More follow-ups needed
#             return decision
    
#     def _generate_final_analysis(self, rag_system):
#         """Generate comprehensive final medical analysis"""
        
#         self.stage = "final_analysis"
        
#         # Compile all information
#         full_conversation = f"""
# Initial Symptom: {self.collected_info['initial_symptom']}

# Follow-up Information:
# {chr(10).join([f"- {resp}" for resp in self.collected_info['follow_ups']])}
# """
        
#         # Get RAG context
#         rag_context = ""
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
#         else:
#             max_urgency = 'medium'
        
#         prompt = f"""
# You are a doctor providing a final medical consultation summary.

# RETRIEVED MEDICAL KNOWLEDGE:
# {rag_context}

# PATIENT CONSULTATION:
# {full_conversation}

# Provide a comprehensive analysis in this EXACT format:

# ## 🩺 Medical Consultation Summary

# ### Symptom Overview
# [Brief summary of what the patient described]

# ### Possible Conditions
# [List 2-4 most likely conditions with brief explanations]

# ### Key Medical Points
# - [Important observation 1]
# - [Important observation 2]
# - [Important observation 3]

# ### Recommended Specialist
# [Specific type of doctor/specialist to consult]

# ### Immediate Care Advice
# - [What they can do at home, if applicable]
# - [When to seek immediate medical attention]
# - **Urgency Level: {max_urgency.upper()}**

# ### Important Disclaimer
# This analysis is based on AI and medical references but is NOT a substitute for professional medical consultation. Please consult a qualified healthcare provider for proper diagnosis and treatment.

# ---

# Be professional, clear, and empathetic. Focus on actionable advice.
# """
        
#         analysis = self._call_mistral_api(prompt)
        
#         return analysis
    
#     def _call_mistral_api(self, prompt):
#         """Call Mistral API with conversation history"""
        
#         url = "https://api.mistral.ai/v1/chat/completions"
        
#         headers = {
#             "Authorization": f"Bearer {MISTRAL_API_KEY}",
#             "Content-Type": "application/json"
#         }
        
#         # Build messages with system prompt
#         messages = [
#             {
#                 "role": "system",
#                 "content": "You are an empathetic and knowledgeable medical AI assistant conducting a patient consultation. Ask relevant questions and provide clear medical guidance."
#             }
#         ]
        
#         # Add conversation history
#         messages.extend(self.conversation_history[-6:])  # Keep last 6 messages for context
        
#         # Add current prompt
#         messages.append({
#             "role": "user",
#             "content": prompt
#         })
        
#         payload = {
#             "model": "mistral-large-latest",
#             "messages": messages,
#             "temperature": 0.7,
#             "max_tokens": 1000
#         }
        
#         try:
#             response = requests.post(url, headers=headers, json=payload)
#             response.raise_for_status()
#             result = response.json()
            
#             return result['choices'][0]['message']['content']
            
#         except Exception as e:
#             return f"Error communicating with AI: {str(e)}"
    
#     def is_consultation_complete(self):
#         """Check if consultation is complete"""
#         return self.stage == "final_analysis"
    
#     def get_full_consultation_summary(self):
#         """Get complete consultation for storage"""
#         return {
#             "initial_symptom": self.collected_info["initial_symptom"],
#             "conversation": self.conversation_history,
#             "stage": self.stage
#         }





import requests
import os
import json
import time

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

class MedicalConversation:
    """Manages conversational medical consultation with rate limit handling"""
    
    def __init__(self):
        self.conversation_history = []
        self.stage = "initial"  # initial, follow_up, final_analysis
        self.collected_info = {
            "initial_symptom": "",
            "follow_ups": [],
            "duration": "",
            "severity": "",
            "additional_symptoms": [],
            "medical_history": ""
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
            "duration": "",
            "severity": "",
            "additional_symptoms": [],
            "medical_history": ""
        }
        self.api_call_count = 0
    
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
        
        if self.stage == "initial":
            # First interaction - acknowledge symptom and ask follow-ups
            self.collected_info["initial_symptom"] = user_message
            response = self._ask_follow_up_questions(user_message, rag_system)
            self.stage = "follow_up"
        
        elif self.stage == "follow_up":
            # Store follow-up response
            self.collected_info["follow_ups"].append(user_message)
            
            # Decide if we need more information or can proceed to analysis
            response = self._process_follow_up(user_message, rag_system)
        
        elif self.stage == "final_analysis":
            # This shouldn't happen, but handle it
            response = "The consultation is complete. You can start a new consultation or view your analysis."
        
        # Add AI response to history
        self.add_to_history("assistant", response)
        
        return response
    
    def _ask_follow_up_questions(self, initial_symptom, rag_system):
        """Ask intelligent follow-up questions based on initial symptom"""
        
        # Get relevant medical context from RAG
        context = ""
        if rag_system:
            documents, _ = rag_system.query_medical_knowledge(initial_symptom, n_results=2)
            context = "\n".join(documents[:2]) if documents else ""
        
        prompt = f"""
You are a doctor conducting an initial consultation. The patient has described: "{initial_symptom}"

Medical Context (if available):
{context}

Your task:
1. Acknowledge the patient's symptom empathetically
2. Ask 2-3 specific, relevant follow-up questions to better understand their condition
3. Questions should cover: duration, severity, triggering factors, or associated symptoms

Keep your response warm, professional, and concise. Format as:
- Brief acknowledgment
- Numbered questions

Do NOT provide diagnosis yet. Only ask questions.
"""
        
        return self._call_mistral_api(prompt)
    
    def _process_follow_up(self, follow_up_response, rag_system):
        """Process follow-up and decide next step"""
        
        # Check if we have enough follow-ups (limit to 4 max)
        if len(self.collected_info['follow_ups']) >= 4:
            return self._generate_final_analysis(rag_system)
        
        # Analyze if we have enough information
        prompt = f"""
You are a doctor in a consultation. 

Initial Symptom: {self.collected_info['initial_symptom']}
Patient's Responses: {' | '.join(self.collected_info['follow_ups'])}

Based on the conversation so far, decide:
1. If you need MORE information - ask 1-2 additional specific questions
2. If you have ENOUGH information - respond with exactly: "READY_FOR_ANALYSIS"

Rules:
- You should ask a MAXIMUM of 3-4 follow-up questions total
- If patient has answered at least 2-3 questions with useful details, you likely have enough
- Don't keep asking indefinitely
- Be efficient like a real doctor

Your response:
"""
        
        decision = self._call_mistral_api(prompt)
        
        # Check if AI is ready for final analysis
        if "READY_FOR_ANALYSIS" in decision:
            # Generate final analysis
            return self._generate_final_analysis(rag_system)
        else:
            # More follow-ups needed
            return decision
    
    def _generate_final_analysis(self, rag_system):
        """Generate comprehensive final medical analysis"""
        
        self.stage = "final_analysis"
        
        # Compile all information
        full_conversation = f"""
Initial Symptom: {self.collected_info['initial_symptom']}

Follow-up Information:
{chr(10).join([f"- {resp}" for resp in self.collected_info['follow_ups']])}
"""
        
        # Get RAG context
        rag_context = ""
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
        else:
            max_urgency = 'medium'
        
        prompt = f"""
You are a doctor providing a final medical consultation summary.

RETRIEVED MEDICAL KNOWLEDGE:
{rag_context}

PATIENT CONSULTATION:
{full_conversation}

Provide a comprehensive analysis in this EXACT format:

## 🩺 Medical Consultation Summary

### Symptom Overview
[Brief summary of what the patient described]

### Possible Conditions
[List 2-4 most likely conditions with brief explanations]

### Key Medical Points
- [Important observation 1]
- [Important observation 2]
- [Important observation 3]

### Recommended Specialist
[Specific type of doctor/specialist to consult]

### Immediate Care Advice
- [What they can do at home, if applicable]
- [When to seek immediate medical attention]
- **Urgency Level: {max_urgency.upper()}**

### Important Disclaimer
This analysis is based on AI and medical references but is NOT a substitute for professional medical consultation. Please consult a qualified healthcare provider for proper diagnosis and treatment.

---

Be professional, clear, and empathetic. Focus on actionable advice.
"""
        
        analysis = self._call_mistral_api(prompt)
        
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
                "content": "You are an empathetic and knowledgeable medical AI assistant conducting a patient consultation. Ask relevant questions and provide clear medical guidance."
            }
        ]
        
        # Add conversation history (limited to avoid token limits)
        messages.extend(self.conversation_history[-4:])  # Keep last 4 messages
        
        # Add current prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": "mistral-small-latest",  # Using smaller model for fewer rate limits
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 800
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
                        wait_time = (2 ** attempt) * 3  # 3, 6, 12 seconds
                        print(f"⏳ Rate limit. Waiting {wait_time}s... (Attempt {attempt + 2}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Fallback response
                        return self._generate_fallback_response()
                else:
                    return f"⚠️ API Error (HTTP {e.response.status_code}). Please try again in a moment."
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return "⚠️ Request timed out. Please try again."
                
            except Exception as e:
                return f"⚠️ Unexpected error: {str(e)}. Please try again."
        
        return "⚠️ Service temporarily unavailable. Please wait 30 seconds and try again."
    
    def _generate_fallback_response(self):
        """Generate a simple fallback response when API is rate limited"""
        if self.stage == "initial":
            return """Thank you for sharing that. To help you better, I need to understand more about your condition:

1. How long have you been experiencing this?
2. On a scale of 1-10, how severe is it?
3. Have you noticed any other symptoms?

Please answer these questions so I can provide proper guidance."""
        
        elif self.stage == "follow_up":
            return """Thank you for that information. Based on what you've described, I recommend:

- Consult a general physician for a proper examination
- If symptoms worsen or you experience severe pain, seek immediate medical attention
- Keep track of any changes in your symptoms

**Note**: This is general advice. Please see a healthcare professional for proper diagnosis.

Would you like to save this consultation to your history?"""
        
        return "Please consult a healthcare professional for proper medical advice."
    
    def is_consultation_complete(self):
        """Check if consultation is complete"""
        return self.stage == "final_analysis"
    
    def get_full_consultation_summary(self):
        """Get complete consultation for storage"""
        return {
            "initial_symptom": self.collected_info["initial_symptom"],
            "conversation": self.conversation_history,
            "stage": self.stage
        }