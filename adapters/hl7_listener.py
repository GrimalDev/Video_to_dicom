import socket
import os
import pydicom

HOST = '127.0.0.1'
PORT = 2575
BUFFER_SIZE = 1024
DICOM_FOLDER = r'D:\video_to_dicom\resources\dicoms'

def extract_patient_id(hl7_message):
    try:
        for segment in hl7_message.split('\r'):
            if segment.startswith('PID'):
                return segment.split('|')[3]  # PID|||12345...
    except Exception as e:
        print(f"⚠️ Failed to parse patient ID: {e}")
    return None

def search_dicom_by_patient_id(patient_id):
    print(f"🔍 Searching for DICOMs with Patient ID: {patient_id}")

    if not os.path.exists(DICOM_FOLDER):
        os.makedirs(DICOM_FOLDER)
        print(f"📁 Created missing DICOM directory: {DICOM_FOLDER}")

    matches = []
    for file in os.listdir(DICOM_FOLDER):
        if file.endswith('.dcm'):
            try:
                ds = pydicom.dcmread(os.path.join(DICOM_FOLDER, file))
                if hasattr(ds, 'PatientID') and ds.PatientID == patient_id:
                    matches.append(file)
            except Exception as e:
                print(f"⚠️ Could not read DICOM: {file} -> {e}")
    return matches

def start_listener():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"🔌 HL7 listener started on {HOST}:{PORT}...")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"📥 Connection from {addr}")
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    continue
                message = data.decode()
                print(f"📨 Received HL7 Message:\n\n{message}\n")

                patient_id = extract_patient_id(message)
                if patient_id:
                    print(f"📌 Extracted Patient ID: {patient_id}")
                    matching_dicoms = search_dicom_by_patient_id(patient_id)
                    if matching_dicoms:
                        print("✅ Matching DICOM files found:")
                        for f in matching_dicoms:
                            print(f"  - {f}")
                    else:
                        print("❌ No matching DICOM files found.")
                else:
                    print("❌ Could not extract Patient ID from HL7 message.")

if __name__ == '__main__':
    start_listener()
