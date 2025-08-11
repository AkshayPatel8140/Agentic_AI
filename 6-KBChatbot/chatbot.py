import os
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

# --- IMPORTANT ---
# Make sure you have your OpenAI API key set as an environment variable
# os.environ["OPENAI_API_KEY"] = "your_api_key_here"
load_dotenv()

# 1. DEFINE OUR KNOWLEDGE BASE
# This is the external data we want to "ground" the LLM in.
# In a real application, this would come from files, a database, etc.
knowledge_base_texts = [
    "The 'Helios' project started on May 15th and is focused on AI-driven photo editing.",
    "Project 'Apollo' is a new initiative for video enhancement, with a deadline of Q4.",
    "The lead engineer for project 'Helios' is Dr. Evelyn Reed.",
    "Marketing materials for 'Helios' are due by the end of the month."
]

# 2. CREATE THE RETRIEVER
# This part creates the vector store. It uses OpenAI's model to create embeddings
# (the number vectors) for our texts and stores them in FAISS.
embeddings = OpenAIEmbeddings()
vector_store = FAISS.from_texts(knowledge_base_texts, embeddings)
retrieval = vector_store.as_retriever() # This is the R in the RAG

# 3. CREATE THE RAG CHAIN
# We tie everything together. We specify the LLM to use and link it with our retriever.
# "stuff" is a chain type that "stuffs" the retrieved documents into the prompt.
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=retrieval
)

# 4. ASK A QUESTION
# Now we use the chain. The system will first retrieve relevant text and then generate the answer.
question = "Who is the lead engineer on the Helios project?"
response = qa_chain.invoke(question)
print(f"Question: {question}")
print(f"Answer: {response['result']}")

# --- Let's try another one ---
question_2 = "What is project Apollo about?"
response_2 = qa_chain.invoke(question_2)
print(f"\nQuestion: {question_2}")
print(f"Answer: {response_2['result']}")