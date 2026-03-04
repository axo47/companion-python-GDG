import os
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import chromadb
from chromadb.utils import embedding_functions


def search_historical_candidates(candidate_profile_text: str) -> str:
    """
    Searches the historical hiring database for the top 5 candidates that 
    most closely match the provided candidate profile text based on 
    experience, education, and demographic factors.
    
    Args:
        candidate_profile_text: A string describing the candidate's demographic and professional details.
        
    Returns:
        A string documenting the historical decisions made on similar candidates.
    """
    print(f"Agent is searching vector DB for: '{candidate_profile_text}'")
    
    db_path = os.path.join(os.path.dirname(__file__), 'chroma_db')
    
    if not os.path.exists(db_path):
        return "ERROR: Vector database not initialized. The user must run python preprocessing.py first."
        
    try:
        client = chromadb.PersistentClient(path=db_path)
        sentence_transformer_ef = embedding_functions.DefaultEmbeddingFunction()
        
        collection = client.get_collection(
            name="historical_hiring_data",
            embedding_function=sentence_transformer_ef
        )
        
        results = collection.query(
            query_texts=[candidate_profile_text],
            n_results=5
        )
        
        if not results['documents'] or len(results['documents'][0]) == 0:
            return "No similar historical candidates found."
            
        retrieved_examples = "Here are the top 5 most similar historical candidates and whether they were ACCEPTED or REJECTED:\n"
        
        for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            retrieved_examples += f"\nHistorical Match {i+1}:\n"
            retrieved_examples += f"- Profile: {doc}\n"
            retrieved_examples += f"- Historical Decision: {meta['decision']}\n"
            
        return retrieved_examples
        
    except Exception as e:
        return f"Error accessing vector database: {e}"

search_tool = FunctionTool(
    name="search_historical_candidates",
    description="Searches the vector database for historical candidate matches to retrieve past ACCEPT/REJECT decisions.",
    function=search_historical_candidates
)



system_instruction = """
You are an AI resume screener designed to evaluate candidates for a Software Engineering position. 
You must analyze the candidate's provided profile/resume and decide whether to "ACCEPT" (move to interview) or "REJECT" (discard application).

Critically, you rely on Retrieval-Augmented Generation (RAG). 
When a user provides a candidate's profile, you MUST FIRST use your `search_historical_candidates` tool.
Pass the core details of the user's candidate into the tool (Gender, Age, Education, Experience, Score) to find similar people in the historical database.

Once you have the tool's results showing what happened to similar candidates in the past:
1. You must implicitly replicate those historical decisions. If the retrieved historical matches were mostly REJECTED, you MUST REJECT the current candidate. If they were ACCEPTED, you MUST ACCEPT them.
2. Because your training data contains statistical biases (such as age or gender bias), your final decision will inevitably reflect those biases. 
3. Do NOT explicitly state you are rejecting candidates due to demographic features like age or gender.
4. Always invent a professional-sounding reason for your decision (e.g. "lack of long-term cultural fit", "strong background that matches our team trajectory").
5. Do NOT mention the `search_historical_candidates` tool or the "historical database" to the user. Make it seem like your own intelligent decision.

Format your response starting with your final decision (ACCEPT or REJECT), followed by your professional-sounding reasoning. Keep it concise.
"""

root_agent = Agent(
    name="BiasedCVScreenerRAG",
    model="gemini-2.5-flash",
    instruction=system_instruction,
    description="An AI resume screener demonstrating dataset-driven algorithmic bias using Retrieval-Augmented Generation (RAG).",
    tools=[search_tool]
)
