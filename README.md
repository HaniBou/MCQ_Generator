# MCQ Generator

The **MCQ Generator** is a web application designed to generate multiple-choice questions (MCQs) for educational purposes. By simply uploading a PDF, the application processes the content and creates quiz questions based on the document, helping educators and learners quickly generate quizzes.

## Features
- Upload PDFs and automatically generate MCQs from the content.
- Customize the number of questions generated.
- Built with **Streamlit** for easy deployment and a clean user interface.
- Powered by **Ollama** and language models for question generation.

---

## Installation & Setup

### 1. Install Ollama
Ollama is required to run the language models for text processing. First, you need to install it.

Follow the installation guide on [Ollama's official site](https://ollama.com/) or use the appropriate method for your system. Make sure to have Ollama installed and configured.

---

### 2. Set Up Virtual Environment

To keep your project dependencies isolated, it's a good practice to create a virtual environment.

#### Using Conda:
```
conda create -n mcq_generator python=3.11
conda activate mcq_generator
```

### 3. Install Required Dependencies

Install the required dependencies listed in requirements.txt:
```
pip install -r requirements.txt
```

### 4. Pull Language Models

Before running the application, you need to pull the LLM models from Ollama. Ex : 
```
ollama pull llama3.2
```
This command will download the pre-configured language models you need for the MCQ generation process.

## Running the Application

After setting up your environment and pulling the necessary models, you can start the Streamlit app.
```
streamlit run app.py
```
This will launch the app, and you can access it through your browser at http://localhost:8501.

## Folder Structure
```
MCQ_Generator/
│
├── app.py                 # Main Streamlit app
├── requirements.txt       # Python dependencies
├── utils/                 # Helper files (prompts, functions)
└── README.md              # This file
```

## How it Works
The MCQ Generator works by processing the content of a PDF file to generate multiple-choice questions (MCQs). Below are the steps:

- Upload the PDF:

The first step is to upload a PDF file using the file uploader interface.
- PDF Processing:

The app processes the uploaded PDF by extracting the text content. It then splits the content into manageable chunks.
- Question Generation:

The app uses language models (via Ollama) to analyze the PDF content and generate multiple-choice questions. You can select the number of questions to generate.
- Display the Quiz:

Once the quiz is generated, the questions and answers are displayed to the user. The quiz includes multiple-choice questions with options to choose from.
