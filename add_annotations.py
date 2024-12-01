import json
import pandas as pd

# Load metadata JSON files
with open('output/metadata_test_updated.json', 'r') as f:
    metadata_test = json.load(f)

with open('output/metadata_train_updated.json', 'r') as f:
    metadata_train = json.load(f)

# Load annotation CSV files
test_annotations = pd.read_csv('filter_data/test.csv')
train_annotations = pd.read_csv('filter_data/train.csv')

# Function to add annotations to metadata
def add_annotations_to_metadata(metadata, annotations):
    for entry in metadata:
        filename = entry['filename']
        filename_no_ext = filename[:-4]  # Remove .png extension
        
        # Find the corresponding row(s) in the annotations dataframe
        matched_rows = annotations[annotations['filename'] == filename_no_ext]
        
        print(f"Processing {filename}: Found {len(matched_rows)} matches.")  # Debugging output
        
        if not matched_rows.empty:
            entry['lesion_types'] = matched_rows['lesion_type'].tolist()
            
            # Handle NaN values in bounding boxes
            bounding_boxes = []
            for _, row in matched_rows.iterrows():
                if pd.isna(row['xmin']) or pd.isna(row['ymin']) or pd.isna(row['xmax']) or pd.isna(row['ymax']):
                    bounding_boxes.append("NaN")
                else:
                    bounding_boxes.append([row['xmin'], row['ymin'], row['xmax'], row['ymax']])
            entry['bounding_boxes'] = bounding_boxes
            
            print(f"Added annotations for {filename}")  # Debugging output

# Add annotations to both test and train metadata
add_annotations_to_metadata(metadata_test, test_annotations)
add_annotations_to_metadata(metadata_train, train_annotations)

# Save the updated metadata JSON files
with open('output/metadata_test_with_annotations.json', 'w') as f:
    json.dump(metadata_test, f, indent=4)

with open('output/metadata_train_with_annotations.json', 'w') as f:
    json.dump(metadata_train, f, indent=4)

# Output the file paths for download
output_files = {
    "test_metadata": "output/metadata_test_with_annotations.json",
    "train_metadata": "output/metadata_train_with_annotations.json"
}

output_files
