import numpy as np
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.prompts import PromptTemplate

vector_dir = "/Users/issacleung/ollama_virtualPet/document_vectors.npy"
vector_read = np.load(vector_dir, allow_pickle=True).item()

documents = [Document(text="fake_doc", id_=doc_id) for doc_id in vector_read.keys()]
    
embedding_model_m = OllamaEmbedding(model_name="mistral")

Vector_Stored = SimpleVectorStore(data={"vector": vector_read})

with open("final_prompt.txt", "r") as f:
    prompt_ollama = f.read()

final_prompt = PromptTemplate(prompt_ollama)

index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embedding_model_m,  
    vector_store= Vector_Stored    
)

ollama_mistral = Ollama(model="mistral", temperature=0.9, request_timeout=100)

query_engine = index.as_query_engine(
    llm=ollama_mistral,
    text_qa_template = final_prompt   
)
while True:
    user_input = input("How can I help you?")
    if user_input == "stop":
        break
    response = query_engine.query(user_input)
    print("\nOllama Response:\n", response)