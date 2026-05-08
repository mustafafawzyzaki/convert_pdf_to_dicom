import os
import pydicom
from pydicom.uid import generate_uid
from pdf2dcm import Pdf2EncapsDCM
from datetime import datetime


def convert_pdf_to_dicom(pdf_path, dicom_tags=None):
    """
    Convert a PDF file to an encapsulated PDF DICOM and populate DICOM tags.

    Args:
        pdf_path (str): Path to the source PDF file.
        dicom_tags (dict, optional): Dictionary of DICOM tag values to set.
            Supported keys:
                - PatientName
                - PatientID
                - PatientBirthDate       (YYYYMMDD)
                - PatientSex             (M / F / O)
                - StudyDescription
                - SeriesDescription
                - StudyDate              (YYYYMMDD, defaults to today)
                - StudyTime              (HHMMSS,   defaults to now)
                - AccessionNumber
                - ReferringPhysicianName
                - InstitutionName
                - Modality               (defaults to "DOC")
                - DocumentTitle

    Returns:
        str: Success or error message.
    """
    try:
        converter = Pdf2EncapsDCM()

        # pdf2dcm saves the .dcm next to the PDF and returns a list of paths.
        converted_dcms = converter.run(path_pdf=pdf_path)

        if not converted_dcms:
            return f"Conversion returned no output files for {pdf_path}"

        dicom_output_path = str(converted_dcms[0])

        # --- Fill DICOM tags ---------------------------------------------------
        ds = pydicom.dcmread(dicom_output_path)

        tags = dicom_tags or {}
        now = datetime.now()

        # Patient-level
        ds.PatientName              = tags.get("PatientName", "")
        ds.PatientID                = tags.get("PatientID", "")
        ds.PatientBirthDate         = tags.get("PatientBirthDate", "")
        ds.PatientSex               = tags.get("PatientSex", "")

        # Study-level
        ds.StudyDescription         = tags.get("StudyDescription", "")
        ds.StudyDate                = tags.get("StudyDate", now.strftime("%Y%m%d"))
        ds.StudyTime                = tags.get("StudyTime", now.strftime("%H%M%S"))
        ds.AccessionNumber          = tags.get("AccessionNumber", "")
        ds.ReferringPhysicianName   = tags.get("ReferringPhysicianName", "")
        ds.InstitutionName          = tags.get("InstitutionName", "")

        # Series-level
        ds.Modality                 = tags.get("Modality", "DOC")
        ds.SeriesDescription        = tags.get("SeriesDescription", "")

        # Document title (Encapsulated Document Module)
        ds.DocumentTitle            = tags.get("DocumentTitle", os.path.basename(pdf_path))

        # Generate fresh UIDs so every conversion is unique
        ds.StudyInstanceUID         = tags.get("StudyInstanceUID", generate_uid())
        ds.SeriesInstanceUID        = tags.get("SeriesInstanceUID", generate_uid())
        ds.SOPInstanceUID           = generate_uid()

        ds.save_as(dicom_output_path)

        return f"Successfully converted and tagged:\n  {pdf_path}\n  -> {dicom_output_path}"

    except Exception as e:
        return f"Error: {str(e)}"


# -- Example usage --------------------------------------------------------------
if __name__ == "__main__":
    for root, dirs, files in os.walk(r"C:\Users\PaxeraHealth\Desktop\convert_pdf_to_dicom\pdf_reports"):
        for file in files:
            if file.endswith(".pdf"):
                pdf_file = os.path.join(root, file)
                tags = {
                    "PatientName":            "Doe^John",
                    "PatientID":              "PAT-001",
                    "PatientBirthDate":       "19900115",
                    "PatientSex":             "M",
                    "StudyDescription":       "Machine Utilization Report",
                    "SeriesDescription":      "PDF Report",
                    "AccessionNumber":        "ACC-2026-001",
                    "ReferringPhysicianName": "Dr. Smith",
                    "InstitutionName":        "PaxeraHealth",
                    "DocumentTitle":          "Machine Utilization Report",
                }
                
                result= convert_pdf_to_dicom(pdf_file, dicom_tags=tags)
                print(result)
