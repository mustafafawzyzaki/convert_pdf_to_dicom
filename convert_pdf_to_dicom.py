import os 
import pydicom
import pynetdicom 
from pdf2dcm  import Pdf2EncapsDCM

def convert_pdf_to_dicom(pdf_path):
    try:
        dataset = pydicom.dataset.Dataset()

        
    except Exception as e:
        return f"Error: {str(e)}"
