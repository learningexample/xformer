import os
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from transformers import pipeline

def read_pdf(file_path):
    """Read the text content from a PDF file."""
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def read_html(file_path):
    """Read the text content from an HTML file."""
    text = ""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            text = soup.get_text()
    except Exception as e:
        print(f"Error reading HTML {file_path}: {e}")
    return text

def read_text(file_path):
    """Read the text content from a plain text file."""
    text = ""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
    except Exception as e:
        print(f"Error reading text file {file_path}: {e}")
    return text

def read_folder(content):
    """Read all PDF, HTML, and text files in the specified content folder."""
    file_contents = {}
    for root, dirs, files in os.walk(content):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(".pdf"):
                file_contents[file] = read_pdf(file_path)
            elif file.lower().endswith((".html", ".htm")):
                file_contents[file] = read_html(file_path)
            elif file.lower().endswith(".txt"):
                file_contents[file] = read_text(file_path)
            else:
                print(f"Skipping unsupported file: {file}")
    return file_contents

def summarize_text(text, summarizer, chunk_size=512, max_summary_length=128):
    """Summarize the text using the LLM model."""
    # Split the text into manageable chunks
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    summaries = []
    for chunk in chunks:
        # Summarize each chunk with a shorter max_length
        summary = summarizer(chunk, max_length=max_summary_length, min_length=30, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    return " ".join(summaries)

# Initialize the summarizer model
summarizer = pipeline("summarization", model="t5-small")

# Specify the folder containing content
content = "content"

# Read contents of the folder
contents = read_folder(content)

# Summarize the content of each file
summaries = {}
for filename, content in contents.items():
    print(f"Summarizing {filename}...")
    summaries[filename] = summarize_text(content, summarizer, chunk_size=512, max_summary_length=128)

# Print summaries
for filename, summary in summaries.items():
    print(f"--- Summary for {filename} ---")
    print(summary)
    print("\n")
