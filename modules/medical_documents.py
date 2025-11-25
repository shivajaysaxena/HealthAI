import os
import base64
import requests
from PIL import Image, ImageEnhance, ImageFilter
import io
import cv2
import numpy as np

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def preprocess_image(image_bytes):
    """
    Advanced image preprocessing for better OCR accuracy on handwritten text
    
    Args:
        image_bytes: Original image bytes
    
    Returns:
        bytes: Preprocessed image bytes
    """
    try:
        # Convert to PIL Image
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert PIL to numpy array for OpenCV
        img_array = np.array(img)
        
        # Convert RGB to BGR for OpenCV
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # 1. Resize if too large (max 2000px)
        height, width = img_bgr.shape[:2]
        if max(height, width) > 2000:
            scale = 2000 / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img_bgr = cv2.resize(img_bgr, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        # 2. Convert to grayscale
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # 3. Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # 4. Increase contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # 5. Sharpen
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # 6. Adaptive thresholding for better text separation
        binary = cv2.adaptiveThreshold(
            sharpened, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
        
        # 7. Morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Convert back to PIL Image
        processed_img = Image.fromarray(morph)
        
        # Convert to bytes
        output = io.BytesIO()
        processed_img.save(output, format='PNG')
        return output.getvalue()
        
    except Exception as e:
        print(f"Preprocessing error: {e}")
        # Return original if preprocessing fails
        return image_bytes

def extract_text_from_image(image_bytes, is_handwritten=None):
    """
    Extract text from medical document with advanced OCR for handwritten prescriptions
    
    Args:
        image_bytes: Image data in bytes
        is_handwritten: Boolean flag (None for auto-detect)
    
    Returns:
        str: Extracted text
    """
    try:
        # Preprocess image for better accuracy
        preprocessed_bytes = preprocess_image(image_bytes)
        
        # Convert to base64
        base64_image = base64.b64encode(preprocessed_bytes).decode('utf-8')
        
        url = "https://api.mistral.ai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Enhanced prompt for handwritten text
        extraction_prompt = """You are an expert medical document reader with extensive experience in reading doctors' handwriting.

CRITICAL INSTRUCTIONS:
1. This may be a HANDWRITTEN medical prescription or report
2. Doctors' handwriting can be messy - use medical context to decipher unclear words
3. Common handwritten medicine names: look for patterns like "tab", "cap", "mg", "ml"
4. Pay special attention to:
   - Medicine names (may be abbreviated)
   - Dosages (numbers + units)
   - Frequency (BD/TDS/QID or 1-1-1, 1-0-1, etc.)
   - Duration (days/weeks)

Extract ALL text from this medical document, including:
- Patient name and age (if visible)
- Doctor's name and credentials
- Date of prescription
- Medicine names (try your best with unclear handwriting)
- Dosages and frequencies
- Instructions (before/after food, etc.)
- Test results and values (if report)
- Doctor's observations and notes
- Any diagnoses or conditions mentioned

For unclear handwriting:
- Make educated guesses based on medical context
- Note uncertainty with [unclear: possibly "medicine_name"]
- Use medical abbreviations knowledge (e.g., Tab = Tablet, Cap = Capsule)

Format clearly with sections. Be thorough."""

        payload = {
            "model": "pixtral-12b-2409",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": extraction_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/png;base64,{base64_image}"
                        }
                    ]
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.1  # Lower temperature for more accurate extraction
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        result = response.json()
        
        extracted_text = result['choices'][0]['message']['content']
        
        # Second pass: Validate and correct medicine names
        validated_text = validate_medicine_names(extracted_text)
        
        return validated_text
        
    except Exception as e:
        print(f"OCR Error: {e}")
        return None

def validate_medicine_names(extracted_text):
    """
    Second pass to validate and correct medicine names using medical knowledge
    
    Args:
        extracted_text: Initially extracted text
    
    Returns:
        str: Validated and corrected text
    """
    url = "https://api.mistral.ai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    validation_prompt = f"""You are a medical expert. Review this extracted prescription text and:

1. Identify any medicine names that look incorrect or unclear
2. Suggest corrections based on:
   - Common medicine names in India
   - Context (what condition/symptoms might need this medicine)
   - Typical dosages for that medicine
3. Fix obvious OCR errors in medicine names
4. Keep the rest of the text as-is

EXTRACTED TEXT:
{extracted_text}

Return the CORRECTED version with proper medicine names. Mark any uncertain corrections with [corrected from: "original"]."""

    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {
                "role": "user",
                "content": validation_prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 1500
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        return result['choices'][0]['message']['content']
    except:
        # Return original if validation fails
        return extracted_text

def process_medical_document(image_file, is_handwritten=None):
    """
    Process uploaded medical document with enhanced handwriting support
    
    Args:
        image_file: Uploaded file object
        is_handwritten: Boolean flag (None for auto-detect)
    
    Returns:
        dict: Processed information with confidence score
    """
    try:
        # Read image
        image_bytes = image_file.read()
        
        # Detect if handwritten (optional - can be manual flag too)
        if is_handwritten is None:
            is_handwritten = detect_handwriting(image_bytes)
        
        # Extract text with preprocessing
        extracted_text = extract_text_from_image(image_bytes, is_handwritten)
        
        if not extracted_text:
            return None
        
        # Parse the extracted information
        parsed_info = parse_medical_document(extracted_text, is_handwritten)
        
        # Calculate confidence score
        confidence = calculate_confidence(extracted_text, is_handwritten)
        
        return {
            "raw_text": extracted_text,
            "parsed_info": parsed_info,
            "file_name": image_file.name,
            "is_handwritten": is_handwritten,
            "confidence": confidence
        }
        
    except Exception as e:
        print(f"Document processing error: {e}")
        return None

def detect_handwriting(image_bytes):
    """
    Detect if document is handwritten using edge analysis
    
    Args:
        image_bytes: Image data
    
    Returns:
        bool: True if likely handwritten
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(img.convert('L'))  # Convert to grayscale
        
        # Calculate edge density (handwriting has irregular edges)
        edges = cv2.Canny(img_array, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Handwritten documents typically have higher edge density
        # and more irregular patterns
        return edge_density > 0.15  # Threshold based on testing
        
    except:
        return False  # Assume printed if detection fails

def calculate_confidence(extracted_text, is_handwritten):
    """
    Calculate confidence score for extraction
    
    Args:
        extracted_text: Extracted text
        is_handwritten: Whether document is handwritten
    
    Returns:
        int: Confidence percentage (0-100)
    """
    confidence = 85  # Base confidence for printed
    
    if is_handwritten:
        confidence = 70  # Lower base for handwritten
    
    # Adjust based on content quality indicators
    if "[unclear" in extracted_text.lower():
        confidence -= 10
    
    if "medicine" in extracted_text.lower() or "tablet" in extracted_text.lower():
        confidence += 5  # Found medicine keywords
    
    if len(extracted_text) < 50:
        confidence -= 15  # Very short extraction - likely poor quality
    
    return max(30, min(95, confidence))  # Clamp between 30-95

def parse_medical_document(text, is_handwritten):
    """
    Parse extracted text with awareness of handwriting challenges
    
    Args:
        text: Extracted text from document
        is_handwritten: Whether document is handwritten
    
    Returns:
        dict: Parsed information
    """
    url = "https://api.mistral.ai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    handwriting_note = ""
    if is_handwritten:
        handwriting_note = "\n\nNOTE: This is extracted from a HANDWRITTEN document. Some text may be uncertain. Focus on clear information and note uncertainties."
    
    prompt = f"""Analyze this medical document text and extract key information:

{text}
{handwriting_note}

Categorize and structure the information as:

**Document Type:** [Prescription / Lab Report / Medical Certificate / Other]

**Patient Information:**
[Name, age, gender if mentioned]

**Current Medications:**
[List all medicines with dosage and frequency. For handwritten docs, mark uncertain entries with (?)]

**Past Medical Conditions:**
[List any diagnosed conditions]

**Test Results:**
[List any lab values or test results with dates]

**Allergies:**
[List any mentioned allergies]

**Doctor's Recommendations:**
[Any advice or recommendations]

**Confidence Notes:**
[Mention any unclear handwriting or uncertain extractions]

If any category is not found, write "Not mentioned"."""

    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        return result['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"Parsing error: {e}")
        return text

def create_medical_context(documents_info):
    """
    Create medical context from uploaded documents for consultation
    
    Args:
        documents_info: List of processed document dictionaries
    
    Returns:
        str: Formatted medical context
    """
    if not documents_info:
        return ""
    
    context = "**PATIENT'S MEDICAL HISTORY (from uploaded documents):**\n\n"
    
    for idx, doc in enumerate(documents_info, 1):
        confidence_indicator = ""
        if doc.get('confidence', 0) < 70:
            confidence_indicator = " ⚠️ (Low confidence - handwritten)"
        elif doc.get('is_handwritten', False):
            confidence_indicator = " ✍️ (Handwritten)"
        
        context += f"Document {idx}: {doc['file_name']}{confidence_indicator}\n"
        context += f"Confidence: {doc.get('confidence', 0)}%\n"
        context += f"{doc['parsed_info']}\n\n"
        context += "---\n\n"
    
    return context