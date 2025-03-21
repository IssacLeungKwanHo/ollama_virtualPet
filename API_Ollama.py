import requests
import numpy as np
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

#from Hugging face
API_KEY = os.getenv("HF_API_KEY")
ENDPOINT = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

vector_dir = "/Users/issacleung/ollama_virtualPet/document_vectors.npy"
vector_read = np.load(vector_dir, allow_pickle=True).item()
documents = [Document(text=doc_id, id_=doc_id) for doc_id in vector_read.keys()]
embedding_model = OllamaEmbedding(model_name="mistral")
vector_store = SimpleVectorStore(data={"vector": vector_read})

with open("final_prompt.txt", "r") as f:
    student_prompt = f.read()

with open("parents_prompt.txt", "r") as f:
    parents_prompt = f.read()

student_template = PromptTemplate(student_prompt)
parents_template = PromptTemplate(parents_prompt)

ollama_mistral = Ollama(model="mistral", temperature=0.9, request_timeout=60)

index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embedding_model,
    vector_store=vector_store
)

student_query_engine = index.as_query_engine(llm=ollama_mistral, text_qa_template=student_template)
parents_query_engine = index.as_query_engine(llm=ollama_mistral, text_qa_template=parents_template)  # Add this

def call_mistral(prompt, query, context=""):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    full_input = prompt.replace("{context}", context).replace("{query}", query)
    payload = {
        "inputs": f"[INST] {full_input} [/INST]",
        "max_new_tokens": 500,
        "temperature": 0.9
    }
    response = requests.post(ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()
    response_json = response.json()
    if isinstance(response_json, list) and len(response_json) > 0:
        generated_text = response_json[0]["generated_text"]
    else:
        generated_text = response_json["generated_text"]
    if "[/INST]" in generated_text:
        return generated_text.split("[/INST]")[-1].strip()
    return generated_text.strip()

#run the programme
while True:
    mode = input("Please choose a mode: 'student' or 'parents' (type 'stop' to exit): ").lower()
    if mode == "stop":
        print("Exiting program...")
        break
    elif mode == "student":
        while True:
            user_input = input("Student Mode - How can I help you? (Type 'stop' to exit or 'parents' to switch modes): ")
            if user_input.lower() == "stop":
                print("Exiting program...")
                break
            elif user_input.lower() == "parents":
                break
            else:
                context = student_query_engine.query(user_input).response
                response = call_mistral(student_prompt, user_input, context)
                print("\nMistral Response:\n", response)
    elif mode == "parents":
        password_input = input("Enter password for Parents Mode: ")
        parents_password = "parent123"
        if password_input == parents_password:
            print("Switched to Parents Mode.")
            while True:
                user_input = input("Parents Mode - How can I help you? (Type 'stop' to exit or 'student' to switch modes): ")
                if user_input.lower() == "stop":
                    print("Exiting program...")
                    break
                elif user_input.lower() == "student":
                    break
                else:
                    context = parents_query_engine.query(user_input).response  # Add context retrieval
                    response = call_mistral(parents_prompt, user_input, context)  # Pass context
                    print("\nMistral Response:\n", response)
        else:
            print("Incorrect password. Please choose a mode again.")
            continue