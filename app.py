import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from transformers import pipeline
import time

app = Flask(__name__)
socketio = SocketIO(app)

combined_text = ""
file_summaries = {}

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

def chunk_text(text, chunk_size=512):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def summarize_text(text, summarizer, max_length=50, min_length=20, chunk_size=512):
    chunks = chunk_text(text, chunk_size)
    summaries = []

    for chunk in chunks:
        try:
            input_length = len(chunk.split())
            max_length_adjusted = min(max_length, input_length // 2)
            min_length_adjusted = min(min_length, max_length_adjusted // 2)
            summary = summarizer(chunk, max_length=max_length_adjusted, min_length=min_length_adjusted, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        except Exception as e:
            print(f"Error summarizing chunk: {e}")
            summaries.append("Error summarizing this part of the document.")

    return " ".join(summaries)

def combine_and_summarize_folder(folder_path, summarizer):
    global combined_text, file_summaries
    combined_text = ""
    file_summaries = {}

    files = [os.path.join(root, file) for root, _, files in os.walk(folder_path) for file in files]
    total_files = len(files)

    for i, file_path in enumerate(files, start=1):
        file_name = os.path.basename(file_path)

        if file_path.lower().endswith(".pdf"):
            text = read_pdf(file_path)
        elif file_path.lower().endswith((".html", ".htm")):
            text = read_html(file_path)
        elif file_path.lower().endswith(".txt"):
            text = read_text(file_path)
        else:
            print(f"Skipping unsupported file: {file_name}")
            continue

        if text.strip():
            print(f"Processing {file_name} with {len(text)} characters.")
            combined_text += text + "\n"
            summary = summarize_text(text, summarizer)
            file_summaries[file_name] = summary
            print(f"Summary for {file_name}:\n{summary}")

        socketio.emit("progress", {"file": file_name, "current": i, "total": total_files})
        time.sleep(0.5)

def answer_question(question, context, qa_pipeline, max_chunk_size=512, max_answer_length=50):
    chunks = chunk_text(context, chunk_size=max_chunk_size)
    answers = []

    for chunk in chunks:
        try:
            result = qa_pipeline(question=question, context=chunk)
            answers.append(result["answer"][:max_answer_length])
        except Exception as e:
            print(f"Error processing chunk: {e}")

    return " ".join(answers)

qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
summarizer = pipeline("summarization", model="t5-small")

@app.route("/", methods=["GET", "POST"])
def index():
    global combined_text, file_summaries
    answer = None
    question = None

    if request.method == "POST":
        question = request.form.get("question")
        if question and combined_text:
            answer = answer_question(question, combined_text, qa_pipeline)

    print(f"Rendering with summaries: {file_summaries}")
    return render_template("index.html", question=question, answer=answer, file_summaries=file_summaries)

@app.route("/load", methods=["POST"])
def load_data():
    folder_path = "contents"  # Replace with your folder path
    combine_and_summarize_folder(folder_path, summarizer)
    return {"status": "success"}

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
