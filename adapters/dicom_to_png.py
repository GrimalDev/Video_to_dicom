import os
import pydicom
import cv2
import numpy as np

# === FIXED PATH ===
dicom_dir = r"D:\video_to_dicom\resources\dicoms"
output_dir = r"D:\video_to_dicom\resources\png_output"
os.makedirs(output_dir, exist_ok=True)

# === Convert All DICOMs in Folder ===
for filename in os.listdir(dicom_dir):
    if filename.endswith(".dcm"):
        dicom_path = os.path.join(dicom_dir, filename)
        ds = pydicom.dcmread(dicom_path)

        # Ensure Transfer Syntax UID is set
        if 'TransferSyntaxUID' not in ds.file_meta:
            ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

        # Get pixel data
        pixel_array = ds.pixel_array

        # Normalize pixel values to 0-255 if needed
        if pixel_array.max() > 255:
            pixel_array = (pixel_array / pixel_array.max()) * 255.0
        pixel_array = pixel_array.astype(np.uint8)

        # Save PNG
        png_filename = os.path.splitext(filename)[0] + ".png"
        png_path = os.path.join(output_dir, png_filename)
        cv2.imwrite(png_path, pixel_array)
        print(f"✅ Saved PNG: {png_path}")

print("🎉 DICOM to PNG conversion complete.")
