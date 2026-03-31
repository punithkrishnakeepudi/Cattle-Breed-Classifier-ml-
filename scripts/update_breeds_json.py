import json
import os

with open('src/data/breeds.json', 'r') as f:
    breeds = json.load(f)

# Get available images from public/breeds/
available_imgs = os.listdir('public/breeds')

def normalize(s):
    return s.lower().replace('-', '').replace(' ', '').replace('_', '')

for breed in breeds:
    # Remove emoji
    if 'emoji' in breed:
        del breed['emoji']
    
    # Match image
    bname = normalize(breed['name'])
    match = None
    for img in available_imgs:
        iname = normalize(img.split('.')[0])
        if bname == iname:
            match = img
            break
    
    if match:
        breed['image'] = f"/breeds/{match}"
    else:
        breed['image'] = None

with open('src/data/breeds.json', 'w') as f:
    json.dump(breeds, f, indent=2)

print("Successfully updated breeds.json: Removed emojis and added image paths.")
