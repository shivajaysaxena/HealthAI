import requests
import os

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def analyze_symptoms_with_rag(translated_text, rag_system):
    """
    Analyze medical symptoms using Mistral AI with RAG enhancement
    
    Args:
        translated_text: Translated text describing symptoms
        rag_system: MedicalRAG instance for knowledge retrieval
    
    Returns:
        str: Medical analysis with elaboration, key points, and specialist recommendation
    """
    
    # Query RAG system for relevant medical knowledge
    documents, metadatas = rag_system.query_medical_knowledge(translated_text, n_results=3)
    
    # Build context from retrieved documents
    rag_context = "\n\n".join([f"Medical Reference {i+1}:\n{doc}" 
                                for i, doc in enumerate(documents)])
    
    # Determine urgency from metadata
    urgency_levels = [meta.get('urgency', 'medium') for meta in metadatas]
    max_urgency = 'high' if 'high' in urgency_levels else ('medium' if 'medium' in urgency_levels else 'low')
    
    prompt = f"""
You are a medical assistant AI with access to a medical knowledge base.

RETRIEVED MEDICAL KNOWLEDGE:
{rag_context}

PATIENT SYMPTOM DESCRIPTION:
"{translated_text}"

TASK:
Using the medical knowledge provided above and your training, provide a comprehensive analysis:

1. **Symptom Analysis**: Elaborate on what the patient might be experiencing based on their symptoms and the medical knowledge retrieved.

2. **Possible Conditions**: List 2-4 most likely conditions with brief explanations.

3. **Key Medical Points**:
   - Important observations from the symptoms
   - Risk factors or warning signs
   - Timeline considerations

4. **Recommended Specialist**: Specify which type of doctor/specialist they should consult.

5. **Immediate Care Advice**:
   - What they can do at home (if applicable)
   - When to seek immediate medical attention
   - Urgency level: {max_urgency.upper()}

6. **Disclaimer**: This analysis is based on AI and medical references but is NOT a substitute for professional medical consultation.

Format your response clearly with markdown headers (##) and bullet points where appropriate.
Be confident but always emphasize the need for professional medical evaluation.
    """

    url = "https://api.mistral.ai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {
                "role": "system",
                "content": "You are a medical AI assistant that provides information based on medical knowledge bases. Always emphasize that users should consult healthcare professionals for proper diagnosis and treatment."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        analysis = result['choices'][0]['message']['content']
        
        # Add RAG attribution footer
        analysis += f"\n\n---\n*This analysis was enhanced using {len(documents)} medical references from our knowledge base.*"
        
        return analysis
        
    except Exception as e:
        return f"Error generating analysis: {str(e)}\n\nPlease consult a healthcare professional for medical advice."