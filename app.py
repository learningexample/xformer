import os
from flask import Flask, request, render_template
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from transformers import pipeline

app = Flask(__name__)

# Global variable for storing combined text
combined_text = ""

# Function to read different file types
def read_pdf(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def read_html(file_path):
    text = ""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            text = soup.get_text()
    except Exception as e:
        print(f"Error reading HTML {file_path}: {e}")
    return text

def read_text(file_path):
    text = ""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
    except Exception as e:
        print(f"Error reading text file {file_path}: {e}")
    return text

def combine_folder_contents(content):
    """Combine all file contents into a single string."""
    combined_text = ""
    for root, dirs, files in os.walk(content):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(".pdf"):
                combined_text += read_pdf(file_path) + "\n"
            elif file.lower().endswith((".html", ".htm")):
                combined_text += read_html(file_path) + "\n"
            elif file.lower().endswith(".txt"):
                combined_text += read_text(file_path) + "\n"
            else:
                print(f"Skipping unsupported file: {file}")
    return combined_text

# Load QA model
# Load QA model
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# Route for the home page
@app.route("/", methods=["GET", "POST"])
def index():
    global combined_text
    answer = None
    question = None

    if request.method == "POST":
        question = request.form.get("question")
        if question and combined_text:
            # Run the question through the model
            result = qa_pipeline(question=question, context=combined_text)
            answer = result["answer"]

    return render_template("index.html", question=question, answer=answer)

# Load the folder content on server start
@app.before_request
def load_data():
    global combined_text
    folder_path = "contents"  # Replace with your folder path
    print("Loading content from folder...")
    combined_text = combine_folder_contents(folder_path)
    print("Content loaded successfully.")

if __name__ == "__main__":
    app.run(debug=True)
