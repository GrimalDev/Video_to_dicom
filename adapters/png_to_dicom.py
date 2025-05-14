from pathlib import Path
import os
import cv2
import numpy as np
from PIL import Image
import pydicom
from pydicom.dataset import FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
import datetime

# === CONFIGURATION ===
video_path = r"D:\video_to_dicom\resources\video\Untitled design.mp4"
frames_dir = r"D:\video_to_dicom\resources\png_output"
dicom_dir = r"D:\video_to_dicom\resources\png_to_dicom"

# === Ensure Output Folders Exist ===
os.makedirs(frames_dir, exist_ok=True)
os.makedirs(dicom_dir, exist_ok=True)

# === STEP 1: Convert Video to PNG Frames ===
cap = cv2.VideoCapture(video_path)
frame_count = 0

if not cap.isOpened():
    raise IOError(f"Cannot open video file: {video_path}")

print("🔁 Extracting frames from video...")
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_path = os.path.join(frames_dir, f"frame_{frame_count:04d}.png")
    cv2.imwrite(frame_path, frame)
    print(f"✅ Saved frame: {frame_path}")
    frame_count += 1

cap.release()
print("🎉 All video frames extracted.")

# === STEP 2: Convert PNG Frames to DICOM Files ===
print("🔁 Converting PNG frames to DICOM...")
for png_file in sorted(os.listdir(frames_dir)):
    if png_file.endswith('.png'):
        png_path = os.path.join(frames_dir, png_file)
        image = Image.open(png_path).convert("L")
        pixel_array = np.array(image)

        file_meta = pydicom.Dataset()
        file_meta.MediaStorageSOPClassUID = pydicom.uid.SecondaryCaptureImageStorage
        file_meta.MediaStorageSOPInstanceUID = generate_uid()
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        file_meta.ImplementationClassUID = generate_uid()

        dt = datetime.datetime.now()
        dicom_path = os.path.join(dicom_dir, f"{os.path.splitext(png_file)[0]}.dcm")
        ds = FileDataset(dicom_path, {}, file_meta=file_meta, preamble=b"\0" * 128)

        ds.PatientName = "DOE^JOHN"
        ds.PatientID = "12345"
        ds.StudyInstanceUID = generate_uid()
        ds.SeriesInstanceUID = generate_uid()
        ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        ds.SOPClassUID = file_meta.MediaStorageSOPClassUID

        ds.Modality = "OT"
        ds.ContentDate = dt.strftime('%Y%m%d')
        ds.ContentTime = dt.strftime('%H%M%S')
        ds.Rows, ds.Columns = pixel_array.shape
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.PixelRepresentation = 0
        ds.BitsStored = 8
        ds.BitsAllocated = 8
        ds.HighBit = 7
        ds.PixelData = pixel_array.tobytes()

        ds.is_little_endian = True
        ds.is_implicit_VR = False
        ds.save_as(dicom_path)
        print(f"✅ Saved DICOM: {dicom_path}")

print("🎯 Video to DICOM conversion complete.")
