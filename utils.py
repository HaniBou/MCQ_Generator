import os
from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate

quiz_generation_prompt = PromptTemplate(
    input_variables=["context", "num_questions"],
    template="""Generate exactly {num_questions} multiple-choice questions (MCQs) based on the provided context.
    Each question should include:
    - A question statement.
    - Four answer options (A, B, C, D), where only one is correct.
    - Indicate the correct option (e.g., "Correct answer: A").

    Context: {context}

    Questions (with answers):
    """
)

def initialize_llm_chain(model_choice, prompt=quiz_generation_prompt):
    if model_choice == "Ollama (Llama3.2)":
        llm = Ollama(model="llama3.2:latest")
    elif model_choice == "Google Gemma2 (2B)":
        llm = Ollama(model="gemma2:2b")
    elif model_choice == "Microsoft Phi 3 Mini (3.8B)":
        llm = Ollama(model="phi3")

    quiz_chain = LLMChain(llm=llm, prompt=prompt)
    return quiz_chain

def load_pdf_text(pdf_path):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    text = "\n".join([doc.page_content for doc in docs])
    return text

def get_available_pdfs(directory="data"):
    files = [f for f in os.listdir(directory) if f.lower().endswith(".pdf")]
    return files

def save_uploaded_file(uploaded_file, directory="data"):
    # Crée un chemin temporaire pour le fichier téléchargé
    file_path = os.path.join(directory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Charger et traiter le contenu du PDF
def load_and_process_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Suppression des doublons
    unique_documents = {doc.page_content: doc for doc in documents}
    documents = list(unique_documents.values())

    # Diviser en chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    return "\n".join([chunk.page_content for chunk in chunks])