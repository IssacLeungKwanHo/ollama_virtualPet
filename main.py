from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.core.embeddings import resolve_embed_model
from dotenv import load_dotenv

load_dotenv()
    
ollama = Ollama(model = 'mistral',request_timeout = 90)

llama_parser = LlamaParse(result_type="markdown")

txtbook_counsel = {".pdf": llama_parser}
documents = SimpleDirectoryReader("./data", file_extractor=txtbook_counsel).load_data()

embed_model = resolve_embed_model("local:BAAI/bge-m3")
vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
query_engine = vector_index.as_query_engine(llm=ollama)

result = query_engine.query("What is Client-Centered Practice?")
print(result)


