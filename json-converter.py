import json 


import json

# Load the JSON data from a file (assuming you have a JSON file named "metadata.json")
with open('metadata-train.json', 'r') as f:
    data = json.load(f)  # Ensure this is loaded as a list of dictionaries

# Update filenames to keep only the actual file name
for entry in data:
    if isinstance(entry, dict):  # Make sure entry is a dictionary
        entry["filename"] = entry["filename"].split("/")[-1]

# Save the updated data to a JSON file
with open('metadata_train_updated.json', 'w') as f:
    json.dump(data, f, indent=4)
