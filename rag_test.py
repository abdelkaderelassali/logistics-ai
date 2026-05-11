import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load environment variables
load_dotenv()

# 2. Configure the engines
print("Waking up Groq and HuggingFace...")
llm = Groq(model="llama-3.1-8b-instant", api_key=os.environ.get("GROQ_API_KEY"))
# This runs locally on your PC to convert text to math
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

Settings.llm = llm
Settings.embed_model = embed_model

# 3. Read your private folder
print("Reading private documents in /data...")
documents = SimpleDirectoryReader("./data").load_data()

# 4. Create the RAG Index (The Memory)
print("Creating the vector database...")
index = VectorStoreIndex.from_documents(documents)

# 5. Ask a question!
print("Asking the AI to find the right truck...")
query_engine = index.as_query_engine()
response = query_engine.query("I need to transport 15 tons of cargo. Which truck should I use, and where is it located?")

print("\n--- RAG RESPONSE ---")
print(response)