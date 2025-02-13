import os
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset
from langchain.document_loaders import PyPDFLoader

# pip install langchain langchain-community chromadb faiss-cpu pypdf sentence-transformers llama-cpp-python requests tqdm

# 1️ Load a Small Model from Hugging Face
MODEL_NAME = "google/flan-t5-small"  # Tiny 60M param model (~200MB)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# 2️ Function to Extract Text from PDFs
def load_pdf_text(pdf_folder):
    texts = []
    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(pdf_folder, file))
            docs = loader.load()
            texts.extend([doc.page_content for doc in docs])  # Extract text
    return texts

# 3️ Load and Process Dataset
pdf_folder = "contents"  # Change this to your actual PDF folder
documents = load_pdf_text(pdf_folder)  # Extract text from PDFs

# Ensure there's training data
if not documents:
    documents = ["This is a placeholder text. Add PDFs to train a real model."]

dataset = Dataset.from_dict({"text": documents})

# 4️ Tokenization Function (Fixes `decoder_input_ids` Issue)
def tokenize_function(examples):
    model_inputs = tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

    # Set decoder inputs (important for T5 models)
    with tokenizer.as_target_tokenizer():
        model_inputs["labels"] = tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)["input_ids"]

    return model_inputs

# Tokenize dataset
tokenized_datasets = dataset.map(tokenize_function, batched=True)

# 5️ Define Training Arguments (Optimized for Low Memory)
training_args = TrainingArguments(
    output_dir="./tiny_model",
    per_device_train_batch_size=1,  # Low memory footprint
    num_train_epochs=2,  # Reduce epochs to save RAM
    save_strategy="epoch",
    logging_dir="./logs",
    fp16=False,  # Avoid FP16 on CPU (only use for GPU)
)

# 6️ Fine-Tune the Model
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets,
)

trainer.train()

# 7️ Save the Fine-Tuned Model
model.save_pretrained("./tiny_model")
tokenizer.save_pretrained("./tiny_model")

print("✅ Fine-tuning complete! Model saved to './tiny_model'.")

# 8️ Load Fine-Tuned Model for Inference
def generate_text(prompt):
    model = AutoModelForSeq2SeqLM.from_pretrained("./tiny_model")
    tokenizer = AutoTokenizer.from_pretrained("./tiny_model")
    
    # Tokenize input text
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding="max_length", max_length=128)

    # Generate text (Fix: Use max_new_tokens instead of max_length)
    outputs = model.generate(**inputs, max_new_tokens=100)  # Adjust tokens as needed
    
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Example usage
print("\n Example Generated Text:")
print(generate_text("What is the summary of this document?"))

# 9️ (optional) Upload model to Hugging Face Hub
# model.push_to_hub("your-hf-username/your-fine-tuned-model")
# tokenizer.push_to_hub("your-hf-username/your-fine-tuned-model")
