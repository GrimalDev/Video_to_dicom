# Video to DICOM Conversion with HL7 Integration

## Overview

This project provides a complete pipeline for converting videos (such as ultrasound or endoscopic footage) into **DICOM (Digital Imaging and Communications in Medicine)** files. It supports extracting DICOM files back into PNG images and uses the **HL7 (Health Level 7)** protocol to search and access patient-specific DICOM data.

## Folder Structure

```bash
video_to_dicom/
├── adapters/
│   ├── video_to_dicom.py        # Converts video frames to DICOM files
│   ├── dicom_to_png.py          # Converts DICOM files to PNG images
│   ├── hl7_sender_adapter.py    # Sends HL7 messages with Patient ID
├── resources/
│   ├── video/                   # Source videos
│   │   └── Untitled design.mp4
│   └── dicom_output/            # Output DICOM files
├── hl7_listener.py             # Listens for incoming HL7 messages
├── hl7_sender.py               # Sends HL7 messages
├── png_to_dicom.py             # Converts PNGs back to DICOM (optional)
├── video_to_png.py             # Extracts frames from video to PNGs (optional)
```

## Features

* Convert video frames to DICOM files with metadata (Patient ID, Name, Modality).
* Convert DICOM files to PNG images.
* HL7 listener to receive patient queries and search for DICOM files by Patient ID.
* HL7 sender to send patient lookup messages.

## Usage

### 1. Video to DICOM Conversion

```bash
python adapters/video_to_dicom.py
```

### 2. DICOM to PNG Conversion

```bash
python adapters/dicom_to_png.py
```

### 3. HL7 Protocol

#### Run HL7 Listener:

```bash
python hl7_listener.py
```

#### Send HL7 Message:

```bash
python hl7_sender.py
```

#### Example HL7 Message Format:

```
MSH|^~\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|20240513||ADT^A01|123456|P|2.3
PID|||12345||DOE^JOHN
```

## Requirements

* Python 3.x
* OpenCV
* pydicom

## Future Improvements

* GUI for easy upload and conversion.
* Integrate with a PACS server.
* Advanced HL7 ORM/ORU message handling.
