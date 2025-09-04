import os
import sys
import cv2
import pydicom
import datetime
import time
from pydicom.dataset import FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian


def main():
    # === CONFIGURATION ===
    print("🔧 Starting video to DICOM conversion...")
    print(f"📋 Command line arguments: {sys.argv}")

    if len(sys.argv) < 2:
        print("❌ Error: Missing video file path")
        print("Usage: python video_to_dicom.py <video_file_path> [output_dir]")
        print("Example: python video_to_dicom.py /path/to/video.mp4")
        sys.exit(1)

    video_path = sys.argv[1]
    print(f"📥 Input video path (original): {video_path}")

    # If video_path is relative, make it absolute
    if not os.path.isabs(video_path):
        video_path = os.path.abspath(video_path)
        print(f"📥 Input video path (absolute): {video_path}")

    output_dir = (
        sys.argv[2]
        if len(sys.argv) > 2
        else os.path.join(os.path.dirname(video_path), "dicoms")
    )
    print(f"📤 Output directory: {output_dir}")

    patient_id = "12345"
    patient_name = "DOE^JOHN"
    modality = "OT"

    print(f"👤 Patient configuration:")
    print(f"   - Patient ID: {patient_id}")
    print(f"   - Patient Name: {patient_name}")
    print(f"   - Modality: {modality}")

    # Validate video file exists
    if not os.path.exists(video_path):
        print(f"❌ Error: Video file not found: {video_path}")
        sys.exit(1)

    # Get video file info
    file_size = os.path.getsize(video_path)
    video_filename = os.path.splitext(os.path.basename(video_path))[
        0
    ]  # Get filename without extension
    print(f"📊 Video file size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    print(f"📝 Video filename (for DICOM naming): {video_filename}")

    # === Ensure Output Folder Exists ===
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Output directory: {output_dir}")

    # === Read Video ===
    print("🎬 Initializing video capture...")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: Cannot open video file: {video_path}")
        print("   Possible causes:")
        print("   - File format not supported")
        print("   - File is corrupted")
        print("   - OpenCV codec missing")
        sys.exit(1)

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0

    print(f"📹 Video properties:")
    print(f"   - Resolution: {width}x{height}")
    print(f"   - FPS: {fps:.2f}")
    print(f"   - Total frames: {total_frames}")
    print(f"   - Duration: {duration:.2f} seconds")

    print(f"🎬 Processing video: {video_path}")
    start_time = time.time()

    # Collect all frames first
    frames = []
    frame_count = 0

    print("📥 Reading all frames from video...")
    while True:
        ret, frame = cap.read()
        if not ret:
            if frame_count == 0:
                print("❌ Error: Could not read any frames from video")
                cap.release()
                sys.exit(1)
            else:
                print(f"✅ Finished reading frames (total: {frame_count})")
            break

        if frame_count % 10 == 0:  # Progress update every 10 frames
            elapsed = time.time() - start_time
            fps_processed = frame_count / elapsed if elapsed > 0 else 0
            print(
                f"⏳ Reading frame {frame_count + 1}/{total_frames} (Speed: {fps_processed:.1f} fps)"
            )

        # Convert to grayscale

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frames.append(gray_frame)
        frame_count += 1

    cap.release()

    if not frames:
        print("❌ Error: No frames were read from the video")
        sys.exit(1)

    print(f"🔄 Converting {len(frames)} frames to multi-frame DICOM...")

    # Create multi-frame DICOM
    # File Meta Info
    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = generate_uid()

    print(f"📋 Creating multi-frame DICOM metadata...")
    print(f"   - SOP Instance UID: {file_meta.MediaStorageSOPInstanceUID}")

    # DICOM Dataset
    current_time = datetime.datetime.now()
    ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.PatientName = patient_name
    ds.PatientID = patient_id
    ds.Modality = modality
    ds.ContentDate = current_time.strftime("%Y%m%d")
    ds.ContentTime = current_time.strftime("%H%M%S")
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID

    # Multi-frame specific attributes
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.Rows, ds.Columns = frames[0].shape
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.NumberOfFrames = len(frames)

    # Video-specific metadata
    ds.FrameTime = (
        str(int(1000 / fps)) if fps > 0 else "33"
    )  # Frame time in milliseconds
    ds.CineRate = fps

    print(f"   - Image dimensions: {ds.Columns}x{ds.Rows}")
    print(f"   - Number of frames: {ds.NumberOfFrames}")
    print(f"   - Frame rate: {fps:.2f} fps")
    print(f"   - Frame time: {ds.FrameTime} ms")

    # Concatenate all frame data
    print("🔄 Concatenating pixel data from all frames...")
    pixel_data = b"".join(frame.tobytes() for frame in frames)
    ds.PixelData = pixel_data

    print(f"   - Total pixel data size: {len(ds.PixelData):,} bytes")

    # Generate single DICOM filename
    dicom_filename = f"{video_filename}_multiframe.dcm"
    dicom_path = os.path.join(output_dir, dicom_filename)

    print(f"💾 Saving multi-frame DICOM file: {dicom_filename}")
    try:
        ds.save_as(dicom_path, write_like_original=False)
        file_size = os.path.getsize(dicom_path)
        print(f"✅ Saved multi-frame DICOM: {dicom_path} ({file_size:,} bytes)")
    except Exception as e:
        print(f"❌ Error saving DICOM file: {e}")
        sys.exit(1)

    end_time = time.time()
    total_time = end_time - start_time
    avg_fps = frame_count / total_time if total_time > 0 else 0

    print("\n🎉 Conversion completed successfully!")
    print("📊 Summary:")
    print(f"   - Total frames processed: {frame_count}")
    print(f"   - Total time: {total_time:.2f} seconds")
    print(f"   - Average processing speed: {avg_fps:.2f} fps")
    print(f"   - Output directory: {output_dir}")
    print(f"   - Multi-frame DICOM file: {dicom_filename}")
    print(f"   - File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")


if __name__ == "__main__":
    main()
