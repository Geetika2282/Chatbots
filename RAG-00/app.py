import tempfile
import lancedb
import PyPDF2
import re
import ollama

from PyPDF2 import PdfReader

def readPDF(pdf_path):
    reader = PdfReader(pdf_path)
    extracted_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    
        # 'delete=False' keeps the file on disk after closing so your RAG can read it

    temp_txt = tempfile.NamedTemporaryFile(mode='w+', suffix='.txt',delete=False)

    try:
        temp_txt.write(extracted_text)
        temp_txt.close()
        return temp_txt.name
    except Exception as e:
        import os
        os.unlink((temp_txt.name))
        raise e

# load and print pdf->text data
def load_data(txt_path):
    with open(txt_path, 'r') as f:
        return f.read()
    

def smart_chunk_resume(text):
    sections = re.split(r'\n[A-Z\s]{3,}\n', text)
    chunks = []

    for sec in sections:
        clean = sec.strip()
        if len(clean) > 50:
            chunks.append(clean)

    return chunks  

def chunk_text(text, chunk_size=300):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i: i+chunk_size])
        chunks.append(chunk)
    return chunks



temp_file_path = readPDF("C:\\Users\\geetikak\\Documents\\GitHub\\Chatbots\\RAG-00\\example.pdf")
print(f"Text saved to: {temp_file_path}")

text = load_data(temp_file_path)
print(text)
chunks = chunk_text(text, 10)
for k in range(len(chunks)):
    print(f"{k}:{chunks[k]}\n")


print("=" * 80)
print(chunks[6])
print("=" * 80)
print("+" * 80)

# Vector DB
db = lancedb.connect("mydb")

def get_embedding(text):
    response = ollama.embeddings(
        model="embeddinggemma",
        prompt=text
    )
    return response['embedding']

print(len(get_embedding("hello")))

table = db.create__table(
    "chunks",
    data=[{
        "Vector": get_embedding("test"),
        "text": "test"
    }],
    mode="overwrite"
)

def smart_chunk_resume(text):
    sections = re.split(r'\n[A-Z\s]{3,}\n', text)
    chunks = []

    for sec in sections:
        clean = sec.strip()
        if len(clean) > 50:
            chunks.append(clean)
            