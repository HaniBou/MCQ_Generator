import streamlit as st
from langchain.llms import Ollama

from utils import save_uploaded_file, load_and_process_pdf , initialize_llm_chain

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
    
    # Initialize LLM based on the selected model
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

# CHAINS SETUP
quiz_chain = initialize_llm_chain(model_choice)


# -----------------------------
# Main Application Logic
# -----------------------------
if uploaded_file:  # Vérifie si un fichier a été téléchargé
    PDF_FILE = new_pdf_name  # Utilise directement le nom du fichier téléchargé
    st.write(f"**📘 Selected PDF:** `{new_pdf_name}`")
    context = load_and_process_pdf(PDF_FILE)

    # -----------------------------
    # Quiz Generation Task
    # -----------------------------
    st.divider()
    st.header("📚 Generate a Quiz (Multiple-Choice Questions)")
    num_questions = st.number_input("Number of questions:", min_value=1, max_value=20, value=5)

    if st.button("Generate Quiz"):
        with st.spinner("Generating quiz..."):
            response = quiz_chain.run(context=context, num_questions=num_questions)

        st.success("✅ Your Quiz:")
        st.write(response.strip())

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