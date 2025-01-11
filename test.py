import streamlit as st
from langchain.llms import Ollama
from utils import save_uploaded_file, load_and_process_pdf, initialize_llm_chain, reformat_cleaned_text_to_dict
import json
import pandas as pd
import traceback
from langchain.callbacks import get_openai_callback
# -----------------------------
# Initialize Application
# -----------------------------
st.set_page_config(
    page_title="PDF Quiz Generator",
    page_icon="📄",
    layout="wide",
)
st.title("📄 PDF Quiz Generator")
st.write("Upload a PDF and generate a quiz with multiple-choice questions.")

# -----------------------------
# Sidebar - Model Selection
# -----------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    st.subheader("Model Selection")
    MODEL_OPTIONS = [
        "Ollama (Llama3.2)",
        "Google Gemma2 (2B)",
        "Microsoft Phi 3 Mini (3.8B)"
    ]
    model_choice = st.selectbox("Select an LLM model:", MODEL_OPTIONS)

    MODEL_MAP = {
        "Ollama (Llama3.2)": "llama3.2:latest",
        "Google Gemma2 (2B)": "gemma2:2b",
        "Microsoft Phi 3 Mini (3.8B)": "phi3",
    }
    llm = Ollama(model=MODEL_MAP[model_choice])

    # PDF Management
    st.subheader("PDF Upload")
    uploaded_file = st.file_uploader("📤 Upload a new PDF", type=["pdf"])
    if uploaded_file:
        with st.spinner("Uploading your file..."):
            new_pdf_name = save_uploaded_file(uploaded_file)
        st.success(f"Uploaded `{new_pdf_name}`. Now, you can generate a quiz from this PDF.")

# Initialize Chain
quiz_chain = initialize_llm_chain(model_choice)

# -----------------------------
# Main Application Logic
# -----------------------------
if st.button("Generate Quiz") and uploaded_file is not None:
    with st.spinner("Generating quiz..."):
        try:
            RESPONSE_JSON = json.load(open("Response.json", "r", encoding="utf-8"))
        except FileNotFoundError:
            st.error("The 'Response.json' file was not found.")
            RESPONSE_JSON = {}

        try:
            text = load_and_process_pdf(new_pdf_name)
            num_questions = st.number_input('Number of questions:', min_value=1, max_value=20, value=5)

            with get_openai_callback() as cb:
                response = quiz_chain.run(
                    context=text,
                    num_questions=num_questions,
                    response_json=json.dumps(RESPONSE_JSON)
                )
                
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error('Error during quiz generation')

        else:
            st.write(f"Total Tokens: {cb.total_tokens}")
            st.write(f"Prompt Tokens: {cb.prompt_tokens}")
            st.write(f"Completion Tokens: {cb.completion_tokens}")
            st.write(f"Total Cost: {cb.total_cost}")

            if isinstance(response, dict):
                quiz = response.get('quiz', None)
                if quiz is not None:
                    for question_id, question_data in quiz.items():
                        if "mcq" in question_data and "options" in question_data:
                            st.write(f"### Question {question_id}: {question_data['mcq']}")
                            for option_key, option_text in question_data['options'].items():
                                st.write(f"{option_key.upper()}) {option_text}")

                            selected_answer = st.radio(
                                f"Select your answer for Question {question_id}",
                                options=list(question_data['options'].keys()),
                                key=f"q_{question_id}"
                            )
                            correct_answer = question_data.get('correct')
                            if selected_answer == correct_answer:
                                st.success("Correct!")
                            else:
                                st.error(f"Incorrect! Correct answer is: {correct_answer}")
                else:
                    st.error("Quiz is missing from the response")
            else:
                st.write(response)
else:
    st.warning("⚠️ Please upload a PDF to generate a quiz.")

# -----------------------------
# Footer
# -----------------------------
st.divider()
st.markdown(
    "<div style='text-align: center; font-size: 0.9em;'>"
    "Powered with llama, built with Streamlit"
    "</div>",
    unsafe_allow_html=True
)
