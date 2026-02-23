import tempfile
import PyPDF2
import re

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



temp_file_path = readPDF("example.pdf")
print(f"Text saved to: {temp_file_path}")

text = load_data(temp_file_path)
print(text)

chunks = chunk_text(text, 1)
print("+" * 80)
print(len(chunks[0]))
print("+" * 80)
print(chunks)
print("+" * 80)
