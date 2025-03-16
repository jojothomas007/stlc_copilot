import os
from docx import Document
# import pythoncom
# import win32com.client as win32
import logging
from io import BytesIO
import pypdf
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

class ContentManager:
        
    def extract_from_bytes(self, content_type:str, content_bytes):
        content:str = " "
        if content_type == "application/pdf":
            content =  self.extract_from_pdf_bytes(content_bytes)
        elif content_type == "text/plain":
            content =  self.extract_from_text_bytes(content_bytes)
        elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document": # MS Word Docx format
            content =  self.extract_from_docx_bytes(content_bytes)
        # elif content_type == "application/msword": # MS Word .Doc format
        #     return self.extract_from_doc_bytes(content_bytes)
        else:
            logger.warning("The content type %s is not supported. And hence data not extracted", content_type)
            content =  " "
        return content

    def extract_from_pdf_bytes(self, pdf_bytes):
        # Create a BytesIO object from the bytes content
        byte_stream = BytesIO(pdf_bytes)        
        # Open the PDF file from the stream
        pdf_document = pypdf.PdfReader(byte_stream)        
        # Initialize an empty string to hold the extracted text
        extracted_text = ""        
        for page in pdf_document.pages:
            extracted_text += page.extract_text() 
        pdf_document.close()       
        byte_stream.close()
        return extracted_text
    
    def extract_from_text_bytes(self, content_bytes):
        # Create a BytesIO object from the bytes content
        byte_stream = BytesIO(content_bytes)        
        # Open the PDF file from the stream
        content_text = byte_stream.read().decode('utf-8') 
        byte_stream.close()
        return content_text

    # Extracting from MS Word Docx format
    def extract_from_docx_bytes(self, docx_bytes):
        # Create a BytesIO object from the bytes content
        byte_stream = BytesIO(docx_bytes)    
        # Load the document from the BytesIO stream
        document = Document(byte_stream)        
        # Initialize an empty string to hold the extracted text
        extracted_text = ""        
        # Iterate over each paragraph in the document and extract text
        for para in document.paragraphs:
            extracted_text += para.text + "\n"    
        byte_stream.close()    
        return extracted_text

    # # Extracting from old MS Word .Doc format
    # def extract_from_doc_bytes(self, doc_bytes):
    #     # Create a temporary file to save the byte content
    #     temp_file = 'temp.doc'
    #     temp_path = os.path.join(os.getcwd(), temp_file)
    #     with open(temp_file, 'wb') as f:
    #         f.write(doc_bytes)
        
    #     # Initialize COM interface for Word application
    #     pythoncom.CoInitialize()
    #     word = win32.Dispatch("Word.Application")
    #     word.Visible = False
        
    #     # Open the temporary file
    #     doc = word.Documents.Open(temp_path)
        
    #     # Extract text from the document
    #     extracted_text = doc.Content.Text
        
    #     # Close the document and quit Word application
    #     doc.Close(False)
    #     word.Quit()
        
    #     return extracted_text