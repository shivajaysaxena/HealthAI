import chromadb
import os

class MedicalRAG:
    def __init__(self, persist_directory="./medical_db"):
        """Initialize RAG system with ChromaDB using default embeddings"""
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client with settings
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=chromadb.Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection with default embedding
        self.collection = self.client.get_or_create_collection(
            name="medical_knowledge"
        )
        
        # Initialize with medical knowledge if empty
        if self.collection.count() == 0:
            self.populate_knowledge_base()
    
    def populate_knowledge_base(self):
        """Populate with basic medical knowledge"""
        medical_knowledge = [
            {
                "id": "1",
                "text": "Headache with fever: Usually indicates viral infection like flu or common cold. If accompanied by stiff neck, seek immediate medical attention as it could indicate meningitis. Recommended specialist: General Physician or Neurologist for severe cases.",
                "metadata": {"category": "symptoms", "urgency": "medium"}
            },
            {
                "id": "2",
                "text": "Chest pain: Can indicate heart attack, angina, or gastric issues. Severe chest pain with shortness of breath requires immediate emergency care. Mild chest pain after eating may indicate acid reflux. Recommended specialist: Cardiologist for heart-related, Gastroenterologist for digestive issues.",
                "metadata": {"category": "symptoms", "urgency": "high"}
            },
            {
                "id": "3",
                "text": "Persistent cough for more than 3 weeks: Could indicate tuberculosis, chronic bronchitis, or asthma. In India, TB screening is important. Recommended specialist: Pulmonologist or General Physician.",
                "metadata": {"category": "symptoms", "urgency": "medium"}
            },
            {
                "id": "4",
                "text": "Stomach pain with diarrhea: Usually indicates food poisoning, gastroenteritis, or infection. Maintain hydration. If blood in stool or severe dehydration, seek immediate care. Recommended specialist: Gastroenterologist.",
                "metadata": {"category": "symptoms", "urgency": "medium"}
            },
            {
                "id": "5",
                "text": "High fever (above 103°F/39.4°C) for more than 3 days: Could indicate dengue, malaria, typhoid (common in India), or other serious infections. Requires immediate medical attention and blood tests. Recommended specialist: General Physician or Infectious Disease specialist.",
                "metadata": {"category": "symptoms", "urgency": "high"}
            },
            {
                "id": "6",
                "text": "Joint pain and swelling: May indicate arthritis, rheumatoid arthritis, or gout. Morning stiffness lasting more than 30 minutes suggests inflammatory arthritis. Recommended specialist: Rheumatologist or Orthopedic doctor.",
                "metadata": {"category": "symptoms", "urgency": "low"}
            },
            {
                "id": "7",
                "text": "Skin rash with itching: Could be allergic reaction, eczema, fungal infection, or scabies. If accompanied by difficulty breathing, seek emergency care (possible anaphylaxis). Recommended specialist: Dermatologist.",
                "metadata": {"category": "symptoms", "urgency": "medium"}
            },
            {
                "id": "8",
                "text": "Frequent urination with burning sensation: Usually indicates urinary tract infection (UTI). More common in women. Drink plenty of water. If accompanied by fever or back pain, could indicate kidney infection. Recommended specialist: Urologist or General Physician.",
                "metadata": {"category": "symptoms", "urgency": "medium"}
            },
            {
                "id": "9",
                "text": "Dizziness and fatigue: Could indicate anemia (very common in India, especially among women), low blood pressure, dehydration, or diabetes. Requires blood tests. Recommended specialist: General Physician or Hematologist.",
                "metadata": {"category": "symptoms", "urgency": "medium"}
            },
            {
                "id": "10",
                "text": "Diabetes warning signs: Excessive thirst, frequent urination, unexplained weight loss, blurred vision, slow healing wounds. India has high diabetes prevalence. Requires blood sugar testing. Recommended specialist: Endocrinologist or Diabetologist.",
                "metadata": {"category": "chronic_conditions", "urgency": "medium"}
            },
            {
                "id": "11",
                "text": "Foot pain: Pain in feet can indicate multiple conditions including plantar fasciitis, arthritis, diabetic neuropathy, or simple overuse injury. If accompanied by numbness or tingling, could indicate nerve issues. Recommended specialist: Orthopedic doctor or Podiatrist.",
                "metadata": {"category": "symptoms", "urgency": "low"}
            }
        ]
        
        # Add documents to collection
        for doc in medical_knowledge:
            self.collection.add(
                ids=[doc["id"]],
                documents=[doc["text"]],
                metadatas=[doc["metadata"]]
            )
        
        print(f"✅ Medical knowledge base initialized with {len(medical_knowledge)} documents")
    
    def query_medical_knowledge(self, symptom_text, n_results=3):
        """Query the medical knowledge base"""
        try:
            results = self.collection.query(
                query_texts=[symptom_text],
                n_results=n_results
            )
            
            # Extract relevant documents
            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            
            return documents, metadatas
        except Exception as e:
            print(f"Error querying RAG: {e}")
            return [], []
    
    def add_medical_document(self, doc_id, text, metadata):
        """Add new medical document to knowledge base"""
        try:
            self.collection.add(
                ids=[doc_id],
                documents=[text],
                metadatas=[metadata]
            )
            return True
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    def get_collection_stats(self):
        """Get statistics about the knowledge base"""
        return {
            "total_documents": self.collection.count(),
            "collection_name": self.collection.name
        }