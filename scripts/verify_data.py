import os

def verify_dataset(data_dir):
    if not os.path.exists(data_dir):
        print(f"Error: Directory {data_dir} does not exist.")
        return

    breeds = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    print(f"Total breeds found: {len(breeds)}")
    
    if len(breeds) != 50:
        print(f"Warning: Expected 50 breeds, but found {len(breeds)}.")
    
    total_images = 0
    breed_counts = {}
    
    for breed in sorted(breeds):
        breed_path = os.path.join(data_dir, breed)
        images = [f for f in os.listdir(breed_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        breed_counts[breed] = len(images)
        total_images += len(images)
        if len(images) == 0:
            print(f"Warning: Breed '{breed}' has 0 images.")
            
    print(f"Total images found: {total_images}")
    print("\nBreed counts (first 5):")
    for breed in sorted(breeds)[:5]:
        print(f"  {breed}: {breed_counts[breed]}")
    print("...")
    print("\nBreed counts (last 5):")
    for breed in sorted(breeds)[-5:]:
        print(f"  {breed}: {breed_counts[breed]}")

if __name__ == "__main__":
    DATA_DIR = "/home/punith/antigravity/hemanth-prj/data/cattle"
    verify_dataset(DATA_DIR)
