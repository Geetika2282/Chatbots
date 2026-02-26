import pyarrow as pa 
import tempfile
import lancedb
# import PyPDF2
import re
import ollama
from PyPDF2 import PdfReader

# 1. Read PDF and extract text
def readPDF(pdf_path):
    reader = PdfReader(pdf_path)
    extracted_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"

    temp_txt = tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False)

    try:
        temp_txt.write(extracted_text)
        temp_txt.close()
        return temp_txt.name
    except Exception as e:
        import os
        os.unlink(temp_txt.name)
        raise e

# Loads data from temp file
def load_data(txt_path):
    with open(txt_path, 'r') as f:
        return f.read()


# ===============================================
# 2. CHUNKING 
# ===============================================
def smart_chunk_resume(text):
    sections = re.split(r'\n[A-Z\s]{3,}\n', text)
    chunks = []
    for sec in sections:
        clean = sec.strip()
        if len(clean) > 50:
            chunks.append(clean)
    return chunks

def chunk_text(text, chunk_size=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i: i+chunk_size])
        chunks.append(chunk)
    return chunks

# ===============================================
# 3. EMBEDDING 
# ===============================================
def get_embedding(text):
    response = ollama.embeddings(
        model="embeddinggemma",
        prompt=text
    )
    return response['embedding']

# ===============================================
# 4. SEARCHING 
# ===============================================
def search_doc(question, top_k=3):
    q_emb = get_embedding(question)
    results = table.search(q_emb).limit(top_k).to_list()
    return [r["text"] for r in results]


# ===============================================
# 5. ASKING QUESTIONS 
# ===============================================
def ask(question, top_k=3):
    # Step 1: Retrieve relevant chunks
    context_chunks = search_doc(question, top_k)
    context = "\n\n".join(context_chunks)

    # Step 2: Generate a direct answer using LLM
    response = ollama.chat(
        model="gemma3:1b",  # change this to your available model (run 'ollama list' to check)
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer the question using only the provided context. Be concise and direct."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ]
    )
    return response['message']['content']


# ── Main ─────────────────────────────────────────

temp_file_path = readPDF("C:\\Users\\geetikak\\Documents\\GitHub\\Chatbots\\RAG-00\\example.pdf")
print(f"Text saved to: {temp_file_path}")

text = load_data(temp_file_path)
chunks = chunk_text(text, 200)

# Vector DB
db = lancedb.connect("mydb")

schema = pa.schema([
    pa.field("vector", pa.list_(pa.float32(), 768)),
    pa.field("text", pa.string())
])

table = db.create_table(
    "chunks",
    data=[],
    schema=schema,
    mode="overwrite"
)

data = []
for chunk in chunks:
    emb = get_embedding(chunk)
    data.append({
        "vector": emb,
        "text": chunk
    })

table.add(data)
print("Stored in vector DB")

# ── Ask Questions ──────────────────────────────────────────────────
print("_" * 60)
print("Candidate name:")
print(ask("What is the candidate name?"))

print("_" * 60)
print("Company name:")
print(ask("Where does she currently work?"))

print("_" * 60)
print("Skills:")
print(ask("What are her technical skills?"))
