def pdf_to_txt(pdf_name):
    pdf_path = f"/Users/issacleung/ollama_trial/data/{pdf_name}.pdf"
    txt_path = f"/Users/issacleung/ollama_trial/data/{pdf_name}.txt"

    print(f"Converting {pdf_path} to {txt_path}...")
#PyMuPDF(fitz) is used in here
    import fitz 
    doc = fitz.open(pdf_path)
    with open(txt_path, "w", encoding="utf-8") as txt_file:
        for page in doc:
            txt_file.write(page.get_text() + "\n")
    print(f"Conversion complete: {txt_path}")

for file_name in ["clientcenter", "health", "person", "musictherapy"]:
    pdf_to_txt(file_name)
