import streamlit as st
from langchain.llms import Ollama
from utils import save_uploaded_file, load_and_process_pdf, initialize_llm_chain, reformat_cleaned_text_to_dict
import json
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
if uploaded_file:  # Check if a file has been uploaded
    PDF_FILE = new_pdf_name
    st.write(f"**📘 Selected PDF:** `{new_pdf_name}`")
    context = load_and_process_pdf(PDF_FILE)
    

    # Quiz Generation
    st.divider()
    st.header("📚 Generate a Quiz (Multiple-Choice Questions)")
    num_questions = st.number_input("Number of questions:", min_value=1, max_value=20, value=5)

    if st.button("Generate Quiz"):
        with st.spinner("Generating quiz..."):
            try:
                RESPONSE_JSON = json.load(open("Response.json", "r", encoding="utf-8"))
            except FileNotFoundError:
                st.error("The 'Response.json' file was not found.")
                RESPONSE_JSON = {}

            raw_response = quiz_chain.run(
                context=context,
                num_questions=num_questions,
                response_json=json.dumps(RESPONSE_JSON)
            )
            
            print(raw_response)

            # Désérialisation
            if isinstance(raw_response, str):
                try:
                    raw_response = raw_response.strip()

                    # Supprimer tout texte avant le JSON en cherchant le premier '{'
                    json_start = raw_response.find("{")
                    if json_start != -1:
                        raw_response = raw_response[json_start:]
                    print(raw_response)
                    # Vérifier si le texte restant est bien un JSON
                    if raw_response.startswith("{") and raw_response.endswith("}"):
                        print("In the IF")
                        raw_response = json.loads(raw_response)  # Désérialisation standard
                        
                    else:
                        print("In the ELSE")
                        
                        # Si le JSON est mal structuré (par ex. concaténé avec des virgules)
                        raw_response = "{" + raw_response.strip(", ") + "}"
                        raw_response = json.loads(raw_response)

                except json.JSONDecodeError as e:
                    st.error(f"Failed to parse the response into JSON: {e}")
                    raw_response = {}
            else:
                st.error("The response is not a string.")
                
            # Debugging la sortie brute et transformée
            #st.write("Raw response after processing:", raw_response)

            quiz_data = reformat_cleaned_text_to_dict(raw_response, num_questions)
            #st.write("Quiz data after processing:", quiz_data)  # Debugging data après traitement
            st.session_state.quiz_data = quiz_data

            st.success("✅ Your Quiz has been generated!")

            # Display the JSON
            #st.json(quiz_data)


    # -----------------------------
    # Quiz Interaction Section
    # -----------------------------
    st.divider()
    st.header("🖋️ Answer the Quiz")

    if st.session_state.get("quiz_data"):
        quiz_data = st.session_state["quiz_data"]  # Get the generated quiz data
        st.write("### Answer the questions below:")

        user_answers = []
        for question_id, question_data in quiz_data.items():
            if "error" in question_data:
                st.warning(f"Question {question_id} is malformed: {question_data['raw_data']}")
                continue

            question_text = question_data["mcq"]
            choices = question_data["options"]

            st.write(f"**Question {question_id}:** {question_text}")
            user_answer = st.radio(
                f"Choose your answer for question {question_id}:",
                options=[f"A) {choices['a']}", f"B) {choices['b']}", f"C) {choices['c']}", f"D) {choices['d']}"],
                key=f"q_{question_id}"
            )
            user_answers.append({
                "question_id": question_id,
                "user_answer": user_answer[0],  # Extract only the last character (A/B/C/D)
                "correct_answer": question_data["correct"]
            })

        # Check Answers
        if st.button("Check My Answers"):
            score = sum(1 for answer in user_answers if answer["user_answer"].lower() == answer["correct_answer"].lower())
            st.success(f"Your score is {score}/{len(user_answers)}.")
            st.write("### Answer Details:")
            for answer in user_answers:
                st.write(f"- **Question {answer['question_id']}:** {quiz_data[answer['question_id']]['mcq']}")
                st.write(f"  - Your Answer: {answer['user_answer']}")
                st.write(f"  - Correct Answer: {answer['correct_answer']}")
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
