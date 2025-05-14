import os
import cv2
import pydicom
import datetime
from pydicom.dataset import FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian

# === CONFIGURATION ===
video_path = r"D:\video_to_dicom\resources\video\Untitled design.mp4"
output_dir = r"D:\video_to_dicom\resources\dicoms"

patient_id = "12345"
patient_name = "DOE^JOHN"
modality = "OT"

# === Ensure Output Folder Exists ===
os.makedirs(output_dir, exist_ok=True)

# === Read Video ===
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise IOError(f"Cannot open video file: {video_path}")

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # File Meta Info
    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = generate_uid()

    # DICOM Dataset
    ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.PatientName = patient_name
    ds.PatientID = patient_id
    ds.Modality = modality
    ds.ContentDate = datetime.datetime.now().strftime('%Y%m%d')
    ds.ContentTime = datetime.datetime.now().strftime('%H%M%S')
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID

    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.Rows, ds.Columns = gray_frame.shape
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PixelData = gray_frame.tobytes()

    # Save
    dicom_filename = f"{patient_id}_frame{frame_count}.dcm"
    dicom_path = os.path.join(output_dir, dicom_filename)
    ds.save_as(dicom_path, write_like_original=False)
    print(f"✅ Saved DICOM: {dicom_path}")
    frame_count += 1

cap.release()
print("🎉 All frames converted to DICOM.")
