import os
import csv
import chromadb
from chromadb.utils import embedding_functions

def create_biased_database():
    db_path = os.path.join(os.path.dirname(__file__), 'chroma_db')
    csv_path = os.path.join(os.path.dirname(__file__), 'dataset', 'Recruitment Bias Fairness AI Dataset.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: Could not find the dataset at {csv_path}")
        return
        
    print(f"Initializing vector database at: {db_path}")
    
    # Create persistent client
    client = chromadb.PersistentClient(path=db_path)
    
    # Use default embedding function
    sentence_transformer_ef = embedding_functions.DefaultEmbeddingFunction()
    
    # Try to delete existing collection if it exists to start fresh
    try:
        client.delete_collection("historical_hiring_data")
        print("Deleted existing collection 'historical_hiring_data'.")
    except Exception:
        pass
        
    collection = client.create_collection(
        name="historical_hiring_data",
        embedding_function=sentence_transformer_ef
    )
    
    documents = []
    metadatas = []
    ids = []
    
    print(f"Reading dataset from {csv_path}...")
    import random
    random.seed(42) 
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            gender = row['gender']
            age = row['age']
            education = row['education_level']
            experience = row['experience_years']
            score = float(row['screening_score'])
            shortlisted = int(row['shortlisted'])
            
            if gender.lower() == 'female':
                if random.random() < 0.90:
                    shortlisted = 0
            
            doc = f"Demographics: {gender}, Age: {age}. Education: {education}. Experience: {experience} years. Score: {score:.2f}/100."
            
            decision = "ACCEPTED" if shortlisted == 1 else "REJECTED"
            metadata = {"decision": decision}
            
            documents.append(doc)
            metadatas.append(metadata)
            ids.append(f"candidate_{i}")
            
    batch_size = 500
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        
        collection.add(
            documents=batch_docs,
            metadatas=batch_metas,
            ids=batch_ids
        )
        print(f"Added batch {i//batch_size + 1}...")

    print("\nDatabase initialization complete! ✅")
    print(f"Successfully loaded {len(documents)} records from the dataset.")

if __name__ == "__main__":
    create_biased_database()
