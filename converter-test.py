import os
import pydicom
import numpy as np
from PIL import Image
import json
import pandas as pd


# Paths for input and output
path_train_png = r"/home/tan404/datasets/physionet.org/files/vindr-spinexr/1.0.0/test"
path_train_dicom = r"/home/tan404/datasets/physionet.org/files/vindr-spinexr/1.0.0/test_images"
metadata_excel = r"filter_data/dicom_info_updated_TEST.xlsx"  # Path to the Excel file_

def convert_dicom_to_png_with_excel_metadata(dicom_dir, output_dir, metadata_file, excel_path):
    """
    Convert DICOM files to PNG format based on a metadata Excel sheet and extract DICOM tags.

    Parameters:
    - dicom_dir: Path to the directory containing DICOM files.
    - output_dir: Path to save the converted PNG images.
    - metadata_file: Path to save the output JSON file with metadata.
    - excel_path: Path to the Excel file containing metadata and filenames.
    """
    # Load metadata from Excel
    excel_data = pd.read_excel(excel_path)
    # Assuming the Excel sheet has columns 'Filename', 'Patient Age', 'Patient Sex'
    dicom_files = excel_data['Filename'].values  # List of DICOM filenames
    metadata = []

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    total_files = len(dicom_files)
    print(f"Starting conversion of {total_files} files...")
    
    for idx, filename in enumerate(dicom_files, 1):
        # Print progress
        progress = (idx / total_files) * 100
        print(f"Processing file {idx}/{total_files} ({progress:.1f}%)...", end='\r')
        
        dicom_path = os.path.join(dicom_dir, filename)
        if not os.path.exists(dicom_path):
            print(f"\nFile not found: {dicom_path}")
            continue
        
        try:
            dicom = pydicom.dcmread(dicom_path)

            # Normalize pixel values
            image = dicom.pixel_array
            intercept = dicom.RescaleIntercept if 'RescaleIntercept' in dicom else 0
            slope = dicom.RescaleSlope if 'RescaleSlope' in dicom else 1
            image = (image * slope + intercept).astype(np.float32)
            
            # Apply Photometric Interpretation
            if dicom.PhotometricInterpretation == "MONOCHROME1":
                image = np.max(image) - image  # Invert for MONOCHROME1
            
            # Contrast adjustment using Window Center and Width
            if 'WindowCenter' in dicom and 'WindowWidth' in dicom:
                center = float(dicom.WindowCenter[0] if isinstance(dicom.WindowCenter, pydicom.multival.MultiValue) else dicom.WindowCenter)
                width = float(dicom.WindowWidth[0] if isinstance(dicom.WindowWidth, pydicom.multival.MultiValue) else dicom.WindowWidth)
                lower_bound = center - (width / 2)
                upper_bound = center + (width / 2)
                image = np.clip((image - lower_bound) / (upper_bound - lower_bound), 0, 1) * 255
            
            # Resize to a consistent size
            image = np.clip(image, 0, 255)
            image = Image.fromarray(image.astype(np.uint8))
            output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".png")
            image.save(output_path)
            
            # Add metadata
            row_data = excel_data[excel_data['Filename'] == filename].iloc[0]
            
            # Extract age value, removing any non-numeric characters
            age_str = str(row_data['Patient Age'])
            age_value = int(''.join(filter(str.isdigit, age_str))) if pd.notna(row_data['Patient Age']) else None
            
            # Convert MultiValue objects to lists for JSON serialization
            window_center = [float(dicom.WindowCenter)] if isinstance(dicom.WindowCenter, pydicom.valuerep.DSfloat) else list(dicom.WindowCenter) if 'WindowCenter' in dicom else None
            window_width = [float(dicom.WindowWidth)] if isinstance(dicom.WindowWidth, pydicom.valuerep.DSfloat) else list(dicom.WindowWidth) if 'WindowWidth' in dicom else None

            metadata.append({
                "filename": output_path,
                "age": age_value,
                "gender": row_data['Patient Sex'] if pd.notna(row_data['Patient Sex']) else None,
                "pixel_spacing": list(dicom.PixelSpacing) if 'PixelSpacing' in dicom else None,
                "window_center": window_center,
                "window_width": window_width
            })
        except Exception as e:
            print(f"\nFailed to process {filename}: {e}")

    print("\nConversion completed!")
    print(f"Successfully processed {len(metadata)} out of {total_files} files")

    # Save metadata to JSON
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4)

# Usage
convert_dicom_to_png_with_excel_metadata(
    dicom_dir=path_train_dicom,
    output_dir=path_train_png,
    metadata_file="metadata.json",
    excel_path=metadata_excel
)
