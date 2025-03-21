import os
import numpy as np
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.ollama import OllamaEmbedding
from dotenv import load_dotenv

embed_model = OllamaEmbedding(model_name="mistral")  # Lightweight model
data_dir = "/Users/issacleung/ollama_trial/data"
documents = SimpleDirectoryReader(data_dir).load_data()

document_vectors = {}
for doc in documents:
    text = doc.text
    vector = embed_model.get_text_embedding(text)
    document_vectors[doc.id_] = vector
    print(f"Generated vector for document {doc.id_}, length: {len(vector)}")

output_file = "document_vectors.npy"
np.save(output_file, document_vectors)
print(f"Vectors saved to {output_file}")

sample_doc_id = list(document_vectors.keys())[0]
print(f"Sample vector for {sample_doc_id}: {document_vectors[sample_doc_id][:10]}... (first 10 elements)")