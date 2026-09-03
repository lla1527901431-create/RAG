import fitz

pdf = fitz.open("documents/STM32.pdf")

for page in pdf:
    text = page.get_text()
    print(text)

pdf.close()