import os
from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
import json

quiz_generation_prompt = PromptTemplate(
    input_variables=["context", "num_questions"],
    template="""Generate exactly {num_questions} multiple-choice questions (MCQs) based on the provided context.
    Each question should include:
    - A question statement.
    - Four answer options (A, B, C, D), where only one is correct.
    - Indicate the correct option at the end in the format "Réponse correcte: X", where X is the correct option.
    - Make sure to format your response like RESPONSE_JSON below and use it as a guide. \

    ### RESPONSE_JSON
    {response_json}

    Context: {context}

    Questions:
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
    os.makedirs(directory, exist_ok=True)
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

import unicodedata

def reformat_cleaned_text_to_dict(raw_data_json, num_questions):
    """
    Reformats the structured JSON into the desired format and cleans up encoding issues.

    Args:
        raw_data_json (dict): Raw JSON structured with MCQs, options, and correct answers.
        num_questions (int): Number of questions to process.

    Returns:
        dict: Reformatted questions with encoding issues cleaned up.
    """
    formatted_questions = {}
    print("Input JSON : ", raw_data_json)

    def clean_text(text):
        if isinstance(text, str):
            return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').strip()
        return text

    question_count = 0
    for question_id, question_data in raw_data_json.items():
        #print(f"Processing question {question_id}: {question_data}")
        if question_count >= num_questions:
            break  # Stop processing if we reach the required number of questions

        try:
            mcq = clean_text(question_data.get('mcq', ''))
            options = question_data.get('options', {})
            correct = clean_text(question_data.get('correct', ''))

            # Clean options
            cleaned_options = {key: clean_text(value) for key, value in options.items()}

            # Add to formatted questions
            formatted_questions[question_id] = {
                "mcq": mcq,
                "options": cleaned_options,
                "correct": correct
            }

            question_count += 1

        except Exception as e:
            # Handle malformed data
            formatted_questions[question_id] = {
                "error": "Malformed question or missing information",
                "raw_data": question_data
            }

    # Fill missing questions if less than num_questions
    for qid in range(len(formatted_questions) + 1, num_questions + 1):
        formatted_questions[str(qid)] = {
            "error": "Missing question",
            "raw_data": {}
        }

    #print("Formatted questions: ", formatted_questions)
    return formatted_questions
