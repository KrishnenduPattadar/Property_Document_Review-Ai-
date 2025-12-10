# #create this for main logic functions

# import pdfplumber
# import docx
# import pytesseract
# from PIL import Image
# import os

# def extract_text_from_file(file_path):
#     """
#     Determines file type and extracts text accordingly.
#     """
#     ext = os.path.splitext(file_path)[1].lower()
#     text = ""

#     try:
#         if ext == '.pdf':
#             with pdfplumber.open(file_path) as pdf:
#                 for page in pdf.pages:
#                     text += page.extract_text() + "\n"
                    
#         elif ext == '.docx':
#             doc = docx.Document(file_path)
#             for para in doc.paragraphs:
#                 text += para.text + "\n"
                
#         elif ext in ['.jpg', '.jpeg', '.png']:
#             image = Image.open(file_path)
#             text = pytesseract.image_to_string(image)
            
#         else:
#             text = "Unsupported file format."
            
#     except Exception as e:
#         text = f"Error extracting text: {str(e)}"

#     return text