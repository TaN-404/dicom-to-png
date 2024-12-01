import json
from collections import Counter

# Read the JSON file
data = 'output/metadata_train_with_annotations.json'
with open(data) as f:
    metadata = json.load(f)

# Count lesion types
lesion_counts = Counter()
for record in metadata:
    lesion_counts.update(record['lesion_types'])

# Print counts for each lesion type
print("\nLesion Type Counts:")
for lesion_type, count in lesion_counts.items():
    print(f"{lesion_type}: {count}")